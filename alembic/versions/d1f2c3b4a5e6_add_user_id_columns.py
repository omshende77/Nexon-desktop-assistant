"""Add user_id foreign keys to remaining tables

Revision ID: d1f2c3b4a5e6
Revises: c937555f444c
Create Date: 2026-05-31 14:10:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d1f2c3b4a5e6"
down_revision: Union[str, Sequence[str], None] = "c937555f444c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id to messages, tasks, notes, reminders, memories

    op.add_column("messages", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_messages_user_id"),
        "messages",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "messages",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("tasks", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_tasks_user_id"),
        "tasks",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "tasks",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("notes", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_notes_user_id"),
        "notes",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "notes",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("reminders", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_reminders_user_id"),
        "reminders",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "reminders",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.add_column("memories", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_memories_user_id"),
        "memories",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "memories",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Remove the columns and constraints in reverse order

    op.drop_constraint(None, "memories", type_="foreignkey")
    op.drop_index(op.f("ix_memories_user_id"), table_name="memories")
    op.drop_column("memories", "user_id")

    op.drop_constraint(None, "reminders", type_="foreignkey")
    op.drop_index(op.f("ix_reminders_user_id"), table_name="reminders")
    op.drop_column("reminders", "user_id")

    op.drop_constraint(None, "notes", type_="foreignkey")
    op.drop_index(op.f("ix_notes_user_id"), table_name="notes")
    op.drop_column("notes", "user_id")

    op.drop_constraint(None, "tasks", type_="foreignkey")
    op.drop_index(op.f("ix_tasks_user_id"), table_name="tasks")
    op.drop_column("tasks", "user_id")

    op.drop_constraint(None, "messages", type_="foreignkey")
    op.drop_index(op.f("ix_messages_user_id"), table_name="messages")
    op.drop_column("messages", "user_id")