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

class LearningModules(Resource):
    def get(self):
        # do a simple query to check if MySQL connection is open
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
        except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        query = ("select MID, Name from LM_Module")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))


#Get the Learning module description from a name
#TODO rename to Description
class Description(Resource):
    def get(self, Name):
        # do a simple query to check if MySQL connection is open
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
        except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
            
        query = ("select Description from LM_Module where Name=%s")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query, (Name,))
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))

#Get the introduction module based on the learning module name
class Intro(Resource):
      def get(self, Name):
          try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
          except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
            
          query = ("Select Header, Content from LM_Intro natural join LM_Module where Name=%s")
          cursor = cnx.cursor(dictionary=True)

          cursor.execute(query, (Name,))
          result = cursor.fetchall()
          cursor.close()
          return json.loads(json.dumps(result))


api.add_resource(LearningModules, "/modules")
api.add_resource(Description, "/modules/description/<string:Name>")
api.add_resource(Intro, "/modules/intro/<string:Name>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001")
