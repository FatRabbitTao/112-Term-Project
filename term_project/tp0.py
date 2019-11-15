import pygame, math, random, copy, time

#edited from http://blog.lukasperaza.com/getting-started-with-pygame/
class PygameGame(object):

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=400, height=600, fps=50, title="Bridge"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title


        self.tableScreenHeight = 200
        self.biddingOptScreenHeight = 200
        self.biddingOptScreen = pygame.Surface((self.width, 
            self.biddingOptScreenHeight))
        self.biddingBarScreenHeight = 80
        self.biddingBarScreen = pygame.Surface((self.width, 80))
        self.handScreen = pygame.Surface(
            (self.width, self.height - self.tableScreenHeight - self.biddingBarScreenHeight - self.biddingOptScreenHeight))

        self.initButtons()

        pygame.init()

    def initButtons(self):

        #biddingOptScreen buttons
        buttonNames = [0, 141, 282, 423, 564]
        self.buttons = []
        newRow = []
        for i in range(5):
            newPos = ((i*80 + 10, 0), ((i+1)*80, 50))
            newImg = pygame.image.load(f'imgs/button{buttonNames[i]}.jpeg')
            newButton = Button(self.tableScreenHeight, newPos, pygame.transform.scale(newImg, (60, 40)))
            newRow.append(newButton)   
        self.buttons.append(newRow)

        for row in range(2, 5):
            newRow = []
            for col in range(5):
                newPos = ((col*80 + 10, 50*(row-1)), ((col+1)*80 + 10, 50*row))
                newImg = pygame.image.load(f'imgs/row{row}button{buttonNames[col]}.jpeg')
                newButton = Button(self.tableScreenHeight, newPos, pygame.transform.scale(newImg, (60, 40)))
                newRow.append(newButton)  
            self.buttons.append(newRow)


        self.biddingBarButtons = []
        #biddingBarScreen buttons
        for bb in range(1, 5):
            newPos = (((bb-1)*100 + 10, 10), (bb*100 + 10, 50*row))
            newImg = pygame.image.load(f'imgs/bar{bb}.jpg')
            newButton = Button(self.tableScreenHeight + self.biddingOptScreenHeight, newPos, pygame.transform.scale(newImg, (80, 60)))
            self.biddingBarButtons.append(newButton)

    def timerFired(self, dt):
        pass

    def redrawAll(self, screen):
        pass

    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)

        # call game-specific initialization
        #self.init()
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            
            # take turns bid
            '''
            while True:
                turn = self.turn % 4
                if turn != 2:
                    self.allPlayers[turn].makeBid(self)'''
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False

                for row in range(len(self.buttons)):
                    for col in range(len(self.buttons[0])):
                        response = self.buttons[row][col].event_handler(event)
                        if response != None:
                            self.player.makeBid(self,response)

                for bb in range(len(self.biddingBarButtons)):
                    self.biddingBarButtons[bb].event_handler(event)

            #fill background colors of surfaces
            screen.fill((70, 130, 50))
            self.biddingOptScreen.fill((50, 110, 30))
            self.biddingBarScreen.fill((0, 0, 0))
            self.handScreen.fill((70, 130, 50))

            #draw buttons
            for row in range(len(self.buttons)):
                for col in range(len(self.buttons[0])):
                    self.buttons[row][col].draw(self.biddingOptScreen)
            for bb in range(len(self.biddingBarButtons)):
                self.biddingBarButtons[bb].draw(self.biddingBarScreen)
            
            #draw compass
            self.compass = pygame.transform.scale(pygame.image.load(f'imgs/compass.png').convert_alpha(), (120, 150))
            screen.blit(self.compass, (10, 10))

            #put all the other surfaces on the back screen
            screen.blit(self.biddingOptScreen, (0, self.tableScreenHeight))
            screen.blit(self.biddingBarScreen, 
                (0, self.tableScreenHeight + self.biddingOptScreenHeight))
            screen.blit(self.handScreen, 
                (0, self.tableScreenHeight + self.biddingOptScreenHeight + self.biddingBarScreenHeight))

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()


game = PygameGame()
game.run()