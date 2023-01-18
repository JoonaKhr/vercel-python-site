import math, threading, time
from flask import Flask, render_template
from lxml import etree
from requests import Session, request
from flask_apscheduler import APScheduler
from turbo_flask import Turbo
from datetime import datetime, timedelta

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

def delete_drone(droneKey: str):
    dronesDict.pop(droneKey)

@scheduler.scheduler.scheduled_job('interval', id='getdrones', seconds=3, misfire_grace_time=10)
def get_drones():
    try:
        responseObj = s.get("http://assignments.reaktor.com/birdnest/drones")
    except:
        print("Response Content empty")
    else:
        try:
            #Parses the received response content into xml element tree
            tree = etree.fromstring(responseObj.content)
        except:
            print(responseObj.headers)
            print("Error occurred")
        else:
            #Finds all the drone elements from element tree
            droneList = tree.findall(".//drone")
            for drone in droneList:
                #Gets drone positions and serial
                droneX = float(drone.find("positionX").text)
                droneY = float(drone.find("positionY").text)
                droneSerial = drone.find("serialNumber").text
                #Checks if drone position is inside the NDZ
                if droneX > deviceMinimumRangeX and droneX < deviceMaximumRangeX and droneY > deviceMinimumRangeY and droneY < deviceMaximumRangeY:
                    #Requests pilot information
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
                            #If drone is not in the dictionary yet, add it in also add a timer for removing it's information
                            if droneSerial not in dronesDict:
                                dronesDict.update({f'{droneSerial}': droneDict})
                                scheduler.add_job(id=f'{droneSerial}', func=delete_drone, args=(droneSerial,), trigger='date', run_date=datetime.now() + timedelta(minutes=10))
                            #If the drone is in, update it's position whenever it gets closer to the nest
                            elif droneSerial in dronesDict:
                                currentDistance = math.hypot(droneX, deviceX, droneY, deviceY)
                                if currentDistance < math.hypot(dronesDict[droneSerial]["positionX"], deviceX, dronesDict[droneSerial]["positionY"], deviceY):
                                    dronesDict[droneSerial]["positionX"] = droneX
                                    dronesDict[droneSerial]["positionY"] = droneY
                                    print("switched")
                        else:
                            print(f'URL returned {url.status_code}')
            #Print relevant information to console for debugging
            for key in dronesDict:
                print(f'{dronesDict[key]}')
            return responseObj
scheduler.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.context_processor
def inject_load():
    droneKeys = [key for key in dronesDict]
    return {'load1': droneKeys, 'load5': "", 'load15': ""}

@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()