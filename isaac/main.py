#Run this python file to use Isaac
#Written by James Glynn
import yaml
import speech_recognition as sr
import vosk_recognition
from shared import *
from commands import *
import subprocess
from pathlib import Path
import time
import os
import ytmusicapi
import requests
import ast
from bardapi import Bard

###########################################################################################################
#Variables
vosk = False; google = False; text = False #Speech selector variables

hotword_present = False

human_lights = []
human_covers = []
lights = []
covers = []

bard_token = ''

def try_lights(on_off):
    try:
        homeassistant_call(homeassistanturl, 'services/light/turn_{}'.format(on_off), homeassistantapikey, data={"entity_id": lights[human_lights.index(remove_hotword(heard, extras=['turn {} the '.format(on_off), 'turn {} '.format(on_off)], replacements={'lights': 'light'}))]})
    except:
        try:
            homeassistant_call(homeassistanturl, 'services/light/turn_{}'.format(on_off), homeassistantapikey, data={"entity_id": lights[human_lights.index(remove_hotword(heard, extras=['turn {} the '.format(on_off), 'turn {} '.format(on_off)], replacements={'light': 'lights'}))]})
        except:
            return "Sorry, I couldn't find that light."
        
def try_covers(open_close):
    try:
        homeassistant_call(homeassistanturl, 'services/cover/{}'.format(open_close), homeassistantapikey, data={"entity_id": covers[human_covers.index(remove_hotword(heard, extras=['{} the '.format(open_close), '{} '.format(open_close)], replacements={'blinds': 'blind', 'curtains': 'curtain'}))]})
    except:
        try:
            homeassistant_call(homeassistanturl, 'services/cover/{}'.format(open_close), homeassistantapikey, data={"entity_id": covers[human_covers.index(remove_hotword(heard, extras=['{} the '.format(open_close), '{} '.format(open_close)], replacements={'blind': 'blinds', 'curtain': 'curtains'}))]})
        except:
            return "Sorry, I coundn't find that cover."

###########################################################################################################
#Dictionary for commands
commands = {
            0: {'bard_phrases': ['[music]'], 'and_or': 'and', 'phrases': ["play ", " on youtube music"], 'command': lambda: play_song(remove_hotword(heard, extras=commands[0]['phrases']))},
            1: {'bard_phrases': ['[video]'], 'and_or': 'and', 'phrases': ["play ", " on youtube"], 'command': lambda: play_video(remove_hotword(heard, extras=commands[1]['phrases']))},
            2: {'bard_phrases': ['[light on]', '[on light]'], 'and_or': 'and', 'phrases': ["turn on the ", "turn on ", "light"], 'command': lambda: try_lights('on')},
            3: {'bard_phrases': ['[light off]', '[off light]'], 'and_or': 'and', 'phrases': ["turn off the ", "turn off ","light"], 'command': lambda: try_lights('off')},
            4: {'bard_phrases': ['[cover open]', '[open cover]'], 'and_or': 'and', 'phrases': ["open the ", "open ", "blind", "curtain"], 'command': lambda: try_covers('open')},
            5: {'bard_phrases': ['[cover close]', '[close cover]'], 'and_or': 'and', 'phrases': ["close the ", "close ","blind", "curtain"], 'command': lambda: try_covers('close')},
            6: {'bard_phrases': ['[play]'], 'and_or': 'or', 'phrases': ["stop playing", "stop", "pause", "start", "play", "press pause", "press play"], 'command': lambda: press_and_release(Key.media_play_pause)},
            7: {'bard_phrases': [], 'and_or': 'or', 'phrases': ["open"], 'command': lambda: open_app(remove_hotword(heard, extras=commands[3]['phrases']))}}


###########################################################################################################
#Setup config
try:
    with open('main/settings.yaml') as settings_yaml:
        settings = yaml.load(settings_yaml, Loader=yaml.FullLoader)
except:
    with open('settings.yaml') as settings_yaml:
        settings = yaml.load(settings_yaml, Loader=yaml.FullLoader)
try:
    with open('main/prompt.txt') as prompt_txt:
        prompt = prompt_txt.readline()
