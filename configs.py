import os
from dotenv import dotenv_values
from pydantic_settings import BaseSettings
from custom_logger import get_logger
import wandb

logger = get_logger(__name__)
if not os.path.exists(".env"):
    raise FileNotFoundError(".env file not found")
dot_env = dotenv_values(".env")


class Settings(BaseSettings):
    model_config = {"extra": "allow"}

    openai_api_key: str = dot_env["OPENAI_API_KEY"]
    gemini_api_key: str = dot_env["GEMINI_API_KEY"]
    open_weather_api_key: str = dot_env["OPEN_WEATHER_API_KEY"]
    line_channel_access_token: str = dot_env["LINE_CHANNEL_ACCESS_TOKEN"]
    line_channel_secret: str = dot_env["LINE_CHANNEL_SECRET"]
    wandb.login(key=dot_env["WANDB_API_KEY"])
    naver_map_client_id: str = dot_env["NAVER_MAP_CLIENT_ID"]
    naver_map_client_secret: str = dot_env["NAVER_MAP_CLIENT_SECRET"]
    db_port: int = dot_env["DB_PORT"]
    db_user: str = dot_env["DB_USER"]
    db_password: str = dot_env["DB_PASSWORD"]
    db_host: str = "localhost"
    db_name: str = dot_env["DB_NAME"]
    seoul_openapi_key: str = dot_env["SEOUL_OPENAPI_KEY"]


class DevSettings(Settings):
    env: str = "dev"
    project_name: str = f"aline-{env}"
    pass


class ProdSettings(Settings):
    env: str = "prod"
    project_name: str = f"aline-{env}"
    pass


def get_settings():
    env = os.getenv("ENV")
    if env == "dev":
        return DevSettings()
    elif env == "prod":
        return ProdSettings()
    else:
        # raise ValueError(f"Invalid environment: {env}")
        return DevSettings()


settings: Settings = get_settings()
logger.info(f"ENV: {settings.env}")
