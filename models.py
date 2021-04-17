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
    clubMembers = db.relationship('ClubMember', cascade="all, delete", backref='membership')

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

        if not myClubs:
            return None
        
        listOfMyClubs = [club.toDict() for club in myClubs]

        return listOfMyClubs
    
    def myManagingElections(self):
        memberships = db.session.query(ClubMember).filter_by(id=self.id).all()
        
        allMyManagingElections = []

        for membership in memberships:
            listOfMyClubElections = membership.myManagingElections()
            for clubElection in listOfMyClubElections:
                allMyManagingElections.append(clubElection)

        return allMyManagingElections

    def changePosition(self, electionID, position):
        membership = db.session.query(ClubMember).filter_by(id=self.id).first()
        
        if not membership:
            return False

        return membership.changePosition(electionID, position)

    def addCandidate(self, electionID, candidateDetails):
        membership = db.session.query(ClubMember).filter_by(id=self.id).first()
        
        if not membership:
            return False

        return membership.addCandidate(electionID, candidateDetails)

    def deleteCandidate(self, electionID, candidateID):
        membership = db.session.query(ClubMember).filter_by(id=self.id).first()
        
        if not membership:
            return False

        return membership.deleteCandidate(electionID, candidateID)

    def myElections(self):
        memberships = db.session.query(ClubMember).filter_by(id=self.id).all()
        
        if not memberships:
            return None

        allMyElections = []

        for membership in memberships:
            listOfMyClubElections = membership.myElections()

            if listOfMyClubElections:
                for clubElection in listOfMyClubElections:
                    allMyElections.append(clubElection)
            
        return allMyElections

    def viewElection(self, electionID):
        memberships = db.session.query(ClubMember).filter_by(id=self.id).all()

        if not memberships:
            return None

        election = db.session.query(Election).filter_by(electionID=electionID).first()
        
        if not election:
            return None


        for membership in memberships:
            if election.clubID == membership.clubID:
                return election.toDict()

        return None

    def getElectionCandidatesDetails(self, electionID):
        election = db.session.query(Election).filter_by(electionID=electionID).first()

        if not election:
            print("Election does not eixst!")
            return None

        clubMembership = db.session.query(ClubMember).filter_by(clubID=election.clubID, id=self.id).first()

        if not clubMembership:
            print("User does not have permission to view these candidates!")
            return None
        
        candidates = db.session.query(Candidate).filter_by(electionID=electionID).all()

        return [candidate.toDict() for candidate in candidates]

    def viewCandidate(self, electionID, candidateID):
        cand = db.session.query(Candidate).filter_by(candidateID=candidateID, electionID=electionID).first()

        if not cand:
            print("Candidate does not eixst!")
            return None

        election = db.session.query(Election).filter_by(electionID=electionID).first()

        if not election:
            print("Election does not exist or may have been deleted!")
            return None

        clubMembership = db.session.query(ClubMember).filter_by(clubID=election.clubID, id=self.id).first()

        if not election:
            print("User does not have permission to view this candidate!")
            return None
        
        return cand.toDict()

    def viewMyClubElections(self):
        membership = db.session.query(ClubMember).filter_by(id=self.id).first()
        
        if not membership:
            return False

        return membership.viewMyClubElections()


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
            #delete active elections when host leaves
            activeElections = db.session.query(Election).filter_by(memberID=membership.memberID, isOpen=True).all()
            for election in activeElections:
                try:
                    db.session.delete(election)
                    db.session.commit()
                    print("Cleaning up user's active elections!")
                except:
                    db.session.rollback()
                    print("Error cleaning up user's active elections!")

            #leave finished elections
            db.session.delete(membership)
            db.session.commit()
            print("User has been removed from club!")
            return True
        except:
            db.session.rollback()
            print("Unable to remove user from club!")

        return False

    def castVote(self, electionID, candidateID):
        elec = db.session.query(Election).filter_by(electionID=electionID).first()
        if not elec:
            print("Election cannot be found!")
            return False

        clubMembership = db.session.query(ClubMember).filter_by(clubID=elec.clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.castVote(candidateID)
    
    def closeElection(self, electionID):
        electionClub = db.session.query(Election).filter_by(electionID=electionID).first()
        if not electionClub:
            print("No election found!")
            return False
        clubMembership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.closeElection(electionID=electionID)

    def openElection(self, electionID):
        electionClub = db.session.query(Election).filter_by(electionID=electionID).first()
        if not electionClub:
            print("No election found!")
            return False
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

    def deleteElection(self, electionID):
        electionClub = db.session.query(Election).filter_by(electionID=electionID).first()
        if not electionClub:
            print("No election found!")
            return False
        clubMembership = db.session.query(ClubMember).filter_by(clubID=electionClub.clubID, id=self.id).first()
        
        if not clubMembership:
            print("User is not a member of this club!")
            return False
        
        return clubMembership.deleteElection(electionID=electionID)

    def updateCandidateDetails(self, electionID, candidateID, newDetails):
        membership = db.session.query(ClubMember).filter_by(id=self.id).first()
        
        if not membership:
            return False

        return membership.updateCandidateDetails(electionID, candidateID, newDetails)

class Club(db.Model):
    clubID = db.Column(db.Integer, primary_key=True)
    clubDescription = db.Column(db.String(300), nullable = False, default="This group does not have a description.")
    clubImage = db.Column(db.String(300), nullable = False, default="https://cdn.pixabay.com/photo/2017/03/31/17/44/avatar-2191932_1280.png")
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
            "numMembers" : numMembers,
            "clubDescription" : self.clubDescription,
            "clubImage" : self.clubImage
        }

