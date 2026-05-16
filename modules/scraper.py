# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #

import base64
import concurrent.futures
import ipaddress
import os
import re
import socket
import threading
import time
from collections import deque
from urllib.parse import urlparse

try:
    import resource
except ImportError:  # non-POSIX (Windows)
    resource = None

import requests
from tqdm import tqdm

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False


IP_CHECK_URLS = (
    "https://api.ipify.org?format=json",
    "https://icanhazip.com",
)
GITHUB_TEST_URL = "https://api.github.com/zen"

PROXY_SOURCES = [
    ("Proxifly all", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt", None),
    ("Proxifly HTTP", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt", "http"),
    ("Proxifly SOCKS4", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt", "socks4"),
    ("Proxifly SOCKS5", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt", "socks5"),
    ("TheSpeedX HTTP", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", "http"),
    ("TheSpeedX SOCKS4", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt", "socks4"),
    ("TheSpeedX SOCKS5", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt", "socks5"),
    ("TheSpeedX legacy HTTP", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "http"),
    ("Monosans HTTP", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", "http"),
    ("Monosans SOCKS4", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt", "socks4"),
    ("Monosans SOCKS5", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt", "socks5"),
    ("Jetkai HTTP", "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt", "http"),
    ("Jetkai HTTPS", "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt", "http"),
    ("Jetkai SOCKS4", "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt", "socks4"),
    ("Jetkai SOCKS5", "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt", "socks5"),
    ("OpenProxy HTTPS", "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt", "http"),
    ("OpenProxy SOCKS4", "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt", "socks4"),
    ("OpenProxy SOCKS5", "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt", "socks5"),
    ("ALIILAPRO HTTP", "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt", "http"),
    ("ALIILAPRO SOCKS4", "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt", "socks4"),
    ("ALIILAPRO SOCKS5", "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt", "socks5"),
    ("IPLocate HTTP", "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt", "http"),
    ("IPLocate HTTPS", "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/https.txt", "http"),
    ("IPLocate SOCKS4", "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt", "socks4"),
    ("IPLocate SOCKS5", "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt", "socks5"),
    ("ProxyScrape all", "https://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&proxy_format=protocolipport&format=text", None),
    ("ProxyList.download HTTP", "https://www.proxy-list.download/api/v1/get?type=http", "http"),
    ("ProxyList.download SOCKS4", "https://www.proxy-list.download/api/v1/get?type=socks4", "socks4"),
    ("ProxyList.download SOCKS5", "https://www.proxy-list.download/api/v1/get?type=socks5", "socks5"),
    ("JoyDeploy all", "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/proxies.txt", None),
    ("JoyDeploy HTTP", "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/http/proxies.txt", "http"),
    ("JoyDeploy SOCKS4", "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/socks4/proxies.txt", "socks4"),
    ("JoyDeploy SOCKS5", "https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/socks5/proxies.txt", "socks5"),
    ("MMPX HTTP", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt", "http"),
    ("MMPX SOCKS4", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt", "socks4"),
    ("MMPX SOCKS5", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt", "socks5"),
    ("HookzOf SOCKS5", "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt", "socks5"),
    ("ProxyScraper mixed", "https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt", None),
    ("Sunny9577 mixed", "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt", None),
    ("Clarketm raw", "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt", "http"),
    ("ShiftyTR mixed", "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt", None),
    ("Zloi HTTP", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt", "http"),
    ("Zloi SOCKS4", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt", "socks4"),
    ("Zloi SOCKS5", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt", "socks5"),
]

FOFA_KEY = os.getenv("FOFA_KEY", "")
FOFA_QUERY = (
    'protocol="http" || protocol="socks4" || protocol="socks5" || '
    'port="80" || port="443" || port="8080" || port="3128" || port="8000" || '
    'port="9000" || port="1080" || port="1081" || port="4145" || port="9050"'
)

CRIMINALIP_KEY = os.getenv("CRIMINALIP_KEY", "")
CRIMINALIP_QUERY = (
    "port: 80 OR port: 443 OR port: 8080 OR port: 3128 OR port: 8000 OR "
    "port: 9000 OR port: 1080 OR port: 1081 OR port: 4145 OR port: 9050"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
PROXY_PATTERN = re.compile(r'\b(?:(https?|socks4a?|socks5h?)://)?((?:[0-9]{1,3}\.){3}[0-9]{1,3}):([0-9]{1,5})\b', re.I)
SUPPORTED_SCHEMES = {"http", "socks4", "socks5"}
HTTP_PORTS = {"80", "443", "8000", "8080", "8081", "8118", "8888", "9000", "3128"}
SOCKS_PORTS = {"1080", "1081", "10800", "4145", "5678", "9050", "9051"}
SUCCESSFUL_GITHUB_STATUSES = {200, 401, 403, 429}

_thread_local = threading.local()


def env_int(name, default, minimum=None, maximum=None):
    try:
        value = int(os.getenv(name, default))
    except (TypeError, ValueError):
        value = default

    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)

    return value


def env_float(name, default, minimum=None, maximum=None):
    try:
        value = float(os.getenv(name, default))
    except (TypeError, ValueError):
        value = default

    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)

    return value


def open_file_limit():
    try:
        import resource

        soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft == resource.RLIM_INFINITY:
            return 8192
        return soft
    except (ImportError, OSError, ValueError):
        return 1024


def default_validate_threads():
    cpu_target = (os.cpu_count() or 4) * 128
    fd_target = max(256, (open_file_limit() - 256) // 4)
    return min(2048, max(500, cpu_target), fd_target)


SOURCE_THREADS = env_int("SOURCE_THREADS", 64, 1, 256)
VALIDATE_THREADS = env_int("VALIDATE_THREADS", default_validate_threads(), 1, 4096)
FETCH_TIMEOUT = env_float("FETCH_TIMEOUT", 12, 1, 60)
CONNECT_TIMEOUT = env_float("PROXY_CONNECT_TIMEOUT", 4, 0.5, 30)
READ_TIMEOUT = env_float("PROXY_READ_TIMEOUT", 8, 1, 60)
TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)
FAST_CONNECT_TIMEOUT = env_float("FAST_PROXY_CONNECT_TIMEOUT", 1.2, 0.2, CONNECT_TIMEOUT)
FAST_READ_TIMEOUT = env_float("FAST_PROXY_READ_TIMEOUT", 2.5, 0.5, READ_TIMEOUT)
FAST_TIMEOUT = (FAST_CONNECT_TIMEOUT, FAST_READ_TIMEOUT)
PREFLIGHT_ENABLED = os.getenv("PROXY_PREFLIGHT", "0").lower() in {"1", "true", "yes", "on"}
PREFLIGHT_TIMEOUT = env_float("PROXY_PREFLIGHT_TIMEOUT", min(0.75, FAST_CONNECT_TIMEOUT), 0.1, CONNECT_TIMEOUT)
RETRY_SLOW_TIMEOUTS = os.getenv("RETRY_SLOW_TIMEOUTS", "0").lower() in {"1", "true", "yes", "on"}
IN_FLIGHT_MULTIPLIER = env_int("IN_FLIGHT_MULTIPLIER", 3, 1, 10)
VALIDATION_WAIT_INTERVAL = env_float("VALIDATION_WAIT_INTERVAL", 0.5, 0.1, 5)
MIN_VALIDATION_STALL_TIMEOUT = env_int("MIN_VALIDATION_STALL_TIMEOUT", 15, 5, 600)


def get_session():
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.trust_env = False
        _thread_local.session = session
    return session


def normalize_scheme(scheme):
    scheme = (scheme or "").lower().strip()
    if scheme in {"https", "http"}:
        return "http"
    if scheme in {"socks4", "socks4a"}:
        return "socks4"
    if scheme in {"socks5", "socks5h"}:
        return "socks5"
    return None


def public_ip(ip):
    try:
        parsed = ipaddress.ip_address(str(ip).strip())
    except ValueError:
        return None

    if not parsed.is_global or parsed.is_multicast:
        return None

    return str(parsed)


def build_proxy_url(scheme, ip, port):
    scheme = normalize_scheme(scheme)
    ip = public_ip(ip)

    try:
        port = int(port)
    except (TypeError, ValueError):
        return None

    if not scheme or not ip or not 1 <= port <= 65535:
        return None

    return f"{scheme}://{ip}:{port}"


def schemes_for_port(port):
    port = str(port)
    schemes = []

    if port in SOCKS_PORTS:
        schemes.extend(["socks5", "socks4"])
    if port in HTTP_PORTS or not schemes:
        schemes.append("http")

    return schemes


def candidate_proxy_urls(ip, port, scheme=None):
    schemes = [normalize_scheme(scheme)] if normalize_scheme(scheme) else schemes_for_port(port)
    return {proxy for proxy in (build_proxy_url(s, ip, port) for s in schemes) if proxy}


def extract_proxies_from_text(text, default_scheme=None):
    proxies = set()
    for match in PROXY_PATTERN.finditer(text):
        scheme, ip, port = match.groups()
        proxies.update(candidate_proxy_urls(ip, port, scheme or default_scheme))
    return proxies


def count_by_scheme(proxies):
    counts = {scheme: 0 for scheme in SUPPORTED_SCHEMES}
    for proxy in proxies:
        scheme = urlparse(proxy).scheme
        if scheme in counts:
            counts[scheme] += 1
    return counts


def extract_proxies(url, default_scheme=None, source_name=None):
    try:
        if "github.com" in url and "/raw/" not in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        resp = requests.get(url, headers=HEADERS, timeout=FETCH_TIMEOUT)
        if resp.status_code != 200:
            return set()

        proxies = extract_proxies_from_text(resp.text, default_scheme)
        if proxies:
            print(f"[+] {source_name or url}: {len(proxies)}")
        return proxies
    except requests.RequestException:
        return set()


def extract_fofa_proxies():
    if not FOFA_KEY:
        return set()

    proxies = set()
    print("[*] Extracting from FOFA...")
    try:
        qbase64 = base64.b64encode(FOFA_QUERY.encode()).decode()
        url = "https://fofa.info/api/v1/search/all"
        params = {"key": FOFA_KEY, "qbase64": qbase64, "size": 1000, "fields": "ip,port,protocol"}
        resp = requests.get(url, params=params, timeout=FETCH_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("error"):
                for row in data.get("results", []):
                    if len(row) < 2:
                        continue
                    ip, port = row[0], row[1]
                    scheme = row[2] if len(row) > 2 else None
                    proxies.update(candidate_proxy_urls(ip, port, scheme))
            else:
                print(f"[!] FOFA API error: {data.get('errmsg')}")
    except Exception as e:
        print(f"[!] FOFA extraction error: {e}")

    print(f"[+] Found {len(proxies)} proxies from FOFA.")
    return proxies


def extract_criminalip_proxies():
    if not CRIMINALIP_KEY:
        return set()

    proxies = set()
    print("[*] Extracting from CriminalIP...")
    try:
        url = "https://api.criminalip.io/v1/banner/search"
        headers = {"x-api-key": CRIMINALIP_KEY}
        params = {"query": CRIMINALIP_QUERY, "offset": 0}
        resp = requests.get(url, headers=headers, params=params, timeout=FETCH_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get("data", {}).get("result", []):
                ip = result.get("ip_address")
                port = result.get("open_port_no")
                scheme = result.get("protocol") or result.get("app_name") or result.get("product")
                proxies.update(candidate_proxy_urls(ip, port, scheme))
    except Exception as e:
        print(f"[!] CriminalIP extraction error: {e}")

    print(f"[+] Found {len(proxies)} proxies from CriminalIP.")
    return proxies


def extract_geonode_proxies():
    proxies = set()
    print("[*] Extracting from Geonode...")
    try:
        for page in range(1, 4):
            url = (
                "https://proxylist.geonode.com/api/proxy-list"
                f"?limit=500&page={page}&sort_by=lastChecked&sort_type=desc"
            )
            resp = requests.get(url, timeout=FETCH_TIMEOUT)
            if resp.status_code != 200:
                continue

            data = resp.json()
            for item in data.get("data", []):
                ip = item.get("ip")
                port = item.get("port")
                protocols = item.get("protocols") or []

                if protocols:
                    for protocol in protocols:
                        proxy = build_proxy_url(protocol, ip, port)
                        if proxy:
                            proxies.add(proxy)
                else:
                    proxies.update(candidate_proxy_urls(ip, port))
    except Exception as e:
        print(f"[!] Geonode error: {e}")

    print(f"[+] Found {len(proxies)} proxies from Geonode.")
    return proxies


def parse_ip_response(resp):
    try:
        if "json" in resp.headers.get("Content-Type", ""):
            value = resp.json().get("ip")
        else:
            value = resp.text.strip().split()[0]
    except Exception:
        return None

    return public_ip(value)


def get_direct_ip():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.trust_env = False

    for url in IP_CHECK_URLS:
        try:
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                ip = parse_ip_response(resp)
                if ip:
                    return ip
        except requests.RequestException:
            continue

    return None


def normalize_proxy_url(proxy):
    if "://" not in proxy:
        proxy = f"http://{proxy}"

    parsed = urlparse(proxy)
    try:
        port = parsed.port
    except ValueError:
        return None

    return build_proxy_url(parsed.scheme, parsed.hostname, port)


def proxy_port_open(parsed):
    if not PREFLIGHT_ENABLED:
        return True

    try:
        with socket.create_connection((parsed.hostname, parsed.port), timeout=PREFLIGHT_TIMEOUT):
            return True
    except OSError:
        return False


def check_proxy(proxy, direct_ip=None, timeout=FAST_TIMEOUT, retry_on_timeout=True):
    """
    Validates the actual proxy route, not just a responsive port.
    """
    proxy = normalize_proxy_url(proxy)
    if not proxy:
        return None, False

    parsed = urlparse(proxy)
    scheme = parsed.scheme
    if scheme.startswith("socks") and not SOCKS_AVAILABLE:
        return None, False
    if not proxy_port_open(parsed):
        return None, False

    try:
        session = get_session()
        proxies = {"http": proxy, "https": proxy}
        observed_ips = []

        resp = session.get(IP_CHECK_URLS[0], proxies=proxies, timeout=timeout)
        if resp.status_code != 200:
            return None, False

        ip = parse_ip_response(resp)
        if not ip:
            return None, False
        if direct_ip and ip == direct_ip:
            return None, False

        observed_ips.append(ip)

        gh_resp = session.get(GITHUB_TEST_URL, proxies=proxies, timeout=timeout)
        if gh_resp.status_code not in SUCCESSFUL_GITHUB_STATUSES:
            return None, False

        for url in IP_CHECK_URLS[1:]:
            resp = session.get(url, proxies=proxies, timeout=timeout)
            if resp.status_code != 200:
                return None, False

            ip = parse_ip_response(resp)
            if not ip:
                return None, False

            observed_ips.append(ip)

        if len(set(observed_ips)) == 1:
            return proxy, False
    except (requests.Timeout, socket.timeout):
        return None, retry_on_timeout
    except requests.RequestException:
        pass

    return None, False


def proxy_sort_key(proxy):
    parsed = urlparse(proxy)
    return (parsed.scheme, parsed.hostname or "", parsed.port or 0)


def validation_stall_timeout(timeout):
    return max(MIN_VALIDATION_STALL_TIMEOUT, int(sum(timeout) * (len(IP_CHECK_URLS) + 1) + 5))


def submit_validation_batch(executor, proxy_queue, pending, direct_ip, limit, timeout, retry_on_timeout):
    while proxy_queue and len(pending) < limit:
        proxy = proxy_queue.popleft()
        pending[executor.submit(check_proxy, proxy, direct_ip, timeout, retry_on_timeout)] = proxy


def run_validation_pass(proxy_list, direct_ip, target_file, label, timeout, retry_on_timeout, valid_counts):
    valid_proxies = []
    retry_proxies = []
    total = len(proxy_list)
    in_flight_limit = max(1, min(total, VALIDATE_THREADS * IN_FLIGHT_MULTIPLIER))
    stall_timeout = validation_stall_timeout(timeout)
    proxy_queue = deque(proxy_list)
    pending = {}

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=VALIDATE_THREADS)

    try:
        with open(target_file, "a") as out, tqdm(total=total, desc=label, unit="px", colour="green") as pbar:
            submit_validation_batch(executor, proxy_queue, pending, direct_ip, in_flight_limit, timeout, retry_on_timeout)
            last_progress = time.monotonic()

            while pending:
                done, _ = concurrent.futures.wait(
                    pending,
                    timeout=VALIDATION_WAIT_INTERVAL,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )

                if not done:
                    stalled_for = time.monotonic() - last_progress
                    if stalled_for >= stall_timeout:
                        print(f"\n[!] Validation stalled for {int(stalled_for)}s. Saving current live proxies...")
                        break
                    continue

                last_progress = time.monotonic()
                completed = 0
                for future in done:
                    proxy = pending.pop(future, None)
                    completed += 1

                    try:
                        res, retry = future.result()
                    except Exception:
                        res, retry = None, False

                    if res:
                        valid_proxies.append(res)
                        out.write(f"{res}\n")
                        out.flush()
                        scheme = urlparse(res).scheme
                        if scheme in valid_counts:
                            valid_counts[scheme] += 1
                        pbar.set_postfix({
                            "Live": sum(valid_counts.values()),
                            "http": valid_counts["http"],
                            "s4": valid_counts["socks4"],
                            "s5": valid_counts["socks5"],
                        }, refresh=False)
                    elif retry and proxy:
                        retry_proxies.append(proxy)

                pbar.update(completed)

                submit_validation_batch(executor, proxy_queue, pending, direct_ip, in_flight_limit, timeout, retry_on_timeout)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Saving current live proxies...")
    finally:
        for future in pending:
            future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)

    return valid_proxies, retry_proxies


def validate_proxies(proxy_list, direct_ip, target_file):
    valid_counts = {scheme: 0 for scheme in SUPPORTED_SCHEMES}
    valid_proxies, retry_proxies = run_validation_pass(
        proxy_list,
        direct_ip,
        target_file,
        "Fast validate",
        FAST_TIMEOUT,
        RETRY_SLOW_TIMEOUTS,
        valid_counts,
    )

    if RETRY_SLOW_TIMEOUTS and retry_proxies:
        print(f"[*] Retrying {len(retry_proxies)} timeout candidates with full timeouts...")
        retry_valid, _ = run_validation_pass(
            retry_proxies,
            direct_ip,
            target_file,
            "Retry validate",
            TIMEOUT,
            False,
            valid_counts,
        )
        valid_proxies.extend(retry_valid)

    return valid_proxies


def scrape_proxies():
    print("[*] Scraping sources...")
    all_raw = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=SOURCE_THREADS) as executor:
        futures = [
            executor.submit(extract_proxies, url, default_scheme, name)
            for name, url, default_scheme in PROXY_SOURCES
        ]
        for future in concurrent.futures.as_completed(futures):
            all_raw.update(future.result())

    all_raw.update(extract_geonode_proxies())

    if FOFA_KEY:
        all_raw.update(extract_fofa_proxies())

    if CRIMINALIP_KEY:
        all_raw.update(extract_criminalip_proxies())

    if not SOCKS_AVAILABLE:
        print("[!] PySocks is not installed. SOCKS proxies were collected but will be skipped during validation.")

    proxy_list = sorted(all_raw, key=proxy_sort_key)
    total = len(proxy_list)
    source_counts = count_by_scheme(proxy_list)
    print(
        f"[+] Scanned {total} unique candidates "
        f"(http={source_counts['http']}, socks4={source_counts['socks4']}, socks5={source_counts['socks5']})."
    )

    direct_ip = get_direct_ip()
    if direct_ip:
        print("[*] Direct public IP captured for leak checks.")
    else:
        print("[!] Could not capture direct public IP. Continuing without direct-IP leak comparison.")

    target_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "live_proxies.txt")

    with open(target_file, "w") as f:
        f.write("")

    if total == 0:
        print("[!] No candidates found. Saved an empty live_proxies.txt.")
        return

    print(
        "[*] Validating with fast strict pass "
        f"(workers={VALIDATE_THREADS}, "
        f"in-flight={min(total, VALIDATE_THREADS * IN_FLIGHT_MULTIPLIER)}, "
        f"timeout={FAST_TIMEOUT[0]}/{FAST_TIMEOUT[1]}s, "
        f"retry_slow={RETRY_SLOW_TIMEOUTS}, "
        f"preflight={PREFLIGHT_ENABLED})..."
    )

    valid_proxies = validate_proxies(proxy_list, direct_ip, target_file)

    valid_counts = count_by_scheme(valid_proxies)
    print(
        f"\n[*] Finished. Found {len(valid_proxies)} live proxies "
        f"(http={valid_counts['http']}, socks4={valid_counts['socks4']}, socks5={valid_counts['socks5']})."
    )
    print(f"[+] Saved to {target_file}")


def raise_fd_limit():
    """
    Validation opens up to IN_FLIGHT sockets concurrently. When launched from a
    subprocess (e.g. the orchestrator) the inherited soft RLIMIT_NOFILE can be
    as low as 256 on macOS, which exhausts before the output file even opens.
    Raise the soft limit toward the hard limit so the in-flight pool fits.
    """
    if resource is None:
        return
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    except (ValueError, OSError):
        return

    needed = VALIDATE_THREADS * IN_FLIGHT_MULTIPLIER + 256
    target = needed if hard == resource.RLIM_INFINITY else min(needed, hard)
    if soft >= target:
        return
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
    except (ValueError, OSError):
        print(f"[!] Could not raise open-file limit (soft={soft}); "
              f"validation may hit 'Too many open files'.")


if __name__ == "__main__":
    raise_fd_limit()
    scrape_proxies()
