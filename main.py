import json
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from datetime import timedelta 
import os

from models import db, Club, Election, User, ClubMember, Candidate, ElectionBallot

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

def authenticate(username, password):
  user = db.session.query(User).filter_by(username=username).first()
  if user and user.checkPassword(password):
    return user

def identity(payload):
  return db.session.query(User).get(payload['identity'])

jwt = JWT(app, authenticate, identity)

@app.route('/')
def clientApp():
  return app.send_static_file('app.html')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('images/favicon.png')

@app.route('/logo.png')
def logo():
    return app.send_static_file('images/logo.png')

@app.route('/api/clubs', methods=["GET"])
def getClubs():
  clubs = db.session.query(Club).all()
  if not clubs:
    return json.dumps({"error": "No clubs have been added yet!"})
  else:
    listOfClubs = [club.toDict() for club in clubs]
    return json.dumps(listOfClubs)

@app.route('/api/clubs/<clubID>/getPastElections', methods=["GET"])
def getPastElections(clubID):
  pastElections = Election.query.filter_by(clubID=clubID, isOpen=False).all()
  if not pastElections:
    return json.dumps({"error" : "Unable to get past elections for this club!"})
  else:
    pastElections = [election.toDict() for election in pastElections]
    return json.dumps(pastElections)
  

@app.route('/api/clubs/<clubID>', methods=["GET"])
def getClubsByID(clubID):
  clubID = int(clubID)
  foundClub = db.session.query(Club).filter_by(clubID=clubID).first()
  if not foundClub:
    return json.dumps({"error" : "Club not found!"})
  else:
    return json.dumps(foundClub.toDict())


@app.route('/api/clubs/<clubID>', methods=["POST"])
@jwt_required()
def joinClub(clubID):
  if not clubID:
    return json.dumps({"error" : "No supplied club ID!"})

  response = current_identity.joinClub(clubID)

  if response:
    return json.dumps({"message" : "Club joined!"})
  else:
    return json.dumps({"error" : "User is already a member of this club or club does not exist!"})

@app.route('/api/myClubs', methods=["GET"])
@jwt_required()
def getMyClubs():
  myClubs = current_identity.myClubs()
  if myClubs:
    return json.dumps(myClubs)
  else:
    return json.dumps({"error" : "Not a member of any club!"})


@app.route('/api/myClubs/<clubID>', methods=["DELETE"])
@jwt_required()
def leaveClub(clubID):
  if not clubID:
    return json.dumps({"error" : "No supplied club ID!"})

  response = current_identity.leaveClub(clubID)

  if response:
    return json.dumps({"message" : "Club left!"})
  else:
    return json.dumps({"error" : "User is not a member of this club!"})

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
  try:
    return json.dumps({"username" : current_identity.username, "firstName" : current_identity.firstName, "lastName" : current_identity.lastName})
  except:
    return json.dumps({"error" : "Not logged in or session has expired!"})

#Remove before production
#@app.route('/debug/elections', methods=["GET"])
#def getElectionsDebug():
#  elections = db.session.query(Election).all()
#  listOfElections = [election.toDict() for election in elections]
#  return json.dumps(listOfElections)

##Remove before production
#@app.route('/debug/candidates', methods=["GET"])
#def getCandidatesDebug():
#  candidates = db.session.query(Candidate).all()
#  listOfCandidates = [candidate.toDict() for candidate in candidates]
#  return json.dumps(listOfCandidates)

@app.route('/api/elections', methods=["GET"])
@jwt_required()
def getMyElections():
  memberships = db.session.query(ClubMember).filter_by(id=current_identity.id).all()
        
  if not memberships:
    return json.dumps({"error" : "You have no elections or are not a member of any club!"})

  allMyElections = []

  for membership in memberships:
    listOfMyClubElections = membership.myElections()

    if listOfMyClubElections:
      for clubElection in listOfMyClubElections:
        allMyElections.append(clubElection)


  if allMyElections:
    return json.dumps(allMyElections)
  else:
    return json.dumps({"error" : "Unable find your elections!"})

@app.route('/api/elections/<electionID>', methods=["GET"])
@jwt_required()
def getElectionByID(electionID):
  memberships = db.session.query(ClubMember).filter_by(id=current_identity.id).all()

  if not memberships:
      return json.dumps({"error" : "You are not a member of this club!"})

  election = db.session.query(Election).filter_by(electionID=electionID).first()
  
  if not election:
      return json.dumps({"error" : "No such election found!"})

  for membership in memberships:
      if election.clubID == membership.clubID:
          electionDetails = election.toDict()

  if electionDetails:
    return json.dumps(electionDetails)
  else:
    return json.dumps({"error" : "Unable find election by ID!"})

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["POST"])
@jwt_required()
def voteForCandidate(electionID, candidateID):
  elec = db.session.query(Election).filter_by(electionID=electionID).first()

  if not elec:
      return json.dumps({"error" : "Election cannot be found!"})

  clubMembership = db.session.query(ClubMember).filter_by(clubID=elec.clubID, id=current_identity.id).first()
        
  if not clubMembership:
      return json.dumps({"error" : "User is not a member of this club!"})

  elec = db.session.query(Election).filter_by(electionID=electionID).first()

  if not elec:
      return json.dumps({"error" : "Election cannot be found!"})

  if clubMembership.castVote(candidateID):
    return json.dumps({"message" : "Vote casted!"})
  else:
    return json.dumps({"error" : "Unable to cast vote!"})


