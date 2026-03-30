# Grayfia Class
from src.grayfia.client import Grayfia

if __name__ == "__main__":
    grayfia = Grayfia()

    if grayfia.creds:
        events = grayfia.get_events()
        all_tasks = grayfia.get_tasks()

        for task in all_tasks:
            print("---Tasks---")
            tasklist  =  task.get('task_list_title')
            task_name = task.get('title')
            print(f"Tasklist: {tasklist}\n Task Name: {task_name}")
            
    else:
        print("Authentication Failed")