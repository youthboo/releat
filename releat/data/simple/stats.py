"""Statistical Features.

Simple statistical calculations for tick groups


"""
from __future__ import annotations

import math
from functools import partial

import numpy as np
import polars as pl
from numba import njit


def get_last(df_group, fc):
    """Last value in group.

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (pydantic.BaseModel):
            feature config

    Returns:
        pl.DataFrame:
            last value for each group

    """
    col = fc.inputs[0]
    df = df_group.agg(
        [
            pl.col(col).last().alias("feat"),
        ],
    )
    return df


def get_mean(df_group, fc):
    """Average value in group.

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (pydantic.BaseModel):
            feature config

    Returns:
        pl.DataFrame:
            average value for each group

    """
    col = fc.inputs[0]
    df = df_group.agg(
        [
            pl.col(col).mean().alias("feat"),
        ],
    )
    return df


def get_min(df_group, fc):
    """Min value in group.

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (pydantic.BaseModel):
            feature config

    Returns:
        pl.DataFrame:
            min value for each group relative to
            the average value of the group

    """
    col = fc.inputs[0]
    df = df_group.agg(
        [
            (pl.col(col).mean() - pl.col(col).min()).alias("feat"),
        ],
    )
    return df


def get_max(df_group, fc):
    """Max value in group.

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (pydantic.BaseModel):
            feature config

    Returns:
        pl.DataFrame:
            max value for each group relative to
            the average value of the group

    """
    col = fc.inputs[0]
    df = df_group.agg(
        [
            (pl.col(col).max() - pl.col(col).mean()).alias("feat"),
        ],
    )
    return df


def get_skew(df_group, fc, pip):
    """Skew of group.

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (pydantic.BaseModel):
            feature config
        pip (float):
            pip value, i.e. 1e-4 for EURUSD

    Returns:
        pl.DataFrame:
            skew of group if there are more than min_num tick in group.
            #TODO scaling doesnt affect skew, remove pip input

    """
    col = fc.inputs[0]
    df = (
        df_group.agg(
            [
                ((pl.col(col) - pl.col(col).first()) / pip).skew().alias("feat"),
                pl.col(col).alias("raw"),
            ],
        )
        .with_columns(
            pl.when(pl.col("raw").list.lengths() > fc.kwargs["min_num"])
            .then(pl.col("feat"))
            .otherwise(0)
            .alias("feat"),
        )
        .select(["time_msc", "feat"])
    )
    return df


def one_hot_fx_flag(df_group, fc):
    """One hot enconding for flag.

    Applies to fx only because futures and stocks have more flags
    #TODO create a one_hot_flag for other trading instruments

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (pydantic.BaseModel):
            feature config

    Returns:
        pl.DataFrame:
            one hot encoded flags where the values are the total number
            of flags + percentage made up by 2 and 4 flags.

    """
    col = fc.inputs[0]
    df = (
        df_group.agg(
            [
                (pl.col(col) == 2).sum().alias("feat_2"),
                (pl.col(col) == 4).sum().alias("feat_4"),
                (pl.col(col) == 6).sum().alias("feat_6"),
            ],
        )
        .with_columns(
            (pl.col("feat_6") + pl.col("feat_4") + pl.col("feat_2")).alias("feat_6"),
        )
        .with_columns((pl.col("feat_2") / pl.col("feat_6")).alias("feat_2"))
        .with_columns((pl.col("feat_4") / pl.col("feat_6")).alias("feat_4"))
    )
    return df


