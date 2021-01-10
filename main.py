# Sudoku
# Author: Shanti Mickens
# Date: April 5, 2020

import pygame
import random

# initializes pygame, creates a window and font
pygame.init()
pygame.display.set_caption("Sudoku")
window = pygame.display.set_mode([710, 600])
font = pygame.font.Font('freesansbold.ttf', 32)
smallFont = pygame.font.Font('freesansbold.ttf', 10)

# button panel number, -1 means it is set to delete
currentNum = -1

# preset sudoku board
super_easy_game = [
	[6, 0, 5, 8, 7, 3, 2, 4, 1],
	[0, 8, 3, 2, 0, 4, 0, 0, 7],
	[0, 7, 0, 0, 9, 0, 8, 0, 0],
	[4, 0, 1, 0, 3, 2, 0, 6, 8],
	[8, 6, 2, 0, 4, 0, 1, 7, 0],
	[7, 3, 0, 0, 0, 8, 4, 0, 0],
	[0, 0, 8, 0, 6, 0, 0, 1, 4],
	[9, 4, 0, 3, 8, 1, 5, 2, 6],
	[3, 0, 6, 4, 0, 5, 0, 0, 9]
]

easy_game = [
	[0, 0, 0, 8, 0, 3, 0, 0, 1],
	[0, 8, 3, 2, 0, 4, 0, 0, 7],
	[0, 7, 0, 0, 9, 0, 0, 0, 0],
	[0, 0, 1, 0, 0, 0, 0, 6, 8],
	[0, 6, 2, 0, 0, 0, 1, 7, 0],
	[7, 3, 0, 0, 0, 0, 4, 0, 0],
	[0, 0, 0, 0, 6, 0, 0, 1, 0],
	[9, 0, 0, 3, 0, 1, 5, 2, 0],
	[3, 0, 0, 4, 0, 5, 0, 0, 0]
]

class Cell:
	DEFAULT_BG = (255, 255, 255)
	HIGHLIGHT_BG = (240, 240, 240)
	DARK_HIGHLIGHT_BG = (220, 220, 220)
	SELECTED_BG = (200, 200, 200)
	DEFAULT_TEXT = (83, 147, 181)
	INVALID_TEXT = (199, 58, 102)
	GIVEN_TEXT = (100, 100, 100)

	def __init__(self, x, y, row, col):
		self.x = x
		self.y = y
		self.row = row
		self.col = col
		self.value = 0
		self.size = 50
		self.bgColor = self.DEFAULT_BG
		self.textColor = self.DEFAULT_TEXT
		self.notes = []

	def highlight(self):
		# highlights cell if it isn't selected
		if self.bgColor != self.SELECTED_BG:
			self.bgColor = self.HIGHLIGHT_BG

	def darkHighlight(self):
		# highlights cell if it isn't selected
		if self.bgColor != self.SELECTED_BG:
			self.bgColor = self.DARK_HIGHLIGHT_BG

	def unhighlight(self):
		self.bgColor = self.DEFAULT_BG

	def setSelected(self):
		self.bgColor = self.SELECTED_BG

	def resetTextColor(self):
		self.textColor = self.DEFAULT_TEXT

	def setInvalid(self):
		self.textColor = self.INVALID_TEXT

	def setGiven(self):
		self.textColor = self.GIVEN_TEXT
# end of cell class

