from main import app
from models import db, Club

db.create_all(app=app)

UWICS = Club(clubName="UWICS")
db.session.add(compSciClub)
db.session.commit()

print('database initialized!')