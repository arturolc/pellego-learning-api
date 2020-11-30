"""
Arturo Lara-Coronado

Learning Modules API
"""

from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector

cnx = mysql.connector.connect(user='admin', password='capstone', host='127.0.0.1', database='pellego_database')
app = Flask(__name__)
api = Api(app)

class LearningModules(Resource):
    def get(self):
        query = "select MID, Name from LM_Module"
        return {"data":"test"}

class Content(Resource):
    def get(self, module_id):
        query = "select" 

api.add_resource(LearningModules, "/modules")
api.add_resource(Content, "/modules/content")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
