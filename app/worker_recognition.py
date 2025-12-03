# Внешние зависимости
import asyncio
import signal
from contextlib import asynccontextmanager
# Внутренние модули
from app.crud import sql_get_legislation_by_have_binary_and_not_text, sql_update_text
from app.config import get_config
from app.recognized import extract_text_from_pdf_bytes
from app.database import setup_database
from app.request import get_legislation_ids, ping_worker, delete_worker

_shutdown_event = asyncio.Event()
config = get_config()


async def worker_recognized_pdf():
    await setup_database()

    config.logger.info("Запуск воркера для обработки PDF")

    try:
        config.logger.info("Получаем ids законопроектов, которые нужно обработать")
        legislation_ids = await get_legislation_ids()
        config.logger.info(f"Получено {len(legislation_ids)} законопроектов для обработки")

        while legislation_ids and not _shutdown_event.is_set():
            config.logger.info("Получаем данные о законопроектах из базы данных")
            legislations = await sql_get_legislation_by_have_binary_and_not_text(legislation_ids)

            if not legislations:
                config.logger.info("Нет законопроектов для обработки")
                break

            config.logger.info(f"Начинаем обработку {len(legislations)} законопроектов")

            for index, (legislation_id, legislation_binary_pdf) in enumerate(legislations):
                if _shutdown_event.is_set():
                    break

                # Пинг воркера для обновления активности
                flag_request = await ping_worker(
                    processed_data=1 if index != 0 else 0,
                    expire_seconds=int(len(legislation_binary_pdf) * config.COEFF_EXPIRE_SECONDS),
                )

                if not flag_request:
                    config.logger.warning(f"Пинг не прошел для законопроекта {legislation_id}")
                    return False

                config.logger.info(f"Извлечение текста для законопроекта с id = {legislation_id}")
                # Запускаем CPU-bound операцию в отдельном потоке
                text = extract_text_from_pdf_bytes(legislation_binary_pdf)

                config.logger.info(f"Запись текста в базу данных для законопроекта {legislation_id}")
                await sql_update_text(legislation_id=legislation_id, content=text)

            config.logger.info("Получаем следующий набор ids законопроектов")
            legislation_ids = await get_legislation_ids()
            config.logger.info(f"Получено {len(legislation_ids)} законопроектов для следующей итерации")

    except asyncio.CancelledError:
        config.logger.info("Задача воркера была отменена")

    except Exception as e:
        config.logger.error(f"Ошибка в работе воркера: {e}")

    finally:
        # Всегда вызываем delete_worker при завершении
        config.logger.info(f"Завершение работы воркера")
        try:
            await delete_worker()
        except Exception as e:
            config.logger.error(f"Ошибка при удалении воркера: {e}")


def handle_shutdown_signal():
    """Обработчик сигналов завершения"""
    config.logger.info("Получен сигнал завершения работы")
    _shutdown_event.set()


async def graceful_shutdown():
    """Graceful shutdown всех компонентов"""
    config.logger.info("Начинаем graceful shutdown...")

    # Ждем завершения текущих задач (если есть)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    if tasks:
        config.logger.info(f"Ожидаем завершения {len(tasks)} задач...")
        await asyncio.sleep(2)  # Даем время на корректное завершение

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


if __name__ == "__main__":
    asyncio.run(main())