"""add constraint user composition relation

Revision ID: 10180113270b
Revises: 4230a75e3914
Create Date: 2024-04-17 11:15:25.834752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10180113270b'
down_revision: Union[str, None] = '4230a75e3914'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_user_composition_relation', 'user_composition_relation', ['composition_id', 'user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_user_composition_relation', 'user_composition_relation', type_='unique')
    # ### end Alembic commands ###
