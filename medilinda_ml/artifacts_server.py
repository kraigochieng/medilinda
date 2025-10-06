from fastapi import FastAPI
import json
import os

app = FastAPI()

# Define paths to stored JSON files
METRICS_PATH = "/opt/ml/model/model_metadata/metrics.json"
PARAMS_PATH = "/opt/ml/model/model_metadata/params.json"

# Load stored metrics and parameters if they exist
metrics = {}
params = {}

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH) as f:
        metrics = json.load(f)

if os.path.exists(PARAMS_PATH):
    with open(PARAMS_PATH) as f:
        params = json.load(f)

@app.get("/metrics")
def get_metrics():
    return metrics

@app.get("/parameters")
def get_parameters():
    return params

