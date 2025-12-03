# Внешние зависимости
import asyncio
# Внутренние модули
from app.worker_parser import worker_parser_pdf


if __name__ == "__main__":
    asyncio.run(worker_parser_pdf())
