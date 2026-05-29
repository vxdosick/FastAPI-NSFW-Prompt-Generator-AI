from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import OWNER_START_CREDITS, OWNER_TELEGRAM_ID, MAX_SAVED_PROMPTS
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


async def get_saved_prompts(telegram_id: str, db: AsyncSession):
    user = await get_user(telegram_id, db)
    if user is None or not user.prompts:
        return []
    return user.prompts


async def save_prompt(telegram_id: str, prompt: str, title: str, db: AsyncSession):
    user = await get_or_create_user(telegram_id, db)
    prompts = list(user.prompts or [])

    if len(prompts) >= MAX_SAVED_PROMPTS:
        return False, prompts

    prompt_index = len(prompts) + 1
    display_title = (title or "").strip() or f"Prompt {prompt_index}"
    prompts.append(
        {
            "index": prompt_index,
            "title": display_title,
            "prompt": prompt,
        }
    )
    user.prompts = prompts
    await db.commit()
    await db.refresh(user)
    return True, prompts


async def delete_saved_prompt(telegram_id: str, list_index: int, db: AsyncSession):
    user = await get_user(telegram_id, db)
    if user is None or not user.prompts:
        return False, []

    prompts = list(user.prompts)
    if list_index < 0 or list_index >= len(prompts):
        return False, prompts

    prompts.pop(list_index)
    for i, item in enumerate(prompts, start=1):
        item["index"] = i

    user.prompts = prompts
    await db.commit()
    await db.refresh(user)
    return True, prompts
