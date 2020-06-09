"""empty message

Revision ID: 358470bc5e0f
Revises: 59d1f84e4894
Create Date: 2020-06-09 08:12:44.615747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '358470bc5e0f'
down_revision = '59d1f84e4894'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity', sa.Column('iso_timestamp', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activity', 'iso_timestamp')
    # ### end Alembic commands ###
