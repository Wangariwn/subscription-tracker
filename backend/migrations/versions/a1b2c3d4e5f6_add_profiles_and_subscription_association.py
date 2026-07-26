"""add profiles and subscription association object

Revision ID: a1b2c3d4e5f6
Revises: 66d24407a20c
Create Date: 2026-07-26 18:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "66d24407a20c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("bio", sa.String(length=255), nullable=True),
        sa.Column("preferred_currency", sa.String(length=3), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.add_column(
            sa.Column("catalog_service_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(sa.Column("enrolled_at", sa.Date(), nullable=True))
        batch_op.create_foreign_key(
            "fk_subscriptions_catalog_service_id",
            "catalog_services",
            ["catalog_service_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # Link existing rows to catalog by service_name when possible (dev/seed DBs).
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE subscriptions
            SET catalog_service_id = (
                SELECT catalog_services.id
                FROM catalog_services
                WHERE catalog_services.service_name = subscriptions.service_name
            )
            WHERE catalog_service_id IS NULL
            """
        )
    )
    connection.execute(
        sa.text(
            """
            UPDATE subscriptions
            SET enrolled_at = renewal_date
            WHERE enrolled_at IS NULL
            """
        )
    )

    # Drop rows that could not be matched so NOT NULL + unique constraints apply.
    connection.execute(
        sa.text("DELETE FROM subscriptions WHERE catalog_service_id IS NULL")
    )

    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.alter_column(
            "catalog_service_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.alter_column(
            "enrolled_at",
            existing_type=sa.Date(),
            nullable=False,
        )
        batch_op.drop_column("service_name")
        batch_op.create_unique_constraint(
            "uq_user_catalog_service",
            ["user_id", "catalog_service_id"],
        )


def downgrade():
    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.drop_constraint("uq_user_catalog_service", type_="unique")
        batch_op.add_column(
            sa.Column("service_name", sa.String(length=120), nullable=True)
        )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE subscriptions
            SET service_name = (
                SELECT catalog_services.service_name
                FROM catalog_services
                WHERE catalog_services.id = subscriptions.catalog_service_id
            )
            """
        )
    )

    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.alter_column(
            "service_name",
            existing_type=sa.String(length=120),
            nullable=False,
        )
        batch_op.drop_constraint(
            "fk_subscriptions_catalog_service_id",
            type_="foreignkey",
        )
        batch_op.drop_column("enrolled_at")
        batch_op.drop_column("catalog_service_id")

    op.drop_table("profiles")
