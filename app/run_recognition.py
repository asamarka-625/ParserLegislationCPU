# Внешние зависимости
import asyncio
import signal
from contextlib import asynccontextmanager
# Внутренние модули
from app.crud import sql_get_legislation_by_have_binary_and_not_text, sql_update_text
from app.config import get_config
from app.recognized import extract_text_from_pdf_bytes
from app.database import setup_database
from app.request import get_legislation_ids, get_my_ip, ping_worker, delete_worker


_shutdown_event = asyncio.Event()
config = get_config()


# Обработчик распознования текста
async def worker_recognized_pdf():
    await setup_database()

    IP_ADDRESS = await get_my_ip()

    if not IP_ADDRESS:
        return

    config.logger.info("Запуск воркера для обработки PDF")

    try:
        config.logger.info("Получаем ids законопроектов, которые нужно обработать")
        legislation_ids = await get_legislation_ids(ip_address=IP_ADDRESS)

        while legislation_ids and not _shutdown_event.is_set():
            config.logger.info("Получаем данные о законопроектах")
            legislations = await sql_get_legislation_by_have_binary_and_not_text(legislation_ids)

            for i, (legislation_id, legislation_binary_pdf) in enumerate(legislations):
                if _shutdown_event.is_set():
                    config.logger.info("Получен сигнал завершения, прерываем обработку")
                    break

                if i != 0:
                    flag_request = await ping_worker(
                        ip_address=IP_ADDRESS,
                        processed_data=1,
                        expire_seconds=int(len(legislation_binary_pdf) * config.COEFF_EXPIRE_SECONDS),
                    )

                    if not flag_request:
                        continue

                config.logger.info(f"Получаем текст для законопроекта с id = {legislation_id}")
                text = extract_text_from_pdf_bytes(legislation_binary_pdf)

                config.logger.info("Записываем текст в базу данных")

                flag_db = await sql_update_text(legislation_id=legislation_id, content=text)

                if not flag_db:
                    continue

            if _shutdown_event.is_set():
                break

            config.logger.info("Получаем ids законопроектов, которые нужно обработать")
            legislation_ids = await get_legislation_ids(IP_ADDRESS)

    except asyncio.CancelledError:
        config.logger.info("Задача воркера была отменена")

    except Exception as e:
        config.logger.error(f"Ошибка в работе воркера: {e}")

    finally:
        # Всегда вызываем delete_worker при завершении
        config.logger.info(f"Завершение работы воркера {IP_ADDRESS}")
        try:
            await delete_worker(ip_address=IP_ADDRESS)
        except Exception as e:
            config.logger.error(f"Ошибка при удалении воркера: {e}")


def handle_shutdown_signal():
    """Обработчик сигналов завершения"""
    config.logger.info("Получен сигнал завершения работы")
    _shutdown_event.set()


async def graceful_shutdown():
    """Graceful shutdown всех компонентов"""
    config.logger.info("Начинаем graceful shutdown...")

    # Даем время на завершение текущих операций
    await asyncio.sleep(1)

    config.logger.info("Graceful shutdown завершен")


@asynccontextmanager
async def worker_lifespan():
    """Контекстный менеджер для управления жизненным циклом воркера"""
    # Устанавливаем обработчики сигналов
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_shutdown_signal)

    try:
        yield
    finally:
        # Выполняем graceful shutdown при выходе
        await graceful_shutdown()


async def main():
    """Основная функция запуска воркера"""
    async with worker_lifespan():
        await worker_recognized_pdf()