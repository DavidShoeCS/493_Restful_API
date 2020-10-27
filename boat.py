



@app.route('/boats',strict_slashes = False, methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json(force=True)
        if len(content) != 1:
            return(jsonify({"Error": "The request object is missing the required number"}),400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({
            "number": content["number"],
            "current_boat": None
        })
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = str(request.url) + "/" + str(new_boat.key.id)
        return (jsonify(new_boat), 201)

    elif request.method == "GET":
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.url) + "/" + str(e.key.id)
        return jsonify(results)

    else:
        return 'Method not recogonized'



@app.route('/boats/<boat_id>/<boat_id>',strict_slashes = False, methods=['PUT', 'DELETE'])
def boat_put(boat_id, boat_id):
    if request.method == "PUT":
        #get boat
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        #get boat
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)


        if boat == None or boat == None:
            return (jsonify({"Error": "The specified boat and/or boat does not exist"}),404)

        if boat["current_boat"] != None:
            return (jsonify({"Error": "The boat is not empty"}),403)
        else:
            boat.update({
                "current_boat": int(boat_id)
            })
            client.put(boat)
            return('',204)

    elif request.method == "DELETE":
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        #get boat
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)


        if boat == None or boat == None:
            return (jsonify({"Error": "No boat with this boat_id is at the boat with this boat_id"}),404)

        if boat["current_boat"] != int(boat_id):
            return (jsonify({"Error": "No boat with this boat_id is at the boat with this boat_id"}),404)

        boat.update({
            "current_boat": None
        })
        client.put(boat)
        return('', 204)


@app.route('/boats/<id>',strict_slashes = False, methods=['PUT','DELETE','GET','PATCH'])
def boats_put_delete_get_patch(id):
        if request.method == 'GET':
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(key=boat_key)
            if boat == None:
                return(jsonify({"Error": "No boat with this boat_id exists"}),404)
            boat["id"] = boat.key.id
            boat["self"] = str(request.url)
            return jsonify(boat)

        elif request.method == 'DELETE':
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(key=boat_key)
            if boat == None:
                return(jsonify({"Error": "No boat with this boat_id exists"}),404)
            client.delete(boat_key)
            return ('',204)
