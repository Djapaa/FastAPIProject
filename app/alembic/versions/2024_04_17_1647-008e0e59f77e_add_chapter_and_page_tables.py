"""add chapter and page tables

Revision ID: 008e0e59f77e
Revises: 9eb988387673
Create Date: 2024-04-17 16:47:02.134798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008e0e59f77e'
down_revision: Union[str, None] = '9eb988387673'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chapter',
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=False),
    sa.Column('pub_date', sa.DateTime(), nullable=True),
    sa.Column('composition_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['composition_id'], ['composition.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('composition_id', 'number', name='uq_chapter_number_composition')
    )
    op.create_table('page',
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('page_image', sa.String(), nullable=False),
    sa.Column('chapter_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['chapter_id'], ['chapter.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number', 'chapter_id', name='uq_page_chapter_number')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('page')
    op.drop_table('chapter')
    # ### end Alembic commands ###