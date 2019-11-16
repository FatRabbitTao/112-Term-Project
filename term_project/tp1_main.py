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
        ### temp minion #####
        self.minions = [Minion(self.width / 2, self.height / 2), \
                        Minion(self.width / 3, self.height / 3) ]

        pygame.init()

        # add your functions here
    def timerFired(self, dt):
        for minion in self.minions:
            minion.move()

    def mouseDrag(self, event_x, event_y):
        if not self.isDraggingMouse:
            self.dragStartPos = (event_x, event_y)
            self.isDraggingMouse = True
        
        start_x, start_y = self.dragStartPos
        width = event_x - start_x
        height = event_y - start_y
        self.selectionBox = pygame.Rect(self.dragStartPos, (width, height))
        for minion in self.minions:
            if self.selectionBox.colliderect(minion.rect):
                minion.isSelected = True

    def mouseReleased(self, event_x, event_y):
        if self.isDraggingMouse:
            self.isDraggingMouse = False

    def keyPressed(self, key):
        if key == pygame.K_s:
            for minion in self.minions:
                if minion.isSelected:
                    minion.isMoving = False

    def redrawAll(self, screen):
        pass

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
                    for minion in self.minions:
                        minion.checkSelection(coords)
                # right click
                elif pygame.mouse.get_pressed()[2]:
                    coords = pygame.mouse.get_pos()
                    for minion in self.minions:
                        minion.setMoveStatus(coords)

                # key presses
                if event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key)

            ################### Drawings ########################
            #fill background colors of surfaces
            screen.fill((255, 255, 242))

            for minion in self.minions:
                minion.draw(screen)

            if self.selectionBox != None:
                pygame.draw.rect(screen, (0,0,0),self.selectionBox,True)
                self.selectionBox = None

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()

game = PygameGame()
game.run()