from flask import Flask
from lxml import etree
import json
from requests import Session, request
from flask_apscheduler import APScheduler

app = Flask(__name__)

s = Session()
deviceY, deviceX = 250000.0, 250000.0
deviceMinimumRangeY, deviceMinimumRangeX = 150000.0, 150000.0
deviceMaximumRangeY, deviceMaximumRangeX = 350000.0, 350000.0
droneDict = {}
dronesDict = {}
droneList = []
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

@scheduler.scheduler.scheduled_job('interval', id='getdrones', seconds=2, misfire_grace_time=10)
def get_drones():
    responseObj = s.get("http://assignments.reaktor.com/birdnest/drones")
    tree = etree.fromstring(responseObj.content)
    droneList = tree.findall(".//drone")
    for drone in droneList:
        droneX = float(drone.find("positionX").text)
        droneY = float(drone.find("positionY").text)
        droneSerial = drone.find("serialNumber").text
        if droneX > deviceMinimumRangeX and droneX < deviceMaximumRangeX and droneY > deviceMinimumRangeY and droneY < deviceMaximumRangeY:
            with request('GET', url=f'http://assignments.reaktor.com/birdnest/pilots/{droneSerial}') as url:
                data = json.loads(url.content)
                droneDict = {
                    "positionX": droneX,
                    "positionY": droneY,
                    "pilot name": f'{data["firstName"]} {data["lastName"]}',
                    "email": data["email"],
                    "phone number": data["phoneNumber"]
                }
                if droneSerial not in dronesDict:
                    dronesDict.update({f'{droneSerial}': droneDict})
    print(dronesDict)
    return responseObj
scheduler.start()

@app.route("/")
def index():
    return "Hello"
