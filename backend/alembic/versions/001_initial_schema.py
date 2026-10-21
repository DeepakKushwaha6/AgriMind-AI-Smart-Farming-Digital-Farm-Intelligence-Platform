"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-21 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='farmer'),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('village', sa.String(length=100), server_default='Jarga', nullable=False),
        sa.Column('district', sa.String(length=100), server_default='Hazaribagh', nullable=False),
        sa.Column('state', sa.String(length=100), server_default='Jharkhand', nullable=False),
        sa.Column('lat', sa.Float(), server_default='24.002', nullable=False),
        sa.Column('lon', sa.Float(), server_default='85.361', nullable=False),
        sa.Column('preferred_language', sa.String(length=10), server_default='en', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # User API Keys (BYOK)
    op.create_table(
        'user_api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=30), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('key_preview', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.Integer(), server_default='1', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='untested', nullable=False),
        sa.Column('last_tested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(length=255), nullable=True),
        sa.Column('quota_limit_hint', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_api_keys_user_id'), 'user_api_keys', ['user_id'], unique=False)

    # Farms table
    op.create_table(
        'farms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('total_area_acres', sa.Float(), nullable=False),
        sa.Column('original_unit_value', sa.Float(), nullable=False),
        sa.Column('original_unit_name', sa.String(length=50), nullable=False),
        sa.Column('tenure', sa.String(length=50), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Fields table
    op.create_table(
        'fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('area_acres', sa.Float(), nullable=False),
        sa.Column('area_hectares', sa.Float(), nullable=False),
        sa.Column('soil_type', sa.String(length=100), nullable=False),
        sa.Column('water_source', sa.String(length=100), nullable=False),
        sa.Column('geojson_boundary', sa.Text(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('fields')
    op.drop_table('farms')
    op.drop_table('user_api_keys')
    op.drop_table('users')
