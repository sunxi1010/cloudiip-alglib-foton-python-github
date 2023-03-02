from pydantic import BaseSettings

class Settings(BaseSettings):
    iotdb_ip: str= "102.168.1.111"
    iotdb_port: str = "6667"
    iotdb_username: str = "root"
    iotdb_password: str = "root"

    database_ip: str = "102.168.1.111"
    database_port: str = "3306"
    database_username: str = "root"
    database_password: str = "cloudiip123"
    database_name: str = "cloudiip_iot"

    class Config:
        env_file = ".env"