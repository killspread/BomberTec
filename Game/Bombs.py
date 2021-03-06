import pygame as pg
import random

class Bomb(pg.sprite.Sprite):
    """
    Class that represents a bomb.
    Extends from the pygame Sprite class.
    """
    def __init__(self, screenWidth, screenHeight, bombId, owner):
        """
        Constructor for the bomb.
        :param screenWidth: The screen width that will be the bomb's x coordinate limit
        :param screenHeight: The screen height that will be the bomb's y coordinate limit
        :param bombId: id to represent the bomb
        :param bombId: player who the bomb belongs to
        """
        super().__init__()
        self.id = bombId
        self.screenW = screenWidth
        self.screenH = screenHeight
        self.image = pg.image.load("Resources/Bomb.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (40,40))

        self.fireImage = pg.image.load("Resources/Flame.png").convert_alpha()
        self.fireImage = pg.transform.scale(self.fireImage, (40, 40))

        self.rect = self.image.get_rect()
        self.time = 3000

        self.owner = owner
        self.rectUp = None
        self.rectDown = None
        self.rectLeft = None
        self.rectRight = None

    def setCoord(self, playerCenterX, playerCenterY):
        """
        Sets the coordinates of the bomb according to the player's center coordinates
        :param playerCenterX: The x coordinate of the player's center
        :param playerCenterY: The y coordinate of the player's center
        :return:
        """
        wallWidth = 40
        bombX = 0
        bombY = 0
        foundX = False
        foundY = False

        if playerCenterX % wallWidth == 0 or playerCenterY % wallWidth == 0:
            # Checks if the center fits exactly in the map block division
            if playerCenterX % wallWidth == 0:
                bombX = playerCenterX
                foundX = True
            if playerCenterY % wallWidth == 0:
                bombY = playerCenterY
                foundY = True
        if not foundX:
            # Searches for the new x coordinate of the bomb
            x1 = 0
            while not x1 < playerCenterX < x1 + wallWidth:
                x1 += wallWidth
            bombX = x1
        if not foundY:
            # Searches for the new y coordinate of the bomb
            y1 = 0
            while not y1 < playerCenterY < y1 + wallWidth:
                y1 += wallWidth
            bombY = y1

        self.rect.topleft = (bombX, bombY)

        # Sets coordinates of bomb collisions
        self.rectUp = pg.Rect(self.rect.topleft[0], self.rect.topleft[1] - 40, 40, 40)
        self.rectDown = pg.Rect(self.rect.bottomleft[0], self.rect.bottomleft[1], 40, 40)
        self.rectLeft = pg.Rect(self.rect.topleft[0] - 40, self.rect.topleft[1], 40, 40)
        self.rectRight = pg.Rect(self.rect.topright[0], self.rect.topright[1], 40, 40)

    def update(self):
        """
        Substracts from the "time" attribute, so the bomb is closer to explosion
        :return: null
        """
        self.time -= 15

    def resetTime(self):
        """
        Resets the bomb time to the initial value
        :return:
        """
        self.time = 3000

    def draw(self, screen):
        """
        Draws the bomb on-screen
        :param screen: The surface where the bomb will be drawn
        :return: null
        """
        screen.blit(self.image, self.rect)

    def drawFlames(self, screen, cross):
        """
        Draws the explosion flames on-screen
        :param screen: The surface where the bomb will be drawn
        :param cross: boolean that tells if bomb will explode in a cross form or not
        :return: null
        """
        if not cross:
            screen.blit(self.fireImage, self.rect)
            screen.blit(self.fireImage, self.rectUp)
            screen.blit(self.fireImage, self.rectDown)
            screen.blit(self.fireImage, self.rectLeft)
            screen.blit(self.fireImage, self.rectRight)

    def explode(self, fakeBlocks, characters, mapMatrix, powerUps, allWalls):
        """
        Destroys the fake walls adjacent to the bomb and hits players
        :param fakeBlocks: list of all fake walls on the map
        :param characters: sprite group of all the characters on the game
        :param mapMatrix: the matrix that represents the game map
        :param powerUps: sprite group of all the power ups on the map
        :param allWalls: list of all walls on the game
        :return: null
        """

        index = 0
        hitBlocks = False
        rectList = []
        for rect in fakeBlocks:  # Destroy blocks and update map matrix
            if not self.owner.cross and (rect.colliderect(self.rectUp) or rect.colliderect(self.rectDown) or
                              rect.colliderect(self.rectLeft) or rect.colliderect(self.rectRight)):
                hitBlocks = True
                rectList.append(rect)
                mapMatrix[rect.i][rect.j] = 0

                # Power-Up probability
                prob = random.randint(0, 4)
                if prob == 0 or prob == 3:  # 40% chance to generate a power up
                    prob = random.randint(0, 3)
                    if prob == 0:
                        typeP = "life"
                    elif prob == 1:
                        typeP = "shield"
                    elif prob == 2:
                        typeP = "cross"
                    else:
                        typeP = "shoe"

                    newPow = PowerUp(typeP, rect.centerx, rect.centery)
                    powerUps.add(newPow)

                fakeBlocks.pop(index)

            index += 1

        index = 0
        hitPlayer = False
        for character in characters.sprites():  # Checks every character for bomb collision
            if (character.rect.colliderect(self.rectUp) or character.rect.colliderect(self.rectDown) or
                character.rect.colliderect(self.rectLeft) or character.rect.colliderect(self.rectRight) or
                character.rect.colliderect(self.rect)) and self.id != character.id:
                hitPlayer = True
                if character.shield:
                    character.shield = False
                else:
                    character.lives -= 1

                if character.lives == 0:
                    character.bomb.kill()
                    character.kill()
            index += 1

        if not self.owner.isPlayer:
            if len(rectList) == 0:
                if self.rectUp.collidelist(allWalls) != -1:
                    rectList.append(self.rectUp)
                if self.rectRight.collidelist(allWalls) != -1:
                    rectList.append(self.rectRight)
                if self.rectLeft.collidelist(allWalls) != -1:
                    rectList.append(self.rectLeft)
                if self.rectDown.collidelist(allWalls) != -1:
                    rectList.append(self.rectDown)

            if len(rectList) != 0:
                self.owner.nextRect = random.choice(rectList)
                for wall in allWalls:
                    if self.owner.nextRect.center == wall.center and mapMatrix[wall.i][wall.j] == 0:
                        self.owner.nextNode = (wall.i, wall.j)
                        break
                self.owner.path.append(self.owner.nextNode)

            if hitBlocks:
                self.owner.blockRecord.append(1)
            else:
                self.owner.blockRecord.append(0)
            if hitPlayer:
                self.owner.enemiesRecord.append(1)
            else:
                self.owner.enemiesRecord.append(0)

class PowerUp(pg.sprite.Sprite):
    """
    Class that represents a power-up.
    Extends from the pygame Sprite class.
    """

    def __init__(self, typeP, centerX, centerY):
        """
        Constructor for the power up
        :param typeP: defines which type of power-up will be created
        :param centerX: the x coordinate of the rect topleft
        :param centerY: the y coordinate of the rect topleft
        """
        super().__init__()
        self.type = typeP
        self.spriteSheet = pg.image.load("Resources/PowerUps.png").convert()

        if self.type == "life":
            self.spriteSheet.set_clip(20, 80, 30, 29)
            self.image = self.spriteSheet.subsurface(self.spriteSheet.get_clip()).convert()
            self.image = pg.transform.scale(self.image, (30, 30))
            self.image.set_colorkey((0, 0, 0))
        elif self.type == "shield":
            self.spriteSheet.set_clip(115, 80, 29, 29)
            self.image = self.spriteSheet.subsurface(self.spriteSheet.get_clip()).convert()
            self.image = pg.transform.scale(self.image, (30, 30))
            self.image.set_colorkey((0, 0, 0))
        elif self.type == "cross":
            self.spriteSheet.set_clip(212, 80, 29, 29)
            self.image = self.spriteSheet.subsurface(self.spriteSheet.get_clip()).convert()
            self.image = pg.transform.scale(self.image, (30, 30))
            self.image.set_colorkey((0, 0, 0))
        elif self.type == "shoe":
            self.spriteSheet.set_clip(179, 80, 29, 29)
            self.image = self.spriteSheet.subsurface(self.spriteSheet.get_clip()).convert()
            self.image = pg.transform.scale(self.image, (30, 30))
            self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = (centerX, centerY)

    def assignPowerUp(self, character):
        """
        Assigns the power up specific benefit to the character entered as a parameter
        :param character: the character who will receive the power-up
        :return: null
        """
        if self.type == "life":
            character.lives += 1
        elif self.type == "shield":
            character.shield = True
