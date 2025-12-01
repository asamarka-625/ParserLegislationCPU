# Внешние зависимости
from dataclasses import dataclass, field
from dotenv import load_dotenv
import os
import logging
# Внутренние модули
from app.logger import setup_logger


load_dotenv()


@dataclass
class Config:
    _database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL"))
    logger: logging.Logger = field(init=False)
    LEGISLATION_LIMIT: int = field(default_factory=lambda: int(os.getenv("LEGISLATION_LIMIT")))
    CONTROLLER: str = field(default_factory=lambda: os.getenv("CONTROLLER"))
    GET_LEGISLATION_IDS: str = f"{CONTROLLER}/api/v1/legislation/ids"
    PING_WORKER: str = f"{CONTROLLER}/api/v1/worker/ping"
    COEFF_EXPIRE_SECONDS: int = field(default_factory=lambda: int(os.getenv("COEFF_EXPIRE_SECONDS")))

    def __post_init__(self):
        self.logger = setup_logger(
            level=os.getenv("LOG_LEVEL", "INFO")
        )

        self.validate()
        self.logger.info("Configuration initialized")

    # Валидация конфигурации
    def validate(self):
        if not self._database_url:
            self.logger.critical("DATABASE_URL is required in environment variables")
            raise ValueError("DATABASE_URL is required")

        self.logger.debug("Configuration validation passed")

    @property
    def DATABASE_URL(self) -> str:
        return self._database_url

    def __str__(self) -> str:
        return f"Config(database={self._database_url}, log_level={self.logger.level})"


_instance = None


def get_config() -> Config:
    global _instance
    if _instance is None:
        _instance = Config()

    return _instance