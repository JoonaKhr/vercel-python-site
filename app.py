from flask import Flask
from lxml import etree
import urllib.request, json
from requests import Session
from flask_apscheduler import APScheduler

app = Flask(__name__)

s = Session()
deviceY, deviceX = 250000.0, 250000.0
deviceMinimumRangeY, deviceMinimumRangeX = 150000.0, 150000.0
deviceMaximumRangeY, deviceMaximumRangeX = 350000.0, 350000.0
droneList = []
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

@scheduler.scheduler.scheduled_job('interval', id='getdrones', seconds=2, misfire_grace_time=10)
def get_drones():
    responseObj = s.get("http://assignments.reaktor.com/birdnest/drones")
    tree = etree.fromstring(responseObj.content)
    return responseObj
scheduler.start()

@app.route("/")
def index():
    droneList = []
    tree = etree.fromstring(get_drones().content)
    droneList = tree.findall(".//drone")
    for drone in droneList:
        droneX = float(drone.find("positionX").text)
        droneY = float(drone.find("positionY").text)
        if droneX > deviceMinimumRangeX and droneX < deviceMaximumRangeX and droneY > deviceMinimumRangeY and droneY < deviceMaximumRangeY:
            print(f'Model: {drone.find("model").text}')
            with urllib.request.urlopen(f'http://assignments.reaktor.com/birdnest/pilots/{drone.find("serialNumber").text}') as url:
                data = json.load(url)
                print(data["pilotId"])
    return ""


    