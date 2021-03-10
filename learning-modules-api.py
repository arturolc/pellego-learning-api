"""
Arturo Lara-Coronado

Learning Modules API
"""
#!/usr/bin/python3
from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector
import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

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

region = 'us-west-2:'
userpool_id = 'us-west-2_AdDJsuC6f'
app_client_id = '589drggbikvfufkiogvrjruvgb'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def verifyToken():
    token = "eyJraWQiOiJKMmE1WExBSFdwaVFZbEZ6cEF5TVFcL0dUTXNmdWRxM1g1Y2U0cGwxeEttST0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJlNzYzOTZiMS03MTNjLTQ3N2YtYTExNi1lMTFmNjM5NTFhYjkiLCJhdWQiOiJvNHVva3NicnNmYTc4ZW82NDR0cGYyMHVtIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImV2ZW50X2lkIjoiZWUwMzlhN2QtODEyNC00Mzk3LWE4MTgtNDQwYTQzMjFlZDNiIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2MTQ5Njg2NjYsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0FkREpzdUM2ZiIsIm5hbWUiOiJUcmV2b3IiLCJjb2duaXRvOnVzZXJuYW1lIjoiZTc2Mzk2YjEtNzEzYy00NzdmLWExMTYtZTExZjYzOTUxYWI5IiwiZXhwIjoxNjE1MzI2NzMxLCJpYXQiOjE2MTUzMjMxMzEsImVtYWlsIjoidHJldm9yLmEud2lsZGVAZ21haWwuY29tIn0.fsBCd-ZAuPtIWCBljUy3zazaS76ZFHmmxy41vVUszCEg1rU8UUUKAvRLtSrDWJJ9BqCJ4_LxlP7pyjBOWgQiRT32JY6InBEUh-BhC5mSUGxHuzncH1IE8oEKoOnEL6oG0q9iA1LCwVKD1PmjkTh67Xh_zcHh0YMVEAr0AeG1_EAPhlk93loqWqyhWLLIdpKsN2dJe22h4OgKvVpPyuUVK0oCcbtswYdXx1d8Ah0_XxilCxduDeKd_T_Pcb7WJPKOuq8wTBFA9ue_39hVVtAwhXPG9AwfLsuVhusMM8VvgmYiruFVYlVp69QyUjl_MAIsmadtPDmEdtBIBSGXFyBhFg"
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


class LearningModules(Resource):
    def get(self):
        verifyToken()
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
