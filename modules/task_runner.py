# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #



import os
import importlib.util
import concurrent.futures
from .proxy_manager import ProxyManager

TASKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasks")

def list_tasks():
    if not os.path.exists(TASKS_DIR):
        print(f"[!] Tasks directory {TASKS_DIR} does not exist.")
        return []
        
    tasks = []
    for file in os.listdir(TASKS_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            tasks.append(file[:-3])
    return tasks

def load_task(task_name):
    task_path = os.path.join(TASKS_DIR, f"{task_name}.py")
    if not os.path.exists(task_path):
        print(f"[!] Task {task_name} not found at {task_path}")
        return None
        
    spec = importlib.util.spec_from_file_location(task_name, task_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[!] Failed to load task {task_name}: {e}")
        return None

def run_task(task_name, target, threads):
    module = load_task(task_name)
    if not module or not hasattr(module, "run"):
        print(f"[!] Task {task_name} must implement a 'run(target, proxy)' function.")
        return
        
    manager = ProxyManager()
    if not manager.proxies:
        print("[!] No proxies loaded. Please scrape first.")
        return
        
    print(f"\n[*] Starting task '{task_name}' against target '{target}' with {threads} threads using {len(manager.proxies)} proxies...")
    
    def task_worker(proxy):
        try:
            result = module.run(target, proxy)
            
            if isinstance(result, tuple) and len(result) == 2:
                success, message = result
            else:
                success = bool(result)
                message = str(result)
                
            if success:
                print(f"[\033[1;34m+\033[0m] Task \033[1;32mSuccess\033[0m | Proxy: {proxy} | Result: {message}")
                return 1
            else:
                if "Error" in message or "Fatal" in message:
                    print(f"[\033[1;31m!\033[0m] Task \033[1;31mFailed\033[0m  | Proxy: {proxy} | Result: {message}")
                else:
                    print(f"[\033[1;33m-\033[0m] Task Failed  | Proxy: {proxy} | Result: {message}")
                return 0
        except Exception as e:
            print(f"[\033[1;31m!\033[0m] Task \033[1;31mException\033[0m| Proxy: {proxy} | Result: {type(e).__name__}")
            return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(task_worker, p) for p in manager.proxies]
        
        total_successes = 0
        for future in concurrent.futures.as_completed(futures):
            total_successes += future.result()

    print(f"\n[*] Finished task '{task_name}'. Total successes: {total_successes}")
