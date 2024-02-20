#Run this python file to use Isaac
#Written by James Glynn
import yaml
import speech_recognition as sr
from commands import *
import requests
import ast
import google.generativeai as genai
from flask import *
import urllib
import pyper

###########################################################################################################
#Variables

hotwords = ['hey isaac', 'okay isaac', 'ok isaac', 'play isaac', 'isaac']

global_request = ''    
    
hotword_present = False

human_lights = []
human_covers = []
lights = []
covers = []

ai_token = ''

prompt_modes = ['happy', 'sassy', 'burn_alive']

safety = [
    {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'block_none'},
    {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'block_none'},
    {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'block_none'},
    {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'block_none'},
]

def remove_hotword(request, extras=None, replacements=None):
    for hotword in hotwords:
        request = request.replace(hotword + ' ', '')
    if extras != None:
        for extra in extras:
            request = request.replace(extra, '', 1)
    if replacements != None:
        for replacement in replacements.items():
            request = request.replace(replacement[0], replacement[1])
    return request

def try_lights(on_off):
    try:
        homeassistant_call(homeassistanturl, 'services/light/turn_{}'.format(on_off), homeassistantapikey, data={"entity_id": lights[human_lights.index(remove_hotword(global_request, extras=['turn {} the '.format(on_off), 'turn {} '.format(on_off)], replacements={'lights': 'light'}))]})
    except:
        try:
            homeassistant_call(homeassistanturl, 'services/light/turn_{}'.format(on_off), homeassistantapikey, data={"entity_id": lights[human_lights.index(remove_hotword(global_request, extras=['turn {} the '.format(on_off), 'turn {} '.format(on_off)], replacements={'light': 'lights'}))]})
        except:
            return "Sorry, I couldn't find that light."
        
def try_covers(open_close):
    try:
        homeassistant_call(homeassistanturl, 'services/cover/{}'.format(open_close), homeassistantapikey, data={"entity_id": covers[human_covers.index(remove_hotword(global_request, extras=['{} the '.format(open_close), '{} '.format(open_close)], replacements={'blinds': 'blind', 'curtains': 'curtain'}))]})
    except:
        try:
            homeassistant_call(homeassistanturl, 'services/cover/{}'.format(open_close), homeassistantapikey, data={"entity_id": covers[human_covers.index(remove_hotword(global_request, extras=['{} the '.format(open_close), '{} '.format(open_close)], replacements={'blind': 'blinds', 'curtain': 'curtains'}))]})
        except:
            return "Sorry, I coundn't find that cover."

###########################################################################################################
#Dictionary for commands
"""
commands = {
            0: {'ai_phrases': ['[music]'], 'and_or': 'and', 'phrases': ["play ", " on youtube music"], 'command': lambda: play_song(remove_hotword(request, extras=commands[0]['phrases']))},
            1: {'ai_phrases': ['[video]'], 'and_or': 'and', 'phrases': ["play ", " on youtube"], 'command': lambda: play_video(remove_hotword(request, extras=commands[1]['phrases']))},
            2: {'ai_phrases': ['[light on]', '[on light]'], 'and_or': 'and', 'phrases': ["turn on the ", "turn on ", "light"], 'command': lambda: try_lights('on')},
            3: {'ai_phrases': ['[light off]', '[off light]'], 'and_or': 'and', 'phrases': ["turn off the ", "turn off ","light"], 'command': lambda: try_lights('off')},
            4: {'ai_phrases': ['[cover open]', '[open cover]'], 'and_or': 'and', 'phrases': ["open the ", "open ", "blind", "curtain"], 'command': lambda: try_covers('open')},
            5: {'ai_phrases': ['[cover close]', '[close cover]'], 'and_or': 'and', 'phrases': ["close the ", "close ","blind", "curtain"], 'command': lambda: try_covers('close')},
            6: {'ai_phrases': ['[play]'], 'and_or': 'or', 'phrases': ["stop playing", "stop", "pause", "start", "play", "press pause", "press play"], 'command': lambda: press_and_release(Key.media_play_pause)},
            7: {'ai_phrases': [], 'and_or': 'or', 'phrases': ["open"], 'command': lambda: open_app(remove_hotword(request, extras=commands[3]['phrases']))}
           }
"""

