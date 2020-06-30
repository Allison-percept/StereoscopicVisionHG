﻿import viz
import vizact
import time
import threading
import random

from targetPositions import stimuliLocations
import vizfx.postprocess
# Use vizfx module to load models and generate effects
import vizfx

class BalloonTrial:
	
	direction = []
	viewDirection = []
	viewSpeed = None
	allowedBalloonDirection = []
	allowedViewDirection = []
	stimuliLocations = []
	fovMask = False
	startWaitTime = 0
	
	#static
	bts = []
	piazza = None
	balloons = []
	forward = [0,0,1]
	back = [0,0,-1]
	left = [-1,0,0]
	right = [1,0,0]
	up = [0,1,0]
	down = [0,-1,0]
	directionArray = [forward,back,left,right,up,down]
	#startPosition = [0,2,-2]
	startPosition = [0,2,-2]




	def startScene(self):
		#Enable full screen anti-aliasing (FSAA) to smooth edges
		viz.setMultiSample(4)

		viz.go()
		viz.window.setFullscreenMonitor(1)
		viz.window.setFullscreen(mode = viz.ON)
		
		#Increase the Field of View
		viz.MainWindow.fov(60)

		viz.MainView.setPosition(BalloonTrial.startPosition)
		
		#disable movement with mouse
		#viz.mouse.setScale(0,0)
		
		BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb')
		#BalloonTrial.piazza = viz.addChild('sky_background.osgb')

		for i in range(len(self.stimuliLocations)):
			balloon = viz.addChild('balloon3.osgb')
			#balloon = viz.addChild('balloon3.osgb')
			balloon.setScale([0.01,0.01,0.01])
			BalloonTrial.balloons.append(balloon)

		self.setBalloonsPosition()
		
		
		
		# Remove head light
		viz.MainView.getHeadLight().remove()
		
		# Add directional light
		vizfx.addDirectionalLight(euler=(0,45,0))
		if (self.fovMask):
			self.applyCircMasking()
		
	@staticmethod
	def applyRectMasking():
		from vizfx.postprocess.color import BrightnessEffect
		from vizfx.postprocess.composite import ViewportEffect
		effect = ViewportEffect(outside=BrightnessEffect(-1),pos=(0.25,0.25),size=(0.5,0.5))
		vizfx.postprocess.addEffect(effect)	
	
	@staticmethod
	def applyCircMasking():
		from vizfx.postprocess.composite import BlendMaskEffect
		from vizfx.postprocess.color import BrightnessEffect
		mask = viz.addTexture('mask.png')
		#mask = viz.addTexture('mask3.png')
		effect = BlendMaskEffect(mask,white=BrightnessEffect(-1))
		vizfx.postprocess.addEffect(effect)
		
	def setBalloons(self,balloons):
		self.balloons = balloons
		
	def setAllowedViewDirection(self,dirList):
		self.allowedViewDirection = dirList[:]
	def setAllowedBalloonDirection(self, dirList):
		self.allowedBalloonDirection = dirList[:]
		
	def getRandomViewDirection(self):
		 randDir = random.choice(self.allowedViewDirection)
		 return randDir
	def getRandomViewDirIndex(self):
		randDir = self.getRandomViewDirection()
		return self.getDirIndex(randDir)
	def getRandomBalloonDirection(self):
		 randDir = random.choice(self.allowedBalloonDirection)
		 return randDir
	def getRandomBalloonDirIndex(self):
		randDir = self.getRandomBalloonDirection()
		return self.getDirIndex(randDir)
	
	def getDirIndex(self,dir):
		for i in range(0,len(self.directionArray)):
			if directionEqual(dir,self.directionArray[i]):
				return i
		return False
	
	
	def setBalloonsPosition(self):
		for i in range(len(self.stimuliLocations)):
			BalloonTrial.balloons[i].setPosition(self.stimuliLocations[i])
		
	
	def hideBalloons(self):
		for i in range(len(self.stimuliLocations)):
			BalloonTrial.balloons[i].setPosition([0,0,-100])

		
	def startTrial(self, balloon, d=direction):
		print "===Trial Starts==="
		print "Set balloon positions."
		self.setBalloonsPosition()
		print "Wait for " + str(self.startWaitTime) + " second(s)."
		timer = threading.Timer(self.startWaitTime, self.startMoving, [balloon, d])
		timer.start()
		return
		
		
		
	def startMoving(self, balloon, d=direction):
		
		print "Ballons Moving in direction " + str(self.direction)
		print "View Moving in direction " + str(self.viewDirection)
		
		
		viz.MainView.velocity(self.viewDirection)
		balloon.addAction(vizact.move(self.direction, 1))
		timer = threading.Timer(1, self.resetPositions)
		timer.start()
		return


	def resetPositions(self):
		print "===Trial Resets==="
		self.hideBalloons()
		viz.MainView.setPosition(BalloonTrial.startPosition)
		viz.MainView.velocity([0,0,0])

	def setDirection(self, d):
		self.direction = d
		print "Balloon Direction is set to " + str(d)

	def setViewDirection(self,d):
		
		self.viewDirection = map(self.viewSpeedmapper, d)
		print "View direction is set to " + str(d)

	def viewSpeedmapper(self,i):
		return float(i) * self.viewSpeed


	def __init__(self, balloonDirections=None, viewDirections=None, viewSpeed=.5, expSet = "A1", fovMask = False, startWaitTime = 0):
		
		#add itself into list
		BalloonTrial.bts.append(self)
		self.stimuliLocations = stimuliLocations[expSet]
		
		
		if (balloonDirections==None):
			balloonDirections = [BalloonTrial.up,BalloonTrial.down]
		if (viewDirections==None):
			viewDirections = [BalloonTrial.forward,BalloonTrial.back]
			
		self.setAllowedBalloonDirection(balloonDirections)
		self.setAllowedViewDirection(viewDirections)
		self.viewSpeed=viewSpeed
		self.fovMask = fovMask
		self.startWaitTime = startWaitTime
		
		
		print self.allowedBalloonDirection
		print self.allowedViewDirection
			
