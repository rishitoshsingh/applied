import argparse
import json
import os

from data.trajectory_reader import read_n_tasks
from tqdm import tqdm


def categorize_tasks(tasks):
    from graph.graph import categorizer_graph
    from graph.state import CategorizerState
    results = []
    for task_obj in tqdm(tasks, desc="Categorizing tasks"):
        task_id = task_obj['task_id']

        state: CategorizerState = {
            "original_conversation": task_obj['conversation'],
            "tasks_conversation": None,
            "task_categorized": 0,
            "router_next_state": None,
            "tasks_category": []
        }
        result = categorizer_graph.invoke(state)
        combined_ = []
        for tasks, tasks_category in zip(result["tasks_conversation"].items, result["tasks_category"]):
            _dict = tasks.model_dump() | tasks_category.model_dump()
            combined_.append(_dict)

        result_json = {
            "Task id": task_id,
            "conversations": combined_,
        }
        results.append(result_json)
    return results

def main(model_name, N, traj_file_path):
    traj_file = traj_file_path.split('/')[-1].replace('.json', '')
    traj_type = None
    if "airline" in traj_file.lower():
        traj_type = "flight"
    elif "retail" in traj_file.lower():
        traj_type = "retail"

    os.environ["traj_type"] = traj_type
    os.environ["model_name"] = model_name

    tasks = read_n_tasks(traj_file_path, N)
    output_json_path = f"categorized_tasks-{model_name}-{traj_file}.json"
    # Load already categorized task ids
    if os.path.exists(output_json_path):
        with open(output_json_path, 'r', encoding='utf-8') as f:
            try:
                existing_results = json.load(f)
                done_ids = set(str(item["Task id"]) for item in existing_results)
            except Exception:
                done_ids = set()
    else:
        done_ids = set()
    # Filter out already processed tasks
    tasks_to_process = [t for t in tasks if str(t['task_id']) not in done_ids]
    if not tasks_to_process:
        print("No new tasks to process.")
        return
    results = categorize_tasks(tasks_to_process)
    if os.path.exists(output_json_path):
        with open(output_json_path, 'r', encoding='utf-8') as f:
            try:
                all_results = json.load(f)
            except Exception:
                all_results = []
        all_results.extend(results)
    else:
        all_results = results
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f'Categorization complete. Results saved to {output_json_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Categorize tasks using LLM models.")
    parser.add_argument("--model", type=str, required=True, choices=['gpt-4o', 'gemini-2.0-flash'], help="Model to use for categorization.")
    parser.add_argument("--trajectory_file_path", type=str, required=True, help="Path to the trajectory file.")
    parser.add_argument("--N", type=int, default=115, help="Number of tasks to read (default: 115).")
    args = parser.parse_args()

    main(args.model, args.N, args.trajectory_file_path)