commands = {
            0: {'ai_phrases': ['[light on]', '[on light]'], 'and_or': 'and', 'phrases': ["turn on the ", "turn on ", "light"], 'command': lambda: try_lights('on')},
            1: {'ai_phrases': ['[light off]', '[off light]'], 'and_or': 'and', 'phrases': ["turn off the ", "turn off ","light"], 'command': lambda: try_lights('off')},
            2: {'ai_phrases': ['[cover open]', '[open cover]'], 'and_or': 'and', 'phrases': ["open the ", "open ", "blind", "curtain"], 'command': lambda: try_covers('open')},
            3: {'ai_phrases': ['[cover close]', '[close cover]'], 'and_or': 'and', 'phrases': ["close the ", "close ","blind", "curtain"], 'command': lambda: try_covers('close')},
           }

###########################################################################################################
#Setup config
try:
    with open('server/settings.yaml') as settings_yaml:
        settings = yaml.load(settings_yaml, Loader=yaml.FullLoader)
except:
    with open('settings.yaml') as settings_yaml:
        settings = yaml.load(settings_yaml, Loader=yaml.FullLoader)
try:
    with open('server/prompt.txt') as prompt_txt:
        prompts = prompt_txt.readlines()
except:
    with open('prompt.txt') as prompt_txt:
        prompts = prompt_txt.readlines()

def set_config(config):
    global homeassistantdevices
    global human_lights; global human_covers
    global lights; global covers
    global homeassistanturl
    global homeassistantapikey
    global ai_token
 
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
    
    ai_token = config['ai_api_key']
    genai.configure(api_key=ai_token)

set_config(settings)

###########################################################################################################
#Main Loop

app = Flask(__name__)

ai = genai.GenerativeModel('gemini-pro', safety_settings=safety)
pyper.load('James4')
                
@app.route('/voice_assistant&request=<request>&prompt=<mode>', methods=['GET'])
def voice_assistant(request, mode):
    global global_request

    answered = False
    
    request = remove_hotword(urllib.parse.unquote(request).replace('+', ' ')) #Basic formatting to remove Isaac's name from the command
    
    global_request = request
    
    print('New request: ' + request)
    
    for entry in range(len(commands)):
        if commands[entry]['and_or'] == 'and':          
            for phrase_num in range(len(commands[entry]) - 1):
                if commands[entry]['phrases'][phrase_num] in request:
                    phrases_in_request = True
                else:
                    phrases_in_request = False
                    break
            if phrases_in_request:    
                commands[entry]['command']()
                answered = True
                break
        else:
            for phrase in commands[entry]['phrases']:
                if phrase in request:
                    #print(commands[entry]['command'])
                    commands[entry]['command']()
                    answered = True
                    break
    else:
        if request != '' and not answered:
            done = False
            while done == False:
                response = ai.generate_content(prompts[prompt_modes.index(mode)] + request).text.replace('**AI:** ', '').replace("*", '').replace(":", ".").replace("Bard.", "")
                done = True
                    
            for phrase in commands[entry]['ai_phrases']:
                if phrase in response:
                    #print(commands[entry]['command'])
                    commands[entry]['command']()
                    break
            else:
                return response

@app.route('/stream', methods=['POST'])
def stream():
    if request.method == 'POST':
        request.files['file'].save('server/audio.wav')
        r = sr.Recognizer()
        with sr.AudioFile('server/audio.wav') as source:
            audio = r.record(source)
        print('HELLO!')
        return r.recognize_vosk(audio)

@app.route('/tts&request=<request>')
def tts(request):
    request = urllib.parse.unquote(request).replace('+', ' ')
    print(request)
    pyper.save(request, 'server/generated_audio.wav')
    return send_file('generated_audio.wav')

if __name__ == '__main__':
    app.run('0.0.0.0', port=7200)