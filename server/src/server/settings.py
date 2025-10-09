from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import find_dotenv


class Settings(BaseSettings):
    client_url: str
    nuxt_public_api_base: str

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

    server_access_secret_key: str
    server_refresh_secret_key: str
    server_access_algorithm: str
    server_refresh_algorithm: str
    server_access_token_expire_minutes: int
    server_refresh_token_expire_days: int


    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="allow")

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
