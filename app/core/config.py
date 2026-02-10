from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Starter"
    secret_key: str = "CHANGE_ME"
    access_token_exp_minutes: int = 60
    cookie_name: str = "access_token"

    class Config:
        env_file = ".env"


settings = Settings()