def directionToString(dir):
	if(dir[0]>0):
		return "right"
	elif(dir[0]<0):
		return "left"
	elif(dir[1]>0):
		return "up"
	elif(dir[1]<0):
		return "down"
	elif(dir[2]>0):
		return "forward"
	elif(dir[2]<0):
		return "backward"

def directionEqual(d1,d2):
	if len(d1)!=len(d2):
		return False
	for i in range(len(d1)):
		if d1[i]!=d2[i]:
			return False
	return True


if __name__ == "__main__":
	
	bt = BalloonTrial()
	
	bt.startScene()
	#bt.applyRectMasking()
	#bt.applyCircMasking()


	vizact.onkeydown('1', bt.startMoving, bt.balloons[0] )
	vizact.onkeydown('2', bt.startMoving, bt.balloons[1] )
	vizact.onkeydown('3', bt.startMoving, bt.balloons[2] )
	vizact.onkeydown('4', bt.startMoving, bt.balloons[3] )


	vizact.onkeydown('z', bt.setDirection, bt.forward )
	vizact.onkeydown('x', bt.setDirection,bt.back )
	vizact.onkeydown('c', bt.setDirection, bt.left )
	vizact.onkeydown('v', bt.setDirection, bt.right )
	vizact.onkeydown('b', bt.setDirection, bt.up )
	vizact.onkeydown('n', bt.setDirection, bt.down )

	vizact.onkeydown('a', bt.setViewDirection, bt.forward )
	vizact.onkeydown('s', bt.setViewDirection, bt.back )
	vizact.onkeydown('d', bt.setViewDirection, bt.left )
	vizact.onkeydown('f', bt.setViewDirection, bt.right )
	vizact.onkeydown('g', bt.setViewDirection, bt.up )
	vizact.onkeydown('h', bt.setViewDirection, bt.down )
