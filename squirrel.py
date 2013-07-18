import random,sys,time,math,pygame
from pygame.locals import *
fps = 30
winwidth = 640
winheight = 480
half_width = int(winwidth/2)
half_height = int(winheight/2)
grass = (24,255,0)
white = (255,255,255)
red = (255,0,0)
cameraslack = 90
moveRate = 9
bounceRate = 6
bounceHeight = 30
startSize = 25
winsize = 300
invulTime = 2
gameOverTime = 4
maxHealth = 3
numGrass = 80
numSqrls = 15
sqrlsMinSpeed = 3
sqrlsMaxSpeed = 7
dirChangeFreq = 2
left = 'left'
right = 'right'

def main():
	global FPSCLOCK,DISPLAYSURF,BASICFONT,L_SQRL_IMG,R_SQRL_IMG,GRASSIMAGES
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	pygame.display.set_icon(pygame.image.load('gameicon.png'))
	DISPLAYSURF = pygame.display.set_mode((winwidth,winheight))
	pygame.display.set_caption('Squirel Eat Squirel')
	BASICFONT = pygame.font.Font('freesansbold.ttf',32)
	L_SQRL_IMG = pygame.image.load('squirrel.png')
	R_SQRL_IMG = pygame.transform.flip(L_SQRL_IMG,True,False)
	GRASSIMAGES = []
	for x in range(1,5):
		GRASSIMAGES.append(pygame.image.load('grass%s.png' % x))
	while True:
		runGame()

