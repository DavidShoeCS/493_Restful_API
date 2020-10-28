from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix = '/loads')

#post and get handler for loads
@bp.route('', strict_slashes = False, methods=['POST','GET'])
def loads_get_post():
    if request.method == 'POST':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        new_load = datastore.entity.Entity(key=client.key(constants.loads))
        new_load.update({
            "weight": content["weight"],
            "content": content["content"],
            "delivery_date": content["delivery_date"],
            "carrier": None
            })
        client.put(new_load)
        new_load["id"] = new_load.key.id
        new_load["self"] = str(request.url) + "/" + str(new_load.key.id)
        return (new_load, 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.loads)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        g_iterator = query.fetch(limit= q_limit, offset=q_offset)
        pages = g_iterator.pages
        results = list(next(pages))
        if g_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.url) + "/" + str(e.key.id)
            if e['carrier']:
                e['carrier']['self'] = request.url_root + 'boats/' + str(e['carrier']['id'])
        output = {"loads": results}
        if next_url:
            output["next"] = next_url
        return jsonify(output)


@bp.route('/<id>', strict_slashes = False, methods=['PUT','DELETE', 'GET', 'PATCH'])
def loads_put_delete(id):
    if request.method == 'PUT' or request.method == 'PATCH':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        load.update({
            "weight": content["weight"],
            "content": content["content"],
            "delivery_date": content["delivery_date"]
            })
        client.put(load)
        load["id"] = int(load.key.id)
        load["self"] = str(request.url)
        return (jsonify(load),200)

    elif request.method == 'GET':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load == None:
            return(jsonify({"Error": "No load with this load_id exists"}),404)
        load["id"] = load.key.id
        load["self"] = str(request.url)
        if load['carrier']:
            load['carrier']['self'] = request.url_root + 'boats/' + str(load['carrier']['id'])
        return jsonify(load)


    #Will need to fix replacing slip_query with a boat--------------------------
    elif request.method == 'DELETE':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load == None:
            return(jsonify({"Error": "No load with this load_id exists"}),404)

        if load['carrier'] != None:
            boat_key = client.key(constants.boats, int(load['carrier']['id']))
            boat = client.get(key=boat_key)

            boat['loads'].remove({
                'id': load.key.id
            })

            load_list = boat['loads']

            client.put(boat)
            client.delete(load_key)
            return('', 204)
        client.delete(load_key)
        return('', 200)
    else:
        return('method not recognized', 405)
