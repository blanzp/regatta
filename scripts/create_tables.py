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
    model.OrganizationCollection(conn).create()
    time.sleep(10)

    model.AthleteCollection(conn).create()
    time.sleep(10)

    model.EventCollection(conn).create()
    time.sleep(10)

    model.RaceCollection(conn).create()
    time.sleep(10)

    model.StageCollection(conn).create()
    time.sleep(10)

    model.CrewCollection(conn).create()
    time.sleep(10)

    model.RacingCrewCollection(conn).create()
    time.sleep(10)

    model.UserCollection(conn).create()
    time.sleep(10)

    model.RegattaCollection(conn).create()
    time.sleep(10)

    model.Audit(conn).create()




def main():
    conn = model.DBConnection("development")

    delete_tables(conn)
    time.sleep(10)
    create_tables(conn)


if "__name__" == "__main__":
    main()