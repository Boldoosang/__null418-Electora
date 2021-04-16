from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app
from models import db
manager = Manager(app)

from models import *

manager.add_command('db', MigrateCommand)

# initDB command
@manager.command
def initDB():
    db.create_all(app=app)
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
        club = db.session.query(Club).filer_by(clubName=clubName)
        if not club:
            return "Unable to find club by that name."
    
        if clubDescription:
            club.clubDescription = clubDescription
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
        club = db.session.query(Club).filer_by(clubName=clubName)
        if not club:
            return "Unable to find club by that name."
    
        if clubDescription:
            club.clubImage = clubImage
            try:
                db.session.add(newClub)
                db.session.commit()
                pprint("Successfully updated club image!")
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

if __name__ == "__main__":
    manager.run()