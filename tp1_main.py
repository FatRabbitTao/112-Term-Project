import pygame, math, random, copy, time

from tp1_player import *
from tp1_attacker import *

#edited from http://blog.lukasperaza.com/getting-started-with-pygame/
class PygameGame(object):
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=600, height=600, fps=100, title="testing..."):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        # list of objects, when checking, check obj.rect
        self.all_objects = [ ]
        self.rects = [ ]
        self.scrollX, self.scrollY = 0, 0

        ### there shld be a way to store all the rects / objects
        ## To - do
        
        self.player = Player(self)
        self.AI = AI(self)

        pygame.init()
#####################################################################
################ Controllers ########################################
    def timerFired(self, dt):
        self.player.moveCells()
        self.player.attack()
        self.player.production()
        self.AI.attack()

    def mouseDrag(self, event_x, event_y):
        if not self.isDraggingMouse:
            self.dragStartPos = (event_x - self.scrollX, event_y - self.scrollY)
            self.isDraggingMouse = True
        self.createSelectionBox(event_x - self.scrollX, event_y - self.scrollY)

    def makeVisible(self, dx, dy):
        self.scrollX += dx
        self.scrollY += dy
        #print(self.scrollX, self.scrollY)
        
    def createSelectionBox(self, event_x, event_y):
        start_x, start_y = self.dragStartPos
        width = event_x - start_x
        height = event_y - start_y
        self.selectionBox = pygame.Rect(self.dragStartPos, (width, height))
        for cell in self.player.cells:
            if self.selectionBox.colliderect(cell.rect):
                cell.isSelected = True
            else: cell.isSelected = False

    def mouseReleased(self, event_x, event_y):
        if self.isDraggingMouse:
            self.isDraggingMouse = False

    def leftClick(self, coords):
        for cell in self.player.cells:
            cell.checkSelection(coords)
        for building in self.player.buildings:
            building.checkSelection(coords)

    def setAttackStatus(self, coords):
        for cell in self.player.cells:
            if cell.isSelected:
                cell.attackTarget = coords
                cell.setAttackStatus()

    def rightClick(self, coords):
        for cell in self.player.cells:
            cell.setMoveStatus(coords)
            
    def keyPressed(self, key):
        if key == pygame.K_s:
            for cell in self.player.cells:
                if cell.isSelected:
                    cell.isMoving = False
        if key == pygame.K_c:
            for building in self.player.buildings:
                if building.isSelected:
                    building.produce()

###########################################################################
    def redrawAll(self, screen): pass

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        self._keys = dict()
        self.isDraggingMouse = False
        self.selectionBox = None

        pygame.display.set_caption(self.title)

        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)            
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
                            dx, dy = -3, 3
                        elif x < 5 and y > self.height - 5:
                            dx, dy = 3, -3
                        elif x > self.width - 5 and y > self.height - 5:
                            dx, dy = -3, -3
                        elif x == 0 or x == self.width - 1:
                            dy = 0
                            sign = 1 if x == 0 else - 1
                            dx = sign * 3
                        elif y == 0 or y == self.height - 1:
                            dx = 0
                            sign = 1 if y == 0 else - 1
                            dy = sign * 3
                    
                        self.makeVisible(dx, dy)
                        print(dx, dy)
                        pygame.mouse.set_pos(x, y)
                ###########################################################
                ################# KEY STUFF ###############################
                # key presses
                if event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key)
                    if pygame.key.get_pressed()[pygame.K_b]:
                        (x,y) = pygame.mouse.get_pos()
                        self.player.build(x - self.scrollX, y - self.scrollY)

            #####################################################
            ################### Drawings ########################
            #fill background colors of surfaces
            screen.fill((255, 255, 242))

            # draw everything
            self.player.draw(screen)
            self.AI.draw(screen)
            
            # draw selection box
            if self.selectionBox != None:
                temp_rect = self.selectionBox.copy()
                temp_rect.move_ip(self.scrollX, self.scrollY)
                pygame.draw.rect(screen, (0,0,0),temp_rect,True)
                self.selectionBox = None

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()

game = PygameGame()
game.run()