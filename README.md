# XeroDay Proxy Toolkit

A small terminal tool for finding live proxies and using them in local task scripts.

It pulls public proxy lists, keeps the proxy type, checks each proxy, and writes the working ones to `live_proxies.txt`.

## What It Does

| Part | What happens |
| --- | --- |
| Scraper | Pulls proxy lists from many public sources. |
| Parser | Reads `http`, `socks4`, and `socks5` proxies. |
| Checker | Tests the proxy route before saving it. |
| Output | Saves live proxies to `live_proxies.txt`. |
| Task runner | Runs scripts from `tasks/` with saved proxies. |

## Proxy Types

| Type | Saved format | Notes |
| --- | --- | --- |
| HTTP | `http://1.2.3.4:8080` | Used for HTTP and HTTPS requests through `requests`. |
| SOCKS4 | `socks4://1.2.3.4:4145` | Needs PySocks. |
| SOCKS5 | `socks5://1.2.3.4:1080` | Needs PySocks. |

## Install

| Need | Command |
| --- | --- |
| Python packages | `python -m pip install requests tqdm PySocks` |
| Run the tool | `python main.py` |

`PySocks` is needed for SOCKS proxies. Without it, HTTP proxies still work, but SOCKS checks are skipped.

## Menu

| Option | Use |
| --- | --- |
| `1` | Scrape and check proxies. |
| `2` | Run a task with proxies from `live_proxies.txt`. |
| `3` | Exit. |

## Output File

`live_proxies.txt` is rewritten each time you scrape.

Example:

```txt
http://158.160.215.167:8125
socks4://72.49.49.11:31034
socks5://98.178.72.21:10919
```

## Proxy Check Rules

| Check | Why it is there |
| --- | --- |
| Public IP only | Drops private, loopback, multicast, and bad IPs. |
| First IP echo | Confirms the proxy returns a real public IP. |
| Direct IP compare | Drops proxies that show your own IP. |
| GitHub request | Confirms the proxy can reach a real HTTPS site. |
| Second IP echo | Confirms the same proxy IP is still being used. |

The fast pass uses short timeouts. A proxy is saved only if it passes all checks inside that pass.

## Speed Settings

These values can be set before running the tool.

| Name | Default | What it controls |
| --- | ---: | --- |
| `SOURCE_THREADS` | `64` | How many source URLs are fetched at once. |
| `VALIDATE_THREADS` | Auto | How many proxy checks run at once. |
| `IN_FLIGHT_MULTIPLIER` | `3` | How many queued checks stay ready for workers. |
| `FAST_PROXY_CONNECT_TIMEOUT` | `1.2` | Connect timeout for the fast proxy check. |
| `FAST_PROXY_READ_TIMEOUT` | `2.5` | Read timeout for the fast proxy check. |
| `RETRY_SLOW_TIMEOUTS` | `0` | Set to `1` to retry timeout hits with slower checks. |
| `PROXY_CONNECT_TIMEOUT` | `4` | Connect timeout for the slow retry pass. |
| `PROXY_READ_TIMEOUT` | `8` | Read timeout for the slow retry pass. |
| `PROXY_PREFLIGHT` | `0` | Set to `1` to test the raw TCP port before proxy checks. |
| `PROXY_PREFLIGHT_TIMEOUT` | `0.75` | Raw TCP port check timeout. |
| `MIN_VALIDATION_STALL_TIMEOUT` | `15` | Stops when no checks finish for this many seconds. |

Fast run:

```bash
python main.py
```

Slower run that gives timeout-heavy proxies another chance:

```bash
RETRY_SLOW_TIMEOUTS=1 python main.py
```

More workers:

```bash
VALIDATE_THREADS=3000 python main.py
```

## API Keys

The scraper can also use FOFA and CriminalIP if keys are present.

| Name | Use |
| --- | --- |
| `FOFA_KEY` | Adds FOFA search results. |
| `CRIMINALIP_KEY` | Adds CriminalIP search results. |

Example:

```bash
FOFA_KEY=your_key CRIMINALIP_KEY=your_key python main.py
```

## Files

| Path | Purpose |
| --- | --- |
| `main.py` | Terminal menu. |
| `modules/scraper.py` | Proxy sources, parsing, and checking. |
| `modules/proxy_manager.py` | Loads a random proxy from `live_proxies.txt`. |
| `modules/task_runner.py` | Finds and runs task files. |
| `live_proxies.txt` | Saved working proxies. |
| `tasks/` | Optional folder for task scripts. |

## Task Scripts

Task files go in `tasks/` and must have a `run(target, proxy)` function.

Example:

```python
import requests


def run(target, proxy):
    proxies = {
        "http": proxy,
        "https": proxy,
    }

    try:
        resp = requests.get(target, proxies=proxies, timeout=10)
        return True, f"Status {resp.status_code}"
    except requests.RequestException as e:
        return False, type(e).__name__
```

## Notes

| Note | Reason |
| --- | --- |
| Free proxies die fast. | Run the scraper again when the list gets stale. |
| Some proxies are slow. | Use `RETRY_SLOW_TIMEOUTS=1` if you want to catch more slow ones. |
| SOCKS needs PySocks. | `requests` uses PySocks for `socks4://` and `socks5://`. |