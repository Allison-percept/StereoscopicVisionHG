import viz
import vizact
import viztask

from BalloonStaircaseB import *
from BalloonTrial import *

from Tkinter import Tk
from tkinter.filedialog import askdirectory


#Open a dialog box to select directory from
#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#directory = askdirectory() # show an "Open" dialog box and return the path to the selected directory
directory="output"

#initiallize the staircases
BalloonStaircaseB(('left'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=.5,
		expSet='B-l',
		startWaitTime = .5),
	foldername=directory)

BalloonStaircaseB(('right'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up],
		viewDirections=[BalloonTrial.forward],
		viewSpeed=.5,
		expSet='B-r',
		startWaitTime = .5),
	foldername=directory,
	leftSide = False)
		

#start the experiment
BalloonStaircaseB.start()