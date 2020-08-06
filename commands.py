import click
from flask import Blueprint
from flask.cli import with_appcontext

from pbl import db
#from pbl.models import *

cmd = Blueprint('db', __name__)

@cmd.cli.command('create_tables') 
def create_tables():         
    db.create_all()
    print('***** Datebase created ****')

# @click.command(name='create_tables')
# @with_appcontext
# def create_tables():
#     db.create_all()
