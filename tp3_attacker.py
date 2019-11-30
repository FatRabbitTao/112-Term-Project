import pygame, math, random, copy, time
from tp3_player import *

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

    def getAttacked(self, ad = 2):
        self.health -= ad
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
                factor = 3 if self.AI.app.player.base.level > 0 else 2
                self.x, self.y = self.x + dx * factor, self.y + dy * factor
                x_low_bound = 5
                x_high_bound = 1390
                y_low_bound = -570
                y_high_bound = 770
                if self.x < x_low_bound:
                    self.x = x_low_bound
                    self.flipDir()
                elif self.y < y_low_bound:
                    self.y = y_low_bound
                    self.flipDir()
                elif self.x > x_high_bound:
                    self.x = x_high_bound
                    self.flipDir()
                elif self.y > y_high_bound:
                    self.y = y_high_bound
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
        timeDiff = random.randint(2500, 5000)
        if nowTime - self.move_time >= timeDiff:
        # decide whether going to homebase or not
            self.isGoingHomeBase = (random.random() > self.AI.probability)
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

            else:
                x = random.random() 
                y = random.random() 
                sign = -1 if x < 0 else 1
                if x == 0: x += 0.0001
                theta = math.atan(y / x)
                dx = sign * math.cos(theta) 
                dy = sign * math.sin(theta) 

            self.movingDir = (dx, dy)
            self.move_time = nowTime

    def checkCollision(self):
        temp = self.AI.app.player.cells + self.AI.app.player.buildings + \
            self.AI.viruses + self.AI.killedCells + [self.AI.base]
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


class VirusBase(object):
    image = pygame.transform.scale(pygame.image.load('virusBase.png'), (50,50))
    def __init__(self, AI):
        self.x, self.y = 1300, -500
        self.size = 50
        self.rect = pygame.Rect(self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)
        self.isProducing = False
        self.color = pygame.Color('#424242')
        self.isMoving = False
        self.AI = AI
    
    def produce(self):
        x = self.x + random.choice([-1,1]) * random.randint(36,50)
        y = self.y + random.choice([-1,1]) * random.randint(36,50)
        newVirus = ViolentVirus(self.AI, x, y)
        while newVirus.checkCollision() or newVirus in self.AI.viruses:
            x = self.x + random.choice([-1,1]) * random.randint(36,50)
            y = self.y + random.choice([-1,1]) * random.randint(36,50)
            newVirus = ViolentVirus(self.AI, x, y)
        self.AI.viruses.append(newVirus)

    def productionProgress(self):
        nowtime = pygame.time.get_ticks()
        for entry in self.isProducing:       
            if nowtime - entry >= 2000:
                i = self.isProducing[entry]
                newCell = Cell(self.player, self.x - .8 * self.size + i * self.size/2,\
                     self.y + .8 * self.size)
                self.isProducing.pop(entry)

                while newCell.checkCollision() or newCell in self.player.cells:
                    i += 1
                    newCell = Cell(self.player, self.x - .8 * self.size + i * self.size / 2,\
                        self.y + .8 * self.size)

                self.player.cells.append(newCell)
                break

    def draw(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.AI.app.scrollX, self.AI.app.scrollY)
        screen.blit(VirusBase.image, temp_rect)

class AI(object):
    def __init__(self, app):
        self.app = app
        self.base = VirusBase(self)
        self.viruses = [ ]
        self.initialNumOfVirus = 3
        self.initializeViruses()
        self.killedCells = [ ]
        self.productionProgress = dict()
        self.difficulty = 0
        self.birthTime = pygame.time.get_ticks()
        self.spawnInterval = 20000 # 10 seconds

    def initializeViruses(self):
        for i in range(self.initialNumOfVirus):
            newVirus = ViolentVirus(self, self.app.width*.8, 5 + self.app.height*(i)/16)
            self.viruses.append(newVirus)

    def spawn(self):
        for i in range(len(self.killedCells) - 1, -1, -1):
            cell = self.killedCells[i]
            cell.spawnVirus()
        
    def spawnFromHome(self):
        nowTime = pygame.time.get_ticks()
        if nowTime - self.birthTime > self.spawnInterval:
            self.base.produce()
            self.birthTime = nowTime

    def attack(self):
        self.spawnFromHome()
        if self.app.currentGoal == 10:
            self.AI.probability = len(self.AI.app.player.buildings) * 0.2 \
                if len(self.AI.app.player.buildings) < 3 else 0.5

        for virus in self.viruses:
            virus.move()
            virus.attack()

    def draw(self,screen):
        for virus in self.viruses:
            virus.draw(screen)
        for cell in self.killedCells:
            cell.draw(screen)
        self.base.draw(screen)
        
        
# image from:
# http://www.safetysignsireland.ie/caution-toxic-hazard-symbol-safety-sign.html