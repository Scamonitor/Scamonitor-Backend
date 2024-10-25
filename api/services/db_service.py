import mysql.connector
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME']
        )

    return g.db

def init_db():
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        schema = f.read().decode('utf8')
        statements = schema.split(';')
        
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
    
    db.commit()
    cursor.close()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)