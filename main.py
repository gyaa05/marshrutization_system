from fastapi import FastAPI
from db_na_kolenke import *
from entitys import *
import datetime, math

app = FastAPI()
api = "/api/v1"

@app.post(api + "/newTeam")
async def new_team(team: EntityTeam):
    new_team = Team(name = team.name, stations = str([i for i in range(1, 20)]), current_station = 0, time = datetime.datetime.now(), summary_time = 0, last_station = 0)
    new_team.save()

    new_team = Team.get(Team.id == new_team)

    return {"code": 200, "details": {"id": new_team.id, "name": new_team.name, "stations": eval(new_team.stations), "current_station": 0, "time": new_team.time, "summary_time": 0, "last_station": 0}}


@app.get(api + "/getTeams")
async def get_teams():
    teams = Team.select()
    return {"teams" : [{
        "id": team.id,
        "name": team.name,
        "stations": eval(team.stations), 
        "current_station": team.current_station, 
        "time": team.time,
        "summary_time": team.summary_time,
        "last_station": team.last_station
                        } for team in teams]
        }


@app.post(api + "/newStation")
async def new_team(station: EntityStation):
    new_station = Station(name = station.name, isBusy = 0, description = station.description, latitude = station.latitude, longtitude = station.longtitude, flag = station.flag)
    new_station.save()

    new_station = Station.get(Station.id == new_station)

    return {"code": 200, "details": {"id": new_station.id, "name": new_station.name, "isBusy": new_station.isBusy, "description": new_station.description, "latitude": new_station.latitude, "longitude": new_station.longtitude, "flag": new_station.flag}}


@app.get(api + "/getStations")
async def get_stations():
    stations = Station.select()
    return {"stations": [{
        "id": station.id,
        "name": station.name,
        "isBusy": station.isBusy,
        "description": station.description,
        "latitude": station.latitude,
        "longitude": station.longitude,
        "flag": station.flag
    } for station in stations]
    }


@app.get(api + "/getStation/{station_id}")
async def get_station(station_id: int):
    try:
        station = Station.get(Station.id == station_id)
        return {"details": {"id": station.id, "name": station.name, "isBusy": station.isBusy, "description": station.description, "latitude": station.latitude, "longitude": station.longtitude, "flag": station.flag}}
    except:
        return {"code": 404}
    

@app.post(api + "/freezeStation")
async def freeze_station(freeze: Freeze):
    try:
        station = Station.get(Station.id == freeze.station_id)

        station.isBusy = True
        station.save()

        team = Team.get(Team.id == freeze.team_id)

        team.current_station = freeze.station_id
        stations = eval(team.stations)
        stations.remove(freeze.station_id)
        team.stations = str(stations)
        team.time = datetime.datetime.now()
        team.save()

        return {"code": 200}
    except:
        return {"code": 404}
    

@app.post(api + "/unfreezeStation")
async def unfreeze_station(unfreeze: Unfreeze):
    try:
        team = Team.get(Team.id == unfreeze.team_id)
        station_id = team.current_station
        station = Station.get(Station.id == station_id)
        if unfreeze.flag != station.flag:
            return {"code": 401}
        station.isBusy = False
        station.save()

        timing = datetime.datetime.now() - team.time
        team.summary_time = team.summary_time + float(timing.total_seconds())
        team.time = datetime.datetime.now()
        team.current_station = 0
        team.last_station = station_id
        team.save()

        return {"code": 200}
    except Exception as e:
        return {"code": 404, "exception": e}


@app.post(api + "/findStation")
async def find_station(team_id: TeamId):
    team = Team.get(Team.id == team_id.team_id)
    stations = eval(team.stations)
    all_stations = list(Station.select())
    if team.last_station != 0:
        last_station = all_stations[team.last_station]
        for i, station_num in stations:
            station = all_stations[station_num]
            rasstoyanie = math.sqrt((station.longtitude - last_station.longtitude)**2 + (station.latitude - last_station.latitude)**2)
            stations[i] = [stations[i], rasstoyanie]
        stations = sorted(stations, key=lambda x: x[1])
        while True:
            for i in stations:
                if not all_stations[i - 1].isBusy:
                    station = all_stations[i - 1]
                    data = {
                        "team_id": team_id.team_id,
                        "station_id": i
                    }
                    freeze = Freeze(**data)
                    await freeze_station(freeze)
                    return {"code": 200, "details": {"name": station.name, "description": station.description, "latitude": station.latitude, "longitude": station.longtitude}}
    else:
        for i in stations:
            if not all_stations[i - 1].isBusy:
                station = all_stations[i - 1]
                data = {
                    "team_id": team_id.team_id,
                    "station_id": i
                }
                freeze = Freeze(**data)
                await freeze_station(freeze)
                return {"code": 200, "details": {"name": station.name, "description": station.description, "latitude": station.latitude, "longitude": station.longtitude}}


with db:
    db.create_tables([Team, Station])