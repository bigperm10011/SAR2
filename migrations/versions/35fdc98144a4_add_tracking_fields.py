"""add tracking fields

Revision ID: 35fdc98144a4
Revises: 905e6ce7fe3d
Create Date: 2018-06-04 18:29:09.236589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35fdc98144a4'
down_revision = '905e6ce7fe3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('leaver', sa.Column('track_firm', sa.String(length=100), nullable=True))
    op.add_column('leaver', sa.Column('track_location', sa.String(length=100), nullable=True))
    op.add_column('leaver', sa.Column('track_role', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('leaver', 'track_role')
    op.drop_column('leaver', 'track_location')
    op.drop_column('leaver', 'track_firm')
    # ### end Alembic commands ###
