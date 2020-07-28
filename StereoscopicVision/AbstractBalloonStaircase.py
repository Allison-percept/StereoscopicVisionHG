import viz
import vizact
import viztask
from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import numpy, random
import os
from os import path
from BalloonTrial import *
from abc import ABCMeta, abstractmethod

class AbstractBalloonStaircase:
	__metaclass__ = ABCMeta
	suffix = None
	observer = None
	filename = ''
	foldername = ''
	bt = None
	staircase = None
	thisResp = None
	thisIncrement = None
	targetIndex = None
	objDirection = []
	viewDirection = []
	dataFile = None
	dinput = None
	joy = None
	
	#----static----
	
	#list of all staircases
	bStaircases = []
	
	#current staircase
	currentStaircase = None

	def __init__(self, suffix='', bt=BalloonTrial(), observer='hy', foldername='output'):
		self.bt = bt
		self.suffix = suffix
		self.observer = observer
		self.foldername = foldername
		self.createOutputFiles()
		self.createStaircase()
		self.register()
		
		# Load DirectInput plug-in
		dinput = viz.add('DirectInput.dle')

		# Add first available joystick
		joy = dinput.addJoystick()
		
		# Set dead zone threshold so small movements of joystick are ignored
		joy.setDeadZone(0.2)
		
		self.dinput = dinput
		self.joy = joy
	
	
	def createOutputFiles(self):
		expInfo = {'observer':self.observer}
		expInfo['dateStr'] = data.getDateStr()  # add the current time

		#toFile('lastParams.pickle', expInfo)  # save params to file for next time


		# make a text file to save data
		self.fileName = expInfo['observer'] + expInfo['dateStr'] +'_'+ self.bt.mode +'_'+self.suffix
		
		#create folder if not exist
		if (self.foldername!=""):
			if(not path.exists(self.foldername)):
				os.mkdir(self.foldername)
				
		filePath = os.path.join(self.foldername, self.fileName + '.csv')
		self.dataFile = open(filePath, 'w')  # a simple text file with 'comma-separated-values'
		self.dataFile.write(self.createOutputFileHeader())

	@abstractmethod
	def createOutputFileHeader(self):
		#the columns header of output file in csv format
		pass

	@abstractmethod
	def createStaircase(self):
		pass
	
	def register(self):
		AbstractBalloonStaircase.bStaircases.append(self)
	
	def unRegister(self):
		AbstractBalloonStaircase.bStaircases.remove(self)
	
	def getStaircase(self):
		return self.staircase

	def savePickle(self):
		self.staircase.saveAsPickle(os.path.join(self.foldername, "QuestPickle" +'_'+ self.bt.mode +'_'+ self.suffix))


	@staticmethod
	def pressToStart():
		print('wait for keypress to start...')
		def pressToStartScheduler():
			#Wait for any keypress.
			yield viztask.waitKeyDown( None )
			
			print('started')
			#start trial of the 1st staircase
			AbstractBalloonStaircase.bStaircases[0].trial()
		
		viztask.schedule( pressToStartScheduler() )


	@staticmethod
	def start():
		#make sure we have staircases initialized
		if (not AbstractBalloonStaircase.bStaircases):
			print("No staircase to start!")
			return
		firstStaircase = AbstractBalloonStaircase.bStaircases[0]
		bt = firstStaircase.bt
		bt.startScene()
		AbstractBalloonStaircase.pressToStart()
		AbstractBalloonStaircase.pressToQuit()

	@staticmethod
	def pressToQuit():
		print('press q to abort')
		def pressToQuitScheduler():
			staircases = AbstractBalloonStaircase.bStaircases
			
			#Wait for q
			yield viztask.waitKeyDown( 'q' )
			
			for staircase in staircases:
				#output experiment data
				staircase.savePickle()
			
			print('aborted by user')
		
			#quit
			viz.quit()
		
		viztask.schedule( pressToQuitScheduler() )
	
	@abstractmethod
	def trial(self):
		pass


	



