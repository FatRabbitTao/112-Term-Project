import pygame, math, random, copy, time

############ minion class will change/move later ###############
class Minion(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.isSelected = False
        self.color = (255, 165, 0)
        self.r = 10
        self.velocity = 2
        self.isMoving = False
        self.rect = pygame.Rect(self.x, self.y, self.r*2, self.r*2)

    def move(self):
        if self.isMoving:
            (dx, dy) = self.movingDir
            (x, y) = self.destination
            if abs(self.x - x) < 0.5 or abs(self.y - y) < 0.5:
                self.isMoving = False
            else:
                self.x, self.y = self.x + dx, self.y + dy
                self.rect = pygame.Rect(self.x, self.y, self.r*2, self.r*2)
            
    def setMoveStatus(self,coords):
        if self.isSelected:
            (x, y) = coords
            xdiff = x - self.x
            sign = -1 if xdiff < 0 else 1
            ydiff = y - self.y
            theta = math.atan(ydiff / xdiff)
            dx = sign * math.cos(theta) * self.velocity
            dy = sign * math.sin(theta) * self.velocity
            self.isMoving = True
            self.movingDir = (dx, dy)
            self.destination = coords

    def checkSelection(self, selection):
        if isinstance(selection, tuple):
            (event_x, event_y) = selection
            if (self.x - event_x) ** 2 + (self.y - event_y) ** 2 \
                <= self.r ** 2:
                self.isSelected = True
            else: self.isSelected = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,\
                (int(self.x), int(self.y)), self.r)
        if self.isSelected:
            pygame.draw.circle(screen, (200,0,0),\
                (int(self.x), int(self.y)), self.r + 2, True)

    
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