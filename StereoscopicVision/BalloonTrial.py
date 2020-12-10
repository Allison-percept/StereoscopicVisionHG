import viz
import vizact
import time
import threading
import viztask
import random
import vizconnect

from expParameters import stimuliLocations, viewMovingSpeed, startViewPosition, trialDuration, trialWaitTime, maxDisplacement
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
	startWaitTime = trialWaitTime
	
	
	
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
	def applyFog(scene):
		"""
		Cover the entire scene with a fog, which color is the mean color of the view. 
		"""
		
		#an example of scene: viz.Scene1
		
		#color: rgb(183, 151, 113)
		scene.fogColor(0.72, 0.59, 0.44)
		scene.fog(1)
		
	@staticmethod
	def liftFog(scene):
		scene.fog(0)

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
			BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb',scene=viz.MainScene)
			
		elif(BalloonTrial.device == constants.HMD):
			vizconnect.go('vizconnect_rifts.py')
			BalloonTrial.transport = vizconnect.getTransport('wandmagiccarpet')
			BalloonTrial.transport.getNode3d().setPosition(BalloonTrial.startPosition)
			#for stereo condition, do nothing
			if(BalloonTrial.mode == constants.MONO):
				window.stereo(viz.STEREO_LEFT)
				#viz.MainWindow.stereo(viz.STEREO_RIGHT)
			elif(BalloonTrial.mode == constants.SYN):
				window.ipd(0)
			BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb',scene=viz.MainScene)
			
		elif(BalloonTrial.device == constants.EGG):
			if(BalloonTrial.mode==constants.STEREO):
				vizconnect.go('vizconnect_egg.py')
				BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb',scene=viz.MainScene)
			elif(BalloonTrial.mode==constants.SYN):
				vizconnect.go('vizconnect_egg_nonstereo.py')
				BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb',scene=viz.MainScene)
			else:
				vizconnect.go('vizconnect_egg_mono.py')
				BalloonTrial.piazza = viz.addChild('piazza_edited2.osgb',scene=viz.Scene1)
				viz.addChild('piazza_edited2.osgb',scene=viz.Scene2)
				BalloonTrial.applyFog(viz.Scene2)
			BalloonTrial.transport = vizconnect.getTransport('walking')
			BalloonTrial.transport.getNode3d().setPosition(BalloonTrial.startPosition)
		
		
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
		Set positions of the balloons(stimuli) with a random displacement applied.
		"""
		for i in range(len(self.stimuliLocations)):
			randomDisplacement = [0,0,0]
			for j in range(len(self.stimuliLocations[i])):
				randomDisplacement[j] = maxDisplacement * random.random() * random.choice([1,-1])
			print("displacement: " + str(randomDisplacement))
			location = map(self.addMapper, self.stimuliLocations[i], randomDisplacement)
			print("location: " + str(location))
			BalloonTrial.balloons[i].setPosition(location)
		
	
	def hideBalloons(self):
		"""
		Hides the stimuli.
		"""
		for i in range(len(self.stimuliLocations)):
			BalloonTrial.balloons[i].setPosition([0,0,-100])

		
	def startTrial(self, balloon, d=direction, callback = None):
		"""
		Starts a trial.
		"""
		print "===Trial Starts==="
		BalloonTrial.liftFog(viz.MainScene)
		print "Set balloon positions."
		self.setBalloonsPosition()
		#wait at the start of trial
		self.wait(self.startWaitTime)
		#start movement by adding the action into queue
		self.startMoving(balloon, d)
		
		#print "Wait for " + str(self.startWaitTime) + " second(s)."
		#timer = threading.Timer(self.startWaitTime, self.startMoving, [balloon, d])
		#timer.start()
		
		if callback != None:
			BalloonTrial.addFunctionAction(balloon, callback)
		
		
		return
		
	@staticmethod
	def addFunctionAction(obj,func):
		funcAct = vizact.call(func)
		obj.addAction(funcAct)
		
	def wait(self,waitTime):
		"""
		Wait for waitTime seconds. 
		"""
		
		print "Ballons Waiting for " + str(waitTime) + " seconds"
		print "View Waiting for " + str(waitTime) + " seconds"
		wait = vizact.waittime(waitTime)

		#if using device
		if(BalloonTrial.device == constants.MONITOR):
			viz.MainView.addAction(wait)
		
		#if using HMD/EGG
		if (BalloonTrial.device == constants.HMD or BalloonTrial.device == constants.EGG):
			transportNode = BalloonTrial.transport.getNode3d()
			transportNode.clearActions()
			transportNode.addAction(wait)
	
		for i in range(len(BalloonTrial.balloons)):
			BalloonTrial.balloons[i].addAction(wait)
		
	def startMoving(self, balloon, d=direction):
		"""
		Starts movement of both view and stimuli.
		"""
		
		print "Ballons Moving in direction " + str(self.direction)
		print "View Moving in direction " + str(self.viewDirection)
		print "Trial Duration: " + str(BalloonTrial.trialDuration) + "s"
		
		#move view
		#if using device
		if(BalloonTrial.device == constants.MONITOR):
			viz.MainView.velocity(self.viewDirection)
		
		#if using HMD/EGG
		if (BalloonTrial.device == constants.HMD or BalloonTrial.device == constants.EGG):
			transportNode = BalloonTrial.transport.getNode3d()
			transportNode.addAction(vizact.move(self.viewDirection, BalloonTrial.trialDuration))
		

		balloon.addAction(vizact.move(self.direction, BalloonTrial.trialDuration))
		balloon.addAction(vizact.call(self.resetPositions))
		#timer = threading.Timer(BalloonTrial.trialDuration, self.resetPositions)
		#timer.start()
		return


	def resetPositions(self):
		"""
		Resets Positions of both view and stimuli.
		"""
		
		print "===Trial Resets==="
		BalloonTrial.applyFog(viz.MainScene)
		#self.hideBalloons()
		viz.MainView.setPosition(BalloonTrial.startPosition)
		viz.MainView.velocity([0,0,0])
		
		#if using HMD/EGG
		if (BalloonTrial.device == "HMD" or BalloonTrial.device == "EGG"):
			BalloonTrial.transport.getNode3d().setVelocity([0,0,0])
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
	
	def addMapper(self, a,b):
		return a + b
	
	def viewSpeedmapper(self,i):
		"""
		Return the magnified viewSpeed. Used for mapping.
		"""
		
		return float(i) * self.viewSpeed


	def __init__(self, balloonDirections=None, viewDirections=None, viewSpeed=None, expSet = "A1", fovMask = False, startWaitTime = trialWaitTime, device=None, mode=None):
		
		
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
		if(viewSpeed == None):
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
	
	bt = BalloonTrial(device="Monitor", mode="MONO")
	
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


