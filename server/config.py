from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ml_model_path: str
    encoders_path: str
    server_access_secret_key: str
    server_refresh_secret_key: str
    server_access_algorithm: str
    server_refresh_algorithm: str
    server_access_token_expire_minutes: int
    server_refresh_token_expire_days: int
    mlflow_tracking_server_host: str
    mlflow_tracking_server_port: str
    mlflow_inference_server_host: str
    mlflow_inference_server_port: str
    mlflow_model_name: str
    mlflow_model_alias: str
    mlflow_model_artifacts_path: str
    minio_host: str
    minio_api_port: str
    minio_access_key: str
    minio_secret_access_key: str
    aws_region: str
    africas_talking_username: str
    africas_talking_api_key: str
    model_config = SettingsConfigDict(env_file="../.env", extra="allow")

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
