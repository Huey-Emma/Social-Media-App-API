from pydantic import BaseSettings


class Settings(BaseSettings):
    dbname: str
    db_user: str
    db_password: str
    db_host: str
    jwt_secret: str
    jwt_algo: str
    jwt_expires: int

    class Config:
        env_file = '.env'


conf = Settings()
