import os


class Config(object):
    """Base config class."""

    # MYSQL Default
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "12345678"
    MYSQL_DB = "lightning-ops"
    MYSQL_CHARSET = "utf8mb4"
    MYSQL_UNIX_SOCKET = ""

    # lightning-go
    LIGHTNING_GO_HOST = "127.0.0.1"
    LIGHTNING_GO_PORT = 9900





class DevelopmentConfig(Config):
    """Development config class."""
    pass


class ProductionConfig(Config):
    """Production config class."""
    pass



if os.environ.get("AIRFLOW_ENV") == "release":
    Config = ProductionConfig()
else:
    Config = DevelopmentConfig()