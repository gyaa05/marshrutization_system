from peewee import *


db = SqliteDatabase("hueta.db")

class Team(Model):
    name = CharField()
    stations = TextField()
    current_station = IntegerField()
    time = DateTimeField()
    summary_time = FloatField()
    last_station = IntegerField()

    class Meta:
        database = db

class Station(Model):
    name = CharField()
    isBusy = BooleanField()
    description = TextField()
    latitude = FloatField()
    longtitude = FloatField()
    flag = CharField()

    class Meta:
        database = db