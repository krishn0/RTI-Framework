"""Minimal development-database compatibility upgrades.

Production PostgreSQL deployments should use a dedicated migration runner. This
keeps an existing zero-data SQLite development database usable during setup.
"""
from sqlalchemy import inspect, text


def upgrade_development_database(engine):
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        if "scraper_runs" in tables:
            columns = {x["name"] for x in inspector.get_columns("scraper_runs")}
            if "duplicates" not in columns:
                connection.execute(text("ALTER TABLE scraper_runs ADD COLUMN duplicates INTEGER NOT NULL DEFAULT 0"))
            if "pages_scanned" not in columns:
                connection.execute(text("ALTER TABLE scraper_runs ADD COLUMN pages_scanned INTEGER NOT NULL DEFAULT 0"))
        if "sources" in tables:
            columns = {x["name"] for x in inspector.get_columns("sources")}
            if "input_kind" not in columns:
                connection.execute(text("ALTER TABLE sources ADD COLUMN input_kind VARCHAR(40) NOT NULL DEFAULT 'website'"))
            if "short_name" not in columns:
                connection.execute(text("ALTER TABLE sources ADD COLUMN short_name VARCHAR(100)"))
            if "category" not in columns:
                connection.execute(text("ALTER TABLE sources ADD COLUMN category VARCHAR(50)"))
            if "evidence_tier" not in columns:
                connection.execute(text("ALTER TABLE sources ADD COLUMN evidence_tier INTEGER NOT NULL DEFAULT 3"))
            if "languages" not in columns:
                connection.execute(text("ALTER TABLE sources ADD COLUMN languages TEXT"))
            if "tags" not in columns:
                connection.execute(text("ALTER TABLE sources ADD COLUMN tags TEXT"))
        if "document_versions" in tables:
            columns = {x["name"] for x in inspector.get_columns("document_versions")}
            if "page_count" not in columns:
                connection.execute(text("ALTER TABLE document_versions ADD COLUMN page_count INTEGER NOT NULL DEFAULT 0"))
            if "raw_extracted_text" not in columns:
                connection.execute(text("ALTER TABLE document_versions ADD COLUMN raw_extracted_text TEXT NOT NULL DEFAULT ''"))
        if "content_index" in tables:
            columns = {x["name"] for x in inspector.get_columns("content_index")}
            count = connection.execute(text("SELECT COUNT(*) FROM content_index")).scalar_one()
            if "content_id" not in columns and count == 0:
                connection.execute(text("DROP TABLE content_index"))
            else:
                if "parent_content_id" not in columns:
                    connection.execute(text("ALTER TABLE content_index ADD COLUMN parent_content_id INTEGER"))
                if "timestamp_seconds" not in columns:
                    connection.execute(text("ALTER TABLE content_index ADD COLUMN timestamp_seconds FLOAT"))
        if "project_events" in tables:
            columns = {x["name"] for x in inspector.get_columns("project_events")}
            if "investigation_id" not in columns:
                connection.execute(text("ALTER TABLE project_events ADD COLUMN investigation_id INTEGER"))
        if "financial_events" in tables:
            columns = {x["name"] for x in inspector.get_columns("financial_events")}
            if "investigation_id" not in columns:
                connection.execute(text("ALTER TABLE financial_events ADD COLUMN investigation_id INTEGER"))

