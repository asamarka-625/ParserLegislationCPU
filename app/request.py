# Внешние зависимости
from typing import Optional, List
import httpx
# Внутренние модули
from app.config import get_config


config = get_config()


# Получаем свой IP
async def get_my_ip() -> Optional[str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://httpbin.org/ip", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("origin")

            else:
                config.logger.error(f"Ошибка получения IP: {response.status_code}")
                return None

        except Exception as e:
            config.logger.error(f"Ошибка получения IP: {e}")
            return None


# Получаем ids законопроектов
async def get_legislation_ids(ip_address: str) -> List[int]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config.GET_LEGISLATION_IDS,
                json={
                    "ip": ip_address,
                    "limit": config.LEGISLATION_LIMIT
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("legislation_ids", [])

            else:
                config.logger.error(f"(get_legislation_ids) Ошибка запроса к контролеру: {response.status_code}")
                return []

        except httpx.RequestError as e:
            config.logger.error(f"(get_legislation_ids) Ошибка запроса к контроллеру: {str(e)}")
            return []

        except Exception as e:
            config.logger.error(f"(get_legislation_ids) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
            return []


# Пингуем воркер
async def ping_worker(
    ip_address: str,
    processed_data: int,
    expire_seconds: int
) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config.PING_WORKER,
                json={
                    "ip": ip_address,
                    "processed_data": processed_data,
                    "expire_seconds": expire_seconds
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                return status == "success"

            else:
                config.logger.error(f"(ping_worker) Ошибка запроса к контролеру: {response.status_code}")
                return False

        except httpx.RequestError as e:
            config.logger.error(f"(ping_worker) Ошибка запроса к контроллеру: {str(e)}")
            return False

        except Exception as e:
            config.logger.error(f"(ping_worker) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
            return False


# Удаляем воркер
async def delete_worker(
    ip_address: str,
) -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config.PING_WORKER,
                json={
                    "ip": ip_address
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                message = data.get("message")

                if message is not None:
                    config.logger.error(f"(delete_worker) message: {message}")

            else:
                config.logger.error(f"(delete_worker) Ошибка запроса к контролеру: {response.status_code}")

        except httpx.RequestError as e:
            config.logger.error(f"(delete_worker) Ошибка запроса к контроллеру: {str(e)}")

        except Exception as e:
            config.logger.error(f"(delete_worker) Неожиданная ошибка при запросе к контроллеру : {str(e)}")