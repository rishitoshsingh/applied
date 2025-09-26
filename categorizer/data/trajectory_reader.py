import json
import os


def read_n_tasks(file_path, n=10):
    """
    Reads n tasks from the given trajectory JSON file and returns a list of dicts:
    [{"task_id": ..., "conversation": ...}, ...]
    Each dict contains the task id and a formatted string with only user/assistant messages (no tool, no null content).
    """
    # print(f"Reading tasks from {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    output = []
    for task in tasks[:n]:
        task_id = task.get('task_id', '')
        traj = task.get('traj', [])
        conversation = []
        for msg in traj:
            role = msg.get('role')
            content = msg.get('content')
            if role in ('user', 'assistant') and content:
                conversation.append(f"{role.capitalize()}: {content}")
        formatted = '\n'.join(conversation)
        output.append({"task_id": task_id, "conversation": formatted})
        # print(f"Read task {task_id} : {conversation}")
    return output


if __name__ == "__main__":
    for t in read_n_tasks(file_path="/Users/rishitoshsingh/Documents/projects/applied/tau-bench/historical_trajectories/gpt-4o-retail.json",n=1):
        print(f"Task ID: {t['task_id']}\n{t['conversation']}\n---")