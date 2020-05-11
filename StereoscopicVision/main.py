import viz
import vizact
import viztask

from BalloonStaircase import *
from BalloonTrial import *


#initiallize the staircases
BalloonStaircase(('1'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.up,BalloonTrial.down],
		viewDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewSpeed=.5))

BalloonStaircase(('2'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.left,BalloonTrial.right],
		viewDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewSpeed=.5))
		
BalloonStaircase(('3'), 
	BalloonTrial(
		balloonDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewDirections=[BalloonTrial.forward,BalloonTrial.back],
		viewSpeed=.5))


#start the experiment
BalloonStaircase.start()