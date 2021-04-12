import json
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta 

from models import db, Club, Election #add application models

''' Begin boilerplate code '''

''' Begin Flask Login Functions '''
# login_manager = LoginManager()
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)

''' End Flask Login Functions '''

def create_app():
  app = Flask(__name__, static_url_path='')
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config['SECRET_KEY'] = "MYSECRET"
#   app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7) # uncomment if using flsk jwt
  CORS(app)
#   login_manager.init_app(app) # uncomment if using flask login
  db.init_app(app)
  return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''

''' Set up JWT here (if using flask JWT)'''
# def authenticate(uname, password):
#   pass

# #Payload is a dictionary which is passed to the function by Flask JWT
# def identity(payload):
#   pass

# jwt = JWT(app, authenticate, identity)
''' End JWT Setup '''

@app.route('/')
def index():
  return render_template('app.html')

@app.route('/app')
def client_app():
  return app.send_static_file('app.html')


@app.route('/api/clubs', methods=["GET"])
def getClubs():
  clubs = db.session.query(Club).all()
  listOfClubs = [club.toDict() for club in clubs]
  return json.dumps(listOfClubs)

@app.route('/api/clubs/<clubID>', methods=["GET"])
def getClubsByID(clubID):
  clubs = db.session.query(Club).filter_by(clubID=clubID).all()
  listOfClubs = [club.toDict() for club in clubs]
  return json.dumps(listOfClubs)

@app.route('/api/elections', methods=["GET"])
def getElections():
  elections = db.session.query(Election).all()
  listOfElections = [election.toDict() for election in elections]
  return json.dumps(listOfElections)

@app.route('/api/elections/<electionID>', methods=["GET"])
def getElectionsByID(electionID):
  elections = db.session.query(Election).filter_by(electionID=electionID).all()
  listOfElections = [election.toDict() for election in elections]
  return json.dumps(listOfElections)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
