from google.cloud import datastore
from flask import Flask, request, jsonify
import json
import constants

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"\

@app.route('/slips',strict_slashes = False, methods=['POST','GET'])
def slips_get_post():
    if request.method == 'POST':
        content = request.get_json(force=True)
        if len(content) != 1:
            return(jsonify({"Error": "The request object is missing the required number"}),400)
        new_slip = datastore.entity.Entity(key=client.key(constants.slips))
        new_slip.update({
            "number": content["number"],
            "current_boat": None
        })
        client.put(new_slip)
        new_slip["id"] = new_slip.key.id
        new_slip["self"] = str(request.url) + "/" + str(new_slip.key.id)
        return (jsonify(new_slip), 201)

    elif request.method == "GET":
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.url) + "/" + str(e.key.id)
        return jsonify(results)

    else:
        return 'Method not recogonized'

@app.route('/slips/<slip_id>/<boat_id>',strict_slashes = False, methods=['PUT', 'DELETE'])
def slip_put(slip_id, boat_id):
    if request.method == "PUT":
        #get boat
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        #get slip
        slip_key = client.key(constants.slips, int(slip_id))
        slip = client.get(key=slip_key)


        if slip == None or boat == None:
            return (jsonify({"Error": "The specified boat and/or slip does not exist"}),404)

        if slip["current_boat"] != None:
            return (jsonify({"Error": "The slip is not empty"}),403)
        else:
            slip.update({
                "current_boat": int(boat_id)
            })
            client.put(slip)
            return('',204)

    elif request.method == "DELETE":
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        #get slip
        slip_key = client.key(constants.slips, int(slip_id))
        slip = client.get(key=slip_key)


        if slip == None or boat == None:
            return (jsonify({"Error": "No boat with this boat_id is at the slip with this slip_id"}),404)

        if slip["current_boat"] != int(boat_id):
            return (jsonify({"Error": "No boat with this boat_id is at the slip with this slip_id"}),404)

        slip.update({
            "current_boat": None
        })
        client.put(slip)
        return('', 204)


@app.route('/slips/<id>',strict_slashes = False, methods=['PUT','DELETE','GET','PATCH'])
def slips_put_delete_get_patch(id):
        if request.method == 'GET':
            slip_key = client.key(constants.slips, int(id))
            slip = client.get(key=slip_key)
            if slip == None:
                return(jsonify({"Error": "No slip with this slip_id exists"}),404)
            slip["id"] = slip.key.id
            slip["self"] = str(request.url)
            return jsonify(slip)

        elif request.method == 'DELETE':
            slip_key = client.key(constants.slips, int(id))
            slip = client.get(key=slip_key)
            if slip == None:
                return(jsonify({"Error": "No slip with this slip_id exists"}),404)
            client.delete(slip_key)
            return ('',204)



@app.route('/boats/<id>',strict_slashes = False, methods=['PUT','DELETE','GET','PATCH'])
def boats_put_delete_get_patch(id):
    if request.method == 'PUT' or request.method == 'PATCH':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat == None:
            return(jsonify({"Error": "No boat with this boat_id exists"}),404)
        boat.update({
            "name": content["name"],
            "type": content["type"],
            "length": content["length"]
            })
        client.put(boat)
        boat["id"] = boat.key.id
        boat["self"] = str(request.url)
        return (jsonify(boat),200)


    elif request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat == None:
            return(jsonify({"Error": "No boat with this boat_id exists"}),404)

        slip_query = client.query(kind=constants.slips)
        slip_query.add_filter('current_boat', '=', int(id))
        results = list(slip_query.fetch())
        if len(results) > 0:
            results[0]["current_boat"] = None
            client.put(results[0])



        client.delete(boat_key)
        return ('',204)

    elif request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat == None:
            return(jsonify({"Error": "No boat with this boat_id exists"}),404)
        boat["id"] = boat.key.id
        boat["self"] = str(request.url)
        return jsonify(boat)

    else:
        return 'Method not recogonized'

@app.route('/boats',strict_slashes = False, methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json(force=True)
        if len(content) != 3:
            return(jsonify({"Error": "The request object is missing at least one of the required attributes"}),400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({
            "name": content["name"],
            "type": content["type"],
            "length": content["length"]
            })
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = str(request.url) + "/" + str(new_boat.key.id)
        return (jsonify(new_boat),201)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.url) + "/" + str(e.key.id)
        return jsonify(results)
    else:
        return 'Method not recogonized'




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
