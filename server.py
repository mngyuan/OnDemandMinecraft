from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from configuration import Config
from server_management import manageServer
import json
import boto3

app = Flask(__name__)
CORS(app)

#Main endpoint for loading the webpage
@app.route('/')
def loadIndex():
    return render_template('index.html')

@app.route('/initServerMC', methods = ['POST'])
def initServerMC():
    inputPass = request.form['pass']
    returnData = {}

    message = "Password Incorrect!"

    if inputPass == Config.SERVER_PASSWORD:
        #Instantiate server here or return ip address if already running
        client = boto3.client(
            'ec2',
            aws_access_key_id=Config.ACCESS_KEY,
            aws_secret_access_key=Config.SECRET_KEY,
            region_name=Config.ec2_region
        )
        message = manageServer(client)
    
    print(message)
    return render_template('index.html', ipMessage=message)

if __name__ == "__main__":
    app.run()
