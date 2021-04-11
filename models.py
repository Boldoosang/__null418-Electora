from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()
import datetime

class User(db.Model):
    username = db.Column(db.String(25), primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)

    def __init__(self, username, password, firstName, lastName):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        generate_password_hash(password, method='sha256')

    def toDict(self):
        return {
            "username" : self.username,
            "password" : self.password,
            "firstName" : self.firstName,
            "lastName" : self.lastName
        }

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Club(db.Model):
    clubID = db.Column(db.Integer, primary_key=True)
    clubName = db.Column(db.String(80), nullable=False)
    elections = db.relationship('Election', backref='Club')

    def toDict(self):
        return {
            "clubID" : self.clubID,
            "clubName" : self.clubName
        }

class Election(db.Model):
    electionID = db.Column(db.Integer, primary_key=True)
    clubID = db.Column(db.Integer, db.ForeignKey('club.clubID'), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    #electionEndDate = db.Column(db.DateTime, nullable=False, default="")
    #electionWinner = db.String(db.String(150), nullable=False)

    def toDict(self):
        return {
            "electionID" : self.electionID,
            "clubID" : self.clubID,
            "position" : self.position,
            "electionEndDate" : self.electionEndDate,
            "electionWinner" : self.electionWinner
        }

    def tallyVotes(self):
        pass

    def declareWinner(self):
        pass


class Candidate(db.Model):
    candidateID = db.Column(db.Integer, primary_key=True)
    electionID = db.Column(db.Integer, nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)

    def toDict(self):
        return {
            "candidateID" : self.candidateID,
            "electionID" : self.electionID,
            "firstName" : self.firstName,
            "lastName" : self.lastName
        }

class ElectionBallot(db.Model):
    ballotID = db.Column(db.Integer, primary_key=True)
    memberID = db.Column(db.Integer, nullable=False)
    candidateID = db.Column(db.Integer, nullable=False)

class ClubMember(db.Model):
    memberID = db.Column(db.Integer, primary_key=True)

    def toDict(self):
        return{
            'id': self.id,
            'studentId': self.studentId,
            'stream': self.stream,
            'created': self.created.strftime("%m/%d/%Y, %H:%M:%S")
        }
