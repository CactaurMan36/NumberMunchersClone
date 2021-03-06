import pygame

from gameobject.GameObject import Munchable
from level.Level import Level

class Board:
	def __init__(self, topLeft, width, height, surface):
		self.topLeft = topLeft
		self.surface = surface
		self.width = width
		self.height = height
		self.level = None
		self.player = None

		self.reset = False

		self.requireContinue = False
		self.endOfGame = False;

		self.titleFont = pygame.font.SysFont("Monospace", 72)
		self.indexFont = pygame.font.SysFont("Monospace", 48)
		self.continueFont = pygame.font.SysFont("Monospace", 32)
		self.scoreFont = pygame.font.SysFont("Monospace", 38)

		self.rows = 5
		self.cols = 6

		self.cellWidth = width/self.cols;
		self.cellHeight = height / self.rows;

		self.boardArray = []
		for x in range(0, self.cols):
			self.boardArray.append([])
			for y in range(0, self.rows):
				self.boardArray[x].append([])

		#Create some static images
		self.continueText = self.continueFont.render("Press Enter To Continue!", 1, (0,255,0))
		self.continueCoords = (self.surface.get_width()/2 - self.continueText.get_width()/2, self.surface.get_height() - self.topLeft['y'] + 6)

		self.endText = self.continueFont.render("Game Over! Press Enter to go back to the main menu.", 1, (0,255,0))
		self.endCoords = (self.surface.get_width()/2 - self.endText.get_width()/2, self.surface.get_height() - self.topLeft['y'] + 6)

		self.scoreText = self.scoreFont.render("Score: 0", 1, (255,255,255))
		self.scoreCoords = (self.topLeft['x'], self.surface.get_height() - self.topLeft['y']/2 - self.scoreText.get_height()/2)

	#Clears the board; helpful for cleaning up and switching levels
	def clearBoard(self):
		for x in range(0, self.cols):
			for y in range(0, self.rows):
				if(len(self.boardArray[x][y]) > 0):
					if(isinstance(self.boardArray[x][y][0], Munchable)):
						del self.boardArray[x][y][0]

		if(self.player != None):
			self.setPosition(self.player, self.cols/2, self.rows/2)

		self.removedMunchables = 0

	def getReset(self):
		return self.reset

	def resetBoard(self):
		self.reset = False
		self.requireContinue = False
		self.endOfGame = False;

		self.player.setLives(3)
		self.player.setPoints(0)

	#Sets a game object as the player
	def addPlayer(self, gameObject, x, y):
		self.player = gameObject;
		self.setPosition(gameObject, x, y)

	#Adds an object to the board at a given position
	def addGameObject(self, gameObject, x, y):
		self.setPosition(gameObject, x, y)

		self.boardArray[x][y].append(gameObject)

	#Adds an object to the board assuming the object knows where it should be already
	def addMunchable(self, gameObject):
		boardCoords = gameObject.get_boardCoords();
		x = boardCoords['x']
		y = boardCoords['y']

		self.addGameObject(gameObject, x, y)

	def removeMunchable(self, boardX, boardY):

		if len(self.boardArray[boardX][boardY]) > 0:
			munchable = self.boardArray[boardX][boardY][0]

			if(munchable != None and isinstance(munchable, Munchable)):
				if munchable.type in self.level.goodMunchableTypes:
					# I decided to use del instead of pop() here since I don't think we need the munchable after it's been eaten
					del self.boardArray[boardX][boardY][0]

					#Count how many munchables we've removed this level
					self.removedMunchables += 1

					#Increment score and update score display
					self.player.addPoints(20 + (5 * self.level.getIndex()))
					self.scoreText = self.scoreFont.render("Score: " + str(self.player.getPoints()), 1, (255, 255, 255))

					#If we've removed as many as exist in the level, move to the next level
					if(self.removedMunchables >= self.level.getNumOfGoodMunchables()):
						if len(Level.Levels) > (self.level.getIndex() + 1):
							self.requireContinue = True
						else:
							#Game is completed or create random challenge level
							self.endOfGame = True
				else:
					#We ate the wrong munchable :(
					self.player.removeLife()

					if self.player.getLives() < 0:
						self.endOfGame = True


	def setNewLevel(self, level):
		self.level = level;

		self.clearBoard()

		levelMunchables = self.level.generateMunchables()

		for i in range(0, len(levelMunchables)):
			self.addMunchable(levelMunchables[i])

		#Setup text
		self.levelText = self.titleFont.render(self.level.getLevelName(), 1, (255,255,255))
		self.levelIndexText = self.indexFont.render("Level: " + str(self.level.getIndex() + 1), 1, (255,255,255))

		levelTextX = self.surface.get_width()/2 - self.levelText.get_width()/2
		levelTextY = self.topLeft['y']/2 - self.levelText.get_height()/2

		self.levelTextCoords = (levelTextX, levelTextY)
		self.levelIndexCoords = (self.topLeft['x'], self.topLeft['y']/2 - self.levelIndexText.get_height()/2)

	def setPosition(self, gameObject, x, y):
		if x > self.cols or y > self.rows or x < 0 or y < 0:
			print "Position " + str(x) + " : " + str(y) +" off board"
			return

		#Calculate screen positon
		screenPos = self.calcScreenPos(x, y);

		#Set the game object's positions
		gameObject.set_boardCoords(x, y)
		gameObject.set_screenPos(screenPos['x'], screenPos['y'])

	def calcScreenPos(self, x, y):
		screenPos = {'x': 0, 'y': 0}

		screenX = (x * self.cellWidth)
		screenY = (y * self.cellHeight)

		screenPos['x'] = screenX
		screenPos['y'] = screenY

		return screenPos

	def events(self, event):

		#Get player pos
		playerPos = self.player.get_boardCoords()

		if event.type == pygame.KEYDOWN:
			# use this to find key values
			#print(event.key)

			if self.requireContinue == False and self.endOfGame == False:
				# Up
				if event.key == 119 or event.key == 273:
					if playerPos['y'] > 0:
						self.setPosition(self.player, playerPos['x'], playerPos['y'] - 1)

				# Left
				elif event.key == 97 or event.key == 276:
					if playerPos['x'] > 0:
						self.setPosition(self.player, playerPos['x'] - 1, playerPos['y'])

				# Down
				elif event.key == 115 or event.key == 274:
					if playerPos['y'] < self.rows - 1:
						self.setPosition(self.player, playerPos['x'], playerPos['y'] + 1)

				# Right
				elif event.key == 100 or event.key == 275:
					if playerPos['x']  < self.cols - 1:
						self.setPosition(self.player, playerPos['x'] + 1, playerPos['y'])

				# Space - Munching
				elif event.key == 32:
					playerX = playerPos['x']
					playerY = playerPos['y']

					self.removeMunchable(playerX, playerY);

			elif self.requireContinue and event.key == 13:
				nextLevel = Level.Levels[self.level.getIndex() + 1]
				self.setNewLevel(nextLevel)
				self.requireContinue = False

			elif self.endOfGame and event.key == 13:
				self.reset = True

		self.player.events(event)

	def draw(self):
		# draw the background, just a rectangle for now
		# to save memory we could maybe use screen.fill(color)
		originX = self.topLeft['x']
		originY = self.topLeft['y']
		background = pygame.Rect(originX, originY, self.width, self.height)
		bgColor = pygame.Color(0, 0, 0)
		lineColor = pygame.Color(255,0,255)
		pygame.draw.rect(self.surface, bgColor, background, 0)

		# draw grid lines
		for x in xrange(0, self.cols + 1):
			pygame.draw.line(self.surface, lineColor, ((x * self.cellWidth) + originX, originY), ((x * self.cellWidth) + originX, originY + self.height), 2)
		for y in xrange(0, self.rows + 1):
			pygame.draw.line(self.surface, lineColor, (originX, (y * self.cellHeight) + originY), (originX + self.width, (y * self.cellHeight) + originY), 2)

		# Draw everything stored on the board
		for x in xrange(0, self.cols):
			for y in xrange(0, self.rows):
				for i in xrange(0, len(self.boardArray[x][y])):
					self.boardArray[x][y][i].draw()

		self.player.draw()

	    #Draw level title text
		self.surface.blit(self.levelText, self.levelTextCoords)
		self.surface.blit(self.levelIndexText, self.levelIndexCoords)
		self.surface.blit(self.scoreText, self.scoreCoords)

		if self.requireContinue:
			self.surface.blit(self.continueText, self.continueCoords)
		elif self.endOfGame:
			self.surface.blit(self.endText, self.endCoords)

		#Draw lives
		imageWidth = self.player.getLivesImage().get_width()
		livesX = self.surface.get_width() - (imageWidth * self.player.getLives()) - (20 * self.player.getLives())
		livesY = self.surface.get_height() - self.topLeft['y']/2 - self.player.getLivesImage().get_height()/2
		for i in range(0, self.player.getLives()):
			lifeX = livesX + (imageWidth * i) - (5 * i)
			self.surface.blit(self.player.getLivesImage(), (lifeX, livesY))

	# TODO: get the immediate neighbors for a given cell, should be useful for enemy AI
	def getNeighbors(self, xIndex, yIndex):
		pass
