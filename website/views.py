from flask import Blueprint, render_template, session, request, redirect, url_for
from .auth import login_required
import requests
from datetime import date, datetime
import calendar
import pandas as pd
import json
from .models import TemporaryPartidas, db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    authenticated = session.get('logged_in')
    email = session.get('identifier')
    
    # Fetch the data from TemporaryPartidas table for the user's email
    data = TemporaryPartidas.query.filter_by(email=email).order_by(TemporaryPartidas.Data.desc()).all()

    # Create a list of dictionaries from the fetched data
    data_list = []
    for row in data:
        data_dict = {
            'Partida': row.Partida,
            'Mapa': row.Mapa,
            'Kills': row.Kills,
            'Assists': row.Assists,
            'Mortes': row.Mortes,
            'Data': row.Data,
            'Score': f"{row.score_ally}:{row.score_enemy}",
            'Vitória': row.vitória,
            'PontosVar': row.PontosVar,
            'Pontos': row.Pontos,
        }
        data_list.append(data_dict)

    return render_template("home.html", authenticated=authenticated, data=data_list)

@views.route('/retrieve-data', methods=['POST'])
@login_required
def retrieve_data():
    if request.method == 'POST':
        cookies = session.get('cookies')
        headers = session.get('headers')
        email = session.get('identifier')

        TemporaryPartidas.query.filter_by(email=email).delete()
        db.session.commit()

        start_date = date(2023, 1, 1)
        today = date.today()
        current_year = today.year
        current_month = today.month

        url_template = 'https://gamersclub.com.br/players/get_playerLobbyResults/{}-{:02}/{}'

        # Fetch results and store them in TemporaryPartidas table
        for year in range(start_date.year, current_year + 1):
            start_month = 1 if year == start_date.year else 1
            end_month = current_month if year == current_year else 12

            for month in range(start_month, end_month + 1):
                month_end = calendar.monthrange(year, month)[1]
                url = url_template.format(year, month, 1)
                r = requests.get(url, cookies=cookies, headers=headers)
                json_data = r.json()
                total_pages = int(json_data['pagination']['pages_total'])
                print(f"Processing data for {year}-{month:02}, total pages: {total_pages}")

                for page in range(1, total_pages + 1):
                    url = url_template.format(year, month, page)
                    r = requests.get(url, cookies=cookies, headers=headers)
                    json_data = r.json()

                    for item in json_data['lista']:
                        room_a_vitoria = item['room_a_vitoria']
                        room_a_player = item['room_a_player']
                        score_ally = item['score_a'] if room_a_player else item['score_b']
                        score_enemy = item['score_b'] if room_a_player else item['score_a']
                        if (room_a_player and room_a_vitoria) or (not room_a_player and not room_a_vitoria):
                            vitória = 1
                        else:
                            vitória = 0
                        
                        
                        partida = TemporaryPartidas(
                            Partida=item['idlobby_game'],
                            Mapa=item['map_name'],
                            Kills=item['nb_kill'],
                            Assists=item['assist'],
                            Mortes=item['death'],
                            Data=datetime.strptime(item['created_at'], "%d/%m/%Y %H:%M"),
                            PontosVar=item['diference'],
                            Pontos=item['rating_final'],
                            vitória=vitória,
                            score_ally=score_ally,
                            score_enemy=score_enemy,
                            email=email
                        )
                        db.session.add(partida)

        db.session.commit()

    return redirect(url_for('views.home'))