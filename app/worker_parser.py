# Внутренние модули
from app.database import setup_database
from app.parser import ParserPDF
from app.crud import sql_get_legislation_by_not_binary_pdf, sql_update_binary_pdf
from app.config import get_config


config = get_config()


# Обработчик парсинга байт-кода pdf файлов
async def worker_parser_pdf():
    await setup_database()

    while True:
        all_legislation = await sql_get_legislation_by_not_binary_pdf()
        batch_size = 300

        if len(all_legislation) == 0:
            break

        for batch_sart in range(0, len(all_legislation), batch_size):
            config.logger.info(f"Берем партию {batch_size} для запросов {batch_sart}/{len(all_legislation)}")

            batch_end = batch_sart + batch_size
            parser = ParserPDF()
            contents_binary = await parser.async_run(
                list_legislation=list(all_legislation[batch_sart:batch_end])
            )

            for i, data in enumerate(contents_binary):
                config.logger.info(f"Обновляем binary_pdf в таблице. Итерация: {i + 1}/{len(contents_binary)}")
                await sql_update_binary_pdf(
                    publication_number=data[0],
                    content=data[1]
                )

