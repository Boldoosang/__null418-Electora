from main import app
from models import db, Club, Election, User, Candidate
import os

os.remove("test.db")

db.create_all(app=app)

UWICS = Club(clubName="UWICS")
db.session.add(UWICS)
db.session.commit()

user1 = User("bob", "bobpass", "Bob", "Johnson")
user2 = User("tom", "tompass", "Tom", "Johnson")

db.session.add(user1)
db.session.add(user2)
db.session.commit()

user1.joinClub("UWICS")

election1 = Election(position="Secretary", hostingClub=UWICS)
election2 = Election(position="President", hostingClub=UWICS)
db.session.add(election1)
db.session.add(election2)
db.session.commit()

candidate1 = Candidate(electionID=1, firstName="Tim", lastName="Rolled")
candidate2 = Candidate(electionID=1, firstName="John", lastName="Harpy")
db.session.add(candidate1)
db.session.add(candidate2)
db.session.commit()

user1.castVote("UWICS", 1)
user1.castVote("UWICS", 1)

election1.declareWinner()

print('Database Initialized!')