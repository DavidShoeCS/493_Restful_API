from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix = '/loads')

#post and get handler for loads
@bp.route('', methods=['POST','GET'])
def loads_get_post():
    if request.method == 'POST':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        new_load = datastore.entity.Entity(key=client.key(constants.loads))
        new_load.update({
            "weight": content["weight"],
            "content": content["content"],
            "delivery_date": content["delivery_date"]
            })
        client.put(new_load)
        return str(new_load.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.loads)
        q_limit = int(request.args.get('limit', '2'))
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
            e["self"] = str(request.url) + "/" + str(new_load.key.id)
        output = {"loads": results}
        if next_url:
            output["next"] = next_url
        return jsonify(output)


@bp.route('/<id>', methods=['PUT','DELETE', 'GET', 'PATCH'])
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
        load["id"] = load.key.id
        load["self"] = str(request.url)
        return (jsonify(load),200)

    elif request.method == 'GET':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load == None:
            return(jsonify({"Error": "No load with this load_id exists"}),404)
        load["id"] = load.key.id
        load["self"] = str(request.url)
        return jsonify(load)


    #Will need to fix replacing slip_query with a boat--------------------------
    elif request.method == 'DELETE':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        if load == None:
            return(jsonify({"Error": "No load with this load_id exists"}),404)

        boat_query = client.query(kind=constants.boats)
        boat_query.add_filter('carrier', '=', int(id))
        results = list(boat_query.fetch())
        if len(results) > 0:
            results[0]["carrier"] = None
        client.put(results[0])

        client.delete(load_key)
        return ('',204)

    else:
        return 'Method not recogonized'



# @app.route('/loads/<id>',strict_slashes = False, methods=['PUT','DELETE','GET','PATCH'])
# def loads_put_delete_get_patch(id):
#     if request.method == 'PUT' or request.method == 'PATCH':
#         content = request.get_json(force=True)
#         if len(content) != 3:
#             return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
#         load_key = client.key(constants.loads, int(id))
#         load = client.get(key=load_key)
#         if load == None:
#             return(jsonify({"Error": "No load with this load_id exists"}),404)
#         load.update({
#             "name": content["name"],
#             "type": content["type"],
#             "length": content["length"]
#             })
#         client.put(load)
#         load["id"] = load.key.id
#         load["self"] = str(request.url)
#         return (jsonify(load),200)
#
#
#     elif request.method == 'DELETE':
#         load_key = client.key(constants.loads, int(id))
#         load = client.get(key=load_key)
#         if load == None:
#             return(jsonify({"Error": "No load with this load_id exists"}),404)
#
#         slip_query = client.query(kind=constants.slips)
#         slip_query.add_filter('current_load', '=', int(id))
#         results = list(slip_query.fetch())
#         if len(results) > 0:
#             results[0]["current_load"] = None
#             client.put(results[0])
#
#
#
#         client.delete(load_key)
#         return ('',204)
#
#     elif request.method == 'GET':
#         load_key = client.key(constants.loads, int(id))
#         load = client.get(key=load_key)
#         if load == None:
#             return(jsonify({"Error": "No load with this load_id exists"}),404)
#         load["id"] = load.key.id
#         load["self"] = str(request.url)
#         return jsonify(load)
#
#     else:
#         return 'Method not recogonized'


# @app.route('/',strict_slashes = False, methods=['POST','GET'])
# def loads_get_post():
#     if request.method == 'POST':
#         content = request.get_json(force=True)
#         if len(content) != 3:
#             return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
#         new_load = datastore.entity.Entity(key=client.key(constants.loads))
#         new_load.update({
#             "name": content["name"],
#             "type": content["type"],
#             "length": content["length"]
#             })
#         client.put(new_load)
#         new_load["id"] = new_load.key.id
#         new_load["self"] = str(request.url) + "/" + str(new_load.key.id)
#         return (jsonify(new_load),201)
#
#     elif request.method == 'GET':
#         query = client.query(kind=constants.loads)
#         results = list(query.fetch())
#         for e in results:
#             e["id"] = e.key.id
#             e["self"] = str(request.url) + "/" + str(e.key.id)
#         return jsonify(results)
#     else:
#         return 'Method not recogonized'
