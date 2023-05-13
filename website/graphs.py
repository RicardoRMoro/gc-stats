from flask import Blueprint, render_template, session
from .auth import login_required
from .models import TemporaryPartidas, db
from sqlalchemy import func, extract
import calendar

graphs = Blueprint('graphs', __name__)

@graphs.route('/graphs')
@login_required
def graphs_page():

    # Graph 1: Total matches by month
    mapsqry = TemporaryPartidas.query.with_entities(TemporaryPartidas.Mapa, db.func.count(TemporaryPartidas.Partida)).group_by(TemporaryPartidas.Mapa).all()
    maps = [row[0] for row in mapsqry]
    partida_count = [row[1] for row in mapsqry]

    # Graph 2: Victories and Defeats by month
    dataqry = db.session.query(extract('month', TemporaryPartidas.Data), func.count(TemporaryPartidas.Partida)).group_by(extract('month', TemporaryPartidas.Data)).all()

    months_dict = {i: calendar.month_name[i] for i in range(1, 13)}
    months_labels = [months_dict[i] for i in range(1, 13)]

    partida_count_by_month = [0] * 12
    vitoria_count_by_month = [0] * 12
    derrota_count_by_month = [0] * 12

    # Update counts based on the data from the database
    for row in dataqry:
        month_index = row[0] - 1
        partida_count_by_month[month_index] = row[1]

    for month in range(1, 13):
        vitoria_count = TemporaryPartidas.query.filter(extract('month', TemporaryPartidas.Data) == month, TemporaryPartidas.vitória == 1).count()
        derrota_count = TemporaryPartidas.query.filter(extract('month', TemporaryPartidas.Data) == month, TemporaryPartidas.vitória == 0).count()

        vitoria_count_by_month[month - 1] = vitoria_count
        derrota_count_by_month[month - 1] = derrota_count

    authenticated = session.get('logged_in')
    return render_template(
        "graphs.html",
        authenticated=authenticated,
        maps=maps,
        partida_count=partida_count,
        months=months_labels,
        partida_count_by_month=partida_count_by_month,
        vitoria_count_by_month=vitoria_count_by_month,
        derrota_count_by_month=derrota_count_by_month
    )

