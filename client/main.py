import pyttsx3
from os import name
import requests
import vosk_recognition
import urllib
#import lamp
import speech_recognition as sr
import json
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #Stop pygame from saying hello in the console

from pygame import mixer

heard = ''
homeassistantapikey = ''
homeassistanturl = ''
text = False
mode = 'happy' #Modes are happy, sassy, burn_alive
voice = '/home/James/Documents/GitHub/Isaac-Voice-Assistant/James4.onnx'

url = "127.0.0.1:7200"

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

mixer.init()

#vosk_recognition.config_set({'vosk_model_name': '/home/James/Documents/GitHub/Isaac-Voice-Assistant/client/vosk_small'})

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
    print(say)
    mixer.music.load('client/saved_audio.wav')
    mixer.music.set_volume(1)
    mixer.music.play()
            
while True:
    found = False
    print('Say something!')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        
        print('Sending Request')
        stream = requests.post(f"http://{url}/stream", files={"file": audio.get_wav_data()})
    
    heard = stream.text
    print(heard)
    
    for hotword in hotwords:
        if hotword in heard:
            found = True
            break
    
    if not found:
        print(f'You said {heard} but you did not say a hotword!')
        continue
    
    print('Heard: ' + heard)
    
    if 'mode ' in heard or 'merge ' in heard or 'most ' in heard or 'mood ' in heard:
        if 'one' in heard or '1' in heard:
            mode = 'happy'
            print_and_say(f'Okay, {mode} mode enabled!')
            continue
        elif 'two' in heard or '2' in heard:
            mode = 'sassy'
            print_and_say(f'Okay, {mode} mode enabled!')
            continue
        elif 'three' in heard or '3' in heard:
            mode = 'burn_alive'
            print_and_say(f'Okay, {mode} mode enabled!')
            continue
    elif 'lamp color ' in heard or 'lamp colour ' in heard:
        lamp.lamp_colour(heard)
        continue
    
    response = requests.get(f'http://{url}/voice_assistant&request={urllib.parse.quote_plus(heard)}&prompt={mode}').text
    
    with open('client/saved_audio.wav', 'wb') as saved_audio_file:
        saved_audio_file.write(requests.get(f'http://{url}/tts&request={urllib.parse.quote_plus(response)}').content)
        
    print_and_say(response)