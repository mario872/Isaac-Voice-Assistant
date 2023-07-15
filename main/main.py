#Run this python file to use Isaac
#Written by James Glynn
import yaml
from commands import commands
import speech_recognition as sr
import vosk_recognition
with open('main/settings.yaml') as settings_yaml:
    settings = yaml.load(settings_yaml, Loader=yaml.FullLoader)

vosk = False; google = False #Speech selector variables

def set_config(config):
    global vosk; global google #Speech selector variables
    
    #Setting up speech selector
    if config['speech_recogniser'] == 'vosk':
        vosk_recognition.config_set(config)
        vosk = True
    elif config['speech_recogniser'] == 'google':
        google = True

set_config(settings) 
       
if vosk:
    print("Vosk")
    heard = vosk_recognition.get_heard_text()
    print(heard)
elif google:
    print("Google")
    r = sr.Recognizer()
    with sr.Microphone() as source: r.adjust_for_ambient_noise(source)
    with sr.Microphone() as source: audio = r.listen(source)
    heard = r.recognize_google(audio)
    print(heard)

for entry in range(len(commands)):
    for phrase in commands[entry]['phrases']:
        if heard == phrase:
            commands[entry]['command']()