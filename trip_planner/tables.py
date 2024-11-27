from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# taken from https://www.reddit.com/r/Python/comments/4kqdyg/cool_sqlalchemy_trick/
def as_dict(self):
    new_data = {}
    data = self.__dict__
    for key, value in data.items():
        if not key.startswith("_") and not hasattr(value, "__call__"):
            new_data[key] = data[key]
    return new_data

def inject_function(func):
    def decorated_class(cls):
        setattr(cls, func.__name__, func)
        return cls
    return decorated_class

@inject_function(as_dict)
class Leg(Base):
    __tablename__ = 'leg'
    id = Column(Integer, primary_key=True)
    agency = Column(String(128))
    stop_id = Column(String(64))
    stop_tag = Column(String(64))
    stop_title = Column(String(128))

@inject_function(as_dict)
class LegDestination(Base):
    __tablename__ = 'leg_destination'
    id = Column(Integer, primary_key=True)
    leg_id = Column(Integer, ForeignKey('leg.id'))
    tag = Column(String(64))

@inject_function(as_dict)
class Trip(Base):
    __tablename__ = 'trip'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))

@inject_function(as_dict)
class TripLeg(Base):
    __tablename__ = 'trip_leg'
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trip.id'))
    leg_id = Column(Integer, ForeignKey('leg.id'))