except:
    with open('prompt.txt') as prompt_txt:
        prompt = prompt_txt.readline()

def set_config(config):
    global vosk; global google; global text #Speech selector variables
    global homeassistantdevices
    global human_lights; global human_covers
    global lights; global covers
    global homeassistanturl
    global homeassistantapikey
    global bard_token
    global voice
    global LLama2_model
    global Ai
    
    #Setting up speech selector
    if config['speech_recogniser'] == 'vosk':
        vosk_recognition.config_set(config)
        vosk = True
    elif config['speech_recogniser'] == 'google':
        google = True
    elif config['speech_recogniser'] == 'text':
        text = True
    
    try:    
        if config['homeassistant_api_key'] != '' and config ['homeassistant_url'] != '':
            #Get data about lights and covers in the user's home
            url = config['homeassistant_url'] + '/api/template'
            headers = {"Authorization": "Bearer {}".format(config['homeassistant_api_key'])}
            homeassistantapikey = config['homeassistant_api_key']
            homeassistanturl = config['homeassistant_url']
            light_data = '{"template": "{% set domain = \'light\' %}{% set entities = states[domain] | map(attribute=\'entity_id\') | list %}{{entities}}"}'
            cover_data = '{"template": "{% set domain = \'cover\' %}{% set entities = states[domain] | map(attribute=\'entity_id\') | list %}{{entities}}"}'
            #Convert stringed dictionary to dictionary
            lights = ast.literal_eval(requests.post(url, headers=headers, data=light_data).text)
            covers = ast.literal_eval(requests.post(url, headers=headers, data=cover_data).text)
            #Format homeassistant's returned dictionary to make the lists human readable
            for light_num in range(len(lights)):
                human_lights.append(lights[light_num].replace('light.', ''))
                human_lights[light_num] = human_lights[light_num].replace('_', ' ')
            for cover_num in range(len(covers)):
                human_covers.append(covers[cover_num].replace('cover.', ''))
                human_covers[cover_num] = human_covers[cover_num].replace('_', ' ')
                
    except:
        pass
    
    try:
        bard_token = config['google_bard_cookie_key']
    except:
        pass
        
    try:
        voice = config['default-voice-piper']
    except:
        voice = 'Windows Not Supported for Piper'
    
set_config(settings)

###########################################################################################################
#Main Loop
bard = Bard(token=bard_token)
while True:
    try:
        answered = False
        if vosk:
            print("Listening")
            heard = vosk_recognition.get_heard_text()
        elif google:
            print("Listening")
            r = sr.Recognizer()
            with sr.Microphone() as source: r.adjust_for_ambient_noise(source)
            with sr.Microphone() as source: audio = r.listen(source)
            heard = r.recognize_google(audio).lower()
        elif text:
            heard = input('Type input: ')
    except KeyboardInterrupt:
        print("Exiting")
        exit()
    
    hotword_present = False   
    for hotword in hotwords:
        if hotword in heard:
            hotword_present = True
    if hotword_present == False:
        heard = ''
    
    if not text:
        print(heard)
        
    heard = remove_hotword(heard) #Basic formatting to remove Isaac's name from the command
    
    for entry in range(len(commands)):
        if commands[entry]['and_or'] == 'and':          
            for phrase_num in range(len(commands[entry]) - 1):
                if commands[entry]['phrases'][phrase_num] in heard:
                    phrases_in_heard = True
                else:
                    phrases_in_heard = False
                    break
            if phrases_in_heard:    
                commands[entry]['command']()
                answered = True
                break
        else:
            for phrase in commands[entry]['phrases']:
                if phrase in heard:
                    #print(commands[entry]['command'])
                    commands[entry]['command']()
                    answered = True
                    break
    else:
        if heard != '' and not answered:
            response = bard.get_answer(prompt + heard)['content'].replace('**Bard:** ', '').replace("*", '').replace(":", ".").replace("Brad.", "")
            for phrase in commands[entry]['bard_phrases']:
                if phrase in response:
                    #print(commands[entry]['command'])
                    commands[entry]['command']()
                    break
            else:
                print_and_say(response, voice, text)