from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import OWNER_START_CREDITS, OWNER_TELEGRAM_ID
from db.models import User


def _is_owner_user(telegram_id: str) -> bool:
    if not OWNER_TELEGRAM_ID:
        return False
    return str(telegram_id).strip() == str(OWNER_TELEGRAM_ID).strip()


def _owner_initial_credits() -> int:
    if OWNER_START_CREDITS is None or str(OWNER_START_CREDITS).strip() == "":
        return 10_000
    return int(str(OWNER_START_CREDITS).strip())


async def get_user(telegram_id: str, db: AsyncSession):
    row = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return row.scalar_one_or_none()


async def create_user(telegram_id: str, db: AsyncSession):
    if _is_owner_user(telegram_id):
        user = User(telegram_id=telegram_id, credits=_owner_initial_credits())
    else:
        user = User(telegram_id=telegram_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(user_id: str, db: AsyncSession):
    user = await get_user(user_id, db)
    if user:
        return user
    try:
        return await create_user(user_id, db)
    except IntegrityError:
        await db.rollback()
        user = await get_user(user_id, db)
        if user is None:
            raise
        return user


async def add_credits(telegram_id: str, credits: int, db: AsyncSession):
    user = await get_user(telegram_id, db)
    if user is None:
        raise ValueError(f"User {telegram_id} not found for add_credits")
    user.credits += credits
    await db.commit()
    await db.refresh(user)