class Board:
	def __init__(self):
		self.backtracks = 0
		self.solveSteps = []
		self.implications = []

		self.solved = False
		self.cellArray = []
		for i in range(9):
			self.cellArray.append([]);
			for j in range(9):
				self.cellArray[i].append(Cell(j*50+130, i*50+35, i, j)) # i and j for x and y positions are flipped, so it displays the board correctly

	def draw(self, window):
		global currentNum
		global font
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]

				# stores rectangle parameters
				cell.rect = pygame.Rect(cell.x, cell.y, cell.size, cell.size)
				# draws cells
				pygame.draw.rect(window, (200, 200, 200), cell.rect, 2)

				# fills cell if it is the same as the current number
				if str(currentNum) == str(cell.value):
					cell.darkHighlight()

				# draws cell background
				pygame.draw.rect(window, cell.bgColor, (cell.x+2, cell.y+2, cell.size-3, cell.size-3))

				# checks if cell has number to draw
				if cell.value > 0:
					text = font.render(str(cell.value), True, cell.textColor)
					window.blit(text, (cell.rect.x+(cell.rect.width/2)-text.get_width() // 2, cell.rect.y+2+(cell.rect.height/2)-text.get_height() // 2))

				# draws cell's notes
				cellNotes = ""
				for note in cell.notes:
					cellNotes += str(note)
				if cellNotes != "":
					noteText = smallFont.render(cellNotes, True, cell.GIVEN_TEXT)
					window.blit(noteText, (cell.rect.x+(cell.rect.width/2)-noteText.get_width() // 2, cell.rect.y+2+(cell.rect.height/2)-noteText.get_height() // 2))

		for i in range(3):
			for j in range(3):
				# draws sector border
				pygame.draw.rect(window, (100, 100, 100), (i*150+130, j*150+35, 50*3, 50*3), 2)

	def updateBoard(self, mouseX, mouseY):
		global currentNum
		self.clearHighlights()
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]

				if cell.x < mouseX and mouseX < cell.x + cell.size and cell.y < mouseY and mouseY < cell.y + cell.size:

					# highligts row, col, and sector of cell
					for item in self.getRow(i):
						item.highlight()
					for item in self.getCol(j):
						item.highlight()
					for item in self.getSector(i, j):
						item.highlight()

					# changes value if it is not a given value
					if cell.textColor != cell.GIVEN_TEXT:
						# resets cell text color, in case it was previously invalid

						cell.resetTextColor()
						# checks if value already exists in row, col, or sector
						# if it does, it sets that cell to be invalid
						for item in self.getRow(i):
							if item.value == currentNum and(item.row != cell.row or item.col != cell.col):
								cell.setInvalid()
						for item in self.getCol(j):
							if item.value == currentNum and (item.row != cell.row or item.col != cell.col):
								cell.setInvalid()
						for item in self.getSector(i, j):
							if item.value == currentNum and (item.row != cell.row or item.col != cell.col):
								cell.setInvalid()

						if currentNum == "X":
							# erases value
							cell.value = 0
						elif currentNum > 0:
							# sets cell value
							cell.value = currentNum

						# checks if board is complete
						if self.isComplete():
							self.solved = True
							print("solved")
					else:
						print("can't change text of given cell")

					# changes background color to selected bg color
					cell.setSelected()

					break

	def loadBoard(self, values):
		if len(values) == 9 and len(values[0]) == 9:
			for i in range(9):
				for j in range(9):
					self.cellArray[i][j].value = values[i][j]
					if values[i][j] != 0:
						self.cellArray[i][j].setGiven()
		else:
			print("error: board size is not valid")

	def isValid(self, i, j, n):
		for item in self.getRow(i):
			if item.value == n and(item.row != i or item.col != j):
				return False
		for item in self.getCol(j):
			if item.value == n and (item.row != i or item.col != j):
				return False
		for item in self.getSector(i, j):
			if item.value == n and (item.row != i or item.col != j):
				return False

		return True

	def isComplete(self):
		complete = True
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				if cell.value == 0 or cell.textColor == cell.INVALID_TEXT:
					# if 0 is found in a row or a cell is not valid, then it is not complete
					complete = False
					break
		return complete

	def getNextValidCell(self):
		for i in range(9):
			for j in range(9):
				if self.cellArray[i][j].value == 0:
					return i, j
		return -1, -1

	def makeImplications(self):
		for i in range(9):
			for j in range(9):
				self.takeNotes()
				cell = self.cellArray[i][j]
				if len(cell.notes) == 1:
					if self.isValid(i, j, cell.notes[0]):
						self.cellArray[i][j].value = cell.notes[0]
						self.solveSteps.insert(0, [i, j, cell.notes[0]])
						self.implications.insert(0, [i, j])

	def solve(self):
		# gets next open cell
		i, j = self.getNextValidCell()
		# puzzle is solved
		if i == -1:
			print(self.backtracks)
			self.printBoard()
			return True

		# tests 1-9 in next valid cell
		for n in range(1, 10):
			if self.isValid(i, j, n):
				self.cellArray[i][j].value = n
				self.solveSteps.insert(0, [i, j, n])

				# looks for places where only one number would be valid and makes an implication by putting it there
				self.makeImplications()
					
				if self.solve():
					# there is more puzzle left to solve
					return True

				# no more numbers to try in this cell, so removes value and backtracks to find a solution
				self.backtracks += 1
				self.cellArray[i][j].value = 0
				self.solveSteps.insert(0, [i, j, 0])

				# clears out any implications made
				for imp in self.implications:
					i, j = imp
					self.cellArray[i][j].value = 0
					self.solveSteps.insert(0, [i, j, 0])
				self.implications = []
				
		return False # no number 1-9 was valid in this cell

	def clearHighlights(self):
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				cell.unhighlight()

	def takeNotes(self):
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				# clears old notes
				cell.notes = []
				if cell.value == 0:
					cellRow = self.toArray(self.getRow(cell.row))
					cellCol = self.toArray(self.getCol(cell.col))
					cellSector = self.toArray(self.getSector(cell.row, cell.col))
					for x in range(10):
						if not x in cellRow and not x in cellCol and not x in cellSector:
							# if values is not in row, col, or sector it adds it to that cell's notes
							cell.notes.append(x)

	def getRow(self, i):
		row = []
		for j in range(9):
			row.append(self.cellArray[i][j])
		return self.cellArray[i]

	def getCol(self, j):
		col = []
		for i in range(9):
			col.append(self.cellArray[i][j])
		return col

	def getSector(self, i, j):
		sector_row = 6
		sector_col = 6
		if i < 3:
			sector_row = 0
		elif i < 6:
			sector_row = 3

		if j < 3:
			sector_col = 0
		elif j < 6:
			sector_col = 3

		sectorCells = []
		for x in range(3):
			for y in range(3):
				sectorCells.append(self.cellArray[x + sector_row][y + sector_col])
		return sectorCells

	# returns array of cell values
	def toArray(self, cells):
		arr = []
		for cell in cells:
			arr.append(cell.value)
		return arr

	def printBoard(self):
		for i in range(9):
			print(self.toArray(self.getRow(i)))
# end of board class

class Button:
	def __init__(self, x, y, w, h, value):
		self.x = x
		self.y = y
		self.value = value
		self.width = w
		self.height = h
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

	def draw(self, window):
		global currentNum
		global font
		# draws cells
		pygame.draw.rect(window, (200, 200, 200), self.rect, 2)

		# draws button text
		color = (83, 147, 181)
		if currentNum == self.value:
			color = (199, 58, 102)
		text = font.render(str(self.value), True, color)
		window.blit(text, (self.rect.x+(self.rect.width/2)-text.get_width() // 2, self.rect.y+2+(self.rect.height/2)-text.get_height() // 2))
# end of button class

def draw_window(window):
	window.fill((255, 255, 255)) # clears background
	board.draw(window) # draws sudoku board
	solveBtn.draw(window)

	# draws buttons
	for button in buttons:
		button.draw(window)

	# refreshes display
	pygame.display.update()




# creates board and loads preset sudoku game
board = Board()
board.loadBoard(easy_game)
# updates board notes
# board.takeNotes()

# sets up buttons
buttons = []
for i in range(9):
	buttons.append(Button(i*50+50, 515, 50, 50, i+1))
buttons.append(Button(9*50+50, 515, 50, 50, "X"))

# adds a solve button
solveBtn = Button(10*50+50, 515, 110, 50, "solve")
solvePuzzle = False

# clears notes
for i in range(9):
	for j in range(9):
		board.cellArray[i][j].notes = []

# creates main loop
run = True
while run:
	# kind of like clock in game in milliseconds
	pygame.time.delay(100)

	# checks for events (mouse pressed, mouse moved, etc.)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# stops main loop  when user exits game
			pygame.quit() # quit pygame
			quit() # quit program
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			# set the x, y positions of the mouse
			mouse_x, mouse_y = event.pos

			# checks if a cell was clicked
			board.updateBoard(mouse_x, mouse_y)

			# checks if solve button was clicked
			if solveBtn.x < mouse_x and mouse_x < solveBtn.x + solveBtn.width:
				if solveBtn.y < mouse_y and mouse_y < solveBtn.y + solveBtn.height:
					# clears any user progress and solves puzzle
					board.loadBoard(easy_game)
					board.solve()
					# resets board for animation
					board.loadBoard(easy_game)

					solvePuzzle = True

					# checks how many backtracks it took to solve puzzle to determine animation speed
					if board.backtracks < 100:
						animationSpeed = 30
					elif board.backtracks < 300:
						animationSpeed = 40
					elif board.backtracks < 600:
						animationSpeed = 60
					elif board.backtracks < 900:
						animationSpeed = 90
					elif board.backtracks < 1400:
						animationSpeed = 130
					elif board.backtracks < 2000:
						animationSpeed = 180
					elif board.backtracks < 3000:
						animationSpeed = 250
					else:
						animationSpeed = 500

			# checks if a button was clicked
			for button in buttons:
				if button.x < mouse_x and mouse_x < button.x + button.width:
					if button.y < mouse_y and mouse_y < button.y + button.height:
						# if button was already selected it unselects it
						if currentNum != button.value:
							currentNum = button.value
						else:
							currentNum = -1

	if solvePuzzle:
		for _ in range(100):
			if len(board.solveSteps) > 0:
				nextStep = board.solveSteps.pop()
				board.cellArray[nextStep[0]][nextStep[1]].value = nextStep[2]
				board.cellArray[nextStep[0]][nextStep[1]].highlight()
				board.takeNotes()
			else:
				board.clearHighlights()
				solvePuzzle = False
				break

	draw_window(window)
# end of main loop