def validateCandidate(candidate):
  if "firstName" in candidate and "lastName" in candidate:
    if len(candidate["firstName"]) > 0 and len(candidate["lastName"]) > 0:
      return True
  return False

@app.route('/api/elections', methods=["POST"])
@jwt_required()
def createElection():
  electionDetails = request.get_json()

  if not electionDetails or "clubID" not in electionDetails or "position" not in electionDetails or "candidates" not in electionDetails:
    return json.dumps({"error" : "Not enough information provided!"})

  for candidate in electionDetails["candidates"]:
    if not validateCandidate(candidate):
      return json.dumps({"error" : "Invalid candidate information provided!"})

  clubMembership = db.session.query(ClubMember).filter_by(clubID=electionDetails["clubID"], id=current_identity.id).first()
        
  if not clubMembership:
    return json.dumps({"error" : "You are not a member of this club!"})

  response = clubMembership.callElection(electionDetails["clubID"], electionDetails["position"], electionDetails["candidates"])

  if response:
    return json.dumps({"message" : "Election started!"})
  else:
    return json.dumps({"error" : "An active already exists for that position, invalid candidate information provided, or you are not a member of this club!"})

@app.route('/api/elections/<electionID>', methods=["PUT"])
@jwt_required()
def updateElection(electionID):
  updateDetails = request.get_json()

  if not updateDetails or not electionID:
    return json.dumps({"error" : "Not enough information provided!"})
  
  if "isOpen" in updateDetails:
    if updateDetails["isOpen"] == True:
      electionClub = db.session.query(Election).filter_by(electionID=electionID).first()

      if not electionClub:
          return json.dumps({"error" : "No election found!"})

      membership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=current_identity.id).first()

      if not membership:
        return json.dumps({"error" : "User is not a member of this club!"})

      electionClub = db.session.query(Election).filter_by(electionID=electionID).first()

      if not electionClub:
          return json.dumps({"error" : "No election found!"})

      result = membership.openElection(electionID)

      if result:
        return json.dumps({"message" : "Election opened!"})
      else :
        return json.dumps({"error" : "You do not have permission to open this election!"})

    if updateDetails["isOpen"] == False:
      electionClub = db.session.query(Election).filter_by(electionID=electionID).first()

      if not electionClub:
        return json.dumps({"error" : "No election found!"})

      membership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=current_identity.id).first()
        
      if not membership:
        return json.dumps({"error" : "User is not a member of this club!"})

      result = membership.closeElection(electionID)

      if result:
        return json.dumps({"message" : "Election closed!"})
      else :
        return json.dumps({"error" : "You do not have permission to close this election!"})
  
  if "position" in updateDetails:
    membership = db.session.query(ClubMember).filter_by(id=current_identity.id).first()
    if not membership:
        return json.dumps({"error" : "You do not have permission to change the position within this election or the election is closed!"})

    result = membership.changePosition(electionID, updateDetails["position"])

    if result:
      return json.dumps({"message" : "Election position updated!"})
    else:
      return json.dumps({"error" : "You do not have permission to change the position within this election or the election is closed!"})


@app.route('/api/elections/<electionID>', methods=["DELETE"])
@jwt_required()
def deleteElection(electionID):
  if not electionID:
    return json.dumps({"error" : "Not election ID provided!"})
  
  electionClub = db.session.query(Election).filter_by(electionID=electionID).first()

  if not electionClub:
    return json.dumps({"error" : "No election found!"})

  membership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=current_identity.id).first()
  
  if not membership:
    return json.dumps({"error" : "User is not a member of this club!"})

  
  electionClub = db.session.query(Election).filter_by(electionID=electionID).first()

  if not electionClub:
    return json.dumps({"error" : "No election found!"})
        
  response = membership.deleteElection(electionID)

  if response:
    return json.dumps({"message" : "Election deleted!"})
  else:
    return json.dumps({"error" : "Unable to delete election!"})
    

@app.route('/api/myManagingElections', methods=["GET"])
@jwt_required()
def getMyManagingElections():
  memberships = db.session.query(ClubMember).filter_by(id=current_identity.id).all()

  allMyManagingElections = []

  for membership in memberships:
    listOfMyClubElections = membership.myManagingElections()
    if listOfMyClubElections:
      for clubElection in listOfMyClubElections:
        allMyManagingElections.append(clubElection)

  if allMyManagingElections:
    return json.dumps(allMyManagingElections)
  else:
    return json.dumps({"error" : "No managing elections for your account."})

