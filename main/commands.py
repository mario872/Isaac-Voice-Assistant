#This file is where all commands and their responses are stored
from actions import *
from shared import *

import webbrowser
from pynput.keyboard import Key, Controller
import time
from ytmusicapi import YTMusic
from pytube import Search
import yaml
import subprocess
import requests

try:
    with open('main/apps.yaml') as apps_yaml:
        apps = yaml.load(apps_yaml, Loader=yaml.FullLoader)
except:
    with open('apps.yaml') as apps_yaml:
        apps = yaml.load(apps_yaml, Loader=yaml.FullLoader)

def play_song(song_name):
    print_and_say("Okay, playing {} on youtube music.".format(song_name), voice, text)
    ytmusic = YTMusic()
    results = ytmusic.search(song_name, filter='songs', limit=1)
    webbrowser.open_new('https://music.youtube.com/watch?v=' + results[0]['videoId'])
    keyboard = Controller()
    time.sleep(3)
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    
def press_and_release(key_name):
    keyboard = Controller()
    keyboard.press(key_name)
    keyboard.release(key_name)
    
def play_video(video_name):
    print_and_say("Okay, playing {} on youtube.".format(video_name), voice, text)
    results = Search(video_name).results #Get result
    
    #Format
    for video in range(len(results) - 1):
        results.pop()
    results[0] = str(results[0])
    videoID_list = []
    for character in results[0]:
        videoID_list.append(character)
    for i in range(41):
        videoID_list.pop(0)
    videoID_list.pop()
    videoID = ''
    for character in videoID_list:
        videoID += character
    
    #Open in browser
    webbrowser.open_new('https://youtube.com/watch?v=' + videoID)
    keyboard = Controller()
    time.sleep(3)
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    
def open_app(app):
    try:
        print_and_say("Okay, opening {}.".format(app), voice, text)
        subprocess.call(apps[app])
    except:
        print_and_say("Sorry, I couldn't find that app.", voice, text)
        
def homeassistant_call(url_base, url_continued, api_key, data=None):
    api_url = url_base + '/api/' + url_continued
    headers = {"Authorization": "Bearer {}".format(api_key)}

    if data != None:
        requests.post(api_url, headers=headers, json=data).text
    else:
        requests.post(api_url, headers=headers)