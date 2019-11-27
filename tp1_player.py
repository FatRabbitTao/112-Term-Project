import pygame, math, random, copy, time

class Cell(object):
    def __init__(self, player, x, y):
        self.player = player
        self.x, self.y = x, y
        self.isSelected = False
        self.color = (255, 165, 0)
        self.r = 10
        self.velocity = 2
        self.isMoving = False
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r*2)
        self.movingDir = (0, 0)

        self.health = 12
        self.barWidth = 2

        self.attackTarget = None
        self.birth_time = pygame.time.get_ticks()

    def __eq__(self, other):
        return type(self) == type(other) \
            and (abs(self.x - other.x) < 2 and abs(self.y - other.y) < 2)

    def move(self):
        if self.isMoving:   
            for _ in range(self.velocity):
                (dx, dy) = self.setMovingDirection()
                (x, y) = self.destination

                if (abs(self.x - x) < 2 and abs(self.y - y) < 2):
                    # if reached, stop moving
                    self.isMoving = False

                # if for weird reason overshot # may not be necessary
                elif dx != 0 and dy != 0 and \
                    ((x - self.x) * dx < 0 or (y - self.y) * dy < 0):
                    self.isMoving = False # overshot

                else:
                    self.x, self.y = self.x + dx, self.y + dy
                    self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r*2, self.r *2)
                    self.checkCollision()

    def checkCollision(self):
        temp = self.player.cells + self.player.buildings + self.player.app.AI.viruses
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
                return True
        return False
            
    def setAttackStatus(self):
        #if self.attackTarget == None: return 
        (x, y) = self.attackTarget
        if abs(self.x - x) > 5 * self.r or abs(self.y - y) > 5 * self.r:
            #print(self.rect,'move')
            self.isMoving = True
            self.destination = self.attackTarget
        
    def attack(self):
        if self.attackTarget != None:
            if self.isMoving: return
            # else
            nowTime = pygame.time.get_ticks()
            timeDiff = nowTime - self.birth_time
            if timeDiff <= 500: return
            # else:
            self.birth_time = nowTime
            for virus in self.player.app.AI.viruses:
                if (self.x - virus.x)**2 + (self.y - virus.y)**2 <= 20 * self.r **2:
                    virus.getAttacked()
                    return
            self.attackTarget = None

    def getAttacked(self):
        self.health -= 1
        print('ouch')
        if self.health <= 0:
            print('rip')
            self.player.cells.remove(self)

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
            else: self.isSelected = False

    def drawHealthBar(self,screen):    
        height = self.r / 5
        start_x = self.x - self.r
        start_y = self.y - self.r - height

        for i in range(self.health):
            tempRect = pygame.Rect(start_x + i * self.barWidth + self.player.app.scrollX,\
                 start_y + self.player.app.scrollY, self.barWidth, height)
            pygame.draw.rect(screen, (255,0,0), tempRect, 1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,\
                (int(self.x + self.player.app.scrollX), \
                    int(self.y + self.player.app.scrollY)), self.r)
        if self.isSelected:
            pygame.draw.circle(screen, (200,0,0),\
                (int(self.x + self.player.app.scrollX),\
                     int(self.y + self.player.app.scrollY)), self.r + 2, True)
        self.drawHealthBar(screen)

class Building(object):
    def __init__(self, x, y, player):
        self.size = 40
        (self.x, self.y) = (x, y)
        self.rect = pygame.Rect(x - self.size / 2 , y - self.size / 2, self.size, self.size)
        self.level = 0
        self.isProducing = dict()
        self.isSelected = False
        self.player = player
        self.color = (255, 0, 0)
        self.isMoving = False
    
    def produce(self):
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

    def checkSelection(self, selection):
        if isinstance(selection, tuple):
            (event_x, event_y) = selection
            if self.x - self.size/2 <= event_x <= self.x + self.size/2 and \
                self.y - self.size/2 <= event_y <= self.y + self.size/2:
                self.isSelected = True
            else: self.isSelected = False
    
    def draw(self, screen):
        temp_rect = self.rect.copy()
        temp_rect.move_ip(self.player.app.scrollX, self.player.app.scrollY)
        pygame.draw.rect(screen, (self.color), temp_rect)
        if self.isSelected:
            pygame.draw.rect(screen, (0,0,0), temp_rect, True)

class Base(object):
    def __init__(self,player):
        self.player = player
        self.size = 50
        self.position = 0

class Resource(object):
    def __init__(self, player):
        pass

    def getFarmed(self):
        pass


class Player(object):
    def __init__(self, app):
        self.app = app
        # temp cells
        self.cells = [Cell(self, self.app.width / 2, self.app.height / 2), 
                        Cell(self, self.app.width / 3, self.app.height / 3), 
                        Cell(self, self.app.width * .6, self.app.height * .6)]
        self.buildings = [ ]
        self.score = 0
        self.resource = Resource(self)

    def build(self, x, y):
        newBuilding = Building(x, y, self)
        if not self.checkIfOccupied(newBuilding):
            self.buildings.append(newBuilding)

    def checkIfOccupied(self, newObj):
        temp = self.cells + self.buildings
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

    def attack(self):
        for cell in self.cells:
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

        # prevent jerking
        if abs(dy * xdiff - dx * ydiff) <= 2:
            obj1.isMoving = False
        #print(dx, dy, xdiff, ydiff)

        obj1.x = x0 - xdiff / 2
        obj1.y = y0 - ydiff / 2
        
        obj1.rect = pygame.Rect((obj1.x - obj1.r, obj1.y - obj1.r, obj1.r * 2, obj1.r * 2))
        
        try: 
            if obj1.checkCollision():
                obj1.checkCollision()

        except: obj1.isMoving = False

    def draw(self,screen):
        # draw cells
        for cell in self.cells:
            cell.draw(screen)
        # draw buildings
        for building in self.buildings:
            building.draw(screen)
