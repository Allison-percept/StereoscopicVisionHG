targetPositions=[]
targetAmount = 0

viewMovingSpeed = 2
startViewPosition = [0,2,-2]
initialStimulusSpeed = 1
trialDuration = 1

stimuliLocations = {
	"A1": [[-1,2,8],[0,1,8],[1,2,8],[0,3,8]],
	"A2-1a": [[3,1,8],[3,4,8],[-3,1,8],[-3,4,8]],
	"A2-1b": [[3,1,8],[3,4,8],[-3,1,8],[-3,4,8]],
	"A2-2": [[-2,3,8],[0,1,8],[2,3,8],[0,5,8]],
	"A4": [[3,1,8],[3,4,8],[-3,1,8],[-3,4,8]],
	"B-l": [[-3,2,3]],
	"B-r": [[3,2,3]],
}

#A - detection
#A1 - speed & direction
#A2-1a - scattered stimuli
#A2-1B - gathered stimuli
#A2-2 - field of view
#A4 - treadmill walking & real walking
#B - obstacle motion estimation

#scenario = "4 targets"
scenario = "1 target right"

if (scenario == "4 targets"):
	targetPositions = [[3,1,8],[3,4,8],[-3,1,8],[-3,4,8]]
	targetAmount = 4
		#	3	1
		#	2	0
elif (scenario == "1 target left"):
	targetPositions = [[-3,2,8]]
	targetAmount = 1
elif (scenario == "1 target right"):
	targetPositions = [[3,2,3]]
	targetAmount = 1
	
	
	