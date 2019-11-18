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
        self.all_rects = [ ]

        ### there shld be a way to store all the rects / objects
        ## To - do
        

        self.player = Player(self)

        pygame.init()

#####################################################################
################ Controllers ########################################
    def timerFired(self, dt):
        for cell in self.player.cells:
            if not cell.isMoving: continue
            for other_cell in self.player.cells:
                if cell == other_cell: continue
                _rect = other_cell.rect
            
                if cell.rect.colliderect(_rect): # if the 2 cells touched
                    x0, y0 = cell.rect[0], cell.rect[1]  
                    x1, y1 = other_cell.rect[0], other_cell.rect[1]
                    other_cell.movingDir = cell.movingDir
                    xdiff = x1 - x0
                    ydiff = y1 - y0
                    cell.x -= xdiff / 2
                    cell.y -= ydiff / 2
                    cell.touching = other_cell.touching = True

                    # stop them if destination is in the middle ie reached
                    if min(x0, x1) <= cell.destination[0] <= max(x0, x1) and \
                        min(y0, y1) <= cell.destination[1] <= max(y0, y1):
                        cell.isMoving = False
                        other_cell.isMoving = False
                    elif not cell.isMoving:
                        other_cell.isMoving = False
                else: cell.touching = other_cell.touching = False
                    
            cell.move(self)

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

    def rightClick(self, coords):
        for cell in self.player.cells:
            cell.setMoveStatus(coords)
            
    def keyPressed(self, key):
        if key == pygame.K_s:
            for cell in self.player.cells:
                if cell.isSelected:
                    cell.isMoving = False
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

            #####################################################
            ################### Drawings ########################
            #fill background colors of surfaces
            screen.fill((255, 255, 242))

            # draw cells
            for cell in self.player.cells:
                cell.draw(screen)
            
            # draw selection box
            if self.selectionBox != None:
                pygame.draw.rect(screen, (0,0,0),self.selectionBox,True)
                self.selectionBox = None

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()

game = PygameGame()
game.run()