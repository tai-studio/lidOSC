# lidOSC
2025, Till Bovermann

Read the laptop lid angle via `pybooklid` and send it as an OSC (Open Sound Control) message.

## Features

* Immediate sends on every detected lid angle change
* Optional periodic (heartbeat) resend of the latest angle via `--interval`
* Configurable OSC target IP, port, and message address
* Debug logging of angle updates and heartbeat activity

## Installation

Install with uv or pip (Python >= 3.13 required as per `pyproject.toml`).

## Thanks

* [pybooklid](https://github.com/tcsenpai/pybooklid) 
* [python-osc](https://github.com/attwad/python-osc)


## Usage

Basic invocation (defaults to localhost:8000 and message address `/lid`):

```
python -m lidosc
```

Or explicitly:

```
python lidosc.py --ip 127.0.0.1 --port 8000 --message /lid
```

Enable debug output:

```
python lidosc.py --debug
```

## Heartbeat / Interval

By default an interval of `0.5` seconds is used (see `--interval`). When enabled (value > 0), the program sends the most recently observed angle every N seconds even if it has not changed. This acts as a keep-alive / heartbeat.

Disable the heartbeat and only send on change:

```
python lidosc.py --interval 0
```

Send every 2 seconds regardless of change (plus immediate change events):

```
python lidosc.py --interval 2.0
```

## OSC Message

Each OSC message contains the lid angle in degrees as a single float argument.

## Exit / Interrupt

Ctrl+C to stop


