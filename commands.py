import click
from flask.cli import with_appcontext

from pbl import db
from pbl import models
# from models import *

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
