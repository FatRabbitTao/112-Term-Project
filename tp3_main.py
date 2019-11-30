import pygame, math, random, copy, time, wave

from tp3_player import *
from tp3_attacker import *

#edited from http://blog.lukasperaza.com/getting-started-with-pygame/
class PygameGame(object):
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=800, height=800, fps=100, title="testing..."):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        # list of objects, when checking, check obj.rect
        self.all_objects = [ ]
        self.rects = [ ]
        self.selected = [ ]
        self.scrollX, self.scrollY = 0, 0
        self.gameOver = False
        self.isPaused = False
        self.inHelp = False

        # assume starting at bottom left
        self.x0, self.y0 = 0, 600

        ### there shld be a way to store all the rects / objects
        ## To - do
        self._keys = dict()
        self.isDraggingMouse = False
        self.selectionBox = None
        self.waitingToStart = True
        self.player = Player(self)
        self.AI = AI(self)
       # self.loadMusic()
        self.loadImage()

        # levels and goals (changeable)
        self.currentGoal = 10

    def loadMusic(self):
        pygame.mixer.init(55000)
        pygame.mixer.music.load('music.mp3')
        pygame.mixer.music.play(- 1)

    def loadImage(self):
        startImg = pygame.image.load('startPic.png')
        self.startImg = pygame.transform.scale(startImg, (500, 200))
        helpImg = pygame.image.load('helpPic.png')
        self.helpImg = pygame.transform.scale(helpImg, (500, 250))
#####################################################################
################ Controllers ########################################
    pygame.init()


    def timerFired(self, dt):
        if (not self.gameOver) and (not self.waitingToStart) and (not self.isPaused):
            self.player.moveCells()
            self.player.attack()
            self.player.farm()
            self.player.production()
            self.AI.attack()
            self.AI.spawn()
            self.checkGameCondition()

    def checkGameCondition(self):
        if len(self.player.buildings) == 1: # only have the resource pool left
            self.gameOver = True
            print('You lost')
        elif self.player.score >= self.currentGoal:
            self.gameOver = True
            print('You won!')

    def mouseDrag(self, event_x, event_y):
        if not self.isDraggingMouse:
            self.dragStartPos = (event_x - self.scrollX, event_y - self.scrollY)
            self.isDraggingMouse = True
        self.createSelectionBox(event_x - self.scrollX, event_y - self.scrollY)

    def makeVisible(self, dx, dy):
        minScroll = 50
        maxScroll = -600
        if self.scrollX + dx < minScroll and self.scrollY + dy > - minScroll and \
            self.scrollY + dy < - maxScroll and self.scrollX + dx > maxScroll:
            self.scrollX += dx
            self.scrollY += dy
        #print(self.scrollX, self.scrollY)
        
    def createSelectionBox(self, event_x, event_y):
        start_x, start_y = self.dragStartPos
        width = event_x - start_x
        height = event_y - start_y
        self.selected = [ ]
        self.selectionBox = pygame.Rect(self.dragStartPos, (width, height))
        for cell in self.player.cells:
            if self.selectionBox.colliderect(cell.rect):
                cell.isSelected = True
                self.selected.append(cell)
            else: cell.isSelected = False

    def mouseReleased(self, event_x, event_y):
        if self.isDraggingMouse:
            self.isDraggingMouse = False

    def leftClick(self, coords):
        self.selected = [ ]
        for cell in self.player.cells:
            cell.checkSelection(coords)
        for building in self.player.buildings:
            building.checkSelection(coords)

    def setAttackStatus(self, coords):
        for i in range(len(self.player.cells)-1,-1,-1):
            cell = self.player.cells[i]
            if cell.isSelected:
                if cell.isFarming: 
                    cell.isFarming = False
                    self.player.farmingCells.remove(cell)
                for virus in self.AI.viruses:
                    if virus.rect.collidepoint(coords):
                        cell.attackTarget = virus
                if cell.attackTarget == None:
                    cell.attackTarget = coords
                cell.setAttackStatus()
    
    def checkForMerge(self,coords):
        if len(self.selected) == 1:
            cell_1 = self.selected[ 0 ]
            for other_cell in self.player.cells:
                if other_cell.rect.collidepoint(coords) and \
                    (cell_1.x - other_cell.x) ** 2 + \
                    (cell_1.y - other_cell.y) ** 2 <= 25 * cell_1.r ** 2\
                    and cell_1.ad + other_cell.ad <= 7:
                    cell_1.merge(other_cell)

    def setFarmStatus(self,coords):
        if self.player.resourceBase.rect.collidepoint(coords):
            for cell in self.player.cells:
                if cell.isSelected and (not cell.isFarming):
                    cell.isFarming = True
                    cell.destination = (self.player.resourceBase.x - 5,\
                        self.player.resourceBase.y)
                    self.player.farmingCells.append(cell)
                    cell.farm()
        while len(self.player.farmingCells) > 4:
            oldCell = self.player.farmingCells.pop(0)
            oldCell.isFarming = False

    def rightClick(self, coords):
        for i in range(len(self.player.cells)-1, -1, -1):
            cell = self.player.cells[i]
            if cell.isSelected:
                if cell.isFarming: 
                    cell.isFarming = False
                    self.player.farmingCells.remove(cell)
                if cell.attackTarget != None:
                    cell.attackTarget = None
                cell.setMoveStatus(coords)
            
    def keyPressed(self, key):
        if key == pygame.K_s:
            for cell in self.player.cells:
                if cell.isSelected:
                    cell.isMoving = False
                    cell.isFarming = False
                    if cell in self.player.farmingCells:
                        self.player.farmingCells.remove(cell)
                    cell.attackTarget = None
        if key == pygame.K_c:
            for building in self.player.buildings:
                if building.isSelected:
                    building.produce()
        if key == pygame.K_u:
            self.player.base.upgrade()
        
        if key == pygame.K_h:
            self.waitingToStart = False
            self.isPaused = True
            self.inHelp = True

        if key == pygame.K_SPACE:
            self.isPaused = not self.isPaused
