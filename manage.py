from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app
from models import db

manager = Manager(app)
migrate = Migrate(app, db)

from models import *

manager.add_command('db', MigrateCommand)

# initDB command
@manager.command
def initDB():
    db.create_all(app=app)
    clubs = []
    clubs.append(Club(clubName="UWI Computing Society", clubDescription="The University of the West Indies Computing Society welcomes all who wish to partake in the discussion of new and innovative technologies of the modern world."))
    clubs.append(Club(clubName="UWI Biological Society", clubDescription="The University of the West Indies Biological Society is an environmental conservation organization founded in 1987, STA UWI."))
    clubs.append(Club(clubName="UWI Law Society", clubDescription="The University of the West Indies Law Society provides a forum for members to discuss prevalent issues that plague the judicial systems across the globe."))
    clubs.append(Club(clubName="UWI Charity and Outreach Society", clubDescription="The University of the West Indies Law Society's Charity and Outreach Committee devotes to ensuring each student has an extraordinary and memorable university volunteer experience."))

    for club in clubs:
        try:
            db.session.add(club)
            db.session.commit()
        except:
            db.session.rollback()
            print("Club already exists in database!")
        
    print('Database Initialized!')

# serve command
@manager.command
def serve():
    print('Application running in ' +app.config['ENV'] + ' mode')
    app.run(host='0.0.0.0', port = 8080, debug = app.config['ENV']=='development')

@manager.command
def addClub(clubName, clubDescription, clubImage):
    if clubImage == "none":
        clubImage = None
    if clubName and clubDescription:
        newClub = Club(clubName=clubName, clubDescription=clubDescription, clubImage=clubImage)
        try:
            db.session.add(newClub)
            db.session.commit()
            print("Successfully added club to database!")
        except:
            db.session.rollback()
            print("Unable to add club to database!")

@manager.command
def editClubDescription(clubName, clubDescription):
    if clubName:
        newClub = db.session.query(Club).filter_by(clubName=clubName).first()
        if not newClub:
            return "Unable to find club by that name."
    
        if clubDescription:
            newClub.clubDescription = clubDescription
            try:
                db.session.add(newClub)
                db.session.commit()
                print("Successfully updated club description!")
            except:
                db.session.rollback()
                print("Unable to update club description!")
    else:
        print("No club name provided!")

@manager.command
def editClubImage(clubName, clubImage):
    if clubName:
        newClub = db.session.query(Club).filter_by(clubName=clubName).first()
        if not newClub:
            return "Unable to find club by that name."
    
        if clubImage:
            newClub.clubImage = clubImage
            try:
                db.session.add(newClub)
                db.session.commit()
                print("Successfully updated club image!")
            except:
                db.session.rollback()
                print("Unable to update club image!")
        else:
            print("No description provided for club!")
    else:
        print("No club name provided!")


@manager.command
def removeClub(clubName):
    if clubName:
        deletionClub = db.session.query(Club).filter_by(clubName=clubName).first()

        if deletionClub:

            elections = db.session.query(Election).filter_by(clubID=deletionClub.clubID).all()
            if elections:
                for election in elections:
                    try:
                        db.session.delete(election)
                        db.session.commit()
                        print("Successfully deleted election from database!")
                    except:
                        db.session.rollback()
                        print("Unable to delete election from database!")

            clubMembers = db.session.query(ClubMember).filter_by(clubID=deletionClub.clubID).all()
            if clubMembers:
                for clubMember in clubMembers:
                    try:
                        db.session.delete(clubMember)
                        db.session.commit()
                        print("Successfully deleted club member from database!")
                    except:
                        db.session.rollback()
                        print("Unable to delete club member from database!")
            try:
                db.session.delete(deletionClub)
                db.session.commit()
                print("Successfully removed club from database!")
            except:
                db.session.rollback()
                print("Unable to remove club from database!")
        else:
            print("Unable to find club in database!")
    else:
        print("No club name provided!")

@manager.command
def resetDatabase():
    pass
    print("Unable to clear database completely!")


if __name__ == "__main__":
    manager.run()