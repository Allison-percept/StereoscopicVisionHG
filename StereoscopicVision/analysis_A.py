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

expected_threshold = 0.625
expected_min = 0.25
curve_start = 0.0
curve_end = 0.6

colors = 'brgkcmbrgkcmbrgkcmbrgkcm'

exp_set = 'A'

if (exp_set == 'A'):
    expected_threshold = 0.625
    expected_min = 0.25
    curve_start = 0.0
    curve_end = 2.0
elif (exp_set == 'B'):
    expected_threshold = 0.5
    expected_min = 0
    curve_start = 0.0
    curve_end = 1.2



#Open a dialog box to select files from
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
files = askopenfilenames(filetypes=[("Psychopy Outputs", "*.psydat")]) # show an "Open" dialog box and return the path to the selected file

print("data files: ")
print(files)


#get the data from all the files
allIntensities, allResponses = [],[]
for thisFileName in files:
    thisDat = fromFile(thisFileName)
    allIntensities.append( thisDat.intensities )
    allResponses.append( thisDat.data )








#colors = ['b','g','r']

fileNameList = []

#get filenames of the files
for fileN, thisStair in enumerate(allIntensities):
    fullPath = files[fileN]
    fileName = ntpath.basename(fullPath)
    fileNameList.append(fileName)



def checkFileNames(strList):
    for str in strList:
        if(str.find("_") == -1):
            return False
    return True

def getObserver(fileName):
    return fileName.split("_")[4]

def getSeries(fileName):
    return fileName.split("_")[5]
    
def getMode(fileName):
    return fileName.split("_")[6]
    
def getOrientation(fileName):
    return fileName.split("_")[7]
    
def getStair(fileName):
    return fileName.split("_")[8]


def hasSameAttribute(fileName1, fileName2, func):
    if (func(fileName1) == func(fileName2)):
        return True
    else:
        return False

def groupWith(index, fileGroup, allFileNames, func):
    #group file into group of indecies
    if not fileGroup:
        fileGroup.append(index)
        return True
    if(hasSameAttribute(allFileNames[index], allFileNames[fileGroup[0]], func)):
        fileGroup.append(index)
        return True
    return False

def groupFilesWith(files, allFileNames, func, fileGroups=None):
    if not fileGroups:
        fileGroups = []
        
    #given a collection of files and function for grouping, return all groups
    for index in files:
        #set the grouped flag
        grouped = False
        for fileGroup in fileGroups:
            groupingResult = groupWith(index, fileGroup, allFileNames, func)
            if groupingResult:
                grouped = True
                break
        if grouped == False:
            # create a new group
            fileGroups.append([index])
    return fileGroups
    


fileGroups = []
#get files into groups


#group files by observer

fileIndecies = range(len(fileNameList))
observerGroups = groupFilesWith(fileIndecies, fileNameList, getObserver)
print (observerGroups)





nrows = len(observerGroups) + 1
ncolumns = 3


thresholds = {
"MONO" : [],
"STEREO" : [],
"SYN" : []
}



fig = pylab.figure(num='Analysis',figsize=[16,8])

