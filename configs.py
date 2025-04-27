import os
from dotenv import dotenv_values
from pydantic_settings import BaseSettings
from custom_logger import get_logger

logger = get_logger(__name__)
if not os.path.exists(".env"):
    raise FileNotFoundError(".env file not found")
dot_env = dotenv_values(".env")

class Settings(BaseSettings):
    openai_api_key: str = dot_env["OPENAI_API_KEY"]
    open_weather_api_key: str = dot_env["OPEN_WEATHER_API_KEY"]
    line_channel_access_token: str = dot_env["LINE_CHANNEL_ACCESS_TOKEN"]
    line_channel_secret: str = dot_env["LINE_CHANNEL_SECRET"]

class DevSettings(Settings):
    env: str = "dev"
    pass

class ProdSettings(Settings):
    env: str = "prod"
    pass

def get_settings():
    env = os.getenv("ENV")
    if env == "dev":
        return DevSettings()
    elif env == "prod":
        return ProdSettings()
    else:
        #raise ValueError(f"Invalid environment: {env}")
        return DevSettings()
settings: Settings = get_settings()
logger.info(f"ENV: {settings.env}")