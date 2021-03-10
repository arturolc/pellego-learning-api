"""
Arturo Lara-Coronado

Learning Modules API
"""
#!/usr/bin/python3
from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector
import json

cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
app = Flask(__name__)
api = Api(app)
publickKeyUrl = "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_AdDJsuC6f/.well-known/jwks.json"


def reconnect():
    # do a simple query to check if MySQL connection is open
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("Select 1")
        cursor.fetchall()
        cursor.close()
    except:
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

class LearningModules(Resource):
    def get(self):
        reconnect()
        query = ("select MID, Name from LM_Module")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))

class Content(Resource):
    def get(self, module_id):
        reconnect()
            
        query = ("select MID, Name, Tutorial from LM_Module where MID = %s")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query, (module_id,))
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))


api.add_resource(LearningModules, "/modules")
api.add_resource(Content, "/modules/content/<int:module_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
