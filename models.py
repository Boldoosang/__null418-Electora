from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()
import datetime

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(256), nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    clubMembers = db.relationship('ClubMember', backref='membership')

    def __init__(self, username, password, firstName, lastName):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.setPassword(password)

    def toDict(self):
        return {
            "userID" : self.userID,
            "username" : self.username,
            "password" : self.password,
            "firstName" : self.firstName,
            "lastName" : self.lastName
        }

    def setPassword(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def joinClub(self, clubName):
        result = db.session.query(Club).filter_by(clubName=clubName).first()

        if not result:
            print("User attempted to join a club that did not exist!")
            return False
        
        try:
            foundClubID = result.clubID 
            newClubMember = ClubMember(clubID = foundClubID, userID = self.userID)

            db.session.add(newClubMember)
            db.session.commit()
            print("User added to club!")
            return True
        except:
            db.session.rollback()
            print("Unable to add user to club!")

        return False
    
    def castVote(self, clubName, candidateID):
        electionClub = db.session.query(Club).filter_by(clubName=clubName).first()
        clubMembership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, userID=self.userID).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.castVote(candidateID)



class Club(db.Model):
    clubID = db.Column(db.Integer, primary_key=True)
    clubName = db.Column(db.String(80), nullable=False)
    elections = db.relationship('Election', backref='hostingClub')
    members = db.relationship('ClubMember', backref='club')

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
    electionWinner = db.Column(db.String(150))
    candidates = db.relationship('Candidate', backref='candidate')

    def toDict(self):
        return {
            "electionID" : self.electionID,
            "clubID" : self.clubID,
            "position" : self.position,
            "electionEndDate" : self.electionEndDate,
            "electionWinner" : self.electionWinner
        }

    def tallyVotes(self):
        electionCandidates = db.session.query(Candidate).filter_by(electionID=self.electionID).all()

        if not electionCandidates:
            printf("No candidates for this election!")
            return False

        for candidate in electionCandidates:
            votes = db.session.query(ElectionBallot).filter_by(candidateID=candidate.candidateID).all()
            candidate.numVotes = len(votes)

            try:
                db.session.add(candidate)
                db.session.commit()
            except:
                db.session.rollback()
                print("Unable to tally votes!")
                return False
        
        return True

    def declareWinner(self):
        self.tallyVotes()

        electionCandidates = db.session.query(Candidate).filter_by(electionID=self.electionID).all()

        if not electionCandidates:
            print("No candidates for this election!")
            return False

        voteData = [candidate.numVotes for candidate in electionCandidates]
        print(voteData)

        if True:
            #ElectionCandidates (contains duplicates):
            print("There has been a tie!")
            try:
                self.electionWinner = "Tie"
                db.session.add(self)
                db.session.commit()
            except:
                db.session.rollback()
        else:
            pass

        

class Candidate(db.Model):
    candidateID = db.Column(db.Integer, primary_key=True)
    electionID = db.Column(db.Integer, db.ForeignKey('election.electionID'), nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    numVotes = db.Column(db.Integer, nullable=False, default=0)
    votes = db.relationship('ElectionBallot', backref='ballot')

    def toDict(self):
        return {
            "candidateID" : self.candidateID,
            "electionID" : self.electionID,
            "firstName" : self.firstName,
            "lastName" : self.lastName,
        }


class ClubMember(db.Model):
    memberID = db.Column(db.Integer, primary_key=True)
    clubID = db.Column(db.Integer, db.ForeignKey("club.clubID"), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey("user.userID"), nullable=False)
    votesMade = db.relationship('ElectionBallot', backref='voter')
    
    def toDict(self):
        return {
            'memberID': self.memberID,
            #complete
        }
    
    def castVote(self, candidateID):
        #Do check to ensure that the election end date has not passed.
        candidate = db.session.query(Candidate).filter_by(candidateID=candidateID).first()

        if not candidate:
            print("User attempted to join a club that did not exist!")
            return False
        
        try:
            ballot = ElectionBallot(memberID=self.memberID, candidateID=candidateID)
            db.session.add(ballot)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            print("User may have already voted!")
            return False


    def callElection(self, clubName):
        pass


class ElectionBallot(db.Model):
    #ballotID = db.Column(db.Integer, primary_key=True)
    memberID = db.Column(db.Integer, db.ForeignKey("club_member.memberID"), primary_key=True)
    candidateID = db.Column(db.Integer, db.ForeignKey("candidate.candidateID"), primary_key=True)
