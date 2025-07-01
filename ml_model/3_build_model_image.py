import os
import mlflow
from dotenv import load_dotenv
import boto3

dotenv_path = "../.env"
load_dotenv(dotenv_path)
# Credentials
# Set MinIO Credentials
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("MINIO_ACCESS_KEY")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("MINIO_SECRET_ACCESS_KEY")
os.environ["AWS_DEFAULT_REGION"] = os.getenv("AWS_REGION")

os.environ["MLFLOW_S3_ENDPOINT_URL"] = (
    f"http://{os.getenv('MINIO_HOST')}:{os.getenv('MINIO_API_PORT')}"
)

# Test if credentials are set correctly


s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL"),
)


# Set MLflow Tracking Server
MLFLOW_TRACKING_SERVER_HOST = os.getenv("MLFLOW_TRACKING_SERVER_HOST")
MLFLOW_TRACKING_SERVER_PORT = os.getenv("MLFLOW_TRACKING_SERVER_PORT")
MLFLOW_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME")
MLFLOW_MODEL_ALIAS = os.getenv("MLFLOW_MODEL_ALIAS")
MLFLOW_MODEL_IMAGE_NAME = os.getenv("MLFLOW_MODEL_IMAGE_NAME")

os.environ["MLFLOW_TRACKING_URI"] = (
    f"http://{MLFLOW_TRACKING_SERVER_HOST}:{MLFLOW_TRACKING_SERVER_PORT}"
)

# Build Docker Image
mlflow.models.build_docker(
    model_uri=f"models:/{MLFLOW_MODEL_NAME}@{MLFLOW_MODEL_ALIAS}",
    name=MLFLOW_MODEL_IMAGE_NAME,
    enable_mlserver=False,
)
