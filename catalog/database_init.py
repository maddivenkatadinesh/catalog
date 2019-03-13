from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///aeroplanes.db')
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
session = DBSession()

# Delete AeroplaneName if exisitng.
session.query(AeroplaneName).delete()
# Delete ModelName if exisitng.
session.query(ModelName).delete()
# Delete User if exisitng.
session.query(User).delete()


# Create sample users data
User1 = User(name="Maddi Venkata Dinesh",
             email="dineshmaddi15@gmail.com",
             picture='http://www.enchanting-costarica.com/wp-content/'
             'uploads/2018/02/jcarvaja17-min.jpg')

session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample Restaurents
Aeroplane1 = AeroplaneName(name="AIR INDIA",
                           user_id=1)
session.add(Aeroplane1)
session.commit()

Aeroplane2 = AeroplaneName(name="SPICE JET",
                           user_id=1)
session.add(Aeroplane2)
session.commit

Aeroplane3 = AeroplaneName(name="JET AIRWAYS",
                           user_id=1)
session.add(Aeroplane3)
session.commit()

Aeroplane4 = AeroplaneName(name="INDIGO",
                           user_id=1)
session.add(Aeroplane4)
session.commit()

Aeroplane5 = AeroplaneName(name="AIR ASIA",
                           user_id=1)
session.add(Aeroplane5)
session.commit()

Aeroplane6 = AeroplaneName(name="BOEING",
                           user_id=1)
session.add(Aeroplane6)
session.commit()

# Populare a items
# Using different users for items
Model1 = ModelName(name="AIRBUS A330",
                   capacity="500",
                   topspeed="4000",
                   rating="Good",
                   service="passengers",
                   date=datetime.datetime.now(),
                   aeroplanenameid=1,
                   user_id=1)
session.add(Model1)
session.commit()

Model2 = ModelName(name="Q400",
                   capacity="450",
                   topspeed="1900",
                   rating="Good",
                   service="passengers",
                   date=datetime.datetime.now(),
                   aeroplanenameid=2,
                   user_id=1)
session.add(Model2)
session.commit()

Model3 = ModelName(name="AIRCRAFT ATR 72",
                   capacity="300",
                   topspeed="2500",
                   rating="Good",
                   service="passengers",
                   date=datetime.datetime.now(),
                   aeroplanenameid=3,
                   user_id=1)
session.add(Model3)
session.commit()

Model4 = ModelName(name="A320",
                   capacity="550",
                   topspeed="5400",
                   rating="Good",
                   service="passengers",
                   date=datetime.datetime.now(),
                   aeroplanenameid=4,
                   user_id=1)
session.add(Model4)
session.commit()

Model5 = ModelName(name="MYX 5099",
                   capacity="400",
                   topspeed="2000",
                   rating="excellent",
                   service="passengers",
                   date=datetime.datetime.now(),
                   aeroplanenameid=5,
                   user_id=1)
session.add(Model5)
session.commit()

Model6 = ModelName(name="747-A",
                   capacity="300",
                   topspeed="5050",
                   rating="excellent",
                   service="passengers",
                   date=datetime.datetime.now(),
                   aeroplanenameid=6,
                   user_id=1)
session.add(Model6)
session.commit()

print("Your database has been inserted!")
