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
		fovMask=False,
		viewSpeed=2,
		expSet='A2-2',
		startWaitTime = .5,
		device=constants.MONITOR, 
		mode=constants.STEREO),
	foldername=directory)


#set initial speed for upward staircases
st1u.setInitialSpeed(0.01)




#start the experiment
BalloonStaircaseA.start()