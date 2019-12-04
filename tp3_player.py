import pygame, math, random, copy, time
from tp3_attacker import *

class Cell(object):
    img = pygame.image.load('cell.png')
    image = pygame.transform.scale(img,(42,42))
    dimg = pygame.image.load('deadcell.png')
    deadimage = pygame.transform.scale(dimg,(42,42))
    velocity = 3
# pic from: https://www.pinterest.com/pin/365917538467273861/
    def __init__(self, player, x, y):
        self.player = player
        self.x, self.y = x, y
        self.isSelected = False
        self.color = pygame.Color('#ff5252')
        self.r = 20
        self.velocity = Cell.velocity
        self.isMoving = False
        self.isFarming = False
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)
        self.movingDir = (0, 0)

        self.health = self.originalHealth = 11
        self.ad = 2
        self.barWidth = 4

        self.attackTarget = None
        self.birth_time = pygame.time.get_ticks()

    def __eq__(self, other):
        return type(self) == type(other) \
            and (abs(self.x - other.x) < 2 and abs(self.y - other.y) < 2)

    def __hash__(self):
        return hash((self.x, self.y, self.r))

    def move(self):
        if self.isMoving:   
            for _ in range(self.velocity):
                (dx, dy) = self.setMovingDirection()
                (x, y) = self.destination

                if (abs(self.x - x) < 1 and abs(self.y - y) < 1):
                    # if reached, stop moving
                    self.isMoving = False
                    print('reached')

                # if for weird reason overshot # may not be necessary
                elif dx != 0 and dy != 0 and \
                    ((x - self.x) * dx < 0 or (y - self.y) * dy < 0):
                    self.isMoving = False # overshot
                    print('overshot')

                else:
                    self.x, self.y = self.x + dx, self.y + dy
                    self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
                    self.checkCollision()

    def checkCollision(self):
        temp = self.player.cells + self.player.buildings + \
            self.player.app.AI.viruses + self.player.app.AI.killedCells
        for obj in temp:
            # skip if they are actually the same cell
            if self == obj:
                continue
            _rect = obj.rect
            
            if self.rect.colliderect(_rect): # if the 2 cells touched
                # if not yet moving
                if not self.isMoving: return True
                #print('oops','self:',self.rect,'other:',_rect)
                
                self.player.collide(self, obj)
                (x,y) = self.destination
                if abs(self.x - x) < 5 * self.r and abs(self.y - y) < 5 * self.r:
                    self.isMoving = False
                    print('collision_stop')
                return True
        return False

    def farm(self):
        if self.isFarming:
            if self.destination == (self.player.resourceBase.x, self.player.resourceBase.y):
                # move towards there
                self.setMovingDirection()
                self.isMoving = True
                #print('farming...')
            # if reaching 1 of them
                if (self.x - self.player.resourceBase.x)**2 + \
                    (self.y - self.player.resourceBase.y)**2 <= (self.r + self.player.resourceBase.r)**2 + 1200:
                    self.x += 25
                    self.player.resourceBase.progress -= 5
                    self.destination = (self.player.base.x, self.player.base.y)
                    self.setMovingDirection()
                    self.isMoving = True

                # change move direction
            elif self.destination == (self.player.base.x, self.player.base.y):
                self.setMovingDirection()
                self.isMoving = True
                if (self.x - self.player.base.x)**2 + \
                    (self.y - self.player.base.y)**2 <= (self.r + self.player.base.size/2)**2 + 1200:
                    # change move direction
                    self.x -= 25
                    self.destination = (self.player.resourceBase.x, self.player.resourceBase.y)
                    self.setMovingDirection()
                    self.player.resource += 5
                    self.isMoving = True

            else:
                self.destination = (self.player.resourceBase.x, self.player.resourceBase.y)

    def merge(self, other): # other is another cell
        self.ad = self.ad + other.ad
        self.health = min(self.health, other.health)
        self.player.cells.remove(other)

    def setAttackStatus(self):
        if self.attackTarget != None:
            if isinstance(self.attackTarget, Virus):
                (x, y) = (self.attackTarget.x, self.attackTarget.y)
                self.isMoving = True
                self.destination = (x, y)
            else:
                (x, y) = self.attackTarget
            if abs(self.x - x) > 5 * self.r or abs(self.y - y) > 5 * self.r:
                #print(self.rect,'move')
                self.isMoving = True
                self.destination = (x, y)

    def freeze(self, target): # target is a virus
        target.getFreezed()
        
    def attack(self):
        if self.attackTarget != None:
            if isinstance(self.attackTarget, Virus):
                (x,y) = (self.attackTarget.x, self.attackTarget.y)
            else:(x,y) = self.attackTarget
            #if (self.x - x)**2 + (self.y - y)**2 > 5 * self.r ** 2: return
            # else
            nowTime = pygame.time.get_ticks()
            timeDiff = nowTime - self.birth_time
            if timeDiff <= 500: return
            # else:
            self.birth_time = nowTime
            if isinstance(self.attackTarget, Virus):
                if self.attackTarget not in self.player.app.AI.viruses:
                    self.attackTarget = None
                    return

                if (self.x - self.attackTarget.x)**2 + (self.y - self.attackTarget.y)**2 <= 23 * self.r **2:
                    self.attackTarget.getAttacked(self.ad)
                    return
            else:
                for virus in self.player.app.AI.viruses:
                    if (self.x - virus.x)**2 + (self.y - virus.y)**2 <= 23 * self.r **2:
                        virus.getAttacked(self.ad)
                        return

    def getAttacked(self):
        self.health -= 1
        print('ouch')
        if self.health <= 0:
            print('rip')
            self.color = pygame.Color('#9575cd')#(153, 102, 255)
            self.noOfNewVirus = 2
            self.deathTime = pygame.time.get_ticks()
            self.player.app.AI.killedCells.append(self)
            self.player.cells.remove(self)
            if self.isFarming: 
                self.player.farmingCells.remove(self)

    def spawnVirus(self):
        if self.noOfNewVirus == 0:
            self.player.app.AI.killedCells.remove(self)
        else:
            nowTime = pygame.time.get_ticks()
            if nowTime - self.deathTime > 5000:
                loc = self.checkAvailableLocations()
                if loc != None:
                    (x, y) = loc
                    newVirus = ViolentVirus(self.player.app.AI, x, y)
                    self.player.app.AI.viruses.append(newVirus)
                    self.noOfNewVirus -= 1
                    print('yay new virus', self.noOfNewVirus)
                    self.deathTime = nowTime 
    
    # just for spawning viruses
    def checkAvailableLocations(self):
        start = random.randint(1 ,6)
        angle = math.pi / 6
        temp = self.player.cells + self.player.buildings + self.player.app.AI.viruses

        for i in range(start, start + 12):
            x = self.x + math.cos(angle * i) * self.r * 2
            y = self.y + math.sin(angle * i) * self.r * 2
            temp_virus = Cell(self.player, x, y)
            if not temp_virus.checkCollision():
                return (x, y)
        return None

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
    
        if xdiff == 0: xdiff += 0.0001
        theta = math.atan(ydiff / xdiff)
        dx = sign * math.cos(theta) 
        dy = sign * math.sin(theta) 
        self.movingDir = (dx, dy)
        return (dx, dy)

    def checkSelection(self, selection):
        if isinstance(selection, tuple):
            (event_x, event_y) = selection
            if (self.x - event_x) ** 2 + (self.y - event_y) ** 2 \
                <= self.r ** 2:
                self.isSelected = True
                self.player.app.selected.append(self)
            else: self.isSelected = False

    def drawHealthBar(self,screen):    
        height = self.r / 5
        start_x = self.x - self.r
        start_y = self.y - self.r - height

        for i in range(self.health):
            tempRect = pygame.Rect(start_x + i * self.barWidth + self.player.app.scrollX,\
                 start_y + self.player.app.scrollY, self.barWidth, height)
            pygame.draw.rect(screen, (255,0,0), tempRect)

    def draw(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        screen.blit(Cell.image, temp_rect)
        if self.isSelected:
            pygame.draw.circle(screen, pygame.Color('#905548'),\
                (int(self.x + self.player.app.scrollX),\
                     int(self.y + self.player.app.scrollY)), self.r + 1, True)
        self.drawHealthBar(screen)

    def drawDead(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        screen.blit(Cell.deadimage, temp_rect)

class Macrophage(Cell):
    img = pygame.image.load('macrophage.png')
    image = pygame.transform.scale(img, (66,66))
    def __init__(self,player,x,y):
        super().__init__(player,x,y)
        self.r = 30
        self.health = 20
        self.color = pygame.Color('#9e9e9e')
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)
        self.ad = 10
# pic from: https://www.pinterest.com/pin/127367495699425645/
    def spawnVirus(self):pass
    def farm(self):pass
    def merge(self):pass
    def drawDead(self, screen):pass
    def draw(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        screen.blit(Macrophage.image, temp_rect)

        if self.isSelected:
            pygame.draw.circle(screen, pygame.Color('#905548'),\
                (int(self.x + self.player.app.scrollX),\
                     int(self.y + self.player.app.scrollY)), self.r + 1, True)
        self.drawHealthBar(screen)

class Building(object):
    img = pygame.image.load('cellfactory.png')
    image = pygame.transform.scale(img, (120,108))
    def __init__(self, x, y, player):
        self.size = 80
        (self.x, self.y) = (x, y)
        self.rect = pygame.Rect(x - self.size / 2 , y - self.size / 2, self.size, self.size)
        self.level = 0
        self.isProducing = dict()
        self.isSelected = False
        self.player = player
        self.color = (255, 0, 0)
        self.isMoving = False
        self.originalHealth = self.health = 67
        self.barWidth = 2
    
    def produce(self):
        producingCost = 5
        if self.player.resource >= producingCost:
            self.player.resource -= producingCost
            i = len(self.isProducing)
            if i >= 4: 
                return
            startTime = pygame.time.get_ticks()
            self.isProducing[startTime] = i

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

    def upgrade(self):
        buildingCost = 50
        if self.isSelected and self.player.resource >= buildingCost:
            self.level += 1
            Cell.velocity += 1
            self.player.resource -= buildingCost

    def checkSelection(self, selection):
        if isinstance(selection, tuple):
            (event_x, event_y) = selection
            if self.x - self.size/2 <= event_x <= self.x + self.size/2 and \
                self.y - self.size/2 <= event_y <= self.y + self.size/2:
                self.isSelected = True
                self.player.app.selected.append(self)
            else: self.isSelected = False

    def getAttacked(self):
        self.health -= 1
        if self.health <= 0:
            self.player.buildings.remove(self)

    def drawHealthBar(self,screen):    
        height = self.size / 10
        start_x = self.x - self.size / 2
        start_y = self.y - self.size / 2 - height * 2

        for i in range(self.health):
            tempRect = pygame.Rect(start_x + i * self.size / self.originalHealth * self.barWidth \
                + self.player.app.scrollX,\
                 start_y + self.player.app.scrollY, self.barWidth, height)
            pygame.draw.rect(screen, (255,0,0), tempRect)
    
    def draw(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        temp_rect.inflate_ip(40, 30)
        screen.blit(Building.image, temp_rect)
        if self.isSelected:
            pygame.draw.rect(screen, (0,0,0), temp_rect, True)
        if self.health < self.originalHealth:
            self.drawHealthBar(screen)

class ImmuneSystem(Building):
    temp = pygame.image.load('gudcellfactory.png')
    image = pygame.transform.scale(temp, (120,112))

    def __init__(self, x, y, player):
        super().__init__(x, y, player)
        self.color = pygame.Color('#e65100')
        self.producingCost = 10

    def produce(self):
        if self.player.resource >= self.producingCost:
            self.player.resource -= self.producingCost
            self.producingCost = int(self.producingCost*1.5)
            i = len(self.isProducing)
            if i >= 4: 
                return
            startTime = pygame.time.get_ticks()
            self.isProducing[startTime] = i

    def productionProgress(self):
        nowtime = pygame.time.get_ticks()
        for entry in self.isProducing:       
            if nowtime - entry >= 2000:
                i = self.isProducing[entry]
                newCell = Macrophage(self.player, self.x - .8 * self.size + i * self.size/2,\
                     self.y + .8 * self.size)
                self.isProducing.pop(entry)

                while newCell.checkCollision() or newCell in self.player.cells:
                    i += 1
                    newCell = Macrophage(self.player, self.x - .8 * self.size + i * self.size / 2,\
                        self.y + .8 * self.size)

                self.player.cells.append(newCell)
                break

    def draw(self,screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        temp_rect.inflate_ip(40,36)
        screen.blit(ImmuneSystem.image, temp_rect)

        if self.isSelected:
            pygame.draw.rect(screen, (0,0,0), temp_rect, True)
        if self.health < self.originalHealth:
            self.drawHealthBar(screen)


# base is a special kind of building
class Base(Building):
    img = pygame.image.load('base.png')
    image = pygame.transform.scale(img, (120,120))
    def __init__(self, player):
        x = 60
        y = player.app.height - 60
        super().__init__(x, y, player)
        self.color = pygame.Color('#f9a825')
        self.size = 100
        self.health = self.originalHealth = 100
        self.barWidth = self.size / self.originalHealth

        self.rect = pygame.Rect(self.x - self.size / 2 , self.y - self.size / 2, self.size, self.size)

    def upgrade(self):
        buildingCost = 100
        if self.isSelected and self.player.resource >= buildingCost:
            self.level += 1
            self.player.resource -= buildingCost

    def produce(self): pass

    def draw(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        temp_rect.inflate_ip(10, 10)
        screen.blit(Base.image, temp_rect)
        if self.isSelected:
            pygame.draw.rect(screen, (0,0,0), temp_rect, True)
        if self.health < self.originalHealth:
            self.drawHealthBar(screen)

class Resource(object):
    img = pygame.image.load('resource.png')
    image = pygame.transform.scale(img, (110,110))
    def __init__(self, player, x, y):
        self.player = player
        self.x, self.y = x, y
        self.color = pygame.Color('#29b6f6')
        self.r = 40
        self.rect = pygame.Rect(self.x - self.r , self.y - self.r, self.r * 2, self.r*2)
        self.isSelected = False
        self.isMoving = False
        self.progress = 1000 # rmb to change back to 1000

    # the resource is put under building but is not able to do anything
    def produce(self):pass
    def productionProgress(self):pass
    def checkSelection(self,coords): pass
    def getAttacked(self):pass

    def draw(self,screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        temp_rect.inflate_ip(20, 20)
        screen.blit(Resource.image, temp_rect)
        self.drawProgressBar(screen)

    def drawProgressBar(self,screen):    
        height = 8
        start_x = self.x - 36
        start_y = self.y - 40 - height * 2
        n = self.progress // 100
        for i in range(n):
            tempRect = pygame.Rect(start_x + i * 8 + self.player.app.scrollX,\
                 start_y + self.player.app.scrollY, 4, height)
            pygame.draw.rect(screen, (255,0,0), tempRect)

class Player(object):
    def __init__(self, app):
        self.app = app
        self.base = Base(self)
        self.resourceBase = Resource(self, self.base.x, self.base.y - 500)
        self.buildings = [self.resourceBase, self.base]
        self.score = 0
        self.resource = 0
        self.initialNumCell = 3
        self.cells = [  ]
        self.initializeCell()
        self.farmingCells = [ ]
        self.visible = [ ]
    
    def checkVisible(self):
        temp = self.buildings + self.cells
        temp2 = self.app.AI.viruses + self.app.AI.killedCells
        self.visible = [ ]
        for item in temp:
            for virus in temp2:
                if (item.x - virus.x)**2 + (item.y - virus.y)** 2 <= 160000:
                    self.visible.append(virus)
    
    def initializeCell(self):
        for i in range(self.initialNumCell):
            cell = Cell(self, self.base.x, self.base.y - 100 - i * 50)
            self.cells.append(cell)

    def build(self, x, y):
        buildingCost = 20
        if self.resource >= buildingCost:
            newBuilding = Building(x, y, self)
            if not self.checkIfOccupied(newBuilding):
                self.buildings.append(newBuilding)
                self.resource -= buildingCost

    def buildBig(self, x, y):
        buildingCost = 40
        if self.base.level >= 1 and self.resource >= buildingCost:
            newBuilding = ImmuneSystem(x, y, self)
            if not self.checkIfOccupied(newBuilding):
                self.buildings.append(newBuilding)
                self.resource -= buildingCost

    def checkIfOccupied(self, newObj):
        temp = self.cells + self.buildings + self.app.AI.viruses + self.app.AI.killedCells
        for obj in temp:
            _rect = obj.rect
            if newObj.rect.colliderect(_rect): # if the 2 cells touched
                return True
        return False
    ##### automatic functions #### 
    # under timerFired
    def moveCells(self): # mainly check for collision
        for cell in self.cells:
            if cell.isMoving:   
                cell.move()
    def farm(self):
        for cell in self.farmingCells:
            cell.farm()

    def attack(self):
        for cell in self.cells:
            cell.setAttackStatus()
            if cell.attackTarget != None:
                cell.attack()
    
    def production(self):
        for building in self.buildings:
            building.productionProgress()

    # when knowing the 2 obj collide
    # obj1 is the one u trying to move
    # more or less done 0. 0
    def collide(self, obj1, obj2):
        x0, y0 = obj1.x, obj1.y
        x1, y1 = obj2.x, obj2.y

        # if they are moving towards the same direction
        if obj2.isMoving and obj1.destination == obj2.destination:
           obj1.movingDir = obj2.movingDir

        xdiff = x1 - x0
        ydiff = y1 - y0

        dx,dy = obj1.movingDir

        obj1.x = x0 - xdiff / 2
        obj1.y = y0 - ydiff / 2
        
        obj1.rect = pygame.Rect((obj1.x - obj1.r, obj1.y - obj1.r, obj1.r * 2, obj1.r * 2))
        
        try: 
            if obj1.checkCollision():
                obj1.checkCollision()

        except: obj1.isMoving = False

    def draw(self,screen):
        
        # draw buildings
        for building in self.buildings:
            building.draw(screen)
        # draw cells
        for cell in self.cells:
            cell.draw(screen)

        if hasattr(self.app, 'otherResource'):
            self.app.otherResource.draw(screen)

    def drawSpecs(self,screen):
        # draw score
        font = pygame.font.SysFont("comicsansms", 24)
        surf1 = font.render(f'score: {self.score}', True, (0,0,0))
        surf2 = font.render(f'resource: {self.resource}', True, (0,0,0))
        surf3 = font.render(f'base level: {self.base.level}', True, (0,0,0))
        score_rect = pygame.Rect(4,4, 100, 20)
        resource_rect = pygame.Rect(4, 20, 120, 20)
        level_rect = pygame.Rect(4, 38, 140, 20)
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(0,0, 120, 58))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(0,0, 120, 58),3)
        screen.blit(surf1, score_rect)
        screen.blit(surf2, resource_rect)
        screen.blit(surf3, level_rect)
        
# image from:
# https://www.pinterest.com/pin/42362052718055417/?lp=true
# https://www.pinterest.com/pin/560064903643619800/
# https://www.pinterest.com/pin/102597697731733520/
# https://www.123rf.com/photo_111834093_stock-vector-cute-funny-cell-with-nucleus-humanized-bacteria-cartoon-character-vector-illustration-isolated-on-a-.html
# https://www.pinterest.com/pin/460633868139050903/
        