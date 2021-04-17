import json
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta 
import os

from models import db, Club, Election, User, ClubMember, Candidate, ElectionBallot

''' Begin boilerplate code '''

def get_db_uri(scheme='sqlite://', user='', password='', host='//electoraDB.db', port='', name=''):
  return scheme+'://'+user+':'+password+'@'+host+':'+port+'/'+name 

def loadConfig(app):
  try:
      app.config.from_object('config.development')
  except:
      print("No config file used. Using environment variables.")
      DBUSER = os.environ.get("DBUSER")
      DBPASSWORD = os.environ.get("DBPASSWORD")
      DBHOST = os.environ.get("DBHOST")
      DBPORT = os.environ.get("DBPORT", default="8080")
      DBNAME = os.environ.get("DBNAME")
      DBURI = os.environ.get("DBURI")
      SQLITEDB = os.environ.get("SQLITEDB", default="False")

      app.config['ENV'] = os.environ.get("ENV", default="")
      app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri() if SQLITEDB in {'True', 'true', 'TRUE'} else DBURI
      app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")


def create_app():
  app = Flask(__name__)
  loadConfig(app)
  CORS(app)
  db.init_app(app)
  return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''

''' Set up JWT here (if using flask JWT)'''
def authenticate(username, password):
  user = db.session.query(User).filter_by(username=username).first()
  if user and user.checkPassword(password):
    return user

def identity(payload):
  return db.session.query(User).get(payload['identity'])

jwt = JWT(app, authenticate, identity)
''' End JWT Setup '''
'''
@app.route('/')
def index():
  return render_template('app.html')
'''
@app.route('/')
def clientApp():
  return app.send_static_file('app.html')

@app.route('/api/clubs', methods=["GET"])
def getClubs():
  clubs = db.session.query(Club).all()
  if not clubs:
    print("No clubs!")
    return json.dumps({"error": "No clubs have been added yet!"})

  listOfClubs = [club.toDict() for club in clubs]
  return json.dumps(listOfClubs)

@app.route('/api/clubs/<clubID>/getPastElections', methods=["GET"])
def getPastElections(clubID):
  pastElections= Election.query.filter_by(clubID=clubID, isOpen=False)
  pastElections=[election.toDict() for election in pastElections]
  return json.dumps(pastElections)
  

@app.route('/api/clubs/<clubID>', methods=["GET"])
def getClubsByID(clubID):
  clubID = int(clubID)
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
    return json.dumps({"error" : "User is already a member of this club or club does not exist!"})

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
  if not regDetails["username"] and not regDetails["password"] and not regDetails["firstName"] and not regDetails["confirmPassword"] and not regDetails["lastName"]:
    return json.dumps({"error" : "Please ensure all the data ie entered for registration"})
  
  if len(regDetails["password"]) <= 6:
    return json.dumps({"error" : "Password too short!"})

  if regDetails["password"] != regDetails["confirmPassword"]:
    return json.dumps({"error" : "Passwords do not match!"})

  try:
    newUser = User(regDetails["username"], regDetails["password"], regDetails["firstName"], regDetails["lastName"])
    db.session.add(newUser)
    db.session.commit()
    return json.dumps({"message" : "Successfully signed up!"})
  except:
    db.session.rollback()
    return json.dumps({"error" : "Error registering user! User may already exist!"})

@app.route('/identify', methods=["GET"])
@jwt_required()
def identify():
  #try:
    return json.dumps({"username" : current_identity.username})
  #except:
    return json.dumps({"error" : "Not logged in or session has expired!"})

#Remove before production
@app.route('/debug/elections', methods=["GET"])
def getElectionsDebug():
  elections = db.session.query(Election).all()
  listOfElections = [election.toDict() for election in elections]
  return json.dumps(listOfElections)

##Remove before production
@app.route('/debug/candidates', methods=["GET"])
def getCandidatesDebug():
  candidates = db.session.query(Candidate).all()
  listOfCandidates = [candidate.toDict() for candidate in candidates]
  return json.dumps(listOfCandidates)

@app.route('/api/elections', methods=["GET"])
@jwt_required()
def getMyElections():
  myElections = current_identity.myElections()
  return json.dumps(myElections)

@app.route('/api/elections/<electionID>', methods=["GET"])
@jwt_required()
def getElectionByID(electionID):
  election = current_identity.viewElection(electionID)
  return json.dumps(election)

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["POST"])
@jwt_required()
def voteForCandidate(electionID, candidateID):
  if current_identity.castVote(electionID, candidateID):
    return json.dumps({"message" : "Vote casted!"})
  else:
    return json.dumps({"error" : "Unable to cast vote!"})

