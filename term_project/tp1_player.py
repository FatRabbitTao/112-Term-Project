import pygame, math, random, copy, time

class Cell(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.isSelected = False
        self.color = (255, 165, 0)
        self.r = 10
        self.velocity = 2
        self.isMoving = False
        self.rect = pygame.Rect(self.x, self.y, self.r*2, self.r*2)
        self.touching = False
        self.movingDir = (0, 0)

    def __eq__(self, other):
        return type(self)==type(other) \
            and abs(self.x - other.x) < 2 or abs(self.y - other.y) < 2

    def move(self, app):
        if self.isMoving:       
            (dx, dy) = self.movingDir
            #(dx, dy) = self.setMovingDirection()
            (x, y) = self.destination

            if (abs(self.x - x) < 2 and abs(self.y - y) < 2) or \
                (abs(self.x - x) < 5 * self.r and abs(self.y - y) < 5 * self.r \
                    and self.touching):
                self.isMoving = False # reached destination

            elif dx != 0 and dy != 0 and \
                ((x - self.x) * dx < 0 or (y - self.y) * dy < 0):
                self.isMoving = False

            else:
                self.x, self.y = self.x + dx, self.y + dy
                self.rect = pygame.Rect(self.x, self.y, self.r * 2, self.r *2)
            
    def setMoveStatus(self,coords):
        if self.isSelected:
            (x, y) = coords
            self.destination = coords
            self.setMovingDirection()
            self.isMoving = True
            
    def setMovingDirection(self):
        # adjust / re-adjust movingDir
        (x, y) = self.destination
        xdiff = x - self.x
        sign = -1 if xdiff < 0 else 1
        ydiff = y - self.y
        '''if xdiff == 0:
            dy = self.velocity
            dx = 0
        else:'''
        theta = math.atan(ydiff / xdiff)
        dx = sign * math.cos(theta) * self.velocity
        dy = sign * math.sin(theta) * self.velocity
        self.movingDir = (dx, dy)
        return (dx, dy)

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

class Building(object):
    def __init__(self, x, y):
        self.size = 30
        self._pos = (x, y)
        self.rect = (x, y, self.size, self.size)
        self.level = 0
        self.timeForOne = 20
        self.isProducing = [ ]
    
    def produce(self):
        pass

class Resource(object):
    pass

class Player(object):
    def __init__(self, app):
        self.app = app
        # temp cells
        self.cells = [Cell(self.app.width / 2, self.app.height / 2), 
                        Cell(self.app.width / 3, self.app.height / 3), 
                        Cell(self.app.width * .6, self.app.height * .6)]
        self.buildings = [ ]