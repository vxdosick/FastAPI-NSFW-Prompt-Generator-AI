"""add negative_prompt to saved prompt objects

Revision ID: 20260620_0003
Revises: 20260610_0002
Create Date: 2026-06-20
"""

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260620_0003"
down_revision: Union[str, None] = "20260610_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _backfill_negative_prompt(prompts: list) -> list:
    updated = []
    for item in prompts:
        if not isinstance(item, dict):
            updated.append(item)
            continue
        entry = dict(item)
        if "negative_prompt" not in entry:
            entry["negative_prompt"] = ""
        updated.append(entry)
    return updated


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT telegram_id, prompts FROM users WHERE prompts IS NOT NULL")
    ).fetchall()

    for telegram_id, prompts in rows:
        if not prompts or not isinstance(prompts, list):
            continue
        new_prompts = _backfill_negative_prompt(prompts)
        conn.execute(
            sa.text("UPDATE users SET prompts = CAST(:prompts AS JSON) WHERE telegram_id = :tid"),
            {"prompts": json.dumps(new_prompts), "tid": telegram_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT telegram_id, prompts FROM users WHERE prompts IS NOT NULL")
    ).fetchall()

    for telegram_id, prompts in rows:
        if not prompts or not isinstance(prompts, list):
            continue
        stripped = []
        for item in prompts:
            if not isinstance(item, dict):
                stripped.append(item)
                continue
            entry = dict(item)
            entry.pop("negative_prompt", None)
            stripped.append(entry)
        conn.execute(
            sa.text("UPDATE users SET prompts = CAST(:prompts AS JSON) WHERE telegram_id = :tid"),
            {"prompts": json.dumps(stripped), "tid": telegram_id},
        )
