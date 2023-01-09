from flask import Flask
from lxml import etree
import urllib.request, json

app = Flask(__name__)

deviceY, deviceX = 250000.0, 250000.0
deviceMinimumRangeY, deviceMinimumRangeX = 150000.0, 150000.0
deviceMaximumRangeY, deviceMaximumRangeX = 350000.0, 350000.0
@app.route("/")
def index():
    droneList = []
    opener = urllib.request.build_opener()
    tree = etree.parse(opener.open("http://assignments.reaktor.com/birdnest/drones"))
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