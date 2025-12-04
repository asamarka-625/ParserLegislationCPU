# Внешние зависимости
from typing import List, Dict, Union
import httpx
# Внутренние модули
from app.config import get_config
from app.utils import get_base_64_from_bytes


config = get_config()


# Получаем публикационные номера данные законопроектов
async def get_number_legislation() -> List[Dict[str, Union[int, str]]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                config.GET_LEGISLATION_NOT_BINARY,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data

            else:
                config.logger.error(f"(get_number_legislation) Ошибка запроса к контролеру: {response.status_code}")
                return []

        except httpx.RequestError as e:
            config.logger.error(f"(get_number_legislation) Ошибка запроса к контроллеру: {str(e)}")
            return []

        except Exception as e:
            config.logger.error(f"(get_number_legislation) Неожиданная ошибка при запросе к контроллеру : {str(e)}")
            return []


# Обновляем бинарные данные законопроекта
async def update_binary_legislation(id_: int, binary: bytes) -> None:
    async with httpx.AsyncClient() as client:
        try:
            binary_base_64 = get_base_64_from_bytes(binary)

            response = await client.patch(
                config.UPDATE_LEGISLATION_BINARY,
                json={
                    "id": id_,
                    "binary": binary_base_64
                },
                timeout=30.0
            )

            if response.status_code != 200:
                config.logger.error(f"(update_binary_legislation) Ошибка запроса к контролеру: {response.status_code}")

        except httpx.RequestError as e:
            config.logger.error(f"(update_binary_legislation) Ошибка запроса к контроллеру: {str(e)}")

        except Exception as e:
            config.logger.error(f"(update_binary_legislation) Неожиданная ошибка при запросе к контроллеру : {str(e)}")