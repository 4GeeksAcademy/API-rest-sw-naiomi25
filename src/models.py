from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean,Table,Column,ForeignKey,DateTime
from sqlalchemy.orm import Mapped, mapped_column,relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50),nullable = False)
    lastname:Mapped[str] = mapped_column(String(50),nullable = True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorites_people : Mapped[List['People']]=relationship(secondary='favorites_people', back_populates='user_favorites')
    favorites_planet : Mapped[List['Planets']] = relationship(secondary = 'favorites_planet', back_populates = 'user_favorites')



    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            'name':self.name,
            'lastname':self.lastname
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(primary_key = True)
    name : Mapped[str]= mapped_column(String(30), nullable= False)
    temperature : Mapped[int] = mapped_column(nullable = False)
    dimension :Mapped[int]= mapped_column(default=0)
    gravity:Mapped[bool] = mapped_column(nullable=False)

    user_favorites : Mapped[List['User']] = relationship(secondary = 'favorites_planet', back_populates= 'favorites_planet')


    def serialize (self):
        return  { 
        'id' :self.id,
        'name' :self.name,
        'temperature' :self.temperature,
        'dimension' : self.dimension,
        'gravity' :self.gravity

        }
class People(db.Model):
    __tablename__ ='people'

    id : Mapped[int]=mapped_column(primary_key  = True)
    name : Mapped[str]=mapped_column(String(30), nullable= False)
    gender : Mapped[str]= mapped_column(String(30), nullable= False)
    height :  Mapped[int] = mapped_column(nullable = False)
    eye_color: Mapped[str]= mapped_column( nullable= False)
    
    user_favorites : Mapped[List['User']] = relationship(secondary = 'favorites_people', back_populates= 'favorites_people')

    def serialize(self):

        return{
            'id' : self.id,
            'name' : self.name,
            'gender' : self.gender,
            'height' : self.height,
            'eye_color' : self.eye_color,

        }


favorites_planet = Table(

    'favorites_planet',
    db.metadata,
    Column ('id_user',ForeignKey('user.id'), primary_key=True),
    Column ('id_planet',ForeignKey('planet.id'), primary_key=True)


)
favorites_people = Table(

    'favorites_people',
    db.metadata,
    Column ('id_user',ForeignKey('user.id'), primary_key=True),
    Column ('id_people',ForeignKey('people.id'),primary_key=True),

)