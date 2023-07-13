#This file is where all commands from words.yaml and their responses are stored
import yaml

with open('words.yaml') as words_yaml:
    words = yaml.load(words_yaml, Loader=yaml.FullLoader)

print(words)

commands = {
            0: {'phrases': words['numbers']['two_to_three'], 'command': lambda: print('I\'m so good bro')},
            1: {'phrases': words['numbers']['four_to_five'], 'command': lambda: print('Oh, that\'s just sad')}}

commands = {}
