import pyttsx3
from dimits import Dimits
from os import name

heard = ''
hotwords = ['hey isaac', 'okay isaac', 'ok isaac', 'play isaac', 'isaac']
homeassistantapikey = ''
homeassistanturl = ''
text = False
voice = ''

def init():
    global heard
    global hotwords
    global homeassistantapikey
    global homeassistanturl
    global text
    global voice

def remove_hotword(heard, extras=None, replacements=None):
    for hotword in hotwords:
        heard = heard.replace(hotword + ' ', '')
    if extras != None:
        for extra in extras:
            heard = heard.replace(extra, '', 1)
    if replacements != None:
        for replacement in replacements.items():
            heard = heard.replace(replacement[0], replacement[1])
    return heard

def print_and_say(say, voice, text):
    print("Voice: " + voice)
    if name == 'nt':
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
    else:
        engine = Dimits(voice)
        engine.say = engine.text_2_speech
    print(say)
    if text == False:
        engine.say(say)
        if name == 'nt':
            engine.runAndWait()