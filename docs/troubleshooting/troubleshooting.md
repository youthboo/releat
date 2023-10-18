# Troubleshooting

## MetaTrader5

### MT5 window does not open

1. Check that when you run the docker container, you pass through the display with `-v /tmp/.X11-unix:/tmp/.X11-unix`
2. Restart your computer. Sometimes when open / closing / starting / stopping the container multiple times, some weird gui cache behaviour is triggered / locked and the container becomes unable to open new windows
3. Delete container from docker and rebuild container, sometime a fresh install of MT5 just magically fixes the problem. You shouldn't lose any info / data because all the scripts and data available in your docker container mounted from the host.

### Can't programmatically log in to MT5

1. Manually log into MT5 account using the gui interface. When you first install MT5, the instance does not automatically connect to the metaquotes server (no idea why). The first log in must be manual, i.e. click to search through the list of brokers, type in your username and password. Subsequent connections to other brokers so work afterwards

### Can't programmatically download data / trade in MT5

1. Check that you are logged in. If you cant log in see the [question above](./troubleshooting.md#cant-programmatically-log-in-to-mt5).
2. Check that the algotrading button is pressed. By default, the algotrading button is off
