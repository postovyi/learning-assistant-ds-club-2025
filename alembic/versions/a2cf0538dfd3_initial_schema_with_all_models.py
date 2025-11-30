"""Initial schema with all models

Revision ID: a2cf0538dfd3
Revises: 
Create Date: 2025-11-25 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a2cf0538dfd3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    message_role_enum = postgresql.ENUM('user', 'assistant', 'system', name='messagerole')
    message_role_enum.create(op.get_bind(), checkfirst=True)
    
    file_type_enum = postgresql.ENUM('pdf', 'docx', 'txt', 'image', 'other', name='filetype')
    file_type_enum.create(op.get_bind(), checkfirst=True)
    
    homework_status_enum = postgresql.ENUM('pending', 'submitted', 'graded', name='homeworkstatus')
    homework_status_enum.create(op.get_bind(), checkfirst=True)
    
    grade_enum = postgresql.ENUM('A', 'B', 'C', 'D', 'F', 'PASS', 'FAIL', name='grade')
    grade_enum.create(op.get_bind(), checkfirst=True)
    
    lesson_status_enum = postgresql.ENUM('not_started', 'in_progress', 'completed', name='lessonstatus')
    lesson_status_enum.create(op.get_bind(), checkfirst=True)
    
    lesson_message_type_enum = postgresql.ENUM('text', 'quiz', 'explanation', name='lessonmessagetype')
    lesson_message_type_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)

    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)

    # Create materials table
    op.create_table('materials',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_type', file_type_enum, nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_materials_id'), 'materials', ['id'], unique=False)

    # Create mind_maps table
    op.create_table('mind_maps',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('node_count', sa.Integer(), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mind_maps_id'), 'mind_maps', ['id'], unique=False)

    # Create homework table
    op.create_table('homework',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('status', homework_status_enum, nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_homework_id'), 'homework', ['id'], unique=False)

    # Create homework_tasks table
    op.create_table('homework_tasks',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('homework_id', postgresql.UUID(), nullable=False),
        sa.Column('task_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('uploaded_file_url', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['homework_id'], ['homework.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_homework_tasks_id'), 'homework_tasks', ['id'], unique=False)

    # Create homework_reviews table
    op.create_table('homework_reviews',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('homework_id', postgresql.UUID(), nullable=False),
        sa.Column('grade', grade_enum, nullable=True),
        sa.Column('overall_feedback', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reviewed_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['homework_id'], ['homework.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_homework_reviews_id'), 'homework_reviews', ['id'], unique=False)

    # Create homework_task_reviews table
    op.create_table('homework_task_reviews',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('homework_task_id', postgresql.UUID(), nullable=False),
        sa.Column('task_feedback', sa.Text(), nullable=True),
        sa.Column('score', postgresql.NUMERIC(5, 2), nullable=True),
        sa.ForeignKeyConstraint(['homework_task_id'], ['homework_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_homework_task_reviews_id'), 'homework_task_reviews', ['id'], unique=False)

    # Create lessons table
    op.create_table('lessons',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('status', lesson_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lessons_id'), 'lessons', ['id'], unique=False)

    # Create lesson_messages table
    op.create_table('lesson_messages',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(), nullable=False),
        sa.Column('type', lesson_message_type_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lesson_messages_id'), 'lesson_messages', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_lesson_messages_id'), table_name='lesson_messages')
    op.drop_table('lesson_messages')
    
    op.drop_index(op.f('ix_lessons_id'), table_name='lessons')
    op.drop_table('lessons')
    
    op.drop_index(op.f('ix_homework_task_reviews_id'), table_name='homework_task_reviews')
    op.drop_table('homework_task_reviews')
    
    op.drop_index(op.f('ix_homework_reviews_id'), table_name='homework_reviews')
    op.drop_table('homework_reviews')
    
    op.drop_index(op.f('ix_homework_tasks_id'), table_name='homework_tasks')
    op.drop_table('homework_tasks')
    
    op.drop_index(op.f('ix_homework_id'), table_name='homework')
    op.drop_table('homework')
    
    op.drop_index(op.f('ix_mind_maps_id'), table_name='mind_maps')
    op.drop_table('mind_maps')
    
    op.drop_index(op.f('ix_materials_id'), table_name='materials')
    op.drop_table('materials')
    
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_table('sessions')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enums
    postgresql.ENUM(name='lessonmessagetype').drop(op.get_bind())
    postgresql.ENUM(name='lessonstatus').drop(op.get_bind())
    postgresql.ENUM(name='grade').drop(op.get_bind())
    postgresql.ENUM(name='homeworkstatus').drop(op.get_bind())
    postgresql.ENUM(name='filetype').drop(op.get_bind())
    postgresql.ENUM(name='messagerole').drop(op.get_bind())
