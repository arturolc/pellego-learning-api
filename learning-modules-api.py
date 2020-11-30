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
        query = "select * from Modules"
        return {"data":"test"}

class Quiz(Resource):
    def get(self, quiz_id):
        query = "select 
api.add_resource(LearningModules, "/modules")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
