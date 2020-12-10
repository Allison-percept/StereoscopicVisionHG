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
	observer = ''
	series = ''
	mode = ''
	ori = ''
	stair = ''
	bt = None
	staircase = None
	thisResp = None
	thisIncrement = None
	targetIndex = None
	objDirection = []
	viewDirection = []
	dataFile = None

	
	#----static----

	dinput = viz.add('DirectInput.dle')
	#get the input device 
	inputDevice = dinput.addJoystick(dinput.getJoystickDevices()[0])
	
	#list of all staircases
	bStaircases = []
	
	#current staircase
	currentStaircase = None

	def __init__(self, bt=BalloonTrial(), observer='hy', series='A1', mode='STEREO', ori='VER', stair='U', foldername='output'):
		self.bt = bt
		self.observer = observer
		self.series = series
		self.mode = mode
		self.ori = ori
		self.stair = stair
		self.foldername = foldername

		self.fileName = self.getFileName()
		
		self.createOutputFiles()
		self.createStaircase()
		self.register()
		
		
		
		self.initialize()
	
	def initialize(self):
		#Things to run at initialization of a staircase
		pass
	
	def createOutputFiles(self):
		# make a text file to save data
		
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
		"""
		create the psychopy staircase
		"""
		pass
	
	def register(self):
		"""
		register the staricase on the staircase list
		"""
		AbstractBalloonStaircase.bStaircases.append(self)
	
	def unRegister(self):
		"""
		unregister the staircase on the staircase list
		"""
		AbstractBalloonStaircase.bStaircases.remove(self)
	
	def getStaircase(self):
		return self.staircase

	def savePickle(self):
		self.staircase.saveAsPickle(os.path.join(self.foldername, self.getFileName()))

	def getFileName(self):
		fileName = ''
		timestamp = data.getDateStr()
		fileName = timestamp;
		fileName += "_" + self.observer
		fileName += "_" + self.series
		fileName += "_" + self.mode
		fileName += "_" + self.ori
		fileName += "_" + self.stair

		return fileName

	@staticmethod
	def pressToStart():
		"""
		set a trigger that wait for keypress to start
		"""
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
		"""
		get the first staircase and start the experiment. Calls pressToStart()
		"""
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
		"""
		Set a trigger that wait for press of Q or Escape key to quit. Before quitting, pickle file will be saved.
		"""
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
		"""
		Method for the activities within a trial.
		"""
		pass


	



