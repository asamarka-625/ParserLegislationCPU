# Внутренние модули
from app.parser import ParserPDF
from app.config import get_config
from app.request import get_number_legislation, update_binary_legislation


config = get_config()


# Обработчик парсинга байт-кода pdf файлов
async def worker_parser_pdf():
    while True:
        all_legislation_number = await get_number_legislation()
        batch_size = 300

        if len(all_legislation_number) == 0:
            break

        for batch_sart in range(0, len(all_legislation_number), batch_size):
            config.logger.info(f"Берем партию {batch_size} для запросов {batch_sart}/{len(all_legislation_number)}")

            batch_end = batch_sart + batch_size
            parser = ParserPDF()
            contents_binary = await parser.async_run(
                list_publication_number=all_legislation_number[batch_sart:batch_end]
            )

            for i, data in enumerate(contents_binary):
                config.logger.info(f"Обновляем binary_pdf в таблице. Итерация: {i + 1}/{len(contents_binary)}")
                await update_binary_legislation(
                    id_=data[0],
                    binary=data[1]
                )

