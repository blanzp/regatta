from flask import Flask, request, abort, url_for
import json
import logging
# import datetime
import model
import wolfram
# from flask_login import LoginManager, UserMixin
# from flask_login import login_required

#from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
import simplejson
import time


app = Flask(__name__, static_folder='static')

# TODO should i abstract this

# Create db connection
conn = model.DBConnection("development")

auth = HTTPBasicAuth()


@app.route('/api/protected')
@auth.login_required
def get_resource():
    return "hello paul"


audit = model.Audit(conn)


# Main page
@app.route('/')
def index():
    # send_static_file will guess the correct MIME type
    return app.send_static_file('html/index.html')


# Get single item
@app.route('/api/<resource>/<id>')
def get_resource_id(resource, id):
    if resource == 'athletes':
        data = model.AthleteCollection(conn).get_item(_id=id)
    elif resource == 'organizations':
        data = model.OrganizationCollection(conn).get_item(_id=id)
    elif resource == 'events':
        data = model.EventCollection(conn).get_item(_id=id)
    elif resource == 'crews':
        data = model.CrewCollection(conn).get_item(_id=id)
    elif resource == 'flights':
        flights = get_flights()
        return simplejson.dumps(flights[int(id)])
    else:
        return "Invalid resource"
    return simplejson.dumps(data._data)


# Get Items
@app.route('/api/<resource>')
def get_resources(resource):
    if resource == 'events':
        data = model.EventCollection(conn).scan()
    elif resource == 'regattas':
        data = model.RegattaCollection(conn).scan()
    elif resource == 'organizations':
        data = model.OrganizationCollection(conn).scan()
    elif resource == 'flights':
        flights = get_flights()
        return simplejson.dumps(flights)
    else:
        return "Invalid resource"
    return simplejson.dumps(map(lambda x: x._data, data))

def get_flights():
    flights = []
    events = model.EventCollection(conn).scan()
    for event in events:
        stage_index = 0
        for stage in event['stage']:
            race_index = 0
            for race in stage['race']:
                race['racingCrew'] = enrich_racing_crews(race['racingCrew'], event['crew']) if 'racingCrew' in race else ''
                flights.append({'event_id': event['_id'],
                                'eventNumber': event['eventNumber'],
                                'crew': event['crew'],
                                'racingCrew': race['racingCrew'] if 'racingCrew' in race else '',
                                'race_id': race['_id'],
                                'stage_index': stage_index,
                                'flight_index': race_index,
                                'eventTitle': event['eventTitle'],
                                'raceNumber': race['raceNumber'],
                                'start_time': race['start_time'] if 'start_time' in race else '',
                                'winning_time': race['winning_time'] if 'winning_time' in race else '',
                                'status': race['status'] if 'status' in race else ''})
                race_index += 1
            stage_index += 1
    return sorted(
        flights, key=lambda x: (int(x['eventNumber']), x['raceNumber']))


def enrich_racing_crews(racing_crews,crews):
    new_crews = list()
    for racing_crew in racing_crews:
        crew = get_crew_by_id(crews, racing_crew['crew'])
        racing_crew['organization'] = crew['organization']
        racing_crew['subTeamId'] = crew['subTeamId'] if 'subTeamId' in crew else ''
        new_crews.append(racing_crew)
    return new_crews


def get_crew_by_id(crews,id):
    for crew in crews:
        if crew['_id'] == id:
            return crew
    return None
#
# # Get races of event
# @app.route('/api/races')
# def get_races():
# event_id = request.args.get('event_id')
#     if event_id is not None:
#         data = model.RaceCollection(conn).query_2(event__eq=event_id,
#                                               index="event-index")
#     else:
#         data = model.RaceCollection(conn).scan()
#
#     return simplejson.dumps(
#         sorted(
#             map(lambda o: o._data, data),
#             key=lambda x: (int(x['eventNumber']),
#                             x['raceNumber'])))


@app.route('/api/races/<race_id>', methods=['POST'])
def update_race(race_id):
    start_time = request.json['start_time']
    app.logger.debug('in update race' + race_id + ' ' + str(start_time))
    race = model.RaceCollection(conn).get_item(_id=race_id)
    app.logger.debug("Got race: " + race['_id'])
    race['start_time'] = start_time
    race['status'] = "In Progress"
    race.save()
    return "Race updated successfully"


@app.route('/api/racecrews', methods=['POST'])
def update_races():
    race_id = request.args.get('race_id')
    race = model.RaceCollection(conn).get_item(_id=race_id)
    finishes = request.json.get('finishes')

    for finish in finishes:
        crew = model.RacingCrewCollection(conn).get_item(_id=finish['crew'])
        crew['order'] = finish['order']
        crew['split_time'] = finish['split_time']
        crew['finish_time'] = finish['finish_raw_time'] - race['start_time']
        crew.save()

    return "OK"


def get_crew_dict():
    crew_dict = {}
    crew_detail = model.CrewCollection(conn).scan()
    for detail in crew_detail:
        crew_dict[detail['_id']] = detail._data
    return crew_dict


def find_racecrew_by_lane(race_crews, lane):
    i = 0
    for race_crew in race_crews:
        #app.logger.debug("comparing {} to {}".format(race_crew['laneNumber'],lane))
        if int(race_crew['laneNumber']) == lane:
            #app.logger.debug("returning {}".format(i))
            return i
        i += 1
    return None


# Start Race
@app.route('/api/event/<event_id>/stage/<stage_index>/race/<race_index>', methods=['POST'])
def start_race(event_id, stage_index, race_index):
    stage_index = int(stage_index)
    race_index = int(race_index)
    action = request.args.get('action')

    if action == 'start':
        event = model.EventCollection(conn).get_item(_id=event_id)
        if 'status' not in event['stage'][stage_index]['race'][race_index]:
            start_time = request.json.get('start_time')
            event['stage'][stage_index]['race'][race_index]['start_time'] = start_time
            event['stage'][stage_index]['race'][race_index]['status'] = "In Progress"
            event.save()
            #audit.info("StartRace {} {}".format(event['eventTitle'], start_time))
            return "Race Started", 200
        else:
            return "Race already started or finished", 404
    elif action == "finish":
        event = model.EventCollection(conn).get_item(_id=event_id)
        if 'status' not in event['stage'][stage_index]['race'][race_index]:
            return "Race not started", 404
        elif event['stage'][stage_index]['race'][race_index]['status'] == "Finished":
            return "Race already finished", 404
        elif event['stage'][stage_index]['race'][race_index]['status'] == "In Progress":
            finishes = request.json.get('finishes')
            for finish in finishes:
                index = find_racecrew_by_lane(event['stage'][stage_index]['race'][race_index]['racingCrew'],
                                              finish['lane'])
                event['stage'][stage_index]['race'][race_index]['racingCrew'][index]['order'] = finish['order']
                event['stage'][stage_index]['race'][race_index]['racingCrew'][index]['finish_raw_time'] = finish[
                    'finish_raw_time']
                event['stage'][stage_index]['race'][race_index]['racingCrew'][index]['finish_split_time'] = finish[
                    'split_time']
            event['stage'][stage_index]['race'][race_index]['winning_time'] = request.json.get(
                'finish_winning_raw_time')
            event['stage'][stage_index]['race'][race_index]['status'] = "Finished"
            event.save()
            #audit.info("StartRace {} {}".format(event['eventTitle'], start_time))
            return "Race Finish Saved", 200
        else:
            return "Unknown race status", 404
    else:
        return "No such action", 404


@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


@app.route('/api/users', methods=['POST'])
def add_user():
    password = request.json.get('password')
    email = request.json.get('email')
    first = request.json.get('first')
    last = request.json.get('last')

    if email is None or password is None:
        abort(400)  # missing arguments
        user_coll = model.UserCollection(conn)
        new_user = model.User(
            user_coll, email=email, password=password, first=first, last=last)
        new_user.save()
        return json.dumps({'email': email}), 201,
        {'Location': url_for('get_user', email=email, _external=True)}


@app.route('/api/users/<email>', methods=['GET'])
def get_user(email):
    user_coll = model.UserCollection(conn)
    user = user_coll.query_2(email=email)
    return json.dumps({'email': user.email,
                       'first_name': user.first_name,
                       'last_name': user.last_name}), 200


import rml_load
@app.route('/api/loadrml', methods=['POST'])
def upload_rml():
    rml_file = request.files['file']
    app.logger.debug("Received uploaded RML")
    rml = rml_file.stream.read()
    app.logger.debug("Clearing DBs")
    clear_db()
    app.logger.debug("Loading RML")
    rml_load.load_rml_from_string(rml,conn)
    return "Loaded new RML File", 200

def clear_db():
    model.OrganizationCollection(conn).delete()
    model.EventCollection(conn).delete()
    model.RegattaCollection(conn).delete()

    model.OrganizationCollection(conn).create()
    time.sleep(5)
    model.EventCollection(conn).create()
    time.sleep(5)
    model.RegattaCollection(conn).create()
    time.sleep(5)

# TODO clean this up.  Shooud propely wrap user


def verify_password_hash(hash, password):
    return pwd_context.verify(password, hash)


@auth.verify_password
def verify_password(email, password):
    user_coll = model.UserCollection(conn)
    user = user_coll.query_2(email=email)
    if not user or not verify_password_hash(user['password_hash'], password):
        return False
        app.g.user = user
        return True


def assign_lanes(lane_count, events, boats):
    for event in events:
        entries = filter_list_event(boats, event.Event)
        assignments = middle_out(lane_count, len(entries))
    # print "Assigning for event",event.Event, assignments
    i = 0
    for racer in entries:
        racer.Bow_Lane_ID = assignments[i]
        i += 1
        return boats


def filter_list_event(data_list, value):
    obj_list = []
    for obj in data_list:
        if obj.Event == value:
            obj_list.append(obj)
            return obj_list


def middle_out(lane_count, participants):
    lanes = []
    start_lane = int(lane_count / 2)
    for i in range(0, lane_count / 2):
        lanes.append(start_lane - i)
        lanes.append(start_lane + i + 1)

    return lanes[:participants]


def main():
    app.run(host="0.0.0.0", debug=True)
    # app.run(debug=True)


if __name__ == "__main__":
    main()