def runGame():
	invulmode = False
	invulstarttime = 0
	gameOverMode = False
	gameOverStartTime = 0
	winMode = False
	gameOverSurf = BASICFONT.render('Game Over',True,white)
	gameOverRect = gameOverSurf.get_rect()
	gameOverRect.center = (half_width,half_height)
	winSurf = BASICFONT.render('You Have Achieved Omega Squirrel!',True,white)
	winRect = winSurf.get_rect()
	winRect.center = (half_width,half_height)
	winSurf2 = BASICFONT.render('(Press "r" to restart.)',True,white)
	winRect2 = winSurf2.get_rect()
	winRect2.center = (half_width,half_height + 30)
	cameraX = 0
	cameraY = 0
	grassObjs = []
	sqrlObjs = []
	playerobj = {'surface':pygame.transform.scale(L_SQRL_IMG,(startSize,startSize)), 'facing':left, 'size':startSize, 'x':half_width, 'y':half_height, 'bounce':0, 'health':maxHealth}
	moveLeft = False
	moveRight = False
	moveUp = False
	moveDown = False

	for x in range(10):
		grassObjs.append(makeNewGrass(cameraX,cameraY))
		grassObjs[x]['x'] = random.randint(0, winwidth)
		grassObjs[x]['y'] = random.randint(0, winheight)

	while True:
		if invulmode and time.time()-invulstarttime>invulTime:
			invulmode = False
		for sobj in sqrlObjs:
			sobj['x'] += sobj['movex']
			sobj['y'] += sobj['movey']
			sobj['bounce'] += 1
			if sobj['bounce'] > sobj['bouncerate']:
				sobj['bounce'] = 0
			if random.randint(0,99) < dirChangeFreq:
				sobj['movex'] = getRandomVelocity()
				sobj['movey'] = getRandomVelocity()
				if sobj['movex'] > 0:
					sobj['surface'] = pygame.transform.scale(R_SQRL_IMG,(sobj['width'],sobj['height']))
				else:
					sobj['surface'] = pygame.transform.scale(L_SQRL_IMG,(sobj['width'],sobj['height']))

		for x in range(len(grassObjs) -1,-1,-1):
			if isOutsideActiveArea(cameraX, cameraY, grassObjs[x]):
				del grassObjs[x]
		for x in range(len(sqrlObjs) -1,-1,-1):
			if isOutsideActiveArea(cameraX, cameraY, sqrlObjs[x]):
				del sqrlObjs[x]
		
		while len(grassObjs) < numGrass:
			grassObjs.append(makeNewGrass(cameraX, cameraY))
		while len(sqrlObjs) < numSqrls:
			sqrlObjs.append(makeNewSquirrel(cameraX, cameraY))

		playerX = playerobj['x'] + int(playerobj['size'] /2)
		playerY = playerobj['y'] + int(playerobj['size'] /2)
		if cameraX + half_width - playerX > cameraslack:
			cameraX = playerX + cameraslack - half_width
		elif playerX - (cameraX + half_width) > cameraslack:
			cameraX = playerX - cameraslack - half_width
		if cameraY + half_height - playerY > cameraslack:
			cameraY = playerY + cameraslack - half_height
		elif playerY - (cameraY + half_height) > cameraslack:
			cameraY = playerY - cameraslack - half_height

		DISPLAYSURF.fill(grass)
		for gobj in grassObjs:
			grect = pygame.Rect((gobj['x'] - cameraX, gobj['y'] - cameraY, gobj['width'], gobj['height']))
			DISPLAYSURF.blit(GRASSIMAGES[gobj['grassImage']], grect)

		for sobj in sqrlObjs:
			sobj['rect'] = pygame.Rect((sobj['x'] - cameraX,
			sobj['y'] - cameraY - getBounceAmount(sobj['bounce'],sobj['bouncerate'],sobj['bounceheight']),
			sobj['width'], sobj['height']))
			DISPLAYSURF.blit(sobj['surface'],sobj['rect'])

		flashon = round(time.time(), 1) * 10 % 2 == 1

		if not gameOverMode and not (invulmode and flashon):
			playerobj['rect'] = pygame.Rect((playerobj['x'] - cameraX,
			playerobj['y'] - cameraY - getBounceAmount(playerobj['bounce'],bounceRate,bounceHeight),
			playerobj['size'], playerobj['size']))
			DISPLAYSURF.blit(playerobj['surface'],playerobj['rect'])

		drawhealthmeter(playerobj['health'])

		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				if event.key == K_UP:
					moveDown = False
					moveUp = True
				elif event.key == K_DOWN:
					moveDown = True
					moveUp = False
				elif event.key == K_LEFT:
					moveLeft = True
					moveRight = False
					if playerobj['facing'] == right:
						playerobj['surface'] = pygame.transform.scale(L_SQRL_IMG,(playerobj['size'],playerobj['size']))
						playerobj['facing'] = left
				elif event.key == K_RIGHT:
					moveLeft = False
					moveRight = True
					if playerobj['facing'] == left:
						playerobj['surface'] = pygame.transform.scale(R_SQRL_IMG,(playerobj['size'],playerobj['size']))
						playerobj['facing'] = right
				elif winMode and event.key == K_r:
					return
			elif event.type == KEYUP:
				if event.key == K_LEFT:
					moveLeft = False
				elif event.key == K_RIGHT:
					moveRight = False
				elif event.key == K_UP:
					moveUp = False
				elif event.key == K_DOWN:
					moveDown = False
				elif event.key == K_ESCAPE:
					terminate()
		if not gameOverMode:
			if moveLeft:
				playerobj['x'] -= moveRate
			elif moveRight:
				playerobj['x'] += moveRate
			if moveUp:
				playerobj['y'] -= moveRate
			elif moveDown:
				playerobj['y'] += moveRate
			if moveLeft or moveRight or moveUp or moveDown or playerobj['bounce'] != 0:
				playerobj['bounce'] += 1
			if playerobj['bounce'] > bounceRate:
				playerobj['bounce'] = 0
			for x in range(len(sqrlObjs) -1,-1,-1):
				sobj = sqrlObjs[x]
				if 'rect' in sobj and playerobj['rect'].colliderect(sobj['rect']):
					if sobj['width'] * sobj['height'] < playerobj['size'] ** 2:
						playerobj['size'] += int((sobj['width'] * sobj['height'])**0.2)+1
						del sqrlObjs[x]
						if playerobj['facing'] == left:
							playerobj['surface'] = pygame.transform.scale(L_SQRL_IMG,(playerobj['size'],playerobj['size']))
						if playerobj['facing'] == right:
							playerobj['surface'] = pygame.transform.scale(R_SQRL_IMG,(playerobj['size'],playerobj['size']))
						if playerobj['size'] > winsize:
							winMode = True
					elif not invulmode:
						invulmode = True
						invulstarttime = time.time()
						playerobj['health'] -= 1
						if playerobj['health'] == 0:
							gameOverMode = True
							gameOverStartTime = time.time()
		else:
			DISPLAYSURF.blit(gameOverSurf, gameOverRect)
			if time.time() - gameOverStartTime > gameOverTime:
				return
		if winMode:
			DISPLAYSURF.blit(winSurf, winRect)
			DISPLAYSURF.blit(winSurf2, winRect2)
		pygame.display.update()
		FPSCLOCK.tick(fps)

