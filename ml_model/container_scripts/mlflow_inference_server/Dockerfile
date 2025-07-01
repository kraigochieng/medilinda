# # Use the MLflow-built model image as the base
# FROM final_ml_model

# # Set working directory inside the container
# WORKDIR /opt/ml/model

# # Install FastAPI and Uvicorn for serving metadata
# RUN pip install fastapi uvicorn

# # Copy the FastAPI script into the container
# COPY fastapi_server.py /opt/ml/model/fastapi_server.py

# # Expose both MLflow model serving port (8080) and FastAPI metadata server port (5001)
# EXPOSE 8080 5001

# # Run both MLflow Model Server & FastAPI Server in parallel
# CMD mlflow models serve -m /opt/ml/model -p 8080 --no-conda & \
#     uvicorn fastapi_server:app --host 0.0.0.0 --port 5001


# Use the official MLflow base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install MLflow and required dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port MLflow will run on
EXPOSE 5002

# Start the MLflow model server
CMD mlflow models serve \
    --model-uri "models:/final_ml_model@champion" \
    --host 0.0.0.0 \
    --port 5002
