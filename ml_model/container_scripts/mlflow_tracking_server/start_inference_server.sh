#!/bin/bash

echo "Starting MLflow Inference Server..."

REQUIRED_VARS=(
    "MLFLOW_MODEL_NAME"
    "MLFLOW_MODEL_ALIAS"
    "MLFLOW_TRACKING_SERVER_HOST"
    "MLFLOW_TRACKING_SERVER_PORT"
    "MLFLOW_INFERENCE_SERVER_PORT"
    "MLFLOW_TRACKING_URI"
)

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "Error: $VAR is not set."
        exit 1
    fi
done


# Wait for MLflow tracking server to be ready
echo "Waiting for MLflow Tracking Server to start..."
until curl -s $MLFLOW_TRACKING_URI; do
    echo "MLflow Tracking Server is not ready, retrying in 5s..."
    sleep 5
done

echo "MLflow Tracking Server is up, starting inference server..."

mlflow models serve \
    -m "models:/$MLFLOW_MODEL_NAME@$MLFLOW_MODEL_ALIAS" \
    --host 0.0.0.0 \
    -p $MLFLOW_INFERENCE_SERVER_PORT