def drawhealthmeter(health):
	for x in range(health):
		pygame.draw.rect(DISPLAYSURF, red, (15,5 + (10 * maxHealth) - x *10,20,10))
	for x in range(maxHealth):
		pygame.draw.rect(DISPLAYSURF, white, (15,5 + (10 * maxHealth) - x *10,20,10),1)


def terminate():
	pygame.quit()
	sys.exit()

def getBounceAmount(currentBounce, bounceRate, bounceHeight):
	return int(math.sin((math.pi/float(bounceRate)) * currentBounce) * bounceHeight)

def getRandomVelocity():
	speed = random.randint(sqrlsMinSpeed, sqrlsMaxSpeed)
	if random.randint(0,1) == 0:
		return speed
	else:
		return -speed

def getRandomOffCameraPos(cx,cy,objWidth, objHeight):
	camRect = pygame.Rect(cx,cy,winwidth,winheight)
	while True:
		x = random.randint(cx - winwidth, cx + 2*winwidth)
		y = random.randint(cy - winheight, cy + 2*winheight)
		objRect = pygame.Rect(x,y, objWidth, objHeight)
		if not objRect.colliderect(camRect):
			return x,y

def isOutsideActiveArea(cx,cy,obj):
	boundsLeft = cx - winwidth
	boundsTop = cy - winheight
	boundsRect = pygame.Rect(boundsLeft, boundsTop, winwidth*3, winheight*3)
	objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
	return not boundsRect.colliderect(objRect)

def makeNewSquirrel(cameraX, cameraY):
	sq = {}
	generalsize = random.randint(5,25)
	multiplier = random.randint(1,3)
	sq['width'] = (generalsize + random.randint(0,10)) * multiplier
	sq['height'] = (generalsize + random.randint(0,10)) * multiplier
	sq['x'],sq['y'] = getRandomOffCameraPos(cameraX, cameraY, sq['width'], sq['height'])
	sq['movex'] = getRandomVelocity()
	sq['movey'] = getRandomVelocity()
	if sq['movex'] < 0:
		sq['surface'] = pygame.transform.scale(L_SQRL_IMG,(sq['width'],sq['height']))
	else:
		sq['surface'] = pygame.transform.scale(R_SQRL_IMG,(sq['width'],sq['height']))
	sq['bounce'] = 0
	sq['bouncerate'] = random.randint(10,18)
	sq['bounceheight'] = random.randint(10,50)
	return sq

def makeNewGrass(cameraX, cameraY):
	gr = {}
	gr['grassImage'] = random.randint(0, len(GRASSIMAGES)-1)
	gr['width'] = GRASSIMAGES[0].get_width()
	gr['height'] = GRASSIMAGES[0].get_height()
	gr['x'], gr['y'] = getRandomOffCameraPos(cameraX,cameraY, gr['width'], gr['height'])
	gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']))
	return gr

if __name__ == '__main__':
	main()

