from __future__ import print_function
from psychopy import data, gui, core
from psychopy.tools.filetools import fromFile
import pylab
from Tkinter import Tk
from tkinter.filedialog import askopenfilenames

# set bins
bins = 10

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

#keep both list the same length
if(len(allIntensities[0]) > len(allResponses[0])):
    del allIntensities[0][-1]


#plot each staircase
pylab.subplot(121)
colors = 'brgkcmbrgkcm'
lines, names = [],[]
for fileN, thisStair in enumerate(allIntensities):
    #lines.extend(pylab.plot(thisStair))
    #names = files[fileN]
    pylab.plot(thisStair, label=files[fileN])
#pylab.legend()

#get combined data

combinedInten, combinedResp, combinedN = \
             data.functionFromStaircase(allIntensities, allResponses, bins)

#fit curve - in this case using a Weibull function
fit = data.FitWeibull(combinedInten, combinedResp, expectedMin =0.25,sems = [1.0] * bins)
smoothInt = pylab.arange(0.0, 0.5, 0.001)
smoothResp = fit.eval(smoothInt)
thresh = fit.inverse(0.625)
print("threshold: ")
print(thresh)

#plot curve
pylab.subplot(122)
pylab.plot(smoothInt, smoothResp, '-')
pylab.plot([thresh, thresh],[0,0.625],'--'); pylab.plot([0, thresh],\
[0.625,0.625],'--')
pylab.title('threshold = %0.3f' %(thresh))
#plot points
pylab.plot(combinedInten, combinedResp, 'o')
pylab.ylim([0,1])


pylab.show()