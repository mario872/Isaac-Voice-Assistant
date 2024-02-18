import pyttsx3
import pyper
from os import name
import requests
import vosk_recognition
import urllib

heard = ''
homeassistantapikey = ''
homeassistanturl = ''
text = False
voice = '/home/James/Documents/GitHub/Isaac-Voice-Assistant/James4.onnx'

names = ['isaac', 'sack', 'i sat', 'sack']
#names = ['sunny', 'sonny', 'funny']

hotwords = []

for item in names:
    hotwords.append('hey ' + item)
    hotwords.append('okay ' + item)
    hotwords.append('ok ' + item)
    hotwords.append('play ' + item)
    hotwords.append('hi ' + item)
    hotwords.append(item)
    
print(hotwords)

vosk_recognition.config_set({'vosk_model_name': '/home/James/Documents/GitHub/Isaac-Voice-Assistant/client/vosk_small'})

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

def print_and_say(say):
    if name == 'nt':
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
    else:
        engine = pyper.load(voice)
    print(say)
    pyper.say(say)
    if name == 'nt':
        engine.runAndWait()
            
while True:
    found = False
    heard = vosk_recognition.get_heard_text()
    for hotword in hotwords:
        if hotword in heard:
            found = True
            break
    
    if not found:
        print(f'You said {heard} hbut you did not say a hotword!')
        continue
    
    print('Heard: ' + heard)
    
    response = requests.get('http://127.0.0.1:7200/voice_assistant&request={}'.format(urllib.parse.quote_plus(heard))).text
    
    print('Response is ' + response)
    
    print_and_say(response)