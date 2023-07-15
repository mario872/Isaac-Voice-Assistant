#This file is where all commands and their responses are stored
from actions import *

commands = {
            0: {'phrases': ["two", "three"], 'command': lambda: say('I\'m so good bro')},
            1: {'phrases': ["four", "five"], 'command': lambda: say('Oh, that\'s just sad')}}