#Run this python file to use Isaac
#Written by James Glynn

import speech_recognition
import yaml
from commands import commands
#with open('words.yaml') as words_yaml:
#    words = yaml.load(words_yaml, Loader=yaml.FullLoader)  

#print(speech_recognition.get_heard_text())
print('Listening')
heard = speech_recognition.get_heard_text()

def say(d):
    print(d)

for entry in range(len(commands)):
    for phrase in commands[entry]['phrases']:
        if heard == phrase:
            commands[entry]['command']()