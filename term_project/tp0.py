import pygame, math, random, copy, time

#edited from http://blog.lukasperaza.com/getting-started-with-pygame/
class PygameGame(object):

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=400, height=600, fps=50, title="Immunity"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title


        pygame.init()

        # add your functions here

    def timerFired(self, dt):
        pass

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

            #fill background colors of surfaces
            screen.fill((70, 130, 50))33r

            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()


game = PygameGame()
game.run()