@njit(
    "Tuple((float32[:],float32[:,:],float32[:],float32[:]))(float32[:,:], float32[:,:])",
)
def calc_grad_and_error(x, y):
    """Calc grad and error.

    Simple linear least squares

    Args:
        x (np.array)
            1-d array (i think)
        y (np.array)
            also 1-d i think

    Returns:
        grad (np.float)
            gradient in radians
        err (np.float)
            error
        m (np.float)
            gradient as integer on euclidean plane
        c (np.float)
            y intercept

    """
    A = np.hstack((x, np.ones((len(x), 1), dtype="float32")))
    m, c = np.linalg.lstsq(A, y)[0]

    # main gradient
    grad = np.arctan(m) * 180 / math.pi

    # calculate residuals
    err = y - (m * x[:, :1] + c)
    return grad.astype("float32"), err, m, c


@njit("float32(float32[:],float32[:],float32,int32)")
def calc_grad(x, y, pip=1e-4, min_num=10):
    """Calc gradient feature.

    Wrapper for calc_grad_and_error

    Args:
        x (np.array)
            1 d array
        y (np.array)
            1 d i think
        pip (float)
            pip value
        min_num (int)
            minimum required to return gradient

    Returns:
        np.float
            gradient in radians

    """
    if len(y) < min_num:
        return 0.0

    # y = y * (len(y) / (y.max() - y.min()))
    y = (y - y.min()) / pip
    y = y.astype("float32").reshape((-1, 1))
    # x = np.arange(len(y)).astype("float32").reshape(-1, 1)
    x = x.astype("float32").reshape((-1, 1))
    grad, _, _, _ = calc_grad_and_error(x, y)
    return grad[0]


def calc_gradient_feature(df_group, fc, pip):
    """Apply gradient to group.

    Args:
        df_group (pl.GroupBy):
            ticks grouped by the feature timeframe
        fc (dict):
            feature configuration
        pip (float):
            i.e. 1e-4

    Returns:
        pl.DataFrame:
            Gradient for tick group if there are more than min_num ticks

    """
    col = fc.inputs[0]

    def get_grad(pip: float, min_num: int, struct: dict) -> pl.Series:
        """Gradient of series."""
        x = np.array(struct["x"], dtype=np.float32)
        y = np.array(struct["y"], dtype=np.float32)
        val = calc_grad(x, y, pip, min_num)
        return tuple([val])

    p_get_grad = partial(get_grad, pip, fc.kwargs["min_num"])

    df = (
        df_group.agg(
            [
                pl.col(col).alias("y"),
                (
                    (pl.col("time_msc") - pl.col("time_msc").first()).cast(pl.Int64)
                    * 1e-9
                    / 60
                ).alias("x"),
            ],
        )
        .with_columns(pl.struct(["x", "y"]).apply(p_get_grad).alias("feat"))
        .with_columns(pl.col("feat").cast(pl.List(pl.Float32)))
        .with_columns(pl.col("feat").list.get(0))
        .select(["time_msc", "feat"])
    )

    return df


@njit("int32(int32, int32)")
def randint(low, high):
    """Random integer.

    Args:
        low (int)
        high (int)

    Returns:
        int
            an integer between the low and high numbers

    """
    return np.random.randint(low, high)


@njit("float32[:](float32[:])")
def sign(ts):
    """Sign.

    Args:
        ts (float or np.array)

    Returns:
        np.array

    """
    return np.sign(ts)


@njit("float32[:](float32[:],int32)")
def log(ts, base=-1):
    """Log.

    Args:
        ts (float or np.array)
        base (int)

    Returns:
        float or np.array

    """
    if base == -1:
        return np.log(ts).astype("float32")
    else:
        return (np.log(ts) / np.log(base)).astype("float32")


@njit("float32[:](float32[:], float32, int32)")
def apply_log_tail(ts, thresh, log_base):
    """Two-sided log.

    Args:
        ts (np.array)
        thresh (float)
            threshold to start log
        log_base (float)

    Returns:
        np.array

    """
    a = ts > thresh
    ts[a] = thresh + log(ts[a] + 1 - thresh, log_base)

    a = ts < -thresh

    ts[a] = -thresh - log(ts[a] * sign(ts[a]) + 1 - thresh, log_base)

    return ts
