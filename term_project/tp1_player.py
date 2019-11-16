import pygame, math, random, copy, time

class Minion(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.isSelected = False
        self.color = (255, 165, 0)
        self.r = 10
        self.velocity = 2
        self.isMoving = False
        self.rect = pygame.Rect(self.x, self.y, self.r*2, self.r*2)

    def move(self):
        if self.isMoving:
            (dx, dy) = self.movingDir
            (x, y) = self.destination
            if abs(self.x - x) < 1 or abs(self.y - y) < 1:
                self.isMoving = False
            else:
                self.x, self.y = self.x + dx, self.y + dy
                self.rect = pygame.Rect(self.x, self.y, self.r*2, self.r*2)
            
    def setMoveStatus(self,coords):
        if self.isSelected:
            (x, y) = coords
            xdiff = x - self.x
            sign = -1 if xdiff < 0 else 1
            ydiff = y - self.y
            theta = math.atan(ydiff / xdiff)
            dx = sign * math.cos(theta) * self.velocity
            dy = sign * math.sin(theta) * self.velocity
            self.isMoving = True
            self.movingDir = (dx, dy)
            self.destination = coords

    def checkSelection(self, selection):
        if isinstance(selection, tuple):
            (event_x, event_y) = selection
            if (self.x - event_x) ** 2 + (self.y - event_y) ** 2 \
                <= self.r ** 2:
                self.isSelected = True
            else: self.isSelected = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,\
                (int(self.x), int(self.y)), self.r)
        if self.isSelected:
            pygame.draw.circle(screen, (200,0,0),\
                (int(self.x), int(self.y)), self.r + 2, True)
