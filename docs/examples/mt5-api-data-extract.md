# Data extraction via MT5 Api

Jupyter notebook: examples/mt5-api-data-extract.ipynb

Each trading symbol has its own process for the wine mt5 api. This is so that in production, we're able to reduce latency (at the cost of higher memory consumption) by pulling from one or more brokers in parallel.

### IMPORTANT - start mt5 apis

Before running this notebooks, first launch the mt5 apis from the terminal using the command: releat launch-all-mt5-apis

Launching wine processes from jupyter notebooks is unstable and mostly fails to start


```python
from releat.utils.configs.constants import mt5_api_port_map
import requests
from concurrent.futures import ThreadPoolExecutor
from releat.workflows.service_manager import kill_processes, get_pids, stop_mt5
from releat.utils.logging import get_logger
import logging
logger = get_logger(__name__, log_level=logging.INFO)
```


```python
broker_symbol_ports = []
for broker, port_map in mt5_api_port_map.items():
    for symbol, port in port_map.items():
        try:
            requests.get(f"http://127.0.0.1:{port}/healthcheck").json()
            logger.info(f"healthcheck {broker} {symbol} on port {port} success")
            if symbol != "general":
                broker_symbol_ports.append([broker,symbol,port])
        except:
            logger.error("Check that mt5 apis have been started - See the first markdown cell of this notebook")
```

    [94m2023-10-20 13:39:11,620  INFO   __main__  |  healthcheck metaquotes general on port 2000 success[0m
    [94m2023-10-20 13:39:11,632  INFO   __main__  |  healthcheck metaquotes EURUSD on port 2001 success[0m
    [94m2023-10-20 13:39:11,645  INFO   __main__  |  healthcheck metaquotes ND100m on port 2002 success[0m
    [94m2023-10-20 13:39:11,657  INFO   __main__  |  healthcheck metaquotes XAUUSD on port 2003 success[0m
    [94m2023-10-20 13:39:11,672  INFO   __main__  |  healthcheck metaquotes2 general on port 2100 success[0m
    [94m2023-10-20 13:39:11,685  INFO   __main__  |  healthcheck metaquotes2 AUDJPY on port 2101 success[0m
    [94m2023-10-20 13:39:11,698  INFO   __main__  |  healthcheck metaquotes2 USDJPY on port 2102 success[0m



```python
def get_data(broker_symbol_port):
    """Simple function to download data"""
    _, symbol, port = broker_symbol_port

    d_request = {
        "symbol": symbol,
        "dt0": "2023-09-06 12:00:00.000",
        "dt1": "2023-09-06 13:01:00.000",
    }

    data = requests.get(
        f"http://127.0.0.1:{port}/get_tick_data",
        json=d_request,
        timeout=120,
    ).json()

    return data
```


```python
# show example output of function
get_data(broker_symbol_ports[0])[:3]
```




    [{'ask': 1.07341,
      'bid': 1.07341,
      'flags': 130,
      'last': 0.0,
      'time_msc': 1694001600087,
      'volume': 0,
      'volume_real': 0.0},
     {'ask': 1.0734,
      'bid': 1.0734,
      'flags': 134,
      'last': 0.0,
      'time_msc': 1694001600455,
      'volume': 0,
      'volume_real': 0.0},
     {'ask': 1.07341,
      'bid': 1.07341,
      'flags': 134,
      'last': 0.0,
      'time_msc': 1694001601207,
      'volume': 0,
      'volume_real': 0.0}]



### Compare data extraction speed

When run in parallel, the time taken to download data is at least 2x as fast as compared to in sequence. Note results will vary depending on internet speed and whether results are cached


```python
%%timeit
for broker_symbol_port in broker_symbol_ports:
    get_data(broker_symbol_port)
```

    388 ms ± 31.1 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)



```python
pool = ThreadPoolExecutor(5)
```


```python
%%timeit
list(pool.map(get_data,broker_symbol_ports))
```

    194 ms ± 17.7 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)


### Clean processes by deleting MT5 instances and apis


```python
# kill mt5
stop_mt5()
```

    [94m2023-10-20 13:40:23,925  INFO   releat.workflows.service_manager  |  process id: 37361 killed[0m
    [94m2023-10-20 13:40:23,927  INFO   releat.workflows.service_manager  |  process id: 37975 killed[0m
    [94m2023-10-20 13:40:23,929  INFO   releat.workflows.service_manager  |  MetaTrader5 stopped: process ids [37361, 37975] killed[0m



```python
# kill mt5 api process ids
pids = get_pids("wineserver")
kill_processes(pids)


# kill wine processes
pids = get_pids("python.exe")
kill_processes(pids)
```

    [94m2023-10-20 13:40:23,955  INFO   releat.workflows.service_manager  |  process id: 37198 killed[0m
    [94m2023-10-20 13:40:23,973  INFO   releat.workflows.service_manager  |  process id: 37255 killed[0m
    [94m2023-10-20 13:40:23,977  INFO   releat.workflows.service_manager  |  process id: 37320 killed[0m
    [94m2023-10-20 13:40:23,979  INFO   releat.workflows.service_manager  |  process id: 37450 killed[0m
    [94m2023-10-20 13:40:23,980  INFO   releat.workflows.service_manager  |  process id: 37532 killed[0m
    [94m2023-10-20 13:40:23,986  INFO   releat.workflows.service_manager  |  process id: 37578 killed[0m
    [94m2023-10-20 13:40:23,988  INFO   releat.workflows.service_manager  |  process id: 37656 killed[0m
    [94m2023-10-20 13:40:23,989  INFO   releat.workflows.service_manager  |  process id: 37715 killed[0m
    [94m2023-10-20 13:40:23,990  INFO   releat.workflows.service_manager  |  process id: 37796 killed[0m
    [94m2023-10-20 13:40:23,991  INFO   releat.workflows.service_manager  |  process id: 37843 killed[0m
    [94m2023-10-20 13:40:23,992  INFO   releat.workflows.service_manager  |  process id: 37927 killed[0m
    [94m2023-10-20 13:40:23,993  INFO   releat.workflows.service_manager  |  process id: 38063 killed[0m
    [94m2023-10-20 13:40:23,993  INFO   releat.workflows.service_manager  |  process id: 38207 killed[0m
    [94m2023-10-20 13:40:23,994  INFO   releat.workflows.service_manager  |  process id: 38308 killed[0m
    [94m2023-10-20 13:40:23,995  INFO   releat.workflows.service_manager  |  process id: 38405 killed[0m



```python

```
