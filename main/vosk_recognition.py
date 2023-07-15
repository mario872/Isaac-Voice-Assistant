#This is the example file from vosk's github page, but modified to be used as a module

import argparse
import queue
import sys
import sounddevice as sd

from vosk import Model, KaldiRecognizer

import yaml

q = queue.Queue()

config = None

device_info = None
samplerate = None
model = None

def config_set(config_input):
    global config
    global device_info
    global samplerate
    global model
    config = config_input
    
    device_info = sd.query_devices(sd.default.device[0], 'input')
    # soundfile expects an int, sounddevice provides a float:
    samplerate = int(device_info["default_samplerate"])
    model = Model(config['vosk_model_name'], lang="en-us")

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
    
def format_heard(heard):
    heard_list = []

    for character in heard:
        heard_list.append(character)

    for i in range(14):
        heard_list.pop(0)
    
    for i in range(3):
        heard_list.pop()
    
    heard_string = ''
        
    for entry in heard_list:
        heard_string += entry
    
    return heard_string.lower()

def get_heard_text():
    global device_info
    global samplerate
    global model
    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=sd.default.device[0],
            dtype="int16", channels=1, callback=callback):
        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                return format_heard(rec.Result())