@app.route('/api/elections', methods=["POST"])
@jwt_required()
def createElection():
  electionDetails = request.get_json()

  if not electionDetails or not electionDetails["clubID"] or not electionDetails["position"] or not electionDetails["candidates"]:
    return json.dumps({"error" : "Not enough information provided!"})

  response = current_identity.callElection(electionDetails["clubID"], electionDetails["position"], electionDetails["candidates"])

  if response:
    return json.dumps({"message" : "Election started!"})
  else:
    return json.dumps({"message" : "An active already exists for that position, invalid candidate information provided, or you are not a member of this club!"})

@app.route('/api/elections/<electionID>', methods=["PUT"])
@jwt_required()
def updateElection(electionID):
  updateDetails = request.get_json()

  if not updateDetails or not electionID:
    return json.dumps({"message" : "Not enough information provided!"})
  
  if "isOpen" in updateDetails:
    if updateDetails["isOpen"] == True:
      result = current_identity.openElection(electionID)
      if result:
        return json.dumps({"message" : "Election opened!"})
      else :
        return json.dumps({"message" : "You do not have permission to open this election!"})
    if updateDetails["isOpen"] == False:
      result = current_identity.closeElection(electionID)
      if result:
        return json.dumps({"message" : "Election closed!"})
      else :
        return json.dumps({"message" : "You do not have permission to close this election!"})
  
  if "position" in updateDetails:
    if current_identity.changePosition(electionID, updateDetails["position"]):
      return json.dumps({"message" : "Election position updated!"})
    else:
      return json.dumps({"message" : "You do not have permission to change the position within this election or the election is closed!"})


@app.route('/api/elections/<electionID>', methods=["DELETE"])
@jwt_required()
def deleteElection(electionID):
  if not electionID:
    return json.dumps({"message" : "Not election ID provided!"})
  
  response = current_identity.deleteElection(electionID)

  if response:
    return json.dumps({"message" : "Election deleted!"})
  else:
    return json.dumps({"message" : "Unable to delete election!"})
    

@app.route('/api/myElections', methods=["GET"])
@jwt_required()
def getMyManagingElections():
  myElections = current_identity.myManagingElections()
  return json.dumps(myElections)

@app.route('/api/myElections/<electionID>', methods=["GET"])
@jwt_required()
def displayMyElection(electionID):
  myElections = current_identity.myManagingElections()
  currElection = None
  
  for election in myElections:
    for i in range(0, len(election)):
      if election[i]["electionID"] == int(electionID):
        currElection = election[i]
  
  if not currElection:
    return json.dumps({"message" : "You are not a member of the club that is hosting this election or the election does not exist!"})
  else:
    return json.dumps(currElection)

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["PUT"])
@jwt_required()
def updateCandidateDetails(electionID, candidateID):
  updateDetails = request.get_json()

  newDetails = {}

  if "firstName" in updateDetails and "lastName" in updateDetails:
    newDetails = {
      "firstName": updateDetails["firstName"],
      "lastName" : updateDetails["lastName"]
    }
  
  if current_identity.updateCandidateDetails(electionID, candidateID, newDetails):
    return json.dumps({"message" : "Candidate details updated!"})
  else:
    return json.dumps({"message" : "Unable to update candidate!"})

@app.route('/api/elections/<electionID>/candidates', methods=["GET"])
@jwt_required()
def getCandidatesDetails(electionID):
  candidatesDetails = current_identity.getElectionCandidatesDetails(electionID)
  return json.dumps(candidatesDetails)

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["GET"])
@jwt_required()
def getCandidateDetails(electionID, candidateID):
  candidateDetails = current_identity.viewCandidate(electionID, candidateID)
  return json.dumps(candidateDetails)

@app.route('/api/elections/<electionID>/candidates', methods=["POST"])
@jwt_required()
def addCandidate(electionID):
  candidateDetails = request.get_json()

  newDetails = {}

  if "firstName" in candidateDetails and "lastName" in candidateDetails:
    newDetails = {
      "firstName": candidateDetails["firstName"],
      "lastName" : candidateDetails["lastName"]
    }

  result = current_identity.addCandidate(electionID, newDetails)

  if result:
    return json.dumps({"message" : "Candidate has been added to election!"})
  else:
    return json.dumps({"message" : "Unable to add candidate to election!"})

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["DELETE"])
@jwt_required()
def deleteCandidate(electionID, candidateID):
  result = current_identity.deleteCandidate(electionID, candidateID)

  if result:
    return json.dumps({"message" : "Candidate has been deleted from the election!"})
  else:
    return json.dumps({"message" : "Unable to delete candidate from election!"})