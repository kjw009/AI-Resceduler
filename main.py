from src.grayfia.client import Grayfia
from src.grayfia.normalizer import normalize_all

if __name__ == "__main__":
    grayfia = Grayfia()

    if grayfia.creds:
        events = grayfia.get_events()
        tasks = grayfia.get_tasks()

        schedule = normalize_all(events, tasks)

        for item in schedule:
            print(f"[{item['type'].upper()}] {item['title']}")
            print(f"  Start: {item['start']}  End: {item['end']}")
            print(f"  Status: {item['status']}  Source: {item['source']}")
            print()
    else:
        print("Authentication Failed")