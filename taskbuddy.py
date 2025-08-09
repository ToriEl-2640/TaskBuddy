import json
import os
import sys

# ✅ Make sure Python can find `.kiro` folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".kiro"))

import hooks  # now works from .kiro

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠ tasks.json is corrupted, resetting.")
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("📋 Your task list is empty!")
        return

    print("\n📋 Your Tasks:")
    for idx, task in enumerate(tasks, 1):
        task_name = task.get("name") or task.get("title", "Unnamed Task")
        status = "✅" if task.get("done") else "❌"
        print(f"{idx}. {task_name} - {status}")


def add_task(task_name):
    tasks = load_tasks()
    new_task = {"name": task_name, "done": False}
    tasks.append(new_task)
    save_tasks(tasks)
    hooks.on_task_added(new_task)  # Kiro hook
    print(f"➕ Added task: {task_name}")


def mark_done(index):
    tasks = load_tasks()
    if 0 < index <= len(tasks):
        tasks[index - 1]["done"] = True
        save_tasks(tasks)
        hooks.on_task_completed(tasks[index - 1])  # Kiro hook
        print(f"✅ Task {index} marked as done!")
    else:
        print("⚠ Invalid task number.")


def delete_task(index):
    tasks = load_tasks()
    if 0 < index <= len(tasks):
        removed = tasks.pop(index - 1)
        save_tasks(tasks)
        hooks.on_task_deleted(removed)  # Kiro hook
        print(f"🗑 Deleted task {index}.")
    else:
        print("⚠ Invalid task number.")


def main():
    while True:
        print("\n--- TaskBuddy ---")
        print("1. List tasks")
        print("2. Add task")
        print("3. Mark task as done")
        print("4. Delete task")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            list_tasks()
        elif choice == "2":
            task_name = input("Enter task description: ")
            add_task(task_name)
        elif choice == "3":
            try:
                index = int(input("Task number to mark done: "))
                mark_done(index)
            except ValueError:
                print("⚠ Please enter a number.")
        elif choice == "4":
            try:
                index = int(input("Task number to delete: "))
                delete_task(index)
            except ValueError:
                print("⚠ Please enter a number.")
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("⚠ Invalid choice, try again.")


if __name__ == "__main__":
    main()
