from __future__ import print_function
from psychopy import data, gui, core
from psychopy.tools.filetools import fromFile
import pylab
from Tkinter import Tk
from tkinter.filedialog import askopenfilenames
import ntpath
import numpy as np
import math as math

# set bins
bins = 10

expected_threshold = 0.5
expected_min = 0
curve_start = 0.0
curve_end = 1.2



#Open a dialog box to select files from
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
files = askopenfilenames() # show an "Open" dialog box and return the path to the selected file

print("data files: ")
print(files)


#get the data from all the files
allIntensities, allResponses = [],[]
for thisFileName in files:
    thisDat = fromFile(thisFileName)
    allIntensities.append( thisDat.intensities )
    allResponses.append( thisDat.data )






#plot each staircase
fig = pylab.figure(num='Analysis',figsize=[16,8])
pylab.subplot(131)
colors = 'brgkcmbrgkcm'
lines, names = [],[]

#colors = ['b','g','r']

fileNameList = []

#get filenames of the files
for fileN, thisStair in enumerate(allIntensities):
    fullPath = files[fileN]
    fileName = ntpath.basename(fullPath)
    fileNameList.append(fileName)



for fileN, thisStair in enumerate(allIntensities):
    #lines.extend(pylab.plot(thisStair))
    fullPath = files[fileN]
    fileName = ntpath.basename(fullPath)
    pylab.plot(thisStair, label=fileName.split(".")[0], color=colors[fileN])
    pylab.legend(loc='upper right')
    pylab.xlabel('Number of Trials')
    pylab.ylabel('Stimulus Intensity')



def checkFileNames(strList):
    for str in strList:
        if(str.find("_") == -1):
            return False
    return True

def hasSamePrefix(str0,str1):
    if(str0.split("_")[0] == str1.split("_")[0]):
        return True
    return False
    

def groupWithPrefix(str, index, strGroups):
    if not strGroups:
        strGroups.append([[str,index]])
        return
    inserted = False
    for strGroup in strGroups:
        if(hasSamePrefix(strGroup[0][0], str)):
            strGroup.append([str,index])
            inserted = True
            break
    if (not inserted):
        strGroups.append([[str,index]])

def getLabelfromFileName(fileName):
    return fileName.split(".")[0].split("_")[0]


fileGroups = []
#get files into groups


for index, fileName in enumerate(fileNameList):
    groupWithPrefix(fileName, index, fileGroups)

threshs=[]
labels = []

pylab.subplot(132)

for groupN, group in enumerate(fileGroups):
    groupIntensities = []
    groupResponses = []
    groupLabel = ""
    for fileName, index in group:
        intensities = allIntensities[index]
        responses = allResponses[index]
        
        #keep both list the same length
        if(len(intensities) > len(responses)):
            del intensities[-1]
        groupIntensities.extend(intensities)
        groupResponses.extend(responses)
        groupLabel = getLabelfromFileName(fileName)
        
    combinedInten, combinedResp, combinedN = \
                 data.functionFromStaircase(groupIntensities, groupResponses, bins)
                 
    #fit curve - in this case using a Weibull function
    fit = data.FitWeibull(combinedInten, combinedResp, expectedMin = expected_min,sems = [1.0] * bins)
    smoothInt = pylab.arange(curve_start, curve_end, 0.001)
    smoothResp = fit.eval(smoothInt)
    thresh = fit.inverse(expected_threshold)
    threshs.append(thresh)
    labels.append(groupLabel)
    print(fit.ssq)
    print("Threshold: ")
    print(thresh)

    #plot curve
    pylab.plot(smoothInt, smoothResp, '-', label=groupLabel, color=colors[groupN])
    pylab.plot([thresh, thresh],[0,expected_threshold],'--', color=colors[groupN]); pylab.plot([0, thresh],\
    [expected_threshold,expected_threshold],'--')
    
    #pylab.title('threshold = %0.3f' %(thresh))
    #plot points
    pylab.plot(combinedInten, combinedResp, 'o', color=colors[groupN])
    pylab.legend(loc='upper right')
    pylab.ylim([0,1.01])



groupCount = len(fileGroups)

ci = 0.1
cis = [ci/2] * groupCount


pylab.xlabel('Stimulus Intensity')
pylab.ylabel('Correct Response Ratio')
sortedThreshs = threshs[:]
sortedThreshs.sort()
#pylab.title('thresholds = %0.3f, %0.3f, %0.3f,'  %(sortedThreshs[0], sortedThreshs[1], sortedThreshs[2]))
pylab.title('thresholds = %0.3f'  %(sortedThreshs[0]))

pylab.subplot(133)
ind = np.arange(groupCount)
print(cis)

pylab.bar(ind,threshs, 0.5,yerr=cis)
pylab.xticks(ind,labels)
pylab.title('Stimulus Intensity Thresholds')

#register an event to terminate code when window closed
def on_close(event):
    event.canvas.figure.axes[0].has_been_closed = True
    print('Closed Figure')
    quit()

fig.canvas.mpl_connect('close_event', on_close)

pylab.subplots_adjust(bottom=0.2,top=0.8)
pylab.show(block=True)

