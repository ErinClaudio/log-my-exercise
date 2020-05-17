"""updates

Revision ID: ff57d5d6ef22
Revises: e7e289fe969a
Create Date: 2020-05-17 08:00:50.907924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff57d5d6ef22'
down_revision = 'e7e289fe969a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('activity_type')
    op.drop_column('regular_activity', 'is_active')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.VARCHAR(length=140), nullable=True))
    op.add_column('regular_activity', sa.Column('is_active', sa.BOOLEAN(), nullable=True))
    op.create_table('activity_type',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
