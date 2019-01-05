import sqlite3
import click

from flask import g, current_app
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_type=sqlite3.PARCEDECL_TYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db():
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_recourse("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
