import os
from random import randint
from flask import Flask, render_template
from sqlalchemy import create_engine, text

app = Flask(__name__)

engine = create_engine(os.environ['POSTGRES_URI'])

@app.route('/')
def index():
    with engine.connect() as conn:
        rows = conn.execute( text("SELECT * FROM videos ORDER BY \
                random() LIMIT 10;") )
        vid_ids = [vid[0] for vid in rows.all()]
    return render_template('index.html', vids=vid_ids)

@app.route("/vids")
def send_some_vids():
   pass 


