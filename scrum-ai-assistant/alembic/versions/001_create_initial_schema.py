"""Create initial schema with meetings, extracted_items, and tasks tables

Revision ID: 001
Revises:
Create Date: 2024-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""
    # Create meetings table
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "ceremony_type",
            sa.Enum("STANDUP", "PLANNING", "REVIEW", "RETRO", name="ceremonytype"),
            nullable=False,
        ),
        sa.Column("meeting_date", sa.DateTime(), nullable=False),
        sa.Column(
            "tool_type",
            sa.Enum("JIRA", "AZURE", name="tooltype"),
            nullable=False,
        ),
        sa.Column("project_key", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "CREATED",
                "UPLOADED",
                "TRANSCRIBED",
                "EXTRACTED",
                "TASKS_PUSHED",
                "COMPLETED",
                "FAILED",
                name="meetingstatus",
            ),
            nullable=False,
            server_default="CREATED",
        ),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("audio_filename", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create extracted_items table
    op.create_table(
        "extracted_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column(
            "item_type",
            sa.Enum("DECISION", "BLOCKER", "ACTION_ITEM", name="itemtype"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("tool_type", sa.String(length=20), nullable=False),
        sa.Column("external_key_or_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("NEW", "PUSHED", "COMPLETED", "INCOMPLETE", name="taskstatus"),
            nullable=False,
            server_default="NEW",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for better query performance
    op.create_index("ix_meetings_status", "meetings", ["status"])
    op.create_index("ix_meetings_project_key", "meetings", ["project_key"])
    op.create_index("ix_extracted_items_meeting_id", "extracted_items", ["meeting_id"])
    op.create_index("ix_extracted_items_type", "extracted_items", ["item_type"])
    op.create_index("ix_tasks_meeting_id", "tasks", ["meeting_id"])
    op.create_index("ix_tasks_external_key", "tasks", ["external_key_or_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index("ix_tasks_status")
    op.drop_index("ix_tasks_external_key")
    op.drop_index("ix_tasks_meeting_id")
    op.drop_index("ix_extracted_items_type")
    op.drop_index("ix_extracted_items_meeting_id")
    op.drop_index("ix_meetings_project_key")
    op.drop_index("ix_meetings_status")

    op.drop_table("tasks")
    op.drop_table("extracted_items")
    op.drop_table("meetings")

    # Drop enums
    sa.Enum(name="taskstatus").drop(op.get_bind())
    sa.Enum(name="itemtype").drop(op.get_bind())
    sa.Enum(name="meetingstatus").drop(op.get_bind())
    sa.Enum(name="tooltype").drop(op.get_bind())
    sa.Enum(name="ceremonytype").drop(op.get_bind())