###########################################################################
    def redrawAll(self, screen): pass

    def drawStart(self,screen):
        if self.waitingToStart:
            width = 500
            start = self.width / 2 - width / 2
            screen.blit(self.startImg, pygame.Rect(start,50,500,500))

    def drawHelp(self,screen):
        if self.inHelp:
            width = 500
            start = self.width / 2 - width / 2
            screen.blit(self.helpImg, pygame.Rect(start,50,500,500) )


    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption(self.title)
        screen.set_alpha(None)

        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)       
            # music: Diana Boncheva feat. BanYa - Beethoven Virus Full Version 
            # from https://www.youtube.com/watch?v=DtKCNJmARF0
            ################## Events ###########################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                # put your events here
                ####################################################
                ############### MOUSE STUFF ########################
                ## mouse drag
                if (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                ### mouse released
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                ### mouse Pressed
                # left click
                # attacks
                elif pygame.key.get_pressed()[pygame.K_a] and \
                    pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.setAttackStatus((x - self.scrollX, y - self.scrollY))
                # farm
                elif pygame.key.get_pressed()[pygame.K_f] and \
                    pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.setFarmStatus((x - self.scrollX, y - self.scrollY))
                # merge
                elif pygame.key.get_pressed()[pygame.K_u] and \
                    pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.checkForMerge((x - self.scrollX, y - self.scrollY))
                # normal
                elif pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.leftClick((x - self.scrollX, y - self.scrollY))
                # right click
                elif pygame.mouse.get_pressed()[2]:
                    x, y = pygame.mouse.get_pos()
                    self.rightClick((x - self.scrollX, y - self.scrollY))
                ### mouse move / camera move / side scrolling -ish part
                if event.type == pygame.MOUSEMOTION:
                    x, y = pygame.mouse.get_pos()
                    if (not (x <= 49 and y == 0)) and \
                        (x in [0, self.width - 1] or y in [0, self.height - 1]):
                        if x > self.width - 5 and y < 5:
                            dx, dy = -8, 8
                        elif x < 5 and y > self.height - 5:
                            dx, dy = 8, -8
                        elif x > self.width - 5 and y > self.height - 5:
                            dx, dy = -8, -8
                        elif x == 0 or x == self.width - 1:
                            dy = 0
                            sign = 1 if x == 0 else - 1
                            dx = sign * 8
                        elif y == 0 or y == self.height - 1:
                            dx = 0
                            sign = 1 if y == 0 else - 1
                            dy = sign * 8
                    
                        self.makeVisible(dx, dy)
                        pygame.mouse.set_pos(x, y)
                ###########################################################
                ################# KEY STUFF ###############################
                # key presses
                if event.type == pygame.KEYDOWN:
                    if self.waitingToStart:
                        self.waitingToStart = False
                    if self.inHelp:
                        self.inHelp = False
                        self.isPaused = False
                    self._keys[event.key] = True
                    self.keyPressed(event.key)
                    if pygame.key.get_pressed()[pygame.K_b]:
                        (x,y) = pygame.mouse.get_pos()
                        self.player.build(x - self.scrollX, y - self.scrollY)
                    if pygame.key.get_pressed()[pygame.K_m]:
                        (x,y) = pygame.mouse.get_pos()
                        self.player.buildBig(x - self.scrollX, y - self.scrollY)

            #####################################################
            ################### Drawings ########################
            #fill background colors of surfaces
            screen.fill(pygame.Color('#fff59d')) #(255, 255, 179)

            # draw everything
            self.AI.draw(screen)
            self.player.draw(screen)
            
            # draw selection box
            if self.selectionBox != None:
                temp_rect = self.selectionBox.copy()
                temp_rect.move_ip(self.scrollX, self.scrollY)
                pygame.draw.rect(screen, (0,0,0),temp_rect,True)
                self.selectionBox = None

            #self.redrawAll(screen)
            self.drawStart(screen)
            self.drawHelp(screen)
            pygame.display.flip()

        pygame.quit()

game = PygameGame()
game.run()