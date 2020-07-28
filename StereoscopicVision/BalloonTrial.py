import viz
import vizact
import time
import threading
import random
import vizconnect

from expParameters import stimuliLocations, viewMovingSpeed, startViewPosition, trialDuration
import vizfx.postprocess
import constants
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
	startPosition = startViewPosition
	trialDuration = trialDuration
	device = constants.MONITOR #Monitor, HMD, EGG
	transport = None
	mode = constants.STEREO #STEREO, MONO, SYN

	@staticmethod
	def setDevice(device):
		BalloonTrial.device = device
		
	@staticmethod
	def setMode(mode):
		BalloonTrial.mode = mode

	@staticmethod
	def initializeRendering():
		"""
		A static method for initializing rendering
		"""
		
		#Enable full screen anti-aliasing (FSAA) to smooth edges
		viz.setMultiSample(4)
		
		#connect to designated device
		if(BalloonTrial.device == constants.MONITOR):
			viz.go()
			viz.window.setFullscreenMonitor(1)
			viz.window.setFullscreen(mode = viz.ON)
			
			#Increase the Field of View
			viz.MainWindow.fov(60)
			viz.MainView.setPosition(BalloonTrial.startPosition)
			
		elif(BalloonTrial.device == constants.HMD):
			vizconnect.go('vizconnect_rifts.py')
			BalloonTrial.transport = vizconnect.getTransport('wandmagiccarpet')
			BalloonTrial.transport.getNode3d().setPosition(BalloonTrial.startPosition)
			
		elif(BalloonTrial.device == constants.EGG):
			vizconnect.go('vizconnect_egg.py')
		
		#applying display mode conditions
		#for stereo condition, do nothing
		if(BalloonTrial.mode == constants.MONO):
			viz.MainWindow.stereo(viz.STEREO_LEFT)
			#viz.MainWindow.stereo(viz.STEREO_RIGHT)
		elif(BalloonTrial.mode == constants.SYN):
			viz.MainWindow.ipd(0)
		
		#disable movement with mouse
		viz.mouse.setScale(0,0)
		
		# Remove head light
		viz.MainView.getHeadLight().remove()
		
		# Add directional light
		vizfx.addDirectionalLight(euler=(0,45,0))
		


	def startScene(self):
		"""
		Starts the scene. Render the background and the stimulus.
		"""
		
		#call initializeRendering() static method
		BalloonTrial.initializeRendering()
		
		BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb')

		for i in range(len(self.stimuliLocations)):
			balloon = viz.addChild('balloon3.osgb')
			#balloon = viz.addChild('balloon3.osgb')
			balloon.setScale([0.01,0.01,0.01])
			BalloonTrial.balloons.append(balloon)

		self.setBalloonsPosition()
		if (self.fovMask):
			self.applyCircMasking()
		
	@staticmethod
	def applyRectMasking():
		"""
		Adds a rectangular masking onto device.
		"""
		
		from vizfx.postprocess.color import BrightnessEffect
		from vizfx.postprocess.composite import ViewportEffect
		effect = ViewportEffect(outside=BrightnessEffect(-1),pos=(0.25,0.25),size=(0.5,0.5))
		vizfx.postprocess.addEffect(effect)	
	
	@staticmethod
	def applyCircMasking():
		"""
		Adds a circular masking onto device.
		"""
		from vizfx.postprocess.composite import BlendMaskEffect
		from vizfx.postprocess.color import BrightnessEffect

		mask = viz.addTexture('mask3.png')
		effect = BlendMaskEffect(mask,white=BrightnessEffect(-1))
		vizfx.postprocess.addEffect(effect)
		
	def setBalloons(self,balloons):
		"""
		Set the list of balloons(stimuli).
		"""
		self.balloons = balloons
		
	def setAllowedViewDirection(self,dirList):
		"""
		Set the list of possible view movement direction.
		"""
		self.allowedViewDirection = dirList[:]
		
	def setAllowedBalloonDirection(self, dirList):
		"""
		Set the list of possible balloon(stimulus) movement direction.
		"""
		self.allowedBalloonDirection = dirList[:]
		
	def getRandomViewDirection(self):
		"""
		Gets a random direction from the list of possible view movement direction.
		"""
		randDir = random.choice(self.allowedViewDirection)
		return randDir
		 
	def getRandomViewDirIndex(self):
		"""
		Gets the index of a random direction from the list of possible view movement direction.
		"""
		randDir = self.getRandomViewDirection()
		return self.getDirIndex(randDir)
		
	def getRandomBalloonDirection(self):
		"""
		Gets a random direction from the list of possible balloon(stimulus) movement direction.
		"""
		randDir = random.choice(self.allowedBalloonDirection)
		return randDir
		
	def getRandomBalloonDirIndex(self):
		"""
		Gets the index of a random direction from the list of possible balloon(stimulus) movement direction.
		"""
		randDir = self.getRandomBalloonDirection()
		return self.getDirIndex(randDir)
	
	def getDirIndex(self,dir):
		"""
		Gets the index of a direction from the directionArray.
		"""
		for i in range(0,len(self.directionArray)):
			if directionEqual(dir,self.directionArray[i]):
				return i
		return False
	
	
	def setBalloonsPosition(self):
		"""
		Set positions of the balloons(stimuli).
		"""
		for i in range(len(self.stimuliLocations)):
			BalloonTrial.balloons[i].setPosition(self.stimuliLocations[i])
		
	
	def hideBalloons(self):
		"""
		Hides the stimuli.
		"""
		for i in range(len(self.stimuliLocations)):
			BalloonTrial.balloons[i].setPosition([0,0,-100])

		
	def startTrial(self, balloon, d=direction):
		"""
		Starts a trial.
		"""
		print "===Trial Starts==="
		print "Set balloon positions."
		self.setBalloonsPosition()
		print "Wait for " + str(self.startWaitTime) + " second(s)."
		timer = threading.Timer(self.startWaitTime, self.startMoving, [balloon, d])
		timer.start()
		return
		
		
		
	def startMoving(self, balloon, d=direction):
		"""
		Starts movement of both view and stimuli.
		"""
		
		print "Ballons Moving in direction " + str(self.direction)
		print "View Moving in direction " + str(self.viewDirection)
		
		#move view
		#if using device
		if(BalloonTrial.device == constants.MONITOR):
			viz.MainView.velocity(self.viewDirection)
		
		#if using HMD/EGG
		if (BalloonTrial.device == constants.HMD or BalloonTrial.device == constants.EGG):
			BalloonTrial.transport.getNode3d().addAction(vizact.move(self.viewDirection, BalloonTrial.trialDuration))
		
		balloon.addAction(vizact.move(self.direction, BalloonTrial.trialDuration))
		timer = threading.Timer(BalloonTrial.trialDuration, self.resetPositions)
		timer.start()
		return


	def resetPositions(self):
		"""
		Resets Positions of both view and stimuli.
		"""
		
		print "===Trial Resets==="
		self.hideBalloons()
		viz.MainView.setPosition(BalloonTrial.startPosition)
		viz.MainView.velocity([0,0,0])
		
		#if using HMD/EGG
		if (BalloonTrial.device == "HMD" or BalloonTrial.device == "EGG"):
			BalloonTrial.transport.getNode3d().setPosition(BalloonTrial.startPosition)


	def setDirection(self, d):
		"""
		Set direction of the stimuli.
		"""
		
		self.direction = d
		print "Balloon Direction is set to " + str(d)

	def setViewDirection(self,d):
		"""
		Set direction of the view.
		"""
		
		self.viewDirection = map(self.viewSpeedmapper, d)
		print "View direction is set to " + str(d)

	def viewSpeedmapper(self,i):
		"""
		Return the magnified viewSpeed. Used for mapping.
		"""
		
		return float(i) * self.viewSpeed


	def __init__(self, balloonDirections=None, viewDirections=None, viewSpeed=None, expSet = "A1", fovMask = False, startWaitTime = 0, device=None, mode=None):
		
		
		#add itself into list
		BalloonTrial.bts.append(self)
		self.stimuliLocations = stimuliLocations[expSet]
		
		
		if (balloonDirections==None):
			balloonDirections = [BalloonTrial.forward,BalloonTrial.back]
		if (viewDirections==None):
			viewDirections = [BalloonTrial.forward]
		if(device!=None):
			BalloonTrial.setDevice(device)
		if(mode!=None):
			BalloonTrial.setMode(mode)
		if(viewSpeed != None):
			viewSpeed = viewMovingSpeed
			
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
	
	bt = BalloonTrial(device="Monitor", mode="STEREO")
	
	bt.startScene()
	#bt.applyCircMasking()
	
	bt.setDirection(bt.forward)
	bt.setViewDirection(bt.forward)
	
	vizact.onkeydown('1', bt.startMoving, bt.balloons[0] )
	vizact.onkeydown('2', bt.startMoving, bt.balloons[1] )
	vizact.onkeydown('3', bt.startMoving, bt.balloons[2] )
	vizact.onkeydown('4', bt.startMoving, bt.balloons[3] )
	
	#This function will be called when a given 'key' is pressed.
	def onKeyDown(key):
		print key, ' is down.'
		if key == viz.KEY_TAB:
			print 'you hit the tab key'
		
	#Register the callback which to call the 'onKeyDown' function.
	viz.callback(viz.KEYDOWN_EVENT,onKeyDown) 


