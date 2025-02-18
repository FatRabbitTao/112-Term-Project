import pygame, math, random, copy, time
from tp2_player import *

class Virus(object):
    def __init__(self, AI, x, y):
        self.AI = AI
        self.x, self.y = x, y
        # green
        self.color = pygame.Color('#64dd17')
        self.r = 10
        self.velocity = 3
        self.isMoving = False
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)

        self.health = 10
        self.barWidth = self.r * 2 / self.health
        self.movingDir = (0, 0)
        self.attack_time = self.move_time = pygame.time.get_ticks() 
        

    def __eq__(self, other):
        return type(self) == type(other) \
            and (abs(self.x - other.x) < 2 and abs(self.y - other.y) < 2)

    def __repr__(self):
        return f'Virus at ({self.x},{self.y}) position'

    def attack(self):
        nowTime = pygame.time.get_ticks()
        timeDiff = nowTime - self.attack_time
        if timeDiff <= 500: return
        # else:
        self.attack_time = nowTime
        temp = self.AI.app.player.cells + self.AI.app.player.buildings[1: ]
        for obj in temp:
            if obj in self.AI.app.player.cells and (self.x - obj.x)**2 + (self.y - obj.y)**2 <= 20 * self.r **2:
                obj.getAttacked()
                return
            elif obj in self.AI.app.player.buildings:
                (x, y, w, h) = obj.rect
                temp_rect = pygame.Rect(x - 10, y - 10, w + 20, h + 20)
                if self.rect.colliderect(temp_rect):
                    obj.getAttacked()
                    print('building under attack')
                    return

    def getAttacked(self):
        self.health -= 2
        #print('virus ouch')
        if self.health <= 0:
            self.AI.viruses.remove(self)
            self.AI.app.player.score += 1
            #print('virus died')

    def drawHealthBar(self,screen):    
        height = self.r / 5

        start_x = self.x - self.r
        start_y = self.y - self.r - height

        for i in range(self.health):
            tempRect = pygame.Rect(start_x + i * self.barWidth + self.AI.app.scrollX,\
                 start_y + self.AI.app.scrollY, self.barWidth, height)
            pygame.draw.rect(screen, (255,0,0), tempRect, 1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,\
                (int(self.x + self.AI.app.scrollX), \
                    int(self.y + self.AI.app.scrollY)), self.r)
        pygame.draw.circle(screen, pygame.Color('#1b5e20'),\
                (int(self.x + self.AI.app.scrollX), \
                    int(self.y + self.AI.app.scrollY)), self.r + 1, 1)
        self.drawHealthBar(screen)

class ViolentVirus(Virus):
    def __init__(self,AI,x,y):
        super().__init__(AI, x, y)
        self.isMoving = True
        self.attackTarget = None
        self.destination = None

    def move(self):
        if self.isMoving:
            if self.attackTarget == None:
                self.moveInGeneralDir()
                (dx, dy) = self.movingDir
                self.x, self.y = self.x + dx, self.y + dy
                border1 = -50
                border2 = 600
                if self.x < border1:
                    self.x = border1
                    self.flipDir()
                elif self.y < border1:
                    self.y = border1
                    self.flipDir()
                elif self.x > border2:
                    self.x = border2
                    self.flipDir()
                elif self.y > border2:
                    self.y = border2
                    self.flipDir()
                self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
                self.checkCollision()
            else:
                pass
    def flipDir(self):
        dx, dy = self.movingDir
        self.movingDir = (- dx, - dy)

    def moveInGeneralDir(self):
        nowTime = pygame.time.get_ticks()
        if nowTime - self.move_time >= 5000:
        # decide whether going to homebase or not
            self.isGoingHomeBase = (random.random() > 0.6)
            choices = self.AI.app.player.buildings[1:]
            if self.isGoingHomeBase:
                target = random.choice(choices)
                (x, y) = (target.x, target.y)
                xdiff = x - self.x
                sign = -1 if xdiff < 0 else 1
                ydiff = y - self.y
            
                if xdiff == 0: xdiff += 0.0001
                theta = math.atan(ydiff / xdiff)
                dx = sign * math.cos(theta)
                dy = sign * math.sin(theta) 

            elif random.random() < 0.3:
                dx = random.random()
                dy = random.random()

            else:
                x = random.random() 
                y = random.random() 
                sign = -1 if x < 0 else 1
                if x == 0: x += 0.0001
                theta = math.atan(y / x)
                dx = sign * math.cos(theta) / 2
                dy = sign * math.sin(theta) / 2

            self.movingDir = (dx, dy)
            self.move_time = nowTime

    def checkCollision(self):
        temp = self.AI.app.player.cells + self.AI.app.player.buildings + \
            self.AI.viruses + self.AI.killedCells
        for obj in temp:
            # skip if they are actually the same cell
            if self == obj:
                continue
            _rect = obj.rect
            if self.rect.colliderect(_rect): # if the 2 cells touched
                # if not yet moving
                if not self.isMoving: return True
                #print('oops','self:',self.rect,'other:',_rect)
                
                self.collide(self, obj)

                return True
        return False

    def collide(self, obj1, obj2):
        x0, y0 = obj1.x, obj1.y
        x1, y1 = obj2.x, obj2.y

        # if they are moving towards the same direction
        if obj2.isMoving and obj1.destination == obj2.destination:
           obj1.movingDir = obj2.movingDir

        xdiff = x1 - x0
        ydiff = y1 - y0

        dx,dy = obj1.movingDir
        # prevent jerking
        #if abs(dy * xdiff - dx * ydiff) <= 1:
        #   obj1.isMoving = False
        #print(dx, dy, xdiff, ydiff)
        obj1.x = x0 - xdiff / 2
        obj1.y = y0 - ydiff / 2
        
        obj1.rect = pygame.Rect((obj1.x - obj1.r, obj1.y - obj1.r, obj1.r * 2, obj1.r * 2))
        
        try: 
            if obj1.checkCollision():
                obj1.checkCollision()

        except: obj1.isMoving = False

    def stop_to_attack(self):
        pass

    def escape(self):
        pass

class AI(object):
    def __init__(self, app):
        self.app = app
        self.viruses = [ ]
        self.initialNumOfVirus = 3
        self.initializeViruses()
        self.killedCells = [ ]
        self.productionProgress = dict()
        self.difficulty = 0

    def initializeViruses(self):
        for i in range(self.initialNumOfVirus):
            newVirus = ViolentVirus(self, self.app.width*.8, 5 + self.app.height*(i)/16)
            self.viruses.append(newVirus)

    def spawn(self):
        for i in range(len(self.killedCells) - 1, -1, -1):
            cell = self.killedCells[i]
            cell.spawnVirus()

    def attack(self):
        for virus in self.viruses:
            virus.move()
            virus.attack()

    def draw(self,screen):
        for virus in self.viruses:
            virus.draw(screen)
        for cell in self.killedCells:
            cell.draw(screen)
        