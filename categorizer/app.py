import argparse
import json
import os

import prompt_flight
import prompt_retail
from data.trajectory_reader import read_n_tasks
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# from prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE÷
from pydantic import BaseModel, Field
from tqdm import tqdm

# from prompt_flight import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


# Load environment variables from .env file
load_dotenv()

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    procedural: str = Field(description="Either Yes or No.")
    declarative: str = Field(description="Either Yes or No.")
    reason: str = Field(description="A detailed reasoning of why the task is procedural or declarative or both.")

# Langchain rate limiter setup
rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

def categorize_tasks(tasks, traj_type, model):
    results = []
    for task_obj in tqdm(tasks, desc="Categorizing tasks"):
        task_id = task_obj['task_id']
        task_conversation = task_obj['conversation']
        if traj_type == "flight":
            SYSTEM_PROMPT = prompt_flight.SYSTEM_PROMPT
            USER_PROMPT_TEMPLATE = prompt_flight.USER_PROMPT_TEMPLATE
        elif traj_type == "retail":
            SYSTEM_PROMPT = prompt_retail.SYSTEM_PROMPT
            USER_PROMPT_TEMPLATE = prompt_retail.USER_PROMPT_TEMPLATE
        user_prompt = USER_PROMPT_TEMPLATE.format(history=task_conversation, task_id=task_id)
        response = model.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])
        # response is already a ResponseFormatter instance
        result_json = {
            "Task id": task_id,
            "procedural": response.procedural,
            "declarative": response.declarative,
            "reason": response.reason
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
    if model_name not in ['gpt-4o', 'gemini-2.0-flash']:
        raise ValueError("Model must be either 'gpt-4o' or 'gemini-2.0-flash'")
    model = None
    if model_name == 'gemini-2.0-flash':
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            rate_limiter=rate_limiter,
        )
    elif model_name == 'gpt-4o':
        model = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0.1,
            max_retries=2,
            rate_limiter=rate_limiter,
        )
    model_with_structure = model.with_structured_output(ResponseFormatter)
    results = categorize_tasks(tasks_to_process, traj_type, model_with_structure)
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
