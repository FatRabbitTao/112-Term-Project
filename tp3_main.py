import pygame, math, random, copy, time, wave

from tp3_player import *
from tp3_attacker import *
from tp3_general_game import *

#edited from http://blog.lukasperaza.com/getting-started-with-pygame/
class PygameGame(object):
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=800, height=780, fps=30, title="IMMUNITY..."):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.selected = [ ]
        self.scrollX, self.scrollY = 0, 0
        self.gameOver = self.askContinue = False
        self.isPaused = False
        self.inHelp = False
        self.pageCount = 0
        self.grouping = dict()
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
        self.map = Map(self)
        self.all_rects = self.map.rects
        self.loadMusic()
        self.loadImage()
        # levels and goals (changeable)
        self.currentGoal = 10
        pygame.init()

    def loadMusic(self):
        pygame.mixer.init(44100)
        pygame.mixer.music.load('music.mp3')
        pygame.mixer.music.play( -1)

    def loadImage(self):
        startImg = pygame.image.load('startPic.png')
        self.startImg = pygame.transform.scale(startImg, (800, 450))
        helpImg1 = pygame.image.load('helpPic1.png')
        self.helpImg1 = pygame.transform.scale(helpImg1, (800, 450))
        helpImg2 = pygame.image.load('helpPic2.png')
        self.helpImg2 = pygame.transform.scale(helpImg2, (800, 450))
        helpImg3 = pygame.image.load('helpPic3.png')
        self.helpImg3 = pygame.transform.scale(helpImg3, (800, 450))
#####################################################################
################ Controllers ########################################
    
    def timerFired(self, dt):
        if (not self.gameOver) and (not self.waitingToStart) and (not self.isPaused):
            self.player.farm()
            self.player.moveCells()
            self.player.attack()
            self.player.production()
            self.player.checkVisible()
            self.AI.attack()
            self.AI.spawn()
            self.checkGameCondition()
            self.newResource()

    def newResource(self):
        if self.player.resourceBase.progress <= 0:
            x = random.randint(700, 1350)
            y = random.randint(-570, 100)
            tempResource = Resource(self.player, x, y)
            temp = self.player.cells + self.player.buildings + \
            self.AI.viruses + self.AI.killedCells + [self.AI.base]
            while tempResource.rect.collidelist(temp) != -1:
                x = random.randint(700, 1350)
                y = random.randint(-570, 100)
                tempResource = Resource(self.player, x, y)
            self.player.resourceBase = tempResource # the x y position of the resource need to be modified
            self.player.buildings[0] = tempResource

    def checkGameCondition(self):
        if len(self.player.buildings) == 1: # only have the resource pool left
            self.gameOver = True
        elif self.player.score >= self.currentGoal:
            self.isPaused = True
            self.askContinue = True

    def mouseDrag(self, event_x, event_y):
        if not self.isDraggingMouse:
            self.dragStartPos = (event_x - self.scrollX, event_y - self.scrollY)
            self.isDraggingMouse = True
        self.createSelectionBox(event_x - self.scrollX, event_y - self.scrollY)

    def makeVisible(self, dx, dy):
        minScroll = 50
        maxScroll = - 1300
        if self.scrollX + dx < minScroll and self.scrollY + dy > - minScroll and \
            self.scrollY + dy < - maxScroll and self.scrollX + dx > maxScroll:
            self.scrollX += dx
            self.scrollY += dy
        
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

    def adjustView(self,coords):
        x, y = coords
        cx, cy = x + self.scrollX, y + self.scrollY
        if pygame.Rect(0, 59, 142, 142).collidepoint((cx,cy)):
            cy -= 59
            sx = max(0, cx - 40) if cx < 100 else min(87, cx - 40)
            sy = max(0, cy - 39) if cy < 100 else min(87, cy - 39)
            self.scrollX = -sx * 15
            self.scrollY = -15 * (sy - 87)

    def checkContinue(self, coords):
        if self.askContinue:
            x, y = coords
            if self.askScreen.buttons[1].rect.collidepoint((x + self.scrollX,y + self.scrollY)):
                self.currentGoal += 10
                if self.AI.spawnInterval > 1000:
                    self.AI.spawnInterval -= 1000
                if self.AI.probability <= 0.8:
                    self.AI.probability += 0.2
                self.isPaused = False
                self.askContinue = False
            
            elif self.askScreen.buttons[2].rect.collidepoint((x + self.scrollX,y + self.scrollY)):
                self.askContinue = False
                self.gameOver = True

    def leftClick(self, coords):
        self.selected = [ ]
        for cell in self.player.cells:
            cell.checkSelection(coords)
        for building in self.player.buildings:
            building.checkSelection(coords)
        
        self.adjustView(coords)
        self.checkContinue(coords)


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

    def checkForFreeze(self,coords):
        if len(self.selected) == 1:
            cell = self.selected[ 0 ]
            for virus in self.AI.viruses:
                if virus.rect.collidepoint(coords) and \
                    (cell.x - virus.x) ** 2 + \
                    (cell.y - virus.y) ** 2 <= 25 * cell.r ** 2:
                    cell.freeze(virus)

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
                x, y = coords
                cx, cy = x + self.scrollX, y + self.scrollY
                if pygame.Rect(0, 59, 142, 142).collidepoint((cx,cy)):
                    x_target = cx * 15
                    y_target = (cy - 59) * 15 - 1300
                    cell.setMoveStatus((x_target,y_target))
                else: cell.setMoveStatus(coords)
            
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

        if key in [pygame.K_1, pygame.K_2, pygame.K_3]:
            for thing in self.selected:
                thing.isSelected = False
            group = self.grouping.get(key, None)
            if group != None:
                self.selected = group
                cx,cy = group[0].x, group[0].y
                self.resetView(cx, cy)
                for thing in group:
                    thing.isSelected = True

    def resetView(self,cx,cy):
        if cx < 400:
            self.scrollX = 30
        elif cx > 400 and cx < 1600: 
            self.scrollX = 400 - cx
        elif cx >= 1600: 
            self.scrollX = - 1280
        
        if cy > 390:
            self.scrollY = -20
        elif cy < - 890:
            self.scrollY = 1280
        else: self.scrollY = 390 - cy
