from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "15b7965b718e"
down_revision = "14b7965b718d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Compartments
    op.add_column(
        "compartments",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),  # garante valor para linhas existentes
        ),
    )
    op.create_index(
        "ix_compartments_is_active",
        "compartments",
        ["is_active"],
        unique=False,
    )

    # Instances
    op.add_column(
        "instances",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_index(
        "ix_instances_is_active",
        "instances",
        ["is_active"],
        unique=False,
    )

    # opcional: remover server_default depois de popular
    op.alter_column("compartments", "is_active", server_default=None)
    op.alter_column("instances", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_instances_is_active", table_name="instances")
    op.drop_column("instances", "is_active")

    op.drop_index("ix_compartments_is_active", table_name="compartments")
    op.drop_column("compartments", "is_active")
