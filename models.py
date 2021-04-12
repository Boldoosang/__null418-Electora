from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()
import datetime
import uuid

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
            "id" : self.id,
            "username" : self.username,
            "password" : self.password,
            "firstName" : self.firstName,
            "lastName" : self.lastName
        }

    def setPassword(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def joinClub(self, clubID):
        result = db.session.query(Club).filter_by(clubID=clubID).first()

        if not result:
            print("User attempted to join a club that did not exist!")
            return False

        #Determine if user is already in club
        joined = db.session.query(ClubMember).filter_by(clubID=result.clubID, id=self.id).first()

        if joined:
            print("User is already a member of this club!")
            return False
        
        try:
            newClubMember = ClubMember(clubID = result.clubID , id = self.id)
            db.session.add(newClubMember)
            db.session.commit()
            print("User added to club!")
            return True
        except:
            db.session.rollback()
            print("Unable to add user to club!")

        return False
    
    def myClubs(self):
        myClubs = db.session.query(ClubMember).filter_by(id=self.id).all()
        listOfMyClubs = [club.toDict() for club in myClubs]
        return listOfMyClubs
    
    def leaveClub(self, clubID):
        result = db.session.query(Club).filter_by(clubID=clubID).first()

        if not result:
            print("User attempted to leave a club that did not exist!")
            return False

        #Determine if user is already in club
        membership = db.session.query(ClubMember).filter_by(clubID=result.clubID, id=self.id).first()

        if not membership:
            print("User is not a member of this club!")
            return False
        
        try:
            db.session.delete(membership)
            db.session.commit()
            print("User has been removed from club!")
            return True
        except:
            db.session.rollback()
            print("Unable to remove user from club!")

        return False

    def castVote(self, clubID, candidateID):
        clubMembership = db.session.query(ClubMember).filter_by(clubID=clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.castVote(candidateID)
    
    def closeElection(self, electionID):
        electionClub = db.session.query(Election).filter_by(electionID=electionID).first()
        clubMembership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.closeElection(electionID=electionID)

    def openElection(self, electionID):
        electionClub = db.session.query(Election).filter_by(electionID=electionID).first()
        clubMembership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.openElection(electionID=electionID)
    
    def callElection(self, clubID, position, candidates):
        clubMembership = db.session.query(ClubMember).filter_by(clubID=clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.callElection(clubID, position, candidates)

class Club(db.Model):
    clubID = db.Column(db.Integer, primary_key=True)
    clubName = db.Column(db.String(80), nullable=False, unique=True)
    elections = db.relationship('Election', backref='hostingClub')
    members = db.relationship('ClubMember', backref='club')

    def toDict(self):
        allMembers = db.session.query(ClubMember).filter_by(clubID=self.clubID).all()
        numMembers = len(allMembers)
        memberDetails = [member.toDict() for member in allMembers]

        allClubElections = db.session.query(Election).filter_by(clubID=self.clubID).all()
        listOfClubElections = [election.toDict() for election in allClubElections]
        return {
            "clubID" : self.clubID,
            "clubName" : self.clubName,
            "numMembers" : numMembers
        }

class Election(db.Model):
    electionID = db.Column(db.Integer, primary_key=True)
    clubID = db.Column(db.Integer, db.ForeignKey('club.clubID'), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    memberID = db.Column(db.Integer, db.ForeignKey('club_member.memberID'), nullable=False)
    electionEndDate = db.Column(db.DateTime, nullable = True, default = None)
    isOpen = db.Column(db.Boolean, nullable=False, default=True)
    electionWinner = db.Column(db.String(150))
    candidates = db.relationship('Candidate', backref='candidate')
    ballots = db.relationship('ElectionBallot', backref='voteBallots')

    def toDict(self):
        elecCandidates = db.session.query(Candidate).filter_by(electionID=self.electionID).all()
        listOfElectionCandidates = [candidate.toDict() for candidate in elecCandidates]
        return {
            "electionID" : self.electionID,
            "clubID" : self.clubID,
            "position" : self.position,
            "electionEndDate" : None if not self.electionEndDate else self.electionEndDate.strftime("%d-%m-%Y"),
            "hostMemberID" : self.memberID,
            "isOpen" : self.isOpen,
            "electionWinner" : self.electionWinner,
            "candidates" : listOfElectionCandidates
        }

    def tallyVotes(self):
        electionCandidates = db.session.query(Candidate).filter_by(electionID=self.electionID).all()

        if not electionCandidates:
            printf("No candidates for this election!")
            return False

        for candidate in electionCandidates:
            votes = db.session.query(ElectionBallot).filter_by(candidateID=candidate.candidateID).all()
            candidate.finalNumVotes = len(votes)

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
        '''
        for candidate in electionCandidates:
            try:
                candidate.finalNumVotes = len(db.session.query(ElectionBallot).filter_by(candidateID=candidate.candidateID).all())
                db.session.add(candidate)
                db.session.commit()
            except:
                db.session.rollback()
        '''
        voteData = [candidate.finalNumVotes for candidate in electionCandidates]
        highestVotes = max(voteData)
        winningNumberOfVotes = [x for x in voteData if x==highestVotes]

        if len(voteData) != len(set(voteData)):
            print("There has been a tie!")
            try:
                self.electionWinner = "Tie"
                db.session.add(self)
                db.session.commit()
            except:
                db.session.rollback()
        else:
            for candidate in electionCandidates:
                if candidate.finalNumVotes == highestVotes:
                    try:
                        self.electionWinner = candidate.firstName + " " + candidate.lastName
                        db.session.add(self)
                        db.session.commit()
                        print("Winner is " + candidate.firstName + " " + candidate.lastName+"!")
                    except:
                        db.session.rollback()
                        print("Error updating winner!")

class Candidate(db.Model):
    candidateID = db.Column(db.Integer, primary_key=True)
    electionID = db.Column(db.Integer, db.ForeignKey('election.electionID'), nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    finalNumVotes = db.Column(db.Integer, nullable=True, default=None)
    votes = db.relationship('ElectionBallot', backref='ballot')

    def toDict(self):
        candVotes = db.session.query(ElectionBallot).filter_by(candidateID=self.candidateID).all()
        numVotes = len(candVotes)

        return {
            "candidateID" : self.candidateID,
            "firstName" : self.firstName,
            "lastName" : self.lastName,
            "numVotes" : numVotes,
            "finalNumVotes" : self.finalNumVotes
        }

class ClubMember(db.Model):
    memberID = db.Column(db.Integer, primary_key=True)
    clubID = db.Column(db.Integer, db.ForeignKey("club.clubID"), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    votesMade = db.relationship('ElectionBallot', cascade="all, delete", backref='voter')
    hostedElections = db.relationship('Election', backref='election')
    
    def toDict(self):
        member = db.session.query(User).filter_by(id=self.id).first()
        myClub = db.session.query(Club).filter_by(clubID=self.clubID).first()
        return {
            'memberID': self.memberID,
            'username' : member.username,
            'clubID' : myClub.clubID,
            'clubName' : myClub.clubName
        }
    
    def castVote(self, candidateID):
        candidate = db.session.query(Candidate).filter_by(candidateID=candidateID).first()

        if not candidate:
            print("User attempted to vote for a candidate that did not exist!")
            return False

        election = db.session.query(Election).filter_by(electionID=candidate.electionID, isOpen=True).first()

        if not election:
            print("Sorry, the election has closed!")
            return False
        
        try:
            election = db.session.query(ElectionBallot).filter_by(electionID=candidate.electionID, memberID=self.memberID).first()
            if election:
                try:
                    db.session.delete(election)
                    db.session.commit()
                    print("Changing vote!")
                except:
                    db.session.rollback()

            ballot = ElectionBallot(memberID=self.memberID, candidateID=candidateID, electionID=candidate.electionID)
            db.session.add(ballot)
            db.session.commit()
            print("Successfully voted for candidate!")
            return True
        except:
            db.session.rollback()
            print("User may have already voted!")
            return False

    def callElection(self, clubID, position, candidates):#electionEndDate
        electionClub = db.session.query(Club).filter_by(clubID=clubID).first()

        if not electionClub:
            print("No club by this name!")
            return False

        try:
            newElection = Election(clubID=electionClub.clubID, memberID=self.memberID, position=position)
            db.session.add(newElection)
            db.session.commit()
            for candidate in candidates:
                try:
                    newCandidate = Candidate(firstName = candidate["firstName"], lastName= candidate["lastName"], electionID=newElection.electionID)
                    db.session.add(newCandidate)
                    db.session.commit()
                    print("Successfully added " + candidate["firstName"] + " " + candidate["lastName"] + " to database!")
                except:
                    db.session.rollback()
                    print("Unable to add " + candidate["firstName"] + " " + candidate["lastName"] + " to database!")
        except:
            print("Unable to add election to database!")
            db.session.rollback()
            return False
        
        return True
    
    def closeElection(self, electionID):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your elections!")
            return False
        
        try:
            election.isOpen = False
            election.declareWinner()
            election.electionEndDate = datetime.datetime.now()
            db.session.add(election)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            print("Unable to close election!")
            
            return False

    def openElection(self, electionID):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your elections!")
            return False
        
        try:
            election.isOpen = True
            election.electionWinner = None
            election.electionEndDate = None
            db.session.add(election)
            db.session.commit()
        except:
            db.session.rollback()
            print("Unable to open election!")
            return False
        
        return True

class ElectionBallot(db.Model):
    ballotID = db.Column(db.Integer, primary_key=True)
    memberID = db.Column(db.Integer, db.ForeignKey("club_member.memberID"))
    candidateID = db.Column(db.Integer, db.ForeignKey("candidate.candidateID"))
    electionID = db.Column(db.Integer, db.ForeignKey("election.electionID"))
