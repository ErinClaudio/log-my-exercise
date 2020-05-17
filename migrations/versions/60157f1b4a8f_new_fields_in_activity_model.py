"""new fields in activity  model

Revision ID: 60157f1b4a8f
Revises: f6fcf866531c
Create Date: 2020-04-30 07:02:21.873653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60157f1b4a8f'
down_revision = 'f6fcf866531c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity', sa.Column('duration', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activity', 'duration')
    # ### end Alembic commands ###
