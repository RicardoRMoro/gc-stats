from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from . import login_required
import json
from .models import TemporaryPartidas, db


auth = Blueprint('auth', __name__)


#data brings identifier and password
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        result = GCLogin(identifier, password)
        if result[0] == 'success':
            flash('Logged in successfully!', category='success')
            session['logged_in'] = True
            session['cookies'] = result[1]
            session['headers'] = result[2]
            session['identifier'] = result[3]
            return redirect(url_for('views.home'))
        else:
            flash('Failed to login, try again.', category='error')
    authenticated = session.get('logged_in')
    return render_template("login.html", authenticated=authenticated)

@auth.route('/logout')
@login_required
def logout():
    email = session.get('identifier')
    if email:
        TemporaryPartidas.query.filter_by(email=email).delete()
        db.session.commit()

    session.clear()
    return redirect(url_for('auth.login'))


def GCLogin(identifier, password):
    # Login pela GCID, com cookies da gamersclub
    sessionGC = requests.Session()

    # Pegando formulario de login unico
    url = 'https://gcid.gamersclub.gg/'
    response = requests.get(url, allow_redirects=True)
    final_url = response.url
    parsed_url = urlparse(final_url)
    query_params = parse_qs(parsed_url.query)
    flow_param = query_params.get('flow', [''])[0]

    # Enviando GET para obter o CSRF_Token
    login_url = f'https://gcid.gamersclub.gg/kratos/self-service/login?flow={flow_param}'
    login_response = sessionGC.get(login_url)
    soup = BeautifulSoup(login_response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')


    login_data = {
        'identifier': identifier,
        'password': password,
        'csrf_token': csrf_token,
        'method': 'password'
    }

    login_response = sessionGC.post(login_url, data=login_data)

    # Send GET request to retrieve the gclubsess
    testeURL = 'https://gamersclub.com.br/my-matches'
    teste = sessionGC.get(testeURL)
    gclubsess_cookie = sessionGC.cookies.get('gclubsess')

    cookies = {
        'gclubsess': gclubsess_cookie
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }

    # Check the JSON response from the URL
    lobby_results_url = 'https://gamersclub.com.br/players/get_playerLobbyResults/latest/1'
    lobby_results_response = requests.get(lobby_results_url, cookies=cookies, headers=headers)
    json_data = json.loads(lobby_results_response.text)

    if json_data.get('success'):
        return 'success', cookies, headers, identifier
    else:
        return 'failed'
