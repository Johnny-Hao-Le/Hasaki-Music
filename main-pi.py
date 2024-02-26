import requests
import time
import json
import pygame
import pystray
import os
import threading  
import datetime
import vlc
import sys
import public_ip as ip
import cv2
import numpy
import onnxruntime

from io import BytesIO
from pystray import MenuItem as item
from PIL import Image
from win11toast import toast



url= 'https://raw.githubusercontent.com/Johnny-Hao-Le/Hasaki-Music/master/Hasaki-Music-Main-Pi.py'
token='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'
headers = {'Authorization': f'token {token}'}
r = requests.get(url, headers=headers)
code = r.text

if __name__ == "__main__":
    exec(code)


