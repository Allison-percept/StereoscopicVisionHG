import viz
import vizact
import viztask
from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import numpy, random
import os
from os import path
from BalloonTrial import *
from AbstractBalloonStaircase import *
import constants
from expParameters import initialStimulusSpeed


class BalloonStaircaseA(AbstractBalloonStaircase):
	initialSpeed = initialStimulusSpeed
	
	def setInitialSpeed(self,val):
		self.initialSpeed = val

	def createOutputFileHeader(self):
		#the columns header of output file in csv format
		return 'targetIndex,responseIndex,targetDirection,viewDirection,speed,correct\n';

	def createStaircase(self):
		# create the staircase handler
		self.staircase = data.QuestHandler(startVal=self.initialSpeed, 
							startValSd=0.5,
							pThreshold=0.625,
							gamma=0.25,
							stimScale='linear',
							stopInterval=.1, nTrials=100, minVal=0, maxVal=1.5)

	def trial(self):
		print("StaircaseA "+ self.suffix +" is running")
		staircase = self.staircase

		bt = self.bt
		balloons = BalloonTrial.balloons

		
		if(staircase.finished):
			self.savePickle()
			
			self.unRegister()
			
			if(len(BalloonStaircaseA.bStaircases)>0):
				#then pick any staircase that is left and start its trial
				nextStaircase = random.choice(BalloonStaircaseA.bStaircases)
				nextStaircase.trial()

			else:
				viz.quit()
			#stop executing below code
			return
		
		thisIncrement = staircase.next()
		self.thisIncrement = thisIncrement
		print thisIncrement
		
		
		#pick the object to move
		self.targetIndex = random.randrange(len(balloons))
		target = balloons[self.targetIndex]
		
		#pick the direction of object
		objDirectionIndex = bt.getRandomBalloonDirIndex()
		self.objDirection = bt.directionArray[objDirectionIndex]
		print self.objDirection
		
		#pick the direction of view
		viewDirectionIndex = bt.getRandomViewDirIndex()
		self.viewDirection = bt.directionArray[viewDirectionIndex]
		
		#set the speed
		self.objDirection = map(lambda x: x * thisIncrement, self.objDirection) 
		
		#set the directions
		bt.setDirection(self.objDirection)
		bt.setViewDirection(self.viewDirection)
		
		#assign the current staircase
		BalloonStaircaseA.currentStaircase = self
		
		#start Moving
		bt.startTrial(target)

		#get response
		def getResp():

			bs = BalloonStaircaseA.currentStaircase

			staircase = bs.staircase
			dataFile = bs.dataFile
			thisIncrement = self.thisIncrement
			targetIndex = bs.targetIndex
			bt = bs.bt
			objDirection = bs.objDirection
			viewDirection = bs.viewDirection
			
			thisIndex = None		
			thisResp = -1
			if(bt.device == constants.MONITOR):
				#Wait for a keypress.
				respKey = yield viztask.waitKeyDown( [viz.KEY_KP_1,viz.KEY_KP_7,viz.KEY_KP_9,viz.KEY_KP_3] )
				
				if respKey.key == viz.KEY_KP_3:
					thisIndex = 0
					if(targetIndex==0):
						thisResp = 1
					else: 
						thisResp = 0
				if respKey.key == viz.KEY_KP_9:
					thisIndex = 1
					if(targetIndex==1):
						thisResp = 1
					else: 
						thisResp = 0
				if respKey.key == viz.KEY_KP_1:
					thisIndex = 2
					if(targetIndex==2):
						thisResp = 1
					else: 
						thisResp = 0
				if respKey.key == viz.KEY_KP_7:
					thisIndex = 3
					if(targetIndex==3):
						thisResp = 1
					else: 
						thisResp = 0
				print respKey.key
			else:
				print "waiting joystick button press"
				#Wait for a joystick keypress.
				respButton = yield viztask.waitSensorDown( None, None )
				print respButton.button
				#		3
				#	0		2
				#		1
				
				if respButton.button == 0:
					thisIndex = 0
					if(targetIndex==0):
						thisResp = 1
					else: 
						thisResp = 0
				if respButton.button == 1:
					thisIndex = 1
					if(targetIndex==1):
						thisResp = 1
					else: 
						thisResp = 0
				if respButton.button == 2:
					thisIndex = 2
					if(targetIndex==2):
						thisResp = 1
					else: 
						thisResp = 0
				if respButton.button == 3:
					thisIndex = 3
					if(targetIndex==3):
						thisResp = 1
					else: 
						thisResp = 0
					
			# add the data to the staircase so it can calculate the next level
			
			staircase.addResponse(thisResp)
			print targetIndex
			print thisIncrement
			print thisResp
			print objDirection
			print viewDirection
			dataFile.write('%i,%i,%s,%s,%.5f,%i\n' %(targetIndex, thisIndex, directionToString(objDirection), directionToString(viewDirection), thisIncrement, thisResp))
			#continue next trial from a random staircase in the list
			nextStaircase = random.choice(BalloonStaircaseA.bStaircases)
			nextStaircase.trial()
		viztask.schedule(getResp())


#-----

if __name__ == "__main__":
	BalloonStaircaseA('MONO', BalloonTrial(device=constants.MONITOR, mode=constants.STEREO))
	BalloonStaircaseA.start()

	
	



