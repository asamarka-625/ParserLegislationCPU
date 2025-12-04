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
    COEFF_EXPIRE_SECONDS: float = field(default_factory=lambda: float(os.getenv("COEFF_EXPIRE_SECONDS")))

    CONTROLLER: str = field(default_factory=lambda: os.getenv("CONTROLLER"))

    GET_LEGISLATION_NOT_BINARY: str = field(init=False)
    UPDATE_LEGISLATION_BINARY: str = field(init=False)

    GET_LEGISLATION_BINARY: str = field(init=False)
    UPDATE_LEGISLATION_TEXT: str = field(init=False)
    DELETE_WORKER: str = field(init=False)

    WORKER_ID: int = field(default_factory=lambda: int(os.getenv("WORKER_ID") or 0))

    def __post_init__(self):
        self.logger = setup_logger(
            level=os.getenv("LOG_LEVEL", "INFO")
        )

        self.GET_LEGISLATION_NOT_BINARY: str = f"{self.CONTROLLER}/api/v1/legislation/not_binary"
        self.UPDATE_LEGISLATION_BINARY: str = f"{self.CONTROLLER}/api/v1/legislation/update/binary"

        self.GET_LEGISLATION_BINARY: str = f"{self.CONTROLLER}/api/v1/legislation/free"
        self.UPDATE_LEGISLATION_TEXT: str = f"{self.CONTROLLER}/api/v1/legislation/update/text"
        self.DELETE_WORKER: str = f"{self.CONTROLLER}/api/v1/worker/delete"

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