@app.route('/api/myManagingElections/<electionID>', methods=["GET"])
@jwt_required()
def displayMyManagingElection(electionID):
  memberships = db.session.query(ClubMember).filter_by(id=current_identity.id).all()
        
  allMyManagingElections = []

  for membership in memberships:
    listOfMyClubElections = membership.myManagingElections()
    if listOfMyClubElections:
      for clubElection in listOfMyClubElections:
        allMyManagingElections.append(clubElection)


  myElections = membership.myManagingElections()

  currElection = None

  if myElections:
    for election in myElections:
      for i in range(0, len(election)):
        if election[i]["electionID"] == int(electionID):
          currElection = election[i]
  
  if not currElection:
    return json.dumps({"error" : "You are not a member of the club that is hosting this election or the election does not exist!"})
  else:
    return json.dumps(currElection)

@app.route("/debug", methods=["GET"])
@jwt_required()
def test():
  current_identity.performClubAction("action")

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["PUT"])
@jwt_required()
def updateCandidate(electionID, candidateID):
  updateDetails = request.get_json()

  if "firstName" not in updateDetails and "lastName" not in updateDetails:
    return json.dumps({"error" : "Incorrect candidate details provided!"})

  if not validateCandidate(updateDetails):
    return json.dumps({"error" : "Incorrect candidate details provided!"})

  membership = db.session.query(ClubMember).filter_by(id=current_identity.id).first()

  if not membership:
      return json.dumps({"error" : "User does not have permission to update this candidate!"})

  if membership.updateCandidate(electionID, candidateID, updateDetails):
    return json.dumps({"message" : "Candidate details updated!"})
  else:
    return json.dumps({"error" : "Unable to update candidate!"})

@app.route('/api/elections/<electionID>/candidates', methods=["GET"])
@jwt_required()
def getCandidatesDetails(electionID):
  election = db.session.query(Election).filter_by(electionID=electionID).first()

  if not election:
    return json.dumps({"error" : "Election does not exist!"})

  clubMembership = db.session.query(ClubMember).filter_by(clubID=election.clubID, id=current_identity.id).first()

  if not clubMembership:
      return json.dumps({"error" : "User does not have permission to view this candidate."})

  candidatesDetails = clubMembership.getElectionCandidatesDetails(electionID)

  if candidatesDetails:
    return json.dumps(candidatesDetails)
  else:
    return json.dumps({"error" : "No candidates found for this election."})

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["GET"])
@jwt_required()
def getCandidateDetails(electionID, candidateID):
  cand = db.session.query(Candidate).filter_by(candidateID=candidateID, electionID=electionID).first()

  if not cand:
      return json.dumps({"error" : "No candidate found for that ID."})

  election = db.session.query(Election).filter_by(electionID=electionID).first()

  if not election:
      return json.dumps({"error" : "No election found for that ID."})

  clubMembership = db.session.query(ClubMember).filter_by(clubID=election.clubID, id=current_identity.id).first()

  if not election:
      return json.dumps({"error" : "No permissions to view this election."})
        
  candidateDetails = cand.toDict()

  if candidateDetails:
    return json.dumps(candidateDetails)
  else:
    return json.dumps({"error" : "No candidate found for that ID."})

@app.route('/api/elections/<electionID>/candidates', methods=["POST"])
@jwt_required()
def addCandidate(electionID):
  candidateDetails = request.get_json()

  if "firstName" in candidateDetails and "lastName" in candidateDetails:
    if not validateCandidate(candidateDetails):
      return json.dumps({"error" : "Not enough information provided!"})
  else:
    return json.dumps({"error" : "Not enough information provided!"})
  
  membership = db.session.query(ClubMember).filter_by(id=current_identity.id).first()
        
  if not membership:
      return json.dumps({"error" : "Unable to add candidate to election! You may not be a manager!"})

  result = membership.addCandidate(electionID, candidateDetails)

  if result:
    return json.dumps({"message" : "Candidate has been added to election!"})
  else:
    return json.dumps({"error" : "Unable to add candidate to election! Candidate may already exist!"})

@app.route('/api/elections/<electionID>/candidates/<candidateID>', methods=["DELETE"])
@jwt_required()
def deleteCandidate(electionID, candidateID):
  membership = db.session.query(ClubMember).filter_by(id=current_identity.id).first()
        
  if not membership:
      return json.dumps({"error" : "User does not have permission to update this candidate!"})

  result = membership.deleteCandidate(electionID, candidateID)

  if result:
    return json.dumps({"message" : "Candidate has been deleted from the election!"})
  else:
    return json.dumps({"error" : "Unable to delete candidate from election!"})

