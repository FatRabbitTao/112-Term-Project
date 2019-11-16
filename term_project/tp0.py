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

    def move(self):
        if self.isMoving:
            (dx, dy) = self.movingDir
            (x, y) = self.destination
            if int(abs(self.x - x)) < 1 or int(abs(self.y - y)) < 1:
                self.isMoving = False
            else:
                self.x, self.y = self.x + dx, self.y + dy
            
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

            
        elif isinstance(selection, pygame.Rect):
            # do the rect thing
            pass
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
        self.minion = Minion(self.width / 2, self.height / 2)

        pygame.init()

        # add your functions here

    def timerFired(self, dt):
        self.minion.move()

    def redrawAll(self, screen):
        pass

    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        
        pygame.display.set_caption(self.title)

        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                # put your events here

                ### mouse Pressed
                
                # left click
                if pygame.mouse.get_pressed()[0]:
                    coords = pygame.mouse.get_pos()
                    self.minion.checkSelection(coords)

                if pygame.mouse.get_pressed()[2]:
                    coords = pygame.mouse.get_pos()
                    self.minion.setMoveStatus(coords)
                    
            #fill background colors of surfaces
            screen.fill((255, 255, 242))

            self.minion.draw(screen)

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()


game = PygameGame()
game.run()