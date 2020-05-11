from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import numpy, random

from BalloonTrial import *
bt = BalloonTrial()


try:  # try to get a previous parameters file
	expInfo = fromFile('lastParams.pickle')
except:  # if not there then use a default set
	expInfo = {'observer':'jwp'}
expInfo['dateStr'] = data.getDateStr()  # add the current time

toFile('lastParams.pickle', expInfo)  # save params to file for next time


# make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']
dataFile = open(fileName+'.csv', 'w')  # a simple text file with 'comma-separated-values'
dataFile.write('targetIndex,responseIndex,targetDirection,viewDirection,speed,correct\n')

# create the staircase handler

staircase = data.QuestHandler(startVal=0.5, 
							startValSd=0.5,
							pThreshold=0.625,
							gamma=0.25,
							stopInterval=.1, nTrials=100, minVal=0, maxVal=1.5)



thisResp = None
thisIncrement = None
targetIndex = None
objDirection = []
viewDirection = []

# create window and stimuli

bt.startScene()

import viztask




#Create a task.
def pressToStart():
	#Wait for any keypress.
	yield viztask.waitKeyDown( None )

	#Wait for a second.
	#yield viztask.waitTime( 1 )
	
	#start trial
	trial()

#Schedule the task.
viztask.schedule( pressToStart() )

def getStairCase():
	global staircase
	return staircase


def pressToQuit():
	staircase = getStairCase()
	
	#Wait for q
	yield viztask.waitKeyDown( 'q' )
	
	staircase.thisTrialN = staircase.thisTrialN - 1
	
	#output experiment data
	staircase.saveAsPickle("QuestPickle")
	#staircase.saveAsExcel("QuestResult")
	

	print('aborted by user')
	
	#quit
	viz.quit()

viztask.schedule( pressToQuit() )





def trial():	
	global thisResp
	global staircase
	global dataFile
	global thisIncrement
	global targetIndex	
	global bt
	balloons = bt.balloons
	global objDirection
	global viewDirection
	
	if(staircase.finished):
		staircase.saveAsPickle("QuestPickle")
		#staircase.saveAsExcel("QuestResult")
		viz.quit()
		return
	thisIncrement = staircase.next()
	#pick the object to move
	targetIndex = random.randrange(len(balloons))
	target = balloons[targetIndex]
	
	#pick the direction of object
	objDirectionIndex = bt.getRandomBalloonDirIndex()
	objDirection = bt.directionArray[objDirectionIndex]
	
	#pick the direction of view
	viewDirectionIndex = bt.getRandomViewDirIndex()
	viewDirection = bt.directionArray[viewDirectionIndex]
	
	#set the speed
	objDirection = map(lambda x: x * thisIncrement, objDirection) 
	
	#set the directions
	bt.setDirection(objDirection)
	bt.setViewDirection(viewDirection)
	
	#start Moving
	bt.startMoving(target)

	# wait 500ms; but use a loop of x frames for more accurate timing
	
		# get response
	

	
	def getResp():

		global thisResp
		global staircase
		global dataFile
		global thisIncrement
		global targetIndex
		global bt
		global objDirection
		global viewDirection
		
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
		trial()
	viztask.schedule(getResp())



