"""
Arturo Lara-Coronado

Learning Modules API
"""
#!/usr/bin/python3
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import mysql.connector
import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode


app = Flask(__name__)
api = Api(app)
publickKeyUrl = "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_AdDJsuC6f/.well-known/jwks.json"

region = 'us-west-2'
userpool_id = 'us-west-2_AdDJsuC6f'
app_client_id = 'o4uoksbrsfa78eo644tpf20um'
keys_url = 'https://cognito-idp.{0}.amazonaws.com/{1}/.well-known/jwks.json'.format(region, userpool_id)


# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def verifyToken(token):
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims

parser = reqparse.RequestParser()


        


class LearningModules(Resource):
    def post(self):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])        
        #if res is False:
        #    return "401 Unauthorized", 401
        res = request.get_json(force=True) 
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
        
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select MID, Name, Subheader, Icon from LM_Module"))
        result = cursor.fetchall()
        cursor.close()
        
        for item in result:
            cursor = cnx.cursor()
            cursor.execute(("select count(*) from ProgressCompleted where UID = %s and SMID in (select SMID from LM_Submodule where MID = %s)"), (userID, int(item['MID'])))
            item["completed"] =  int(cursor.fetchall()[0][0])
            cursor.close()

            cursor = cnx.cursor()
            cursor.execute(("select count(*) from LM_Submodule where MID = %s"), (int(item['MID']),))
            item["totalSubmodules"] = int(cursor.fetchall()[0][0])
            cursor.close()
        
        cnx.close()
        return json.loads(json.dumps(result))

class AllContent(Resource):
    def post(self):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])        
        #if res is False:
        #    return "401 Unathorized", 401
        res = request.get_json(force=True) 
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
        
        ret = {}
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select * from LM_Module"))
        ret["modules"] = cursor.fetchall()
        cursor.close()
        
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select * from LM_Intro"))
        ret["intros"] = cursor.fetchall()
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select * from LM_Submodule"))
        ret["submodule"] = cursor.fetchall()
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select * from LM_Quiz"))
        ret["quizzes"] = cursor.fetchall()
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select * from Questions"))
        ret["questions"] = cursor.fetchall()
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        cursor.execute("select * from Answers")
        ret["answers"] = cursor.fetchall()
        cursor.close()

        cnx.close()
        return json.loads(json.dumps(ret))


class Content(Resource):
    def post(self, module_id):
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
            
        query = ("select MID, Name, Description from LM_Module where MID = %s")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query, (module_id,))
        result = cursor.fetchall()
        cursor.close()

        query = ("select Name, Subheader from LM_Submodule where MID = %s")
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (module_id,))
        result[0]["Submodules"] = cursor.fetchall()
        cursor.close()
        
        cnx.close()
        return json.loads(json.dumps(result))

class Submodules(Resource):
    def post(self, module_id):
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        query = ("select Header, Content from LM_Intro where MID = %s")
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (module_id,))
        introResult = cursor.fetchall()
        cursor.close();

        query = ("select Name, Subheader, Text from LM_Submodule where MID = %s")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query, (module_id,))
        result = cursor.fetchall()
        result[0]["Content"] = introResult;
        cursor.close()

        cnx.close()
        return json.loads(json.dumps(result))

class Quizzes(Resource):
    def post(self, module_id, submodule_id, quiz_id):
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        query = ("select QUID, Question from Questions where SMID = %s")
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(query, (submodule_id, ))
        result = cursor.fetchall()
        cursor.close()

        for item in range(0,4):
            query = ("select QUID, Answer, Correct from Answers where SMID = %s and QUID = %s")
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(query, (submodule_id, item + quiz_id, ))
            result[item]["Answers"] = cursor.fetchall()
            cursor.close()

        cnx.close()
        return json.loads(json.dumps(result))


api.add_resource(LearningModules, "/modules")
api.add_resource(AllContent, "/modules/allcontent/")
api.add_resource(Content, "/modules/<int:module_id>/content")
api.add_resource(Submodules, "/modules/<int:module_id>/submodules")
api.add_resource(Quizzes, "/modules/<int:module_id>/submodules/<int:submodule_id>/quizzes/<int:quiz_id>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
