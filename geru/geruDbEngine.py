import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists

from geruDbStructure import Session, Base, Request
 
def GetSessions():
    engine = create_engine('sqlite:///geru.db')
    Base.metadata.bind = engine
    
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()
    
    return dbSession.query(Request).all()

def Insert(page, sessionIdentifier):
    engine = create_engine('sqlite:///geru.db')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    
    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    dbSession = DBSession()
    
    if not dbSession.query(exists().where(Session.identifier == sessionIdentifier)).scalar():
        new_session = Session(identifier=sessionIdentifier)
        dbSession.add(new_session)
        dbSession.commit()
    
    new_request = Request(dt=datetime.datetime.now(), page=page, identifier=sessionIdentifier)
    dbSession.add(new_request)
    dbSession.commit()