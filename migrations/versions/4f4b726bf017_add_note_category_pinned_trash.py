"""Add note category, pinned, and soft-delete (trash) support

Revision ID: 4f4b726bf017
Revises: 721a8be00a5b
Create Date: 2026-08-14 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f4b726bf017'
down_revision = '721a8be00a5b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('pinned', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))
        batch_op.drop_constraint('unique_user_title', type_='unique')

    # A trashed note (deleted_at set) shouldn't block creating a new active
    # note with the same title, so this replaces the old plain unique
    # constraint with a partial index that only applies to active notes.
    op.create_index(
        'ix_notes_user_title_active',
        'notes',
        ['user_id', 'title'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
        sqlite_where=sa.text('deleted_at IS NULL'),
    )


def downgrade():
    op.drop_index('ix_notes_user_title_active', table_name='notes')
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_user_title', ['user_id', 'title'])
        batch_op.drop_column('deleted_at')
        batch_op.drop_column('pinned')
        batch_op.drop_column('category')
