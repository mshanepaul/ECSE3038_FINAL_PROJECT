'''
    Author: Shane Paul Mckennon
    Description: ECSE3038 Final Project
    Usage: python main.py
'''

from marshmallow import Schema, fields, ValidationError
from flask import Flask, Response, stream_with_context
from gevent import monkey; monkey.patch_all()
from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
from flask_pymongo import PyMongo
from bson.json_util import dumps
from datetime import datetime
from json import load, loads
from flask_cors import CORS
import pandas as pd
import json
import time

username = pd.read_csv("db_credentials.csv").columns[0]
password = pd.read_csv("db_credentials.csv").columns[1]
mongo_uri = "mongodb+srv://Shane_:mckennon55@cluster0.dv306.mongodb.net/Database1?retryWrites=true&w=majority".format(username, password)

app = Flask(__name__)
app.config["SECRET_KEY"] = "superSecretKey"
app.config["MONGO_URI"] = mongo_uri
cors = CORS(app)
mongo = PyMongo(app)

# Initialize some of the record data
pos = 100
id = "aa:aa:aa:aa:aa"

class RecordSchema(Schema):
    patient_id = fields.String(required=True)
    position = fields.Integer(required=True)
    temperature = fields.Integer(required=True)
    last_updated = fields.String(required=True)

class PatientSchema(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    age = fields.Integer(required=True)
    patient_id = fields.String(required=True)

@app.route("/api/patient", methods=["GET"])
def get_all_patient_data():
    '''
        This route returns all of the patient objects stored in the 
        database
    '''
    print("MADE GET REQUEST")
    patients = mongo.db.patients.find()
    return jsonify(loads(dumps(patients))) 

@app.route("/api/patient/<id>", methods=["GET"])
def get_single_patient_data(id):
    '''
        This route returns a single patient object that is stored in 
        the database
    '''
    patient = mongo.db.patients.find_one({"patient_id": id})
    return jsonify(loads(dumps(patient)))

@app.route("/api/patient", methods=["POST"])
def post_patient_data():
    '''
        This route handles the POST requests made to the server by the 
        frontend 
    '''
    print("POST REQUEST MADE")
    try:
        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")

        first_name = request.json["first_name"]
        last_name = request.json["last_name"]
        age = request.json["age"]
        patient_id = request.json["patient_id"]

        jsonBody = {
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "patient_id": patient_id
        }

        print(jsonBody)

        patient_data = PatientSchema().load(jsonBody)
        mongo.db.patients.insert_one(patient_data)

        return{
            "success": True,
            "message": "Data saved successfully",
            "date": dt
        }
    except ValidationError as e:
        return e.messages, 400

@app.route("/api/patient/<id>", methods=["PATCH"])
def patch_patient_data(id):
    '''
        This route handles the PATCH requests made to the server by the 
        frontend 
    '''
    mongo.db.patients.update_one({"patient_id": id}, {"$set": request.json})
    patient = mongo.db.patients.find_one({"patient_id": id})

    return loads(dumps(patient))

@app.route("/api/patient/<id>", methods=["DELETE"])
def delete_patient_data(id):
    '''
        This route handles the DELETE requests made to the server by the 
        frontend 
    '''
    result = mongo.db.patients.delete_one({"patient_id": id})

    if result.deleted_count == 1:
        return {
            "success": True,
        }
    else:
        return{
            "success": False,
        }, 400

@app.route("/api/record/graph/<id>", methods=["GET"])
def get_graph_data(id):
    '''
        This route returns all of the data for a specific patient that was generated
        within the past 30 minutes so that the graph of the individual patients data 
        can be populated
    ''' 
    def str_to_time(time_data):
        hr = int(time_data[11:13])
        min = int(time_data[14:16])
        return (60*hr + min)        

    graph_data = []

    now = datetime.now()
    dt = now.strftime("%d/%m/%Y %H:%M:%S")
    curr_time = str_to_time(dt)
    print(curr_time)

    record = mongo.db.records.find({"patient_id":id})
    record_data = loads(dumps(record))
    for info in record_data:
        record_time = str_to_time(info["last_updated"])
        print(record_time)
        
        if ((curr_time - record_time) <= 30):
            graph_data.append(info)

    print(graph_data)
    return jsonify(loads(json.dumps(graph_data)))

@app.route("/api/record/<id>", methods=["GET"])
def get_single_record_data(id):
    '''
        This route handles the individual GET requests made to the server by the 
        frontend. It gets the record data so that the position of a patient can
        be determined and displayed in the frontend
    '''
    record = mongo.db.records.find_one({"patient_id":id})
    print(record)
    return jsonify(loads(dumps(record)))

@app.route("/listen")
def listen():
    '''
        This route uses Server Sent Events to send data to the frontend
        of the application every time a POST is made by the embedded 
        circuit. 
    '''
    def respond_to_client():
        while True:
            global pos
            global id
            counter = 100
            _data = json.dumps({"position": str(pos), "id": id})
            yield f"id: 1\ndata: {_data}\nevent: online\n\n"
            time.sleep(3)
    return Response(respond_to_client(), mimetype='text/event-stream')

@app.route("/api/record", methods=["POST"])
def post_record_data():
    '''
        This route handles the POST requests made to the server by the 
        embedded client
    '''
    global pos
    global id
    try:
        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")

        patient_id = request.json["patient_id"]
        position = request.json["position"]
        temperature = request.json["temperature"]
        last_updated = dt

        pos = position
        id = patient_id

        jsonBody = {
            "patient_id": patient_id,
            "position": position,
            "temperature": temperature,
            "last_updated": last_updated
        }

        record_data = RecordSchema().load(jsonBody)
        mongo.db.records.insert_one(record_data)

        print(jsonBody)

        return {
            "success": True,
            "msg": "data saved successfully",
            "date": dt
        }
    except ValidationError as e:
        return e.messages, 400

if __name__ == "__main__":
    http_server = WSGIServer(("192.168.1.5", 5000), app)
    http_server.serve_forever()
