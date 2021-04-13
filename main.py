import json
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta 

from models import db, Club, Election, User, ClubMember, Candidate, ElectionBallot #add application models

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
  #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\jbald\Desktop\\__null418-ElectoraV2\\test.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  app.config['SECRET_KEY'] = "MYSECRET"
  app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7) # uncomment if using flsk jwt
  CORS(app)
#   login_manager.init_app(app) # uncomment if using flask login
  db.init_app(app)
  return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''

''' Set up JWT here (if using flask JWT)'''
def authenticate(username, password):
  user = User.query.filter_by(username=username).first()
  print(user)
  if user and user.checkPassword(password):
    return user

def identity(payload):
  return User.query.get(payload['identity'])

jwt = JWT(app, authenticate, identity)
''' End JWT Setup '''
'''
@app.route('/')
def index():
  return render_template('app.html')
'''
@app.route('/')
def client_app():
  return app.send_static_file('app.html')

@app.route('/api/clubs', methods=["GET"])
def getClubs():
  clubs = db.session.query(Club).all()
  listOfClubs = [club.toDict() for club in clubs]
  return json.dumps(listOfClubs)

@app.route('/api/clubs/<clubID>', methods=["GET"])
def getClubsByID(clubID):
  foundClub = db.session.query(Club).filter_by(clubID=clubID).first()
  if not foundClub:
    return None
  return json.dumps(foundClub.toDict())

@app.route('/api/clubs/<clubID>', methods=["POST"])
@jwt_required()
def joinClub(clubID):
  if not clubID:
    return json.dumps({"message" : "No supplied club ID!"})

  response = current_identity.joinClub(clubID)

  if response:
    return json.dumps({"message" : "Club joined!"})
  else:
    return json.dumps({"message" : "User is already a member of this club!"})

@app.route('/api/myClubs', methods=["GET"])
@jwt_required()
def getMyClubs():
  myClubs = current_identity.myClubs()
  return json.dumps(myClubs)

@app.route('/api/myClubs/<clubID>', methods=["DELETE"])
@jwt_required()
def leaveClub(clubID):
  if not clubID:
    return json.dumps({"message" : "No supplied club ID!"})

  response = current_identity.leaveClub(clubID)

  if response:
    return json.dumps({"message" : "Club left!"})
  else:
    return json.dumps({"message" : "User is not a member of this club!"})

@app.route('/register', methods=["POST"])
def register():
  regDetails = request.get_json()
  if not regDetails["username"] and not regDetails["password"] and not regDetails["firstName"] and not regDetails["lastName"]:
    return json.dumps({"message" : "Please ensure all the data ie entered for registration"})
  
  if len(regDetails["password"]) <= 6:
    return json.dumps({"message" : "Password too short!"})

  try:
    newUser = User(regDetails["username"], regDetails["password"], regDetails["firstName"], regDetails["lastName"])
    db.session.add(newUser)
    db.session.commit()
    return json.dumps({"message" : "Successfully signed up!"})
  except:
    db.session.rollback()
    return json.dumps({"message" : "Error registering user! User may already exist!"})

@app.route('/identify', methods=["GET"])
@jwt_required()
def identify():
  return json.dumps(current_identity.username)

#Remove before production
@app.route('/debug/elections', methods=["GET"])
def getElections():
  elections = db.session.query(Election).all()
  listOfElections = [election.toDict() for election in elections]
  return json.dumps(listOfElections)

@app.route('/api/elections/<electionID>', methods=["GET"])
def getElectionsByID(electionID):
  elections = db.session.query(Election).filter_by(electionID=electionID).all()
  listOfElections = [election.toDict() for election in elections]
  return json.dumps(listOfElections)

@app.route('/api/elections', methods=["POST"])
@jwt_required()
def createElection():
  electionDetails = request.get_json()

  if not electionDetails or not electionDetails["clubID"] or not electionDetails["position"] or not electionDetails["candidates"]:
    return json.dumps({"message" : "Not enough information provided!"})

  
  response = current_identity.callElection(electionDetails["clubID"], electionDetails["position"], electionDetails["candidates"])

  if response:
    return json.dumps({"message" : "Election started!"})
  else:
    return json.dumps({"message" : "An active already exists for that position, invalid candidate information provided, or you are not a member of this club!"})

@app.route('/api/elections/<electionID>', methods=["PUT"])
@jwt_required()
def updateElection(electionID):
  updateDetails = request.get_json()

  #Add ability to update candidates
  if not updateDetails or not electionID:
    return json.dumps({"message" : "Not enough information provided!"})
  
  if "isOpen" in updateDetails:
    if updateDetails["isOpen"] == True:
      current_identity.openElection(electionID)
      return json.dumps({"message" : "Election reopened!"})
    if updateDetails["isOpen"] == False:
      current_identity.closeElection(electionID)
      return json.dumps({"message" : "Election closed!"})

@app.route('/api/elections/<electionID>', methods=["DELETE"])
@jwt_required()
def deleteElection(electionID):
  #Add ability to update candidates
  if not electionID:
    return json.dumps({"message" : "Not election ID provided!"})
  
  response = current_identity.deleteElection(electionID)

  if response:
    return json.dumps({"message" : "Election deleted!"})
  else:
    return json.dumps({"message" : "Unable to delete election!"})
    

@app.route('/api/elections', methods=["GET"])
@jwt_required()
def getMyElections():
  myElections = current_identity.myElections()
  return json.dumps(myElections)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
