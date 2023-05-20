from datetime import timedelta
from pydantic import BaseSettings


class Settings(BaseSettings):
    items_per_page: int = 5
    post_time_limit: timedelta = timedelta(seconds=1)
