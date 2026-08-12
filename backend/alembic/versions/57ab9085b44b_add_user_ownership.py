"""add user ownership

Revision ID: 57ab9085b44b
Revises: 0cee0df426df
Create Date: 2026-08-10 07:18:11.242850

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic

revision: str = "57ab9085b44b"
down_revision: Union[str, Sequence[str], None] = "0cee0df426df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user ownership to financial tables."""

    # ---------------------------------------------------------
    # RECEIPTS
    #
    # user_id already exists because the previous migration
    # partially executed before failing.
    #
    # Therefore we ONLY add the foreign key here.
    # ---------------------------------------------------------

    with op.batch_alter_table("receipts", schema=None) as batch_op:

        batch_op.create_foreign_key(
            "fk_receipts_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )

    # ---------------------------------------------------------
    # RECURRING BILLS
    #
    # user_id does not exist yet.
    # ---------------------------------------------------------

    with op.batch_alter_table("recurring_bills", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_recurring_bills_user_id",
            ["user_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_recurring_bills_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )

    # ---------------------------------------------------------
    # TRANSACTIONS
    #
    # user_id does not exist yet.
    # ---------------------------------------------------------

    with op.batch_alter_table("transactions", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_transactions_user_id",
            ["user_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_transactions_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade() -> None:
    """Remove user ownership from financial tables."""

    # ---------------------------------------------------------
    # TRANSACTIONS
    # ---------------------------------------------------------

    with op.batch_alter_table("transactions", schema=None) as batch_op:

        batch_op.drop_constraint(
            "fk_transactions_user_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_transactions_user_id",
        )

        batch_op.drop_column(
            "user_id",
        )

    # ---------------------------------------------------------
    # RECURRING BILLS
    # ---------------------------------------------------------

    with op.batch_alter_table("recurring_bills", schema=None) as batch_op:

        batch_op.drop_constraint(
            "fk_recurring_bills_user_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_recurring_bills_user_id",
        )

        batch_op.drop_column(
            "user_id",
        )

    # ---------------------------------------------------------
    # RECEIPTS
    # ---------------------------------------------------------

    with op.batch_alter_table("receipts", schema=None) as batch_op:

        batch_op.drop_constraint(
            "fk_receipts_user_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_receipts_user_id",
        )

        batch_op.drop_column(
            "user_id",
        )