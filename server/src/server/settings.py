from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import find_dotenv


class Settings(BaseSettings):
    client_url: str

    mlflow_experiment_name: str
    mlflow_experiment_path: str
    mlflow_artifact_path: str
    mlflow_tracking_uri: str
    mlflow_model_name: str
    mlflow_model_version: str

    databricks_host: str
    databricks_token: str

    africas_talking_username: str
    africas_talking_api_key: str

    better_auth_url: str
    better_auth_audience: str = "medilinda-api"
    better_auth_internal_secret: str

    # App data in Turso. Leave unset to use the local SQLite file.
    turso_app_database_url: str | None = None
    turso_app_auth_token: str | None = None

    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="allow")

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
