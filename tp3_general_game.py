import pygame, math, random, copy, time, wave

class Button(object):
    def __init__(self, rect, message):
        self.rect = rect
        self.msg = message

    def draw(self,screen):
        pass

class AskContinue(object):
    def __init__(self):
        self.bottons = [ ]
        self.loadButtons()

    def loadButtons(self):
        msg1 = ''