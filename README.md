# applied

## Installation

```bash
git clone --recurse-submodules https://github.com/rishitoshsingh/applied.git
cd applied

pip install -r requirements.txt
```

## creating categorizer_new/.env

1. Put your keys in in categorizer_new/template.env
2. Rename it to .env

```bash
mv categorizer_new/template.env categorizer_new/.env 
```

## Running the categorizer

```bash
cd categorizer_new
python app.py \
    --model gpt-4o \
    --temperature 0.1 \
    --trajectory_file_path ../tau-bench/historical_trajectories/gpt-4o-airline.json
```

## Visualizing the trajectories

```bash
cd trajectory-visualize
python flask_app.py
```
