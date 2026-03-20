"""init pipeline tables

Revision ID: 20260320_0001
Revises: None
Create Date: 2026-03-20 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260320_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("base_url", sa.Text(), nullable=False, unique=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "crawl_queue",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("url", name="uq_crawl_queue_url"),
    )

    op.create_table(
        "raw_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=True),
        sa.Column("html", sa.Text(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_duplicate", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("duplicate_of_id", sa.Integer(), sa.ForeignKey("raw_documents.id"), nullable=True),
        sa.UniqueConstraint("url", name="uq_raw_documents_url"),
    )
    op.create_index("ix_raw_documents_content_hash", "raw_documents", ["content_hash"])

    op.create_table(
        "parsed_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_document_id", sa.Integer(), sa.ForeignKey("raw_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("cleaned_text", sa.Text(), nullable=True),
        sa.Column("tokens", sa.Text(), nullable=True),
        sa.Column("stems", sa.Text(), nullable=True),
        sa.Column("bigrams", sa.Text(), nullable=True),
        sa.Column("trigrams", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("raw_document_id", name="uq_parsed_raw_document_id"),
    )

    op.create_table(
        "crawl_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("crawl_events")
    op.drop_table("parsed_documents")
    op.drop_index("ix_raw_documents_content_hash", table_name="raw_documents")
    op.drop_table("raw_documents")
    op.drop_table("crawl_queue")
    op.drop_table("sources")
