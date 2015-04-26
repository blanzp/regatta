__author__ = 'Paul'

import time

import model


def delete_tables(conn):
    model.OrganizationCollection(conn).delete()
    model.AthleteCollection(conn).delete()
    model.EventCollection(conn).delete()
    model.RaceCollection(conn).delete()
    model.StageCollection(conn).delete()
    model.CrewCollection(conn).delete()
    model.RacingCrewCollection(conn).delete()
    model.UserCollection(conn).delete()
    model.RegattaCollection(conn).delete()
    model.Audit(conn).delete()


def create_tables(conn):
    tables = get_list(conn)

    if 'organizations' not in tables:
        model.OrganizationCollection(conn).create()
        time.sleep(10)

    if 'athletes' not in tables:
        model.AthleteCollection(conn).create()
        time.sleep(10)

    if 'events' not in tables:
        model.EventCollection(conn).create()
        time.sleep(10)

    if 'racing_crew' not in tables:
        model.RaceCollection(conn).create()
        time.sleep(10)

    if 'stage' not in tables:
        model.StageCollection(conn).create()
        time.sleep(10)

    if 'crew' not in tables:
        model.CrewCollection(conn).create()
        time.sleep(10)

    if 'crew' not in tables:
        model.RacingCrewCollection(conn).create()
        time.sleep(10)

    if 'users' not in tables:
        model.UserCollection(conn).create()
        time.sleep(10)

    if 'regatta' not in tables:
        model.RegattaCollection(conn).create()
        time.sleep(10)

    if 'audit' not in tables:
        model.Audit(conn).create()

def get_list(conn):
    table = conn.conn.list_tables()
    return table['TableNames']


def main():
    import os
    conn = model.DBConnection(os.environ.get("ENV"))

    #delete_tables(conn)
    #time.sleep(10)
    create_tables(conn)


if __name__ == "__main__":
    main()