"""add-expire-date-in-Token-table

Revision ID: 8fc799c17b26
Revises: 1481de48282b
Create Date: 2024-04-10 13:54:28.470137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fc799c17b26'
down_revision: Union[str, None] = '1481de48282b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('expire_date', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now()) + INTERVAL '14 day'"), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('token', 'expire_date')
    # ### end Alembic commands ###
