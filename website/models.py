from . import db

class TemporaryPartidas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    Partida = db.Column(db.Integer)
    Mapa = db.Column(db.String(15))
    Kills = db.Column(db.Integer)
    Assists = db.Column(db.Integer)
    Mortes = db.Column(db.Integer)
    Data = db.Column(db.DateTime(timezone=True))
    PontosVar = db.Column(db.Integer)
    Pontos = db.Column(db.Integer)
    score_a = db.Column(db.Integer)
    score_b = db.Column(db.Integer)
    vitória = db.Column(db.String(10))
    score_ally = db.Column(db.Integer)
    score_enemy = db.Column(db.Integer)