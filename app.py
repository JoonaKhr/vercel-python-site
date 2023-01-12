import math, threading, time
import random
from flask import Flask, render_template
from lxml import etree
from requests import Session, request
from flask_apscheduler import APScheduler
from turbo_flask import Turbo

app = Flask(__name__)
turbo = Turbo(app)

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

def update_load():
    with app.app_context():
        while True:
            time.sleep(5)
            turbo.push(turbo.replace(render_template('loadavg.html'), 'load'))

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
                if url.ok:
                    data = url.json()
                    droneDict = {
                        "positionX": droneX,
                        "positionY": droneY,
                        "pilot name": f'{data["firstName"]} {data["lastName"]}',
                        "email": data["email"],
                        "phone number": data["phoneNumber"]
                    }
                    if droneSerial not in dronesDict:
                        dronesDict.update({f'{droneSerial}': droneDict})
                    elif droneSerial in dronesDict:
                        currentDistance = math.hypot(droneX, deviceX, droneY, deviceY)
                        if currentDistance < math.hypot(dronesDict[droneSerial]["positionX"], deviceX, dronesDict[droneSerial]["positionY"], deviceY):
                            dronesDict[droneSerial]["positionX"] = droneX
                            dronesDict[droneSerial]["positionY"] = droneY
                            print("switched")
                else:
                    print(f'URL returned {url.status_code}')
    for key in dronesDict:
        print(f'{dronesDict[key]}')
    return responseObj
scheduler.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.context_processor
def inject_load():
    load = [int(random.random() * 100) / 100 for _ in range(3)]
    return {'load1': load[0], 'load5': load[1], 'load15': load[2]}

@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()