from main import app
from models import db, Club, Election, User, Candidate
import os

os.remove("test.db")

db.create_all(app=app)

UWICS = Club(clubName="UWICS")
Rotary = Club(clubName="Rotary")
RRunners = Club(clubName="Road Runners")

db.session.add(UWICS)
db.session.add(Rotary)
db.session.add(RRunners)
db.session.commit()

user1 = User("bob", "bobpass", "Bob", "Johnson")
user2 = User("tom", "tompass", "Tom", "Johnson")

db.session.add(user1)
db.session.add(user2)
db.session.commit()

user1.joinClub("UWICS")
user2.joinClub("UWICS")

candidate1 = {
    "firstName" : "Tim",
    "lastName": "Harpy"
}

candidate2 = {
    "firstName" : "John",
    "lastName": "Rolled"
}

#candidate1 = Candidate(electionID=1, firstName="Tim", lastName="Rolled")
#candidate2 = Candidate(electionID=1, firstName="John", lastName="Harpy")
#db.session.add(candidate1)
#db.session.add(candidate2)
#db.session.commit()

user1.callElection("UWICS", "PRO", [candidate1, candidate2])

user1.castVote("UWICS", 1)
user2.castVote("UWICS", 1)

user1.closeElection(1)
user2.leaveClub("UWICS")
user1.openElection(1)
user1.closeElection(1)

print('Database Initialized!')