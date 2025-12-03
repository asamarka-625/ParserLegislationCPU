# Внешние зависимости
import asyncio
# Внутренние модули
from app.worker_recognition import main


if __name__ == "__main__":
    asyncio.run(main())