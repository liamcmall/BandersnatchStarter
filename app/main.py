from base64 import b64decode
import os

from MonsterLab import Monster
from flask import Flask, render_template, request
from pandas import DataFrame
from datetime import datetime
import plotly.io as pio
import pandas as pd
from app.data2 import Database
from app.graph import chart
from app.machine import Machine

SPRINT = 3
APP = Flask(__name__)


@APP.route("/")
def home():
    return render_template(
        "home.html",
        sprint=f"Sprint {SPRINT}",
        monster=Monster().to_dict(),
        password=b64decode(b"VGFuZ2VyaW5lIERyZWFt"),
    )


@APP.route("/data")
def data():
    if SPRINT < 1:
        return render_template("data.html")
    # for personal reasons
    # collection_name = "Collection_" + datetime.now().strftime("%Y%m%d%H%M%S")
    db = Database()
    return render_template(
        "data.html",
        count=db.count(),
        table=db.html_table(),
    )

@APP.route("/view", methods=["GET", "POST"])
def view():
    if SPRINT < 2:
        return render_template("view.html")
    db = Database()
    options = ["clone_type", "rank","health", "assigned_general", "success_percentage"]
    x_axis = request.values.get("x_axis") or options[1]
    y_axis = request.values.get("y_axis") or options[2]
    target = request.values.get("target") or options[4]
    graph = chart(
        df=db.dataframe(),
        x=x_axis,
        y=y_axis,
        target=target,
    )
    graph_html = pio.to_html(graph, full_html=False)
    return render_template(
        "view.html",
        options=options,
        x_axis=x_axis,
        y_axis=y_axis,
        target=target,
        count=db.count(),
        graph=graph_html,
    )



@APP.route("/model", methods=["GET", "POST"])
def model():
    if SPRINT < 3:
        return render_template("model.html")
    db = Database()
    options = ["clone_type", "rank", "assigned_general"]  # Adjusted options
    filepath = os.path.join("app", "model.joblib")
    if not os.path.exists(filepath):
        df = db.dataframe()
        machine = Machine(df)
        machine.save(filepath)
    else:
        machine = Machine.open(filepath)
    clone_type = request.values.get("clone_type")  # Get clone type from request
    rank = request.values.get("rank")  # Get rank from request
    assigned_general = request.values.get("assigned_general")  # Get assigned general from request
    prediction = machine(pd.DataFrame(
        [dict(zip(options, (clone_type, rank, assigned_general)))]
    ))
    info = machine.info()
    return render_template(
        "model.html",
        info=info,
        clone_type=clone_type,
        rank=rank,
        assigned_general=assigned_general,
        prediction=prediction,
    )


if __name__ == '__main__':
    APP.run()