###########################################################################
    def redrawAll(self, screen): pass

    def drawStart(self,screen):
        if self.waitingToStart:
            width = 500
            start = 0
            screen.blit(self.startImg, pygame.Rect(start,100,500,500))

    def drawHelp(self,screen):
        if self.inHelp:
            width = 500
            start = 0
            imgNum = self.pageCount % 3 + 1
            if imgNum == 1:
                image = self.helpImg1
            elif imgNum == 2:
                image = self.helpImg2
            elif imgNum == 3:
                image = self.helpImg3
            screen.blit(image, pygame.Rect(start,100,500,500) )

    def drawSelectionInfo(self,screen):
        font = pygame.font.SysFont("Helvetica", 22)
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.width / 3, self.height - 22, self.width * 0.67, 22))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.width / 3, self.height - 22, self.width * 0.67, 22),1)
        if isinstance(self.selected[0], Building):
            if type(self.selected[0]) == Base:
                surf1 = font.render(f"Base: 'u' to upgrade; cost: 100; if level >= 1:'m' to build advanced building", True, (0,0,0))
                screen.blit(surf1, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))
            elif isinstance(self.selected[0], ImmuneSystem):
                surf_ = font.render(f"Advanced building: produce powerful macrophages, cost:{self.selected[0].producingCost}", True, (0,0,0))
                screen.blit(surf_, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))
            else:
                surf2 = font.render(f"Building: 'c' to produce cells; cost: 5", True, (0,0,0))
                screen.blit(surf2, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))
        else:
            printPhage = printCell = False
            if len(self.selected) == 1 and (not isinstance(self.selected[0], Macrophage)):
                msg = f"Cell: level {self.selected[0].ad // 2};'f':farm;'u':merge another cell;'a':attack;'i':freeze"
                surf6 = font.render(msg, True, (0,0,0))
                screen.blit(surf6, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))
                return
            for cell in self.selected:
                if isinstance(cell, Macrophage):
                    printPhage = True
                if not isinstance(cell, Macrophage) and isinstance(cell, Cell):
                    printCell = True
            if printPhage and printCell:
                surf3 = font.render(f"Macrophage and cell:'a' to attack, rightclick to move", True, (0,0,0))
                screen.blit(surf3, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))
            elif printPhage:
                surf4 = font.render(f"Macrophage:'a' to attack, huge attack power", True, (0,0,0))
                screen.blit(surf4, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))
            elif printCell:
                surf5 = font.render(f"Normal cell->'f':farm;'u':merge another cell;'a':attack;'i':freeze enemy", True, (0,0,0))
                screen.blit(surf5, pygame.Rect(self.width / 3 + 3, self.height - 20, self.width * 0.67, 20))

    def drawAskContinue(self,screen):
        self.askScreen = AskContinue(self)
        self.askScreen.draw(screen)

    def drawGameOver(self, screen):
        font = pygame.font.Font(None,35)
        text = font.render(f'You have scored {self.player.score}.', True, (0,0,0))
        rect = pygame.Rect(self.width/3, self.height / 3, self.width * 0.4, self.height / 6)
        pygame.draw.rect(screen, pygame.Color('#9e9e9e'), rect) # grey box
        pygame.draw.rect(screen, (0,0,0), rect, 2 ) # outline
        rect1 = pygame.Rect(self.width * 0.4, self.height * 0.4, self.width * 0.4, self.height / 6)
        screen.blit(text, rect1) # text
    
    def drawMiniMap(self,minimap):
        belongings = self.player.cells + self.player.buildings
        for item in belongings:
            cx,cy = item.x /15, item.y / 15 + 87
            color = pygame.Color('#424242')
            r = 26
            pygame.draw.circle(minimap,color,(int(cx),int(cy)),r)
        g = pygame.Color('#4caf50')
        for cell in self.player.cells:
            pygame.draw.circle(minimap,g,(int(cell.x /15), int(cell.y/15) + 87), 2)
        blue = pygame.Color('#42a5f5')
        for building in self.player.buildings:
            rect = pygame.Rect(building.x/15 -2, building.y/15 + 85, 4, 4)
            pygame.draw.rect(minimap,blue,rect)
        red = pygame.Color('#ff1744')
        purple = pygame.Color('#ea80fc')
        for virus in self.player.visible:
            color = red if isinstance(virus, Virus) else purple
            pygame.draw.circle(minimap,color,(int(virus.x/15),int(virus.y/15)+87),2)

        view_rect = pygame.Rect( - int(self.scrollX / 15), 87 - int(self.scrollY / 15), 53, 52 )
        pygame.draw.rect(minimap, (255,255,255),view_rect,True)

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption(self.title)
        screen.set_alpha(None)

        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            minimap = pygame.Surface((140,140))    
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
                # freeze
                elif pygame.key.get_pressed()[pygame.K_i] and \
                    pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.checkForFreeze((x - self.scrollX, y - self.scrollY))
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
                    # cheats
                    if pygame.key.get_pressed()[pygame.K_F1]:
                        self.player.resource += 200

                    if self.inHelp:
                        if pygame.key.get_pressed()[pygame.K_z]:
                            self.inHelp = False
                            self.isPaused = False
                        elif pygame.key.get_pressed()[pygame.K_LEFT]:
                            self.pageCount -= 1
                        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                            self.pageCount += 1
                    self._keys[event.key] = True
                    if pygame.key.get_pressed()[pygame.K_b]:
                        (x,y) = pygame.mouse.get_pos()
                        self.player.build(x - self.scrollX, y - self.scrollY)
                    if pygame.key.get_pressed()[pygame.K_m]:
                        (x,y) = pygame.mouse.get_pos()
                        self.player.buildBig(x - self.scrollX, y - self.scrollY)
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        if pygame.key.get_pressed()[pygame.K_1]:
                            self.grouping[pygame.K_1] = self.selected
                        if pygame.key.get_pressed()[pygame.K_2]:
                            self.grouping[pygame.K_2] = self.selected
                        if pygame.key.get_pressed()[pygame.K_3]:
                            self.grouping[pygame.K_3] = self.selected
                    self.keyPressed(event.key)

            #####################################################
            ################### Drawings ########################
            #fill background colors of surfaces
            screen.fill(pygame.Color('#fff59d'))#'#a1887f')) #(255, 255, 179)

            self.map.draw(screen)
            # draw everything
            self.player.draw(screen)
            self.AI.draw(screen)
            
            # draw selection box
            if self.selectionBox != None:
                temp_rect = self.selectionBox.copy()
                temp_rect.move_ip(self.scrollX, self.scrollY)
                pygame.draw.rect(screen, (0,0,0),temp_rect,True)
                self.selectionBox = None

            
            self.player.drawSpecs(screen)
            self.drawMiniMap(minimap)
            
            screen.blit(minimap, pygame.Rect(0, 59, 142, 142))

            # draw selection info
            if len(self.selected) > 0:
                self.drawSelectionInfo(screen)
            
            self.drawStart(screen)
            self.drawHelp(screen)
            
            if self.askContinue:
                self.drawAskContinue(screen)
            if self.gameOver:
                self.drawGameOver(screen)

            pygame.display.flip()

        pygame.quit()

game = PygameGame()
game.run()