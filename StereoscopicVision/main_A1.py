import viz
import vizact
import viztask

from BalloonStaircaseA import *
from BalloonTrial import *

from Tkinter import Tk
from tkinter.filedialog import askdirectory

import constants
import expParameters

#Open a dialog box to select directory from
#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#directory = askdirectory() # show an "Open" dialog box and return the path to the selected directory
directory = "output"
observer = "obs1"
device=constants.EGG
mode = constants.STEREO
series = "A1"

#initiallize the staircases
BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='VER', 
	stair='U',
	foldername=directory)
	
BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='VER', 
	stair='D',
	foldername=directory)

BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='VER', 
	stair='U',
	foldername=directory)
	
BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.left,BalloonTrial.right],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='HOR', 
	stair='U',
	foldername=directory)

BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.left,BalloonTrial.right],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='HOR', 
	stair='D',
	foldername=directory)

BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='DEP', 
	stair='U',
	foldername=directory)

BalloonStaircaseA( 
	BalloonTrial(
		balloonDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=viewMovingSpeed,
		expSet=series,
		startWaitTime = trialWaitTime,
		device=device, 
		mode=mode),
	observer=observer, 
	series=series, 
	mode=mode, 
	ori='DEP', 
	stair='D',
	foldername=directory)


#start the experiment
BalloonStaircaseA.start()