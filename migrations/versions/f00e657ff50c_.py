"""empty message

Revision ID: f00e657ff50c
Revises: 6ea665fcec3e
Create Date: 2020-06-16 08:04:03.989293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f00e657ff50c'
down_revision = '6ea665fcec3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inspiration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('workout_type', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(length=50), nullable=True),
    sa.Column('instructor', sa.String(length=50), nullable=True),
    sa.Column('instructor_sex', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('why_loved', sa.String(length=200), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('picture_url', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'picture_url')
    op.drop_table('inspiration')
    # ### end Alembic commands ###
