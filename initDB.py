from main import app
from models import db, Club, Election, User, Candidate
import os

os.remove("test.db")

db.create_all(app=app)

clubDescription1 = "The UWICS are..."
clubDescription2 = "Placeholder text"

db.session.add(Club(clubName="UWI Computing Society", clubDescription=clubDescription1)) #clubImage = , 
db.session.add(Club(clubName="UWI Actuarial Science Club", clubDescription=clubDescription2))
db.session.add(Club(clubName="UWI Biological Society", clubDescription=clubDescription2))
db.session.add(Club(clubName="UWI Leadership Council", clubDescription=clubDescription2))
db.session.add(Club(clubName="UWI Art Society", clubDescription=clubDescription2))


db.session.commit()
'''
user1 = User("bobtest", "bobpass", "Bob", "Johnson")
user2 = User("tomtest", "tompass", "Tom", "Johnson")

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
'''
print('Database Initialized!')