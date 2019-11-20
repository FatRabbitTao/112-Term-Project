import pygame, math, random, copy, time

class Virus(object):
    def __init__(self, AI, x, y):
        self.AI = AI
        self.x, self.y = x, y
        # green
        self.color = (0,255,0)
        self.r = 10
        self.velocity = 2
        self.isMoving = False
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)

        self.movingDir = (0, 0)
        
class AI(object):
    def __init__(self):
        pass