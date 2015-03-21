__author__ = 'Paul'

from flask import Flask, request, abort, url_for
import pandas as pd
import json

app = Flask(__name__, static_folder='static')


class Event(object):
    def __init__(self, data_dict):
        self.__dict__ = data_dict


class Boat(object):
    def __init__(self, data_dict):
        self.__dict__ = data_dict


class Team(object):
    def __init__(self, data_dict):
        self.__dict__ = data_dict


class Transaction(object):
    def __init__(self, data_dict):
        self.__dict__ = data_dict


class Entrant(object):
    def __init__(self, data_dict):
        self.__dict__ = data_dict


global events, entrants, boats, teams, transactions, finish_times


@app.route('/')
def index():
    # send_static_file will guess the correct MIME type
    return app.send_static_file('html/index.html')


@app.route('/api/<data_type>')
def get_data(data_type):
    if data_type == 'events':
        return json.dumps(events, default=lambda o: o.__dict__)
    elif data_type == 'teams':
        return json.dumps(teams, default=lambda o: o.__dict__)
    elif data_type == 'boats':
        return json.dumps(boats, default=lambda o: o.__dict__)
    else:
        return


@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


EVENT_LANE_COUNT = 14

@app.route('/api/assignlanes', methods=['GET'])
def set_lanes():
    assign_lanes(EVENT_LANE_COUNT, events, boats)
    return 'OK'

@app.route('/api/start', methods=['POST'])
def finish_race():
    global finish_times
    finish_times.append(json.loads(request.data))
    return "OK", 200

@app.route('/api/start/times', methods=['GET'])
def get_finish_times():
    global finish_times
    return json.dumps(finish_times), 200

@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    first = request.json.get('first')
    last = request.json.get('last')

    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}


def assign_lanes(lane_count, events, boats):
    for event in events:
        entries = filter_list_event(boats, event.Event)
        assignments = middle_out(lane_count, len(entries))
        #print "Assigning for event",event.Event, assignments
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



def create_objects_from_panda(panda_table, obj_class):
    obj_list = []
    for item in panda_table.iterrows():
        item = item[1]
        data_dict = json.loads(item.to_json())
        obj_list.append(obj_class(data_dict))
    return obj_list


def main():
    global events, entrants, boats, teams, transactions, finish_times
    finish_times = []
    data_file = "c:\\users\\paul\\Downloads\\RCtoRMExport.xls"
    events = create_objects_from_panda(pd.read_excel(data_file, sheetname="Events"), Event)
    entrants = create_objects_from_panda(pd.read_excel(data_file, sheetname="Entrants"), Entrant)
    boats = create_objects_from_panda(pd.read_excel(data_file, sheetname="Boats"), Boat)
    teams = create_objects_from_panda(pd.read_excel(data_file, sheetname="Teams"), Team)
    transactions = create_objects_from_panda(pd.read_excel(data_file, sheetname="Transactions"), Transaction)

    app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":
    main()
