import pygame, math, random, copy, time

class Virus(object):
    def __init__(self, AI, x, y):
        self.AI = AI
        self.x, self.y = x, y
        # green
        self.color = (0,255,0)
        self.r = 10
        self.velocity = 3
        self.isMoving = False
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)

        self.health = 10
        self.barWidth = self.r * 2 / self.health
        self.movingDir = (0, 0)
        self.birth_time = pygame.time.get_ticks()
        #self.attackTarget = None

    def __eq__(self, other):
        return type(self) == type(other) \
            and (abs(self.x - other.x) < 2 and abs(self.y - other.y) < 2)

    def move(self):
        pass

    def attack(self):
        nowTime = pygame.time.get_ticks()
        timeDiff = nowTime - self.birth_time
        if timeDiff <= 500: return
        # else:
        self.birth_time = nowTime
        for cell in self.AI.app.player.cells:
            if (self.x - cell.x)**2 + (self.y - cell.y)**2 <= 20 * self.r **2:
                cell.getAttacked()
                return

    def getAttacked(self):
        self.health -= 1
        #print('virus ouch')
        if self.health <= 0:
            self.AI.viruses.remove(self)
            #print('virus died')

    def drawHealthBar(self,screen):    
        height = self.r / 5

        start_x = self.x - self.r
        start_y = self.y - self.r - height

        for i in range(self.health):
            tempRect = pygame.Rect(start_x + i * self.barWidth, start_y, self.barWidth, height)
            pygame.draw.rect(screen, (255,0,0), tempRect, 1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,\
                (int(self.x), int(self.y)), self.r)
        self.drawHealthBar(screen)

class AI(object):
    def __init__(self, app):
        self.app = app
        self.viruses = [ ]
        self.initialNumOfVirus = 3
        self.initializeViruses()

    def initializeViruses(self):
        for i in range(self.initialNumOfVirus):
            newVirus = Virus(self, self.app.width*.8, self.app.height*(4+i)/16)
            self.viruses.append(newVirus)

    def attack(self):
        for virus in self.viruses:
            virus.attack()

    def draw(self,screen):
        for virus in self.viruses:
            virus.draw(screen)
        