import viz
import vizact
import viztask

from BalloonStaircaseA import *
from BalloonTrial import *

from Tkinter import Tk
from tkinter.filedialog import askdirectory

import constants

#Open a dialog box to select directory from
#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#directory = askdirectory() # show an "Open" dialog box and return the path to the selected directory
directory="output"

#initiallize the staircases
st1u= BalloonStaircaseA(('VER_U'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=2,
		expSet='A1',
		startWaitTime = .5,
		device=constants.HMD, 
		mode=constants.STEREO),
	foldername=directory)

st1d = BalloonStaircaseA(('VER_D'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=2,
		expSet='A1',
		startWaitTime = .5,
		device=constants.HMD, 
		mode=constants.STEREO),
	foldername=directory)

st2u = BalloonStaircaseA(('HOR_U'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.left,BalloonTrial.right],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=.2,
		expSet='A1',
		startWaitTime = .5,
		device=constants.HMD, 
		mode=constants.STEREO),
	foldername=directory)

st2d = BalloonStaircaseA(('HOR_D'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.left,BalloonTrial.right],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=.2,
		expSet='A1',
		startWaitTime = .5,
		device=constants.HMD, 
		mode=constants.STEREO),
	foldername=directory)
		
st3u = BalloonStaircaseA(('DEP_U'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=2,
		expSet='A1',
		startWaitTime = .5,
		device=constants.HMD, 
		mode=constants.STEREO),
	foldername=directory)

st3d = BalloonStaircaseA(('DEP_D'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=2,
		expSet='A1',
		startWaitTime = .5,
		device=constants.HMD, 
		mode=constants.STEREO),
	foldername=directory)

#set initial speed for upward staircases
st1u.setInitialSpeed(0.01)
st2u.setInitialSpeed(0.01)
st3u.setInitialSpeed(0.01)

BalloonTrial.startPosition = [0,0.3,-2]

#start the experiment
BalloonStaircaseA.start()