class Election(db.Model):
    electionID = db.Column(db.Integer, primary_key=True)
    clubID = db.Column(db.Integer, db.ForeignKey('club.clubID'), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    memberID = db.Column(db.Integer, db.ForeignKey('club_member.memberID'), nullable=True)
    electionEndDate = db.Column(db.DateTime, nullable = True, default = None)
    isOpen = db.Column(db.Boolean, nullable=False, default=True)
    electionWinner = db.Column(db.String(150))
    candidates = db.relationship('Candidate', backref='candidate')
    ballots = db.relationship('ElectionBallot', backref='voteBallots')

    def toDict(self):
        elecCandidates = db.session.query(Candidate).filter_by(electionID=self.electionID).all()
        listOfElectionCandidates = [candidate.toDict() for candidate in elecCandidates]
        club = db.session.query(Club).filter_by(clubID=self.clubID).first()
        return {
            "electionID" : self.electionID,
            "clubID" : self.clubID,
            "clubName" : club.clubName,
            "position" : self.position,
            "electionEndDate" : None if not self.electionEndDate else self.electionEndDate.strftime("%m-%d-%Y"),
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

        for candidate in electionCandidates:
            try:
                candidate.finalNumVotes = len(db.session.query(ElectionBallot).filter_by(candidateID=candidate.candidateID).all())
                db.session.add(candidate)
                db.session.commit()
            except:
                db.session.rollback()
        
        voteData = [candidate.finalNumVotes for candidate in electionCandidates]
        highestVotes = max(voteData)

        winningNumberOfVotes = [x for x in voteData if x==highestVotes]
        
        if len(winningNumberOfVotes) != len(set(winningNumberOfVotes)):
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
    electionID = db.Column(db.Integer, db.ForeignKey('election.electionID'), nullable=True)
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
            'clubName' : myClub.clubName,
            'clubImage' : myClub.clubImage,
            'clubDescription' : myClub.clubDescription
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
            duplicateActiveElection = db.session.query(Election).filter_by(position=position, clubID=electionClub.clubID, isOpen=True).all()

            if duplicateActiveElection:
                return False

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
                    return False
        except:
            print("Unable to add election to database!")
            db.session.rollback()
            return False
        
        return True
    
    def closeElection(self, electionID):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your managing elections!")
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
            print("No election found in your managing elections!")
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

    def myManagingElections(self):
        myElections = db.session.query(Election).filter_by(memberID=self.memberID).all()
        if not myElections:
            return None

        listOfMyElections = [election.toDict() for election in myElections]
        return listOfMyElections

    def myElections(self):
        myElections = db.session.query(Election).filter_by(clubID=self.clubID).all()
        if not myElections:
            return None

        listOfMyElections = [election.toDict() for election in myElections]
        return listOfMyElections

    def viewElection(self, electionID):
        election = db.session.query(Election).filter_by(electionID=electionID).first()

        if not election:
            return None
        
        return election.toDict()
    
    def changePosition(self, electionID, position):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your managing elections!")
            return False

        if not election.isOpen:
            print("Unable to update position as election is closed!")
            return False
        
        try:
            election.position = position
            db.session.add(election)
            db.session.commit()
        except:
            db.session.rollback()
            print("Unable to update election position!")
            return False
        
        return True

    def addCandidate(self, electionID, candidateDetails):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your managing elections!")
            return False

        if not election.isOpen:
            print("Unable to add candidate as election is closed!")
            return False

        duplicate = db.session.query(Candidate).filter_by(electionID=electionID, firstName=candidateDetails["firstName"], lastName=candidateDetails["lastName"]).first()
        if duplicate:
            print("Candidate already exists for this election!")
            return False

        try:
            newCandidate = Candidate(electionID=electionID, firstName=candidateDetails["firstName"], lastName=candidateDetails["lastName"])
            db.session.add(newCandidate)
            db.session.commit()
            print("Candidate added to election!")
        except:
            db.session.rollback()
            print("Unable to add candidate!")
            return False
        
        return True

    def deleteCandidate(self, electionID, candidateID):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your managing elections!")
            return False

        if not election.isOpen:
            print("Unable to delete candidate as election is closed!")
            return False

        try:
            candidate = db.session.query(Candidate).filter_by(electionID=electionID, candidateID=candidateID).first()
            db.session.delete(candidate)
            db.session.commit()
            print("Candidate deleted from election!")
        except:
            db.session.rollback()
            print("Unable to delete candidate!")
            return False
        
        return True

    def deleteElection(self, electionID):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID).first()

        if not election:
            print("No election found in your managing elections!")
            return False
        
        try:
            db.session.delete(election)
            db.session.commit()
            print("Election deleted!")

            return True
        except:
            db.session.rollback()
            print("Unable to delete election!")
            
            return False

    def updateCandidateDetails(self, electionID, candidateID, newDetails):
        election = db.session.query(Election).filter_by(electionID=electionID, memberID=self.memberID, isOpen=True).first()

        if not election:
            print("No election found in your managing elections!")
            return False

        candidate = db.session.query(Candidate).filter_by(electionID = electionID, candidateID = candidateID).first()

        if not candidate:
            print("No candidate found by that ID!")
            return False

        try:
            candidate.firstName = newDetails["firstName"]
            candidate.lastName = newDetails["lastName"]
            db.session.add(candidate)
            db.session.commit()
        except:
            db.session.rollback()
            print("Unable to update election position!")
            return False
        
        return True


class ElectionBallot(db.Model):
    ballotID = db.Column(db.Integer, primary_key=True)
    memberID = db.Column(db.Integer, db.ForeignKey("club_member.memberID"))
    candidateID = db.Column(db.Integer, db.ForeignKey("candidate.candidateID"))
    electionID = db.Column(db.Integer, db.ForeignKey("election.electionID"))
