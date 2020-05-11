import viz
import vizact
import viztask
from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import numpy, random

from BalloonTrial import *


class BalloonStaircase:
	suffix = None
	observer = None
	filename = ''
	foldername = 'output'
	bt = None
	staircase = None
	thisResp = None
	thisIncrement = None
	targetIndex = None
	objDirection = []
	viewDirection = []
	dataFile = None
	
	#static
	bStaircases = []
	currentStaircase = None

	def __init__(self, suffix='', bt=BalloonTrial(), observer='hy'):
		self.bt = bt
		self.suffix = suffix
		self.observer = observer
		self.createOutputFiles()
		self.createStaircase()
		self.register()
	

	def createOutputFiles(self):
		expInfo = {'observer':self.observer}
		expInfo['dateStr'] = data.getDateStr()  # add the current time

		#toFile('lastParams.pickle', expInfo)  # save params to file for next time


		# make a text file to save data
		self.fileName = expInfo['observer'] + expInfo['dateStr'] +'_'+ self.suffix
		filePath = self.foldername + '/' + self.fileName
		self.dataFile = open(filePath + '.csv', 'w')  # a simple text file with 'comma-separated-values'
		self.dataFile.write('targetIndex,responseIndex,targetDirection,viewDirection,speed,correct\n')

	def createStaircase(self):
		# create the staircase handler
		self.staircase = data.QuestHandler(startVal=0.5, 
							startValSd=0.5,
							pThreshold=0.625,
							gamma=0.25,
							stopInterval=.1, nTrials=1000, minVal=0, maxVal=1.5)
	
	
	def register(self):
		BalloonStaircase.bStaircases.append(self)
	
	def unRegister(self):
		BalloonStaircase.bStaircases.remove(self)
	
	def getStaircase(self):
		return self.staircase

	def savePickle(self):
		self.staircase.saveAsPickle(self.foldername + '/' + "QuestPickle" +'_'+ self.suffix)


	@staticmethod
	def pressToStart():
		print('wait for keypress to start...')
		def pressToStartScheduler():
			#Wait for any keypress.
			yield viztask.waitKeyDown( None )
			
			print('started')
			#start trial of the 1st staircase
			BalloonStaircase.bStaircases[0].trial()
		
		viztask.schedule( pressToStartScheduler() )


	@staticmethod
	def start():
		#make sure we have staircases initialized
		if (not BalloonStaircase.bStaircases):
			print("No staircase to start!")
			return
		BalloonTrial.startScene()
		BalloonStaircase.pressToStart()
		BalloonStaircase.pressToQuit()

	@staticmethod
	def pressToQuit():
		print('press q to abort')
		def pressToQuitScheduler():
			staircases = BalloonStaircase.bStaircases
			
			#Wait for q
			yield viztask.waitKeyDown( 'q' )
			
			for staircase in staircases:
				#output experiment data
				staircase.savePickle()
			
			print('aborted by user')
		
			#quit
			viz.quit()
		
		viztask.schedule( pressToQuitScheduler() )

	def trial(self):
		print("Staircase "+ self.suffix +" is running")
		staircase = self.staircase

		bt = self.bt
		balloons = BalloonTrial.balloons

		
		if(staircase.finished):
			self.savePickle()
			
			self.unRegister()
			
			if(len(BalloonStaircase.bStaircases)>0):
				#then pick any staircase that is left and start its trial
				nextStaircase = random.choice(BalloonStaircase.bStaircases)
				nextStaircase.trial()

			else:
				viz.quit()
			#stop executing below code
			return
		
		thisIncrement = staircase.next()
		self.thisIncrement = thisIncrement
		
		#pick the object to move
		self.targetIndex = random.randrange(len(balloons))
		target = balloons[self.targetIndex]
		
		#pick the direction of object
		objDirectionIndex = bt.getRandomBalloonDirIndex()
		self.objDirection = bt.directionArray[objDirectionIndex]
		
		#pick the direction of view
		viewDirectionIndex = bt.getRandomViewDirIndex()
		self.viewDirection = bt.directionArray[viewDirectionIndex]
		
		#set the speed
		self.objDirection = map(lambda x: x * thisIncrement, self.objDirection) 
		
		#set the directions
		bt.setDirection(self.objDirection)
		bt.setViewDirection(self.viewDirection)
		
		#assign the current staircase
		BalloonStaircase.currentStaircase = self
		
		#start Moving
		bt.startMoving(target)

		# wait 500ms; but use a loop of x frames for more accurate timing
		
			# get response
		
		def getResp():

			bs = BalloonStaircase.currentStaircase

			staircase = bs.staircase
			dataFile = bs.dataFile
			thisIncrement = self.thisIncrement
			targetIndex = bs.targetIndex
			bt = bs.bt
			objDirection = bs.objDirection
			viewDirection = bs.viewDirection
			
			thisIndex = None		
			
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
			# add the data to the staircase so it can calculate the next level
			print respKey.key
			staircase.addResponse(thisResp)
			print targetIndex
			print thisIncrement
			print thisResp
			print objDirection
			print viewDirection
			dataFile.write('%i,%i,%s,%s,%.5f,%i\n' %(targetIndex, thisIndex, directionToString(objDirection), directionToString(viewDirection), thisIncrement, thisResp))
			#continue next trial from a random staircase in the list
			nextStaircase = random.choice(BalloonStaircase.bStaircases)
			nextStaircase.trial()
		viztask.schedule(getResp())


#-----

if __name__ == "__main__":
	BalloonStaircase('test1', BalloonTrial())
	BalloonStaircase.start()

	
	



