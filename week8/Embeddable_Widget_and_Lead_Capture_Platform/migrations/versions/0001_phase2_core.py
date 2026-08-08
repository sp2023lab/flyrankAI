"""phase2 core tables
Revision ID: 0001_phase2_core
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_phase2_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("api_key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("widgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("widget_type", sa.String(40), nullable=False), sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500)), sa.Column("button_text", sa.String(60), nullable=False),
        sa.Column("fields", postgresql.JSONB(), nullable=False), sa.Column("display_options", postgresql.JSONB(), nullable=False),
        sa.Column("allowed_origins", postgresql.JSONB(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_widgets_tenant_id", "widgets", ["tenant_id"])
    op.create_table("submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("widget_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("widgets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False), sa.Column("origin", sa.String(500), nullable=False),
        sa.Column("ip_hash", sa.String(64), nullable=False), sa.Column("user_agent", sa.String(500)),
        sa.Column("country_code", sa.String(2)), sa.Column("country", sa.String(120)), sa.Column("city", sa.String(120)), sa.Column("geo_provider", sa.String(40)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("widget_id", "idempotency_key", name="uq_submission_widget_idempotency"))
    op.create_index("ix_submissions_tenant_created", "submissions", ["tenant_id", "created_at"])
    op.create_index("ix_submissions_widget_created", "submissions", ["widget_id", "created_at"])
    op.create_index("ix_submissions_country_code", "submissions", ["country_code"])
    op.create_table("notification_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False), sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_error", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("submission_id", name="uq_notification_submission"))
    op.create_index("ix_notification_jobs_status_next", "notification_jobs", ["status", "next_attempt_at"])


def downgrade():
    op.drop_table("notification_jobs"); op.drop_table("submissions"); op.drop_table("widgets"); op.drop_table("tenants")
