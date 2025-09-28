# applied

## Prerequisites

- List required software (e.g., Python, Node.js)
- Installation instructions for dependencies

## Installation

```bash
git clone --recurse-submodules https://github.com/yourusername/applied.git
cd applied

pip install -r requirements.txt
```
## creating categorizer/.env
1. Put your keys in in categorizer/template.env
2. Rename it to .env

```bash
mv categorizer/template.env categorizer/.env 
```

## Running the categorizer

```bash
cd categorizer
python app.py \
    --model gpt-4o \
    --trajectory_file_path ../tau-bench/historical_trajectories/gpt-4o-airline.json \
    --N 50
```

## Visualizing the trajectories

```bash
cd trajectory-visualize
python flask_app.py
```