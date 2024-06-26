"""init

Revision ID: 4230a75e3914
Revises: 
Create Date: 2024-04-14 13:20:44.444885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4230a75e3914'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('composition_age_rating',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('composition_genre',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('composition_status',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('composition_tag',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('composition_type',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('is_stuff', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('balance', sa.Numeric(precision=6, scale=2), nullable=False),
    sa.Column('descriptions', sa.String(length=500), nullable=True),
    sa.Column('gender', sa.Enum('female', 'male', 'not_specified', name='genderenum'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('email_not', sa.Boolean(), nullable=False),
    sa.Column('avatar', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('composition',
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('english_title', sa.String(length=255), nullable=False),
    sa.Column('another_name_title', sa.String(length=500), nullable=True),
    sa.Column('year_of_creations', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('descriptions', sa.String(), nullable=True),
    sa.Column('composition_image', sa.String(), nullable=False),
    sa.Column('view', sa.Integer(), nullable=False),
    sa.Column('count_rating', sa.Integer(), nullable=False),
    sa.Column('avg_rating', sa.Numeric(precision=3, scale=1), nullable=False),
    sa.Column('count_bookmarks', sa.Integer(), nullable=False),
    sa.Column('total_votes', sa.Integer(), nullable=False),
    sa.Column('age_rating_id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['age_rating_id'], ['composition_age_rating.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['composition_status.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['composition_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('token',
    sa.Column('access_token', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('expire_date', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now()) + INTERVAL '14 day'"), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_access_token'), 'token', ['access_token'], unique=True)
    op.create_table('composition_genre_relation',
    sa.Column('composition_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['composition_id'], ['composition.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['composition_genre.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('composition_id', 'genre_id', name='uq_composition_genre_ids')
    )
    op.create_table('composition_tag_relation',
    sa.Column('composition_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['composition_id'], ['composition.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['composition_tag.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('composition_id', 'tag_id', name='uq_composition_tag_ids')
    )
    op.create_table('user_composition_relation',
    sa.Column('composition_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('bookmark', sa.Enum('READING', 'WILL_READ', 'READED', 'ABANDONED', 'POSTPONED', name='bookmarkenum'), nullable=True),
    sa.Column('rating', sa.Enum('TEN', 'NINE', 'EIGHT', 'SEVEN', 'SIX', 'FIVE', 'FOUR', 'THREE', 'TWO', 'ONE', name='ratingenum'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['composition_id'], ['composition.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('composition_id', 'user_id', 'id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_composition_relation')
    op.drop_table('composition_tag_relation')
    op.drop_table('composition_genre_relation')
    op.drop_index(op.f('ix_token_access_token'), table_name='token')
    op.drop_table('token')
    op.drop_table('composition')
    op.drop_table('user')
    op.drop_table('composition_type')
    op.drop_table('composition_tag')
    op.drop_table('composition_status')
    op.drop_table('composition_genre')
    op.drop_table('composition_age_rating')
    # ### end Alembic commands ###
