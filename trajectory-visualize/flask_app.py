import json
import os

from flask import Flask, render_template, request
from markdown import markdown

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_tau2_tasks')
def view_tau2_tasks():
    file_path = request.args.get('file')
    if not file_path or not os.path.exists(file_path):
        return f"File not found: {file_path}", 404
    with open(file_path, 'r') as f:
        data = json.load(f)
    # Expecting a list of tasks
    return render_template('view_tau2_tasks.html', data=data, file_path=file_path)

@app.route('/view_json')
def view_json():
    file_path = request.args.get('file')
    if not file_path or not os.path.exists(file_path):
        return f"File not found: {file_path}", 404
    with open(file_path, 'r') as f:
        data = json.load(f)


    # Preprocess: Render conversation as markdown for each task, and extract task/reward details

    for task in data:
        # Conversation as markdown
        full_chat_md = ""
        for msg in task.get("traj", []):
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            # If assistant and no content, but tool_calls present
            if role == "Assistant" and not content and msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    func = call.get("function", {})
                    func_name = func.get("name", "function_call")
                    arguments = func.get("arguments", "")
                    full_chat_md += f"**{role}:**\n\n`{func_name}({arguments})`\n\n---\n\n"
            elif role == "Tool":
                func_name = msg.get("name", "tool")
                tool_data = None
                try:
                    tool_data = json.loads(content) if content else None
                except Exception:
                    tool_data = content
                full_chat_md += f"**{role}:**\n\n`{func_name}(...)`\n\n"
                if tool_data:
                    pretty_json = json.dumps(tool_data, indent=2, ensure_ascii=False)
                    full_chat_md += f"```json\n{pretty_json}\n```\n\n---\n\n"
                else:
                    full_chat_md += "<i>[No data returned]</i>\n\n---\n\n"
            else:
                if role:
                    full_chat_md += f"**{role}:**\n\n{content}\n\n---\n\n"
        task["rendered_markdown"] = markdown(full_chat_md)

        # Task details
        task_details = None
        if task.get("info") and task["info"].get("task"):
            task_details = task["info"]["task"]
        task["task_details"] = task_details

        # Reward details
        reward_details = None
        if task.get("info") and task["info"].get("reward_info"):
            reward_details = task["info"]["reward_info"]
        task["reward_details"] = reward_details

    return render_template('view_json.html', data=data, file_path=file_path)

if __name__ == '__main__':
    app.run(debug=True)