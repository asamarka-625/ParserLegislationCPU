# Внешние зависимости
from typing import Sequence, List
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
# Внутренние модули
from app.config import get_config
from app.database import connection
from app.models import DataLegislation


config = get_config()


# Выводим все законы, у которых нет байткода PDF файла
@connection
async def sql_get_legislation_by_not_binary_pdf(
        session: AsyncSession
) -> Sequence[DataLegislation]:
    try:
        legislation_results = await session.execute(
            sa.select(DataLegislation)
            .where(DataLegislation.binary_pdf == None)
            .order_by(DataLegislation.id)
        )

        legislation = legislation_results.scalars().all()
        return legislation

    except SQLAlchemyError as e:
        config.logger.error(f"Database error read legislation with none binary_pdf: {e}")

    except Exception as e:
        config.logger.error(f"Unexpected error read legislation with none binary_pdf: {e}")


# Записываем бинарный код PDF файла
@connection
async def sql_update_binary_pdf(
        publication_number: str,
        content: bytes,
        session: AsyncSession
) -> bool:
    try:
        legislation_results = await session.execute(
            sa.select(DataLegislation)
            .where(DataLegislation.publication_number == publication_number)
        )

        legislation = legislation_results.scalar_one()
        legislation.binary_pdf = content
        await session.commit()
        return True

    except NoResultFound:
        config.logger.error(f"Legislation not found by publication_number: {publication_number}")
        return False

    except SQLAlchemyError as e:
        config.logger.error(f"Database error update binary_pdf: {e}")
        return False

    except Exception as e:
        config.logger.error(f"Unexpected error update binary_pdf: {e}")
        return False

# Выводим все законы, у которых нет текста, но есть binary_pdf
@connection
async def sql_get_legislation_by_have_binary_and_not_text(
    legislation_ids: List[int],
    session: AsyncSession
) -> Sequence[DataLegislation]:
    try:
        legislation_results = await session.execute(
            sa.select(DataLegislation.id, DataLegislation.binary_pdf)
            .where(DataLegislation.id.in_(legislation_ids))
        )

        legislation = legislation_results.all()
        return legislation

    except SQLAlchemyError as e:
        config.logger.error(f"Database error read legislation with binary_pdf and none text: {e}")
        return []

    except Exception as e:
        config.logger.error(f"Unexpected error read legislation with binary_pdf and none text: {e}")
        return []

# Записываем текст PDf файла
@connection
async def sql_update_text(
    legislation_id: str,
    content: str,
    session: AsyncSession
) -> None:
    try:
        legislation_results = await session.execute(
            sa.select(DataLegislation)
            .where(DataLegislation.id == legislation_id)
        )

        legislation = legislation_results.scalar_one()
        legislation.text = content
        await session.commit()

    except NoResultFound:
        config.logger.error(f"Legislation not found by legislation id: {legislation_id}")

    except SQLAlchemyError as e:
        config.logger.error(f"Database error update text: {e}")

    except Exception as e:
        config.logger.error(f"Unexpected error update text: {e}")