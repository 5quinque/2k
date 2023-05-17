from pydantic import BaseSettings


class Settings(BaseSettings):
    items_per_page: int = 5


settings = Settings()