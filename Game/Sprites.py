import pygame as pg
import random

class Player(pg.sprite.Sprite):
    """
    Class that represents a player.
    Extends from the pygame Sprite class.
    """
    def __init__(self, screenWidth, screenHeight):
        """
        Constructor for the player.
        :param screenWidth: The screen width that will be the player's x coordinate limit
        :param screenHeight: The screen height that will be the player's y coordinate limit
        """
        super().__init__()
        self.screenW = screenWidth   # Screen dimensions
        self.screenH = screenHeight
        self.image = pg.Surface((35,35))  # Player's surface dimensions
        self.image.fill((25,217,255))
        self.rect = self.image.get_rect()  # Fetch the rectangle object that has the dimensions of the image

        self.lives = 3
        self.shield = False
        self.cross = False
        self.bomb = Bomb(screenHeight, screenHeight)  # Creates a bomb sprite
        self.placedBomb = False

    def update(self, keys, blocks, fakeBlocks, powerUps):
        """
        Updates the player according to the keys pressed and detected collisions.
        :param keys: A list of all the keys pressed per frame
        :param blocks: A list of pygame Rects that represent walls
        :param fakeBlocks: A list of pygame Rects that represent fake walls
        :param powerUps: List of powerUps on the map
        :return: null
        """
        if keys[pg.K_w]:
            self.rect.move_ip(0,-5)
            if self.rect.collidelist(blocks) != -1 or self.rect.collidelist(fakeBlocks) != -1: # Detects collision
                self.rect.move_ip(0,5) # Keeps the player from overlapping with walls
        if keys[pg.K_a]:
            self.rect.move_ip(-5, 0)
            if self.rect.collidelist(blocks) != -1 or self.rect.collidelist(fakeBlocks) != -1:
                self.rect.move_ip(5,0)
        if keys[pg.K_s]:
            self.rect.move_ip(0, 5)
            if self.rect.collidelist(blocks) != -1 or self.rect.collidelist(fakeBlocks) != -1:
                self.rect.move_ip(0, -5)
        if keys[pg.K_d]:
            self.rect.move_ip(5,0)
            if self.rect.collidelist(blocks) != -1 or self.rect.collidelist(fakeBlocks) != -1:
                self.rect.move_ip(-5,0)

        # Keep player on-screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screenW:
            self.rect.right = self.screenW
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.screenH:
            self.rect.bottom = self.screenH

    def placeBomb(self):
        """
        Places a bomb on the screen
        :return: null
        """
        self.bomb.setCoord(self.rect.centerx, self.rect.centery)
        self.bomb.resetTime()
        self.placedBomb = True

class Enemy(pg.sprite.Sprite):
    """
    Class that represents an enemy.
    Extends from the pygame Sprite class.
    """

    def __init__(self, screenWidth, screenHeight, lives, speed, id):
        """
        Constructor for the player.
        :param screenWidth: The screen width that will be the player's x coordinate limit
        :param screenHeight: The screen height that will be the player's y coordinate limit
        :param lives: The number of lives the enemy will have
        :param speed: The speed of the enemy's movement
        """
        super().__init__()
        self.screenW = screenWidth  # Screen dimensions
        self.screenH = screenHeight
        self.image = pg.Surface((35, 35))  # Player's surface dimensions
        self.image.fill((25, 217, 255))
        self.rect = self.image.get_rect()  # Fetch the rectangle object that has the dimensions of the image

        self.lives = lives
        self.shield = False
        self.cross = False
        self.speed = speed
        self.id = id
        self.evade = random.randint(7,9)
        # TODO: add attributes and parameters for DNA probabilities
        self.bomb = Bomb(screenHeight, screenHeight)  # Creates a bomb sprite
        self.placedBomb = False

    def update(self, blocks, fakeBlocks):
        # TODO: update enemy movement, right/left/up/down += self.speed

        # Keep enemy on-screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screenW:
            self.rect.right = self.screenW
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.screenH:
            self.rect.bottom = self.screenH

    def placeBomb(self):
        """
        Places a bomb on the screen
        :return: null
        """
        self.bomb.setCoord(self.rect.centerx, self.rect.centery)
        self.bomb.resetTime()
        self.placedBomb = True

    def doAction(self):
        # TODO: choose action from dna probs
        # if place bomb -> self.placeBomb() and get away
        # if hide, powerup, enemy -> A* -> move algorithm
        pass


class Bomb(pg.sprite.Sprite):
    """
    Class that represents a bomb.
    Extends from the pygame Sprite class.
    """
    def __init__(self, screenWidth, screenHeight):
        """
        Constructor for the bomb.
        :param screenWidth: The screen width that will be the bomb's x coordinate limit
        :param screenHeight: The screen height that will be the bomb's y coordinate limit
        """
        super().__init__()
        self.screenW = screenWidth
        self.screenH = screenHeight
        self.image = pg.image.load("Resources/Bomb.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (40,40))

        self.fireImage = pg.image.load("Resources/Flame.png").convert_alpha()
        self.fireImage = pg.transform.scale(self.fireImage, (40, 40))

        self.rect = self.image.get_rect()
        self.time = 3000

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

    def explode(self, fakeBlocks, characters, mapMatrix, powerUps, cross):
        """
        Destroys the fake walls adjacent to the bomb and hits players
        :param fakeBlocks: list of all fake walls on the map
        :param characters: sprite group of all the characters on the game
        :param mapMatrix: the matrix that represents the game map
        :param powerUps: sprite group of all the power ups on the map
        :param cross: boolean that tells if bomb will explode in a cross form or not
        :return: null
        """

        index = 0
        for rect in fakeBlocks:  # Destroy blocks and update map matrix
            if not cross and (rect.colliderect(self.rectUp) or rect.colliderect(self.rectDown) or
                              rect.colliderect(self.rectLeft) or rect.colliderect(self.rectRight)):
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
        for character in characters.sprites():  # Checks every character for bomb collision
            if character.rect.colliderect(self.rectUp) or character.rect.colliderect(self.rectDown) or \
                    character.rect.colliderect(self.rectLeft) or character.rect.colliderect(self.rectRight) or \
                    character.rect.colliderect(self.rect):
                if character.shield: # TODO: check if enemies shield works
                    character.shield = False
                else:
                    character.lives -= 1

                if character.lives == 0:
                    character.kill()
                    # TODO: check if enemies are removed when dead
            index += 1

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
        # TODO: check if enemies power-ups work
        if self.type == "life":
            character.lives += 1
        elif self.type == "shield":
            character.shield = True
