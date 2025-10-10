

import json
import os


def read_n_tasks(file_path="/Users/rishitoshsingh/Documents/projects/applied/categorizer/data/tasks.json", n=10):
	"""
	Reads n tasks from the given tasks.json file and returns a list of dicts:
	[{"id": ..., "task": ...}, ...]
	Each dict contains the task id and a formatted string with description, task_instruction, reason_for_call, and known_info.
	"""
	if not os.path.exists(file_path):
		raise FileNotFoundError(f"File not found: {file_path}")
	with open(file_path, 'r', encoding='utf-8') as f:
		tasks = json.load(f)
	output = []
	for task in tasks[:n]:
		desc = task.get('description', {})
		scenario = task.get('user_scenario', {})
		instructions = scenario.get('instructions', {})
		purpose = desc.get('purpose', '')
		task_instruction = instructions.get('task_instructions', '')
		reason_for_call = instructions.get('reason_for_call', '')
		known_info = instructions.get('known_info', '')
		formatted = (
			f"Purpose: {purpose}\n"
			f"Task Instructions: {task_instruction}\n"
			f"Reason for Call: {reason_for_call}\n"
			f"Known Info: {known_info}\n"
		)
		output.append({"id": task.get('id', ''), "task": formatted})
	return output


if __name__ == "__main__":
	for t in read_n_tasks():
		print(f"Task ID: {t['id']}\n{t['task']}\n---")