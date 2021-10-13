from flask import Flask, jsonify, request
from pymongo import MongoClient
import pymongo
from datetime import datetime
app = Flask(__name__)

def get_db():
    client  = MongoClient(host='users_mongodb',
                          port=27017,
                          username='admin',
                          password='1kr45!5hrtl',
                          authSource='admin')
    db = client.users_db
    return db


@app.route('/api/v1/user/<id>', methods=['GET'])
def get_user(id):
    try:
        id = int(id)
        db = get_db()
        _users = db.users_db.find({"user_id":id})
        response = {"status": "OK",
                    "user_id":_users[0]["user_id"],
                    "companyID": _users[0]["companyID"],
                    "name": _users[0]["name"],
                    "email": _users[0]["email"],
                    "creation_date": _users[0]["creation_date"]}
        return jsonify(response), 200, {"ContentType": "application/json"}
    except IndexError:
        error = f"There is no user with user_id: {id} in db"
        return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
    except  pymongo.errors.ConnectionFailure as e:
        error = "Could not connect to server: {e}"
        return jsonify({"status": "ERROR", "error": error} ), 500, {"ContentType": "application/json"}


@app.route('/api/v1/user/<id>', methods=['DELETE'])
def delete_user(id):
    try:
        id = int(id)
        db = get_db()
        _users = db.users_db.delete_one({"user_id":id})
        if _users.deleted_count > 0:
            return jsonify({"status": "OK"}), 200, {"ContentType": "application/json"}
        else:
            error = f"There is no user with user_id: {id} in db"
            return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
    except  pymongo.errors.ConnectionFailure as e:
        error = "Could not connect to server: {e}"
        return jsonify({"status": "ERROR", "error": error} ), 500, {"ContentType": "application/json"}


@app.route('/api/v1/user/all', methods=['GET'])
def get_all_users():
    try:
        db = get_db()
        _users = db.users_db.find()
        users = []
        for user in _users:
            users.append({"user_id": user["user_id"],
                          "companyID": user["companyID"],
                          "name": user["name"],
                          "email": user["email"],
                          "creation_date": user["creation_date"]})      
        response = {"status": "OK", "users": users}
        return jsonify(response), 200, {"ContentType": "application/json"}   
    except IndexError:
        error = f"There is no user with user_id: {id} in db"
        return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
    except  pymongo.errors.ConnectionFailure as e:
        error = "Could not connect to server: {e}"
        return jsonify({"status": "ERROR", "error": error} ), 500, {"ContentType": "application/json"}
"""
input request:
{
    "user":{
        "user_id": number,
        "companyID": number,
        "name": string,
        "email": string
    }
}
"""

@app.route('/api/v1/user/<id>', methods=['PUT'])
def updated_user(id):
    try:
        id = int(id)
        db = get_db()
        input_request = request.get_json(force=True)        
        if not isinstance(input_request["user"], dict) or input_request["user"] == {}:
            error = "There is invalid update parameters in parameter 'user'"
            return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
        updated_data = {"$set": input_request["user"]}
        _users = db.users_db.update_one({"user_id":id},updated_data)
        if _users.modified_count > 0:
            return jsonify({"status": "OK"}), 200, {"ContentType": "application/json"}
        else:
            error = f"There is no user with user_id: {id} in db"
            return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
    except KeyError as e:
        error = f"invalid request. There is no parameter {e} in request "
        return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
    except  pymongo.errors.ConnectionFailure as e:
        error = "Could not connect to server: {e}"
        return jsonify({"status": "ERROR", "error": error} ), 500, {"ContentType": "application/json"}


"""
input request:
{
    "user":{
        "user_id": number,
        "companyID": number,
        "name": string,
        "email": string
    }
}
user_id - primary key
"""    
@app.route('/api/v1/user', methods=['POST'])
def create_user():
    input_request = request.get_json(force=True)
    try:
        user = input_request["user"]
        keys = ("user_id","companyID","name","email")
        for key in keys:
            user[key]
        db = get_db() 
        _user = list(db.users_db.find({"user_id": user["user_id"]}))
        if len(_user) > 0:
            error = f"invalid request. duplicate user with user_id {user['user_id']}"
            return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
        now = datetime.now() 
        user["creation_date"] = now.strftime("%d/%m/%Y %H:%M:%S")
        db.users_db.insert_one(user)  
        user["status"] ="OK"
        response = {"status":"OK"}
        return jsonify(response), 200, {"ContentType": "application/json"}     
    except KeyError as e:
        if e == "user":
            error = "invalid request. There is no parameter user in request "
        else:
            error = f"invalid request. There is no parameter {e} in parameter 'user'"
        return jsonify({"status": "ERROR", "error": error} ), 400, {"ContentType": "application/json"}
    except  pymongo.errors.ConnectionFailure as e:
        error = "Could not connect to server: {e}"
        return jsonify({"status": "ERROR", "error": error} ), 500, {"ContentType": "application/json"}




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    
