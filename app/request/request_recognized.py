# Внешние зависимости
from typing import List, Dict, Union
import httpx
# Внутренние модули
from app.config import get_config


config = get_config()


# Получаем бинарные данные законопроектов
async def get_binary_legislation() -> List[Dict[str, Union[int, str]]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                config.GET_LEGISLATION_BINARY,
                params={
                    "worker_id": config.WORKER_ID,
                    "limit": config.LEGISLATION_LIMIT
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data

            else:
                config.logger.error(f"(get_binary_legislation) Ошибка запроса к контролеру: {response.status_code}")
                return []

        except httpx.RequestError as e:
            config.logger.error(f"(get_binary_legislation) Ошибка запроса к контроллеру: {str(e)}")
            return []

        except Exception as e:
            config.logger.error(f"(get_binary_legislation) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
            return []


# Обновляем текст законопроекта
async def update_text_legislation(id_: int, text: str) -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                config.UPDATE_LEGISLATION_TEXT,
                json={
                    "worker_id": config.WORKER_ID,
                    "id": id_,
                    "text": text
                },
                timeout=30.0
            )

            if response.status_code != 200:
                config.logger.error(f"(update_text_legislation) Ошибка запроса к контролеру: {response.status_code}")

        except httpx.RequestError as e:
            config.logger.error(f"(update_text_legislation) Ошибка запроса к контроллеру: {str(e)}")

        except Exception as e:
            config.logger.error(f"(update_text_legislation) Неожиданная ошибка при запросе к контроллеру : {str(e)}")


# Удаляем воркер
async def delete_worker() -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                config.DELETE_WORKER,
                json={
                    "worker_id": config.WORKER_ID
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                message = data.get("message")

                if message is not None:
                    config.logger.info(f"(delete_worker) message: {message}")

            else:
                config.logger.error(f"(delete_worker) Ошибка запроса к контролеру: {response.status_code}")

        except httpx.RequestError as e:
            config.logger.error(f"(delete_worker) Ошибка запроса к контроллеру: {str(e)}")

        except Exception as e:
            config.logger.error(f"(delete_worker) Неожиданная ошибка при запросе к контроллеру : {str(e)}")