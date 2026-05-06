# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #



import sys
import os
import re
import shutil

from modules.scraper import scrape_proxies
from modules.task_runner import list_tasks, run_task


ANSI_RE = re.compile(r"\033\[[0-9;]*m")
USE_COLOR = sys.stdout.isatty() and not os.getenv("NO_COLOR")

COLORS = {
    "green": "\033[38;5;46m",
    "dark_green": "\033[38;5;28m",
    "gray": "\033[38;5;244m",
    "yellow": "\033[38;5;220m",
    "red": "\033[38;5;196m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}

BANNER = [
    "XX  XX 3333  RRRR   0000  DDDD    AA   YY  YY",
    " XXXX     3  RR RR 00  00 DD DD  A  A   YYYY ",
    " XXXX   333  RRRR  00  00 DD DD AAAAAA   YY  ",
    "XX  XX    3  RR RR 00  00 DD DD AA  AA   YY  ",
    "XX  XX 3333  RR  RR 0000  DDDD  AA  AA   YY  ",
]


def paint(text, color):
    if not USE_COLOR:
        return text
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def visible_len(text):
    return len(ANSI_RE.sub("", text))


def pad_line(text, width):
    return text + (" " * max(0, width - visible_len(text)))


def ui_width():
    columns = shutil.get_terminal_size((80, 20)).columns
    return max(58, min(76, columns - 4))


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    width = ui_width()
    print()
    for line in BANNER:
        print(paint(line.center(width), "green"))
    print(paint("public proxy scraper / task runner - by Project X3r0Day".center(width), "gray"))
    print()


def print_box(title, lines):
    width = ui_width()
    inner = width - 4
    top = "+" + ("-" * (width - 2)) + "+"
    print(paint(top, "dark_green"))
    print(paint("| ", "dark_green") + paint(title.center(inner), "bold") + paint(" |", "dark_green"))
    print(paint("|" + ("-" * (width - 2)) + "|", "dark_green"))
    for line in lines:
        print(paint("| ", "dark_green") + pad_line(line, inner) + paint(" |", "dark_green"))
    print(paint(top, "dark_green"))


def prompt(text):
    tag = paint("x3r0day", "green")
    arrow = paint(">", "dark_green")
    return input(f"\n{tag}{arrow} {text}: ").strip()


def pause(text="Press Enter to return"):
    input(f"\n{paint('[enter]', 'gray')} {text}...")


def show_error(text):
    print(f"\n{paint('[!]', 'red')} {text}")


def main_menu():
    while True:
        clear_screen()
        print_banner()
        print_box("MAIN CONSOLE", [
            "[01] scrape + validate proxies",
            "[02] run task with live_proxies.txt",
            "[03] exit",
        ])
        
        choice = prompt("select")
        
        if choice in {'1', '01'}:
            clear_screen()
            print_banner()
            print_box("SCRAPER", [
                "mode   : scrape public proxy sources",
                "output : live_proxies.txt",
                "types  : http / socks4 / socks5",
            ])
            print()
            scrape_proxies()
            pause()
            
        elif choice in {'2', '02'}:
            clear_screen()
            manage_tasks_menu()
            
        elif choice in {'3', '03'}:
            print(f"\n{paint('[*]', 'green')} closing console")
            sys.exit(0)
            
        else:
            show_error("Bad command.")
            pause()

def manage_tasks_menu():
    print_banner()
    tasks = list_tasks()
    if not tasks:
        print_box("TASKS", [
            "No task files found in tasks/",
            "Add a .py file with run(target, proxy).",
        ])
        pause()
        return

    rows = []
    for i, task in enumerate(tasks, 1):
        rows.append(f"[{i:02d}] {task}")
    rows.append(f"[{len(tasks) + 1:02d}] back")

    print_box("TASKS", rows)
    
    choice_str = prompt("select task")
    try:
        choice = int(choice_str)
        if 1 <= choice <= len(tasks):
            selected_task = tasks[choice - 1]
            target = prompt(f"target for {selected_task}")
            threads_str = prompt("threads [default 50]")
            threads = int(threads_str) if threads_str.isdigit() else 50
            
            print()
            print_box("RUN", [
                f"task    : {selected_task}",
                f"target  : {target}",
                f"threads : {threads}",
            ])
            run_task(selected_task, target, threads)
            pause("Press Enter to return to the main menu")
        elif choice == len(tasks) + 1:
            return
        else:
            show_error("Bad task number.")
            pause()
    except ValueError:
        show_error("Numbers only here.")
        pause()

if __name__ == "__main__":
    main_menu()