for groupN, observerFiles in enumerate(observerGroups):
    
    threshs=[]
    labels = []
    staircases = []
    lowercis = []
    uppercis = []

    
    
    #plot each staircase
    
    pylab.subplot(nrows, ncolumns, groupN*ncolumns + 1)
    print(groupN*ncolumns+1)
    
    
    lines, names = [],[]
    
    for fileN in observerFiles:
    #lines.extend(pylab.plot(thisStair))
        thisStair = allIntensities[fileN]
        fileName = fileNameList[fileN]
        print(222)
        pylab.plot(thisStair, label=getMode(fileName), color=colors[fileN])
        print(233)
        pylab.legend(loc='upper right')
        pylab.xlabel('Number of Trials')
        pylab.ylabel('Stimulus Intensity')
    print(observerFiles)
    #psychometric function plot
    displayModeGroups = groupFilesWith(observerFiles, fileNameList, getMode)
    print(displayModeGroups)
    pylab.subplot(nrows, ncolumns, groupN*ncolumns + 2)
    
    groupIntensities = []
    groupResponses = []
    groupLabel = ""
    for modeGroup in displayModeGroups:
        groupFirstFileN = modeGroup[0]
        groupLabel = getMode(fileNameList[groupFirstFileN])
        print(groupLabel)
        for modeGroupFileIndex in modeGroup:
            intensities = allIntensities[modeGroupFileIndex]
            responses = allResponses[modeGroupFileIndex]
            
            #keep both list the same length
            if(len(intensities) > len(responses)):
                del intensities[-1]
            groupIntensities.extend(intensities)
            groupResponses.extend(responses)
            
        
        #recreate the staircase from group
        staircase = data.QuestHandler(startVal=groupIntensities[0], 
                                startValSd=0.5,
                                pThreshold=0.625,
                                gamma=0.25,
                                stimScale='linear',
                                stopInterval=.1, nTrials=100, minVal=0, maxVal=1.5)
        staircase.importData(groupIntensities,groupResponses)
        staircases.append(staircase)
        #get the CI
        ci = staircase.confInterval()  
        
        combinedInten, combinedResp, combinedN = \
                     data.functionFromStaircase(groupIntensities, groupResponses, bins)
                     
        #fit curve - in this case using a Weibull function
        fit = data.FitWeibull(combinedInten, combinedResp, expectedMin = expected_min,sems = [1.0] * bins)
        smoothInt = pylab.arange(curve_start, curve_end, 0.001)
        smoothResp = fit.eval(smoothInt)
        thresh = fit.inverse(expected_threshold)
        threshs.append(thresh)
        thresholds[groupLabel].append(thresh)
        labels.append(groupLabel)
        
        
        lowerError = thresh - ci[0]
        upperError = ci[1] - thresh
        
        lowercis.append(lowerError)
        uppercis.append(upperError)
        
        
        #plot curve
        pylab.plot(smoothInt, smoothResp, '-', label=groupLabel, color=colors[groupFirstFileN])
        pylab.plot([thresh, thresh],[0,expected_threshold],'--', color=colors[groupFirstFileN]); pylab.plot([0, thresh],\
        [expected_threshold,expected_threshold],'--')
        
        #pylab.title('threshold = %0.3f' %(thresh))
        #plot points
        pylab.plot(combinedInten, combinedResp, 'o', color=colors[groupFirstFileN])
        pylab.legend(loc='upper right')
        pylab.ylim([0,1.01])



    groupCount = len(displayModeGroups)
    cis = [lowercis,uppercis]


    pylab.xlabel('Stimulus Intensity')
    pylab.ylabel('Correct Response Ratio')
    sortedThreshs = threshs[:]
    sortedThreshs.sort()
    if(len(sortedThreshs)>=3):
        pylab.title('thresholds = %0.3f, %0.3f, %0.3f,'  %(sortedThreshs[0], sortedThreshs[1], sortedThreshs[2]))
    else:
        pylab.title('thresholds = %0.3f'  %(sortedThreshs[0]))
    
    
    #plot for bar chart
    
    pylab.subplot(nrows, ncolumns, groupN*ncolumns + 3)
    print(groupN*ncolumns+1)
    ind = np.arange(groupCount)

    print("Thresholds:")
    print(threshs)

    print("CIs: ")
    print(cis)

    pylab.bar(ind,threshs, 0.5,yerr=cis)
    pylab.xticks(ind,labels)
    pylab.title('Stimulus Intensity Thresholds')
    

            
        
#summary plot
pylab.subplot(nrows, ncolumns, (nrows-1)*ncolumns + 1)
ind = np.arange(3)
print("Thresholds:")
print(thresholds)
thresholdsAvgList = []

def average(lst): 
    if(len(lst) == 0):
        return 0
    return sum(lst) / len(lst) 
    
thresholdsAvgList.append(average(thresholds['STEREO']))
thresholdsAvgList.append(average(thresholds['SYN']))
thresholdsAvgList.append(average(thresholds['MONO']))
thresholdsListLables = ['STEREO','SYN','MONO']

pylab.bar(ind,thresholdsAvgList, 0.5)
pylab.xticks(ind,thresholdsListLables)
pylab.title('Stimulus Intensity Thresholds')


#register an event to terminate code when window closed
def on_close(event):
    event.canvas.figure.axes[0].has_been_closed = True
    print('Closed Figure')
    quit()

fig.canvas.mpl_connect('close_event', on_close)

pylab.subplots_adjust(left=0.2, right=0.8, bottom=0.1, top=0.9)
pylab.tight_layout(pad=3.0)
pylab.show(block=True)

