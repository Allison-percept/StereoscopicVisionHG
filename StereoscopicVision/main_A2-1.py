import viz
import vizact
import viztask

from BalloonStaircaseA import *
from BalloonTrial import *

from Tkinter import Tk
from tkinter.filedialog import askdirectory


#Open a dialog box to select directory from
#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#directory = askdirectory() # show an "Open" dialog box and return the path to the selected directory
directory="output"

#initiallize the staircases
BalloonStaircaseA(('1'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewSpeed=.5,
		expSet='A2-1a'),
	foldername=directory)

BalloonStaircaseA(('2'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.left,BalloonTrial.right],
		viewDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewSpeed=.5,
		expSet='A2-1a'),
	foldername=directory)
		
BalloonStaircaseA(('3'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewSpeed=.5,
		expSet='A2-1a'),
	foldername=directory)


#start the experiment
BalloonStaircaseA.start()