import pygame, math, random, copy, time, wave

class Button(object):
    def __init__(self, app, rect, message, msg2 = None):
        self.rect = rect
        self.msg = message
        self.msg2 = msg2

    def draw(self,screen):
        pygame.draw.rect(screen, pygame.Color('#9e9e9e'),self.rect)
        pygame.draw.rect(screen, (0,0,0),self.rect, 3)
        font = pygame.font.Font(None,25)
        self.text = font.render(self.msg, True,(0,0,0))
        screen.blit(self.text, self.rect.move(3,2))
        if self.msg2 != None:
            self.text1 = font.render(self.msg2, True,(0,0,0))
            (x,y,w,h) = self.rect
            temp_rect = pygame.Rect(x, y + 20, w, h)
            screen.blit(self.text1, temp_rect.move(3,2))

class AskContinue(object):
    def __init__(self, app):
        self.buttons = [ ]
        self.app = app
        self.width = app.width * 0.62
        self.loadButtons()

    def loadButtons(self):
        msg1 = 'You have reached the goal of your current level.'
        msg2 = 'Do you wish to continue playing?'
        msg_yes = 'YES'
        msg_no = 'NO'

        big_rect = pygame.Rect(self.app.width/2 - self.width/2, \
            self.app.height / 2 - self.width / 4, self.width, self.width / 2)
        rect_y = pygame.Rect(self.app.width/2 - self.width * 0.4,\
            self.app.height / 2, self.width *0.3, self.width / 8)
        rect_n = pygame.Rect(self.app.width/2 + self.width * 0.1,\
            self.app.height / 2, self.width *0.3, self.width / 8)
        big_button = Button(self,big_rect, msg1, msg2)
        self.buttons.append(big_button)
        y_button = Button(self,rect_y, msg_yes)
        self.buttons.append(y_button)
        n_button = Button(self,rect_n, msg_no)
        self.buttons.append(n_button)


    def draw(self,screen):
        for button in self.buttons:
            button.draw(screen)
