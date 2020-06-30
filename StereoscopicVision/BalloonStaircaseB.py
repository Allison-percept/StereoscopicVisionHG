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
import operator
import time


class BalloonStaircaseB(AbstractBalloonStaircase):
	#indicates whether the stimulus is on the left side
	leftSide = True
	
	def __init__(self, suffix='', bt=BalloonTrial(), observer='hy', foldername='output', leftSide = True):
		super(BalloonStaircaseB, self).__init__(suffix, bt, observer, foldername)
		self.leftSide = leftSide
		

	def createOutputFileHeader(self):
		#the columns header of output file in csv format
		return 'horizontalSpeed,response,verticalSpeed\n';

	def createStaircase(self):
		# create the staircase handler
		self.staircase = data.QuestHandler(startVal=0.0, 
							startValSd=0.2,
							pThreshold=0.5,
							gamma=0,
							stimScale='linear',
							stopInterval=.1, nTrials=100, minVal=-3, maxVal=3)

	def trial(self):
		print("StaircaseB "+ self.suffix +" is running")
		#reset the balloon positions (could be on the different side!)
		self.bt.resetPositions()
		
		staircase = self.staircase

		bt = self.bt
		balloons = BalloonTrial.balloons
		
		
		if(staircase.finished):
			self.savePickle()
			
			self.unRegister()
			
			if(len(BalloonStaircaseB.bStaircases)>0):
				#then pick any staircase that is left and start its trial
				nextStaircase = random.choice(BalloonStaircaseB.bStaircases)
				nextStaircase.trial()

			else:
				viz.quit()
			#stop executing below code
			return

		thisIncrement = staircase.next()
		self.thisIncrement = thisIncrement
		#this value means the intensity of the stimulus. In this case the horizontal speed component.
		
		#pick the object to move
		#there will be 1 target at a time
		self.targetIndex = 0
		target = balloons[self.targetIndex]	
		
		
		#get the direction of object
		
		#vertically it moves up at 1m/s
		verticalSpeed = 1
		
		#if the stimulus is on the left, add a positive (right) horizontal speed.
		#otherwise, add a negative (left) horizontal speed
		if(self.leftSide):
			horizontalSpeed = thisIncrement
		else:
			horizontalSpeed = -thisIncrement
			
		compositSpeed = [horizontalSpeed, verticalSpeed, 0]
		
		#pick the direction of view
		viewDirectionIndex = bt.getRandomViewDirIndex()
		self.viewDirection = bt.directionArray[viewDirectionIndex]
		
		#set the speed
		self.objDirection = compositSpeed
		
		#set the directions
		bt.setDirection(self.objDirection)
		bt.setViewDirection(self.viewDirection)
		
		#assign the current staircase
		BalloonStaircaseB.currentStaircase = self
		
		#start Moving
		bt.startTrial(target)


		
		# get response
		def getResp():

			bs = BalloonStaircaseB.currentStaircase

			staircase = bs.staircase
			dataFile = bs.dataFile
			thisIncrement = self.thisIncrement
			targetIndex = bs.targetIndex
			bt = bs.bt
			objDirection = bs.objDirection
			viewDirection = bs.viewDirection
			
			thisIndex = None		
			
			#Wait for a keypress.
			respKey = yield viztask.waitKeyDown( [viz.KEY_LEFT,viz.KEY_RIGHT] )
			outputResp = ""
			if respKey.key == viz.KEY_LEFT:
				outputResp = "left"
				if (self.leftSide):
					#if perceiving left with stimulus on left side, we need to increase horizontal speed component
					thisResp = 0
				else:
					thisResp = 1
			else: 
				outputResp = "right"
				if (self.leftSide):
					#perceiving right with stimulus on left side, we need to decrease horizontal speed component
					thisResp = 1
				else:
					thisResp = 0
			# add the data to the staircase so it can calculate the next level
			print respKey.key
			staircase.addResponse(thisResp)
			print targetIndex
			print thisIncrement
			print thisResp
			print objDirection
			print viewDirection
			dataFile.write('%5f,%s,%5f\n' %(thisIncrement, outputResp, verticalSpeed))
			#continue next trial from a random staircase in the list
			nextStaircase = random.choice(BalloonStaircaseB.bStaircases)
			nextStaircase.trial()
		viztask.schedule(getResp())


#-----

if __name__ == "__main__":
	directory="output"
	BalloonStaircaseB(('right'), 
		BalloonTrial(
			balloonDirections=[BalloonTrial.up],
			viewDirections=[BalloonTrial.forward],
			viewSpeed=.5,
			expSet='B-r'),
		foldername=directory,
		leftSide = False)
	BalloonStaircaseB.start()

	
	



