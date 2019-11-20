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

    def mouseDrag(self, event_x, event_y):
        if not self.isDraggingMouse:
            self.dragStartPos = (event_x, event_y)
            self.isDraggingMouse = True
        self.createSelectionBox(event_x, event_y)
        
    def createSelectionBox(self, event_x, event_y):
        start_x, start_y = self.dragStartPos
        width = event_x - start_x
        height = event_y - start_y
        self.selectionBox = pygame.Rect(self.dragStartPos, (width, height))
        for cell in self.player.cells:
            if self.selectionBox.colliderect(cell.rect):
                cell.isSelected = True

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
                    self.setAttackStatus(pygame.mouse.get_pos())
                # normal
                elif pygame.mouse.get_pressed()[0]:
                    coords = pygame.mouse.get_pos()
                    self.leftClick(coords)
                # right click
                elif pygame.mouse.get_pressed()[2]:
                    coords = pygame.mouse.get_pos()
                    self.rightClick(coords)

                ###########################################################
                ################# KEY STUFF ###############################
                # key presses
                if event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key)
                    if pygame.key.get_pressed()[pygame.K_b]:
                        (x,y) = pygame.mouse.get_pos()
                        self.player.build(x, y)

            #####################################################
            ################### Drawings ########################
            #fill background colors of surfaces
            screen.fill((255, 255, 242))

            # draw everything
            self.player.draw(screen)
            self.AI.draw(screen)
            
            # draw selection box
            if self.selectionBox != None:
                pygame.draw.rect(screen, (0,0,0),self.selectionBox,True)
                self.selectionBox = None

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()

game = PygameGame()
game.run()