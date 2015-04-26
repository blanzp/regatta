import xml.etree.ElementTree as ET
import pprint
from collections import defaultdict

import model


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update((k.replace('{http://www.omg.org/XMI}','_'), v if v != '' else None) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def get_by_id(item_list, id):
    return filter(lambda x: x['_id'] == id, item_list)


def force_race_list(events):
    new_events = []
    for event in events:
        print 'processing ', event['eventTitle']
        if 'stage' in event:
            if type(event['stage']) == dict:
                event['stage'] = [event['stage']]
            new_stages = []
            for stage in event['stage']:
                if type(stage['race']) == dict:
                    stage['race'] = [stage['race']]
                new_stages.append(stage)
            event['stage'] = new_stages
            new_events.append(event)
    return new_events


def enrich_events(events, organizations):
    for event in events:
        #print "processing", event['eventTitle']
        if 'crew' in event:
            for crew in event['crew']:
                team = get_by_id(organizations,crew['organization'])
                if len(team) == 0:
                    crew['organization'] = "No Team"
                else:
                    team = team[0]
                    crew['organization'] = {'abbreviatedName': team['abbreviatedName'], 'name': team['name']}
    return events


def get_items(elem):
    item_dict = dict()
    item_dict['_type'] = elem.tag
    for item in elem.items():
        item_dict[item[0]] = item[1]
    if '{http://www.omg.org/XMI}id' in item_dict:
        x = item_dict['{http://www.omg.org/XMI}id']
        del item_dict['{http://www.omg.org/XMI}id']
        item_dict['_id'] = x
    return item_dict


def insert_event(event, conn):
    model.EventCollection(conn).insert(event)
    print "Inserted Event:", event['eventTitle']


def insert_organization(organization, conn):
    model.OrganizationCollection(conn).insert(organization)
    print "Inserted Organization:", organization['name']

def load_rml_from_string(rml_data, conn):
    root = ET.fromstring(rml_data)
    return load_rml(root, conn)

def load_rml_from_file(filename, conn):
    tree = ET.parse(filename)
    root = tree.getroot()
    return load_rml(root, conn)

def load_rml(root, conn):
    events = map(lambda x: etree_to_dict(x)['event'], root.findall('event'))
    organizations = map(lambda x: etree_to_dict(x)['organization'], root.findall('organization'))

    events = enrich_events(events, organizations)
    events = force_race_list(events)
    map(lambda e: insert_event(e, conn), events)
    map(lambda e: insert_organization(e, conn), organizations)

    regatta = get_items(root)
    model.RegattaCollection(conn).insert(data=regatta)


def main():
    #tree = ET.parse('c:\\users\\paul\\downloads\\Long-Island-Junior-Rowing-Championships-2014-05-04.rml')
    tree = ET.parse('c:\\users\\paul\\downloads\\Long-Island-Frostbite-Regatta-2013-11-03-1.rml')


    root = tree.getroot()
    pp = pprint.PrettyPrinter(indent=4)
    conn = model.DBConnection("development")

    load_rml(root, conn)

if __name__ == "__main__":
    main()