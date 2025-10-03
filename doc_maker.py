# %%
import json
import os
import random

# %%
DATA_PATH = "categorizer/final/"
files = os.listdir(DATA_PATH)
files.sort()

gemini_files = [f for f in files if f.startswith("gemini")]
gpt_files = [f for f in files if f.startswith("gpt")]
gemini_files.sort()
gpt_files.sort()

# %%
if os.path.exists("gpt-4o-examples.md"):
    os.remove("gpt-4o-examples.md")
if os.path.exists("gemini-2.0-flash-examples.md"):
    os.remove("gemini-2.0-flash-examples.md")



# %%

for file in gemini_files:
    with open(os.path.join(DATA_PATH, file), "r") as f:
        data = json.load(f)
    random_dict = random.choice(data)
    with open("gemini-2.0-flash-examples.md", "a") as md_file:
        md_file.write(f"## Example from {file}\n\n")
        md_file.write(f"### Reason for this category:\n{random_dict['reason']}\n\n")
        md_file.write(f"### Instruction: \n{random_dict['info']['task']['instruction']}\n\n")
        md_file.write("### Conversation: \n")
        for turn in random_dict["traj"][1:]:
            if turn["content"]:
                if turn["role"] == "user":
                    md_file.write(f"**User:** {turn['content']}\n\n")
                elif turn["role"] == "assistant":
                    md_file.write(f"**Assistant:** {turn['content']}\n\n")

for file in gpt_files:
    with open(os.path.join(DATA_PATH, file), "r") as f:
        data = json.load(f)
    random_dict = random.choice(data)
    with open("gpt-4o-examples.md", "a") as md_file:
        md_file.write(f"## Example from {file}\n\n")
        md_file.write(f"### Reason for this category:\n{random_dict['reason']}\n\n")
        md_file.write(f"### Instruction: \n{random_dict['info']['task']['instruction']}\n\n")
        md_file.write("### Conversation: \n")
        for turn in random_dict["traj"][1:]:
            if turn["content"]:
                if turn["role"] == "user":
                    md_file.write(f"**User:** {turn['content']}\n\n")
                elif turn["role"] == "assistant":
                    md_file.write(f"**Assistant:** {turn['content']}\n\n")