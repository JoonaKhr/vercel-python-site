from flask import Flask
from lxml import etree
import urllib.request

app = Flask(__name__)

deviceY, deviceX = 250000.0, 250000.0

@app.route("/")
def index():
    
    opener = urllib.request.build_opener()
    tree = etree.parse(opener.open("http://assignments.reaktor.com/birdnest/drones"))
    for element in tree.iter("*"):
        print(element.text)
    return ""