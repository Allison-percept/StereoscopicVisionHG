import viz
import vizact
import time
import threading

#Enable full screen anti-aliasing (FSAA) to smooth edges
viz.setMultiSample(4)

viz.go()

#Increase the Field of View
viz.MainWindow.fov(60)

viz.MainView.setPosition([0,2,-2])
piazza = viz.addChild('ground_edited.osgb')

balloons = []
forward = [0,0,1]
back = [0,0,-1]
left = [-1,0,0]
right = [1,0,0]
up = [0,1,0]
down = [0,-1,0]

direction = []
viewDirection = []




def setBalloonsPosition(balloons):
	balloons[0].setPosition([3,2,8])
	balloons[1].setPosition([3,5,8])
	balloons[2].setPosition([-3,2,8])
	balloons[3].setPosition([-3,5,8])
	if len(balloons) > 4:
		balloons[4].setPosition([-4,2,4])
		balloons[5].setPosition([-3,4,12])
		balloons[6].setPosition([4,2,4])
		balloons[7].setPosition([3,4,12])
	

def startMoving(balloon,d=direction):
	print "===Trial Starts==="
	print "Ballons Moving in direction " + str(direction)
	print "View Moving in direction " + str(viewDirection)
	viz.MainView.velocity(viewDirection)
	balloon.addAction(vizact.move(direction, 1))
	timer = threading.Timer(1, resetPositions)
	timer.start()
	return


def resetPositions():
	print "===Trial Ends==="
	setBalloonsPosition(balloons)
	viz.MainView.setPosition([0,2,-2])
	viz.MainView.velocity([0,0,0])

for i in range(4):
	balloon = viz.addChild('balloon.osgb')
	balloon.setScale([0.01,0.01,0.01])
	balloons.append(balloon)

setBalloonsPosition(balloons)





def setDirection(d):
	global direction
	direction = d
	print "Balloon Direction is set to " + str(d)

def setViewDirection(d):
	global viewDirection
	viewDirection = map(viewSpeed, d)
	print "View direction is set to " + str(d)

def viewSpeed(i):
	return float(i)/2

setDirection(forward)
setViewDirection(forward)

vizact.onkeydown('1', startMoving, balloons[0] )
vizact.onkeydown('2', startMoving, balloons[1] )
vizact.onkeydown('3', startMoving, balloons[2] )
vizact.onkeydown('4', startMoving, balloons[3] )


vizact.onkeydown('z', setDirection, forward )
vizact.onkeydown('x', setDirection, back )
vizact.onkeydown('c', setDirection, left )
vizact.onkeydown('v', setDirection, right )
vizact.onkeydown('b', setDirection, up )
vizact.onkeydown('n', setDirection, down )

vizact.onkeydown('a', setViewDirection, forward )
vizact.onkeydown('s', setViewDirection, back )
vizact.onkeydown('d', setViewDirection, left )
vizact.onkeydown('f', setViewDirection, right )
vizact.onkeydown('g', setViewDirection, up )
vizact.onkeydown('h', setViewDirection, down )
