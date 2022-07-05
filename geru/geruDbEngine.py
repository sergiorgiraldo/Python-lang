import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
from geruDbStructure import Session, Base, Request
 
def GetSessions():
    return dbSession.query(Request).all()

def Insert(page, sessionIdentifier):   
    if not dbSession.query(exists().where(Session.identifier == sessionIdentifier)).scalar():
        new_session = Session(identifier=sessionIdentifier)
        dbSession.add(new_session)
        dbSession.commit()
    
    new_request = Request(dt=datetime.datetime.now(), page=page, identifier=sessionIdentifier)
    dbSession.add(new_request)
    dbSession.commit()
    #dbSession.rollback()

engine = create_engine('sqlite:///geru.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbSession = DBSession()
