from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix = '/boats')

# post and get handler for boat
@bp.route('', strict_slashes = False, methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST': #name, type, length, loads*
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({
            'name': content['name'],
            'type': content['type'],
            'length': content['length'],
            "loads": None
            })
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = str(request.url) + "/" + str(new_boat.key.id)
        return (jsonify(new_boat), 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit= q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.url) + "/" + str(e.key.id)
            if e['loads']:
                for load in e['loads']:
                    load['self'] = request.url_root + 'loads/' + str(load['id'])
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return jsonify(output)
    else:
        return 'Method not recogonized'

# change or delete boat and it's attributes
@bp.route('/<id>', strict_slashes = False, methods=['PUT','DELETE', 'GET'])
def boats_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({
            "name": content["name"],
            "length": content["length"],
            "type": content["type"]
            })
        client.put(boat)
        boat["id"] = boat.key.id
        boat["self"] = str(request.url)
        return (jsonify(boat),200)

    # Need to delete the relationships of the loads from this boat
    elif request.method == 'DELETE':

        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)

        if boat == None:
            return(jsonify({"Error": "No boat with this boat_id exists"}),404)

        query = client.query(kind=constants.loads)
        results = query.fetch()


        for e in results:
            if e['carrier']['id'] == boat.key.id:
                e.update({
                    'carrier': None
                })
                client.put(e)

        client.delete(boat_key)
        return ('',204)

    elif request.method == "GET":
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat == None:
            return(jsonify({"Error": "No boat with this boat_id exists"}),404)
        boat["id"] = boat.key.id
        boat["self"] = str(request.url)
        if boat['loads']:
            for load in boat['loads']:
                load['self'] = request.url_root + 'loads/' + str(load['id'])
        return jsonify(boat)

    else:
        return 'Method not recogonized'

@bp.route('/<id>/loads', strict_slashes = False, methods=['GET'])
def get_bid_loads(id):
    boat_key = client.key("boats", int(id))
    boat = client.get(key=boat_key)
    if boat == None:
        return (jsonify({"Error": "No boat with this boat_id exists"}), 404)
    load_list  = []
    if len(boat["loads"]) > 0:
        for load in boat['loads']:
            load_key = client.key("loads", int(load['id']))
            load_obj = client.get(key=load_key)
            load_obj["id"] = load_obj.key.id
            load_obj["self"] = request.url_root + "loads/" + str(load_obj.key.id)
            load_obj["carrier"]["self"] = request.url_root + "boats/" + str(load_obj["carrier"]["id"])
            load_list.append(load_obj)
        return (jsonify(load_list), 200)
    else:
        return (json.dumps([]), 204)

@bp.route('/<boat_id>/loads/<load_id>', strict_slashes = False, methods=['PUT','DELETE'])
def add_delete_boatload(boat_id,load_id):
    if request.method == 'PUT':
        #get boat
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        #get load
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)

        if boat == None and load == None:
            return (jsonify({"Error": "Neither boat, nor load specified exists"}),404)

        if boat == None:
            return (jsonify({"Error": "The specified boat does not exist"}),404)
        if load == None:
            return (jsonify({"Error": "The specified load does not exist"}),404)

        if boat['loads'] == None:
            loads_list = []
            loads_list.append(
                {
                    "id": load.key.id,
                })
            boat.update({'loads': loads_list})
        else:
            loads_list = boat['loads']

            loads_list.append(
                {
                    "id": load.key.id,
                })

            boat.update({'loads': loads_list})

        if load['carrier'] == None:
            load.update({
            'carrier':
                {
                    "id": boat.key.id,
                    "name": str(boat['name'])
                }
            })
        else:
            return(jsonify({'Error': 'Load is already on a boat'}), 403)

        boat_res = {
                    'id': boat.key.id,
                    'name': boat['name'],
                    'type': boat['type'],
                    'length': boat['length'],
                    'loads': boat['loads'],
                    'self': request.url + str(boat.key.id)
                    }

        client.put(boat)
        client.put(load)
        return(jsonify(boat_res),201)


# Deleting a boat must unload all cargo
    if request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)


        if boat == None or load == None:
            return(jsonify({'Error': 'No Boat/load with given ID exists'}), 404)

        if load['carrier'] == None or load['carrier']['id'] != boat.key.id:
            return(jsonify({'Error': 'There is no load associated with this boat'}), 404)

        boat['loads'].remove({
            'id': load.key.id
        })

        loads_list = boat['loads']

        if not loads_list:
            loads_list = None
            boat.update({'loads': loads_list})
        else:
            boat.update({'loads': loads_list})

        load.update({
            'carrier': None
        })
        client.put(boat)
        client.put(load)

        boat_res = {
            'id': boat['name'],
            'type': boat['type'],
            'length': boat['length'],
            'loads': boat['loads'],
            'self': request.url + str(boat.key.id)
            }

        return('',204)
