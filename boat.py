from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix = '/boats')

# post and get handler for boat
@bp.route('', methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST': #name, type, length, loads*
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing the required number"}),400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({
            'name': content['name'],
            'type': content['type'],
            'length': content['length']
            })
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = str(request.url) + "/" + str(new_boat.key.id)
        return (jsonify(new_boat), 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        q_limit = int(request.args.get('limit', '2'))
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
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return jsonify(output)
    else:
        return 'Method not recogonized'

# change or delete boat and it's attributes
@bp.route('/<id>', methods=['PUT','DELETE'])
def boats_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({
            "name": content["name"],
            "description": content["description"],
            "price": content["price"]
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
        client.delete(boat_key)
        return ('',204)


    else:
        return 'Method not recogonized'




# @app.route('/boats/<id>',strict_slashes = False, methods=['PUT','DELETE','GET','PATCH'])
# def boats_put_delete_get_patch(id):
#         if request.method == 'GET':
#             boat_key = client.key(constants.boats, int(id))
#             boat = client.get(key=boat_key)
#             if boat == None:
#                 return(jsonify({"Error": "No boat with this boat_id exists"}),404)
#             boat["id"] = boat.key.id
#             boat["self"] = str(request.url)
#             return jsonify(boat)
#
#         elif request.method == 'DELETE':
#             boat_key = client.key(constants.boats, int(id))
#             boat = client.get(key=boat_key)
#             if boat == None:
#                 return(jsonify({"Error": "No boat with this boat_id exists"}),404)
#             client.delete(boat_key)
#             return ('',204)


# @app.route('/boats',strict_slashes = False, methods=['POST','GET'])
# def boats_get_post():
#     if request.method == 'POST':
#         content = request.get_json(force=True)
#         if len(content) != 1:
#             return(jsonify({"Error": "The request object is missing the required number"}),400)
#         new_boat = datastore.entity.Entity(key=client.key(constants.boats))
#         new_boat.update({
#             "number": content["number"],
#             "current_boat": None
#         })
#         client.put(new_boat)
#         new_boat["id"] = new_boat.key.id
#         new_boat["self"] = str(request.url) + "/" + str(new_boat.key.id)
#         return (jsonify(new_boat), 201)
#
#     elif request.method == "GET":
#         query = client.query(kind=constants.boats)
#         results = list(query.fetch())
#         for e in results:
#             e["id"] = e.key.id
#             e["self"] = str(request.url) + "/" + str(e.key.id)
#         return jsonify(results)
#
#     else:
#         return 'Method not recogonized'
#
#
#
# @app.route('/boats/<boat_id>/<boat_id>',strict_slashes = False, methods=['PUT', 'DELETE'])
# def boat_put(boat_id, boat_id):
#     if request.method == "PUT":
#         #get boat
#         boat_key = client.key(constants.boats, int(boat_id))
#         boat = client.get(key=boat_key)
#         #get boat
#         boat_key = client.key(constants.boats, int(boat_id))
#         boat = client.get(key=boat_key)
#
#
#         if boat == None or boat == None:
#             return (jsonify({"Error": "The specified boat and/or boat does not exist"}),404)
#
#         if boat["current_boat"] != None:
#             return (jsonify({"Error": "The boat is not empty"}),403)
#         else:
#             boat.update({
#                 "current_boat": int(boat_id)
#             })
#             client.put(boat)
#             return('',204)
#
#     elif request.method == "DELETE":
#         boat_key = client.key(constants.boats, int(boat_id))
#         boat = client.get(key=boat_key)
#         #get boat
#         boat_key = client.key(constants.boats, int(boat_id))
#         boat = client.get(key=boat_key)
#
#
#         if boat == None or boat == None:
#             return (jsonify({"Error": "No boat with this boat_id is at the boat with this boat_id"}),404)
#
#         if boat["current_boat"] != int(boat_id):
#             return (jsonify({"Error": "No boat with this boat_id is at the boat with this boat_id"}),404)
#
#         boat.update({
#             "current_boat": None
#         })
#         client.put(boat)
#         return('', 204)
#
#
