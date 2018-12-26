from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from flask_restful import marshal, fields
from flask_cors import CORS, cross_origin
import jwt
from random import randint
import os


app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:please@localhost:5432/E-Voting'
jwtSecretKey = 'halohalosyifa'

db = SQLAlchemy(app)

class Voter(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nama = db.Column(db.String(50))
    nomor_ktp = db.Column(db.Integer)
    password = db.Column(db.String())

class Caleg(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nama = db.Column(db.String(50))

class Capres(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nama = db.Column(db.String(50))

class VotedCapres(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))
    presiden_id = db.Column(db.Integer, db.ForeignKey('capres.id'))

class VotedCaleg(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'))
    legislatif_id = db.Column(db.Integer, db.ForeignKey('caleg.id'))

#login 
@app.route('/login', methods = ['POST'])
def login():
    if request.method == 'POST':
        requestData = request.get_json()
        reqKtp = requestData.get('nomor_ktp')
        reqPassword = requestData.get('password')

        userDB = Voter.query.filter_by(nomor_ktp = reqKtp, password = reqPassword).first()
        if userDB is not None:
            payload = {
                "nomor_ktp": userDB.nomor_ktp
            }

            encoded = jwt.encode(payload, jwtSecretKey, algorithm='HS256')
            return encoded, 200
        else:
            return 'Anda tidak terdaftar sebagai data pemilih', 404
    else:
        return 'Method Not Allowed', 405

#votepresiden
@app.route('/vote-presiden', methods = ['POST'])
def VotePresiden():
    decode = jwt.decode(request.headers["Authorization"], 'halohalosyifa', algorithms=["HS256"])

    nomor_ktp = decode['nomor_ktp']
    requestData = request.get_json()

    if request.method == 'POST':
        userDB = Voter.query.filter_by(nomor_ktp = nomor_ktp).first()
        voting = VotedCapres(
            voter_id = userDB.id,
            presiden_id = requestData.get("id")
        )

        db.session.add(voting)
        db.session.commit()

        return 'Terimakasih telah berpartisipasi dalam pemilihan ini', 200
    else:
        return 'Method Not Allowed', 405

#votelegislatif
@app.route('/vote-legislatif', methods = ['POST'])
def VoteLegislatif():
    decode = jwt.decode(request.headers["Authorization"], 'halohalosyifa', algorithms=["HS256"])

    nomor_ktp = decode['nomor_ktp']
    requestData = request.get_json()

    if request.method == 'POST':
        userDB = Voter.query.filter_by(nomor_ktp = nomor_ktp).first()
        voting = voted_capres(
            voter_id = userDB.id,
            legislatif_id = requestData.get("id")
        )

        db.session.add(voting)
        db.session.commit()

        return 'Terimakasih telah berpartisipasi dalam pemilihan ini', 200
    else:
        return 'Method Not Allowed', 405

#hitungcaleg
@app.route('/hitung-caleg', methods=['POST'])
def hitungCaleg():
    request_data = request.get_json()
    calon_legislatif = request_data.get('caleg')
    jumlahSuara = VotedCaleg.query.filter_by(legislatif_id=calon_legislatif).count()
    return str(jumlahSuara)

#hitungcapres
@app.route('/hitung-capres', methods=['POST'])
def hitungCapres():
    request_data = request.get_json()
    calon_presiden = request_data.get('capres')
    jumlahSuara = VotedCapres.query.filter_by(presiden_id= calon_presiden).count()
    return str(jumlahSuara)

if __name__ == ('__main__'):
    app.run(debug=True, port=os.getenv('PORT'), host=os.getenv('HOST'))