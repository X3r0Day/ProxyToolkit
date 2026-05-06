# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #



import sys
import os

from modules.scraper import scrape_proxies
from modules.task_runner import list_tasks, run_task

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear_screen()
        print("========================================")
        print("          XeroDay Proxy Toolkit         ")
        print("========================================")
        print(" [1] Scrape & Validate Proxies")
        print(" [2] Run a Task (Uses live_proxies.txt)")
        print(" [3] Exit")
        print("========================================")
        
        choice = input("Select an option: ").strip()
        
        if choice == '1':
            clear_screen()
            scrape_proxies()
            input("\nPress Enter to return to the main menu...")
            
        elif choice == '2':
            clear_screen()
            manage_tasks_menu()
            
        elif choice == '3':
            print("Exiting...")
            sys.exit(0)
            
        else:
            print("[!] Invalid option. Please try again.")

def manage_tasks_menu():
    tasks = list_tasks()
    if not tasks:
        print("[!] No tasks found in the 'tasks' directory.")
        input("\nPress Enter to return...")
        return
        
    print("========================================")
    print("            Available Tasks             ")
    print("========================================")
    for i, task in enumerate(tasks, 1):
        print(f" [{i}] {task}")
    print(f" [{len(tasks) + 1}] Back to Main Menu")
    print("========================================")
    
    choice_str = input("Select task to run: ").strip()
    try:
        choice = int(choice_str)
        if 1 <= choice <= len(tasks):
            selected_task = tasks[choice - 1]
            target = input(f"Enter target URL/IP for '{selected_task}': ").strip()
            threads_str = input("Enter number of threads (default: 50): ").strip()
            threads = int(threads_str) if threads_str.isdigit() else 50
            
            run_task(selected_task, target, threads)
            input("\nPress Enter to return to the main menu...")
        elif choice == len(tasks) + 1:
            return
        else:
            print("[!] Invalid selection.")
            input("\nPress Enter to return...")
    except ValueError:
        print("[!] Invalid input.")
        input("\nPress Enter to return...")

if __name__ == "__main__":
    main_menu()