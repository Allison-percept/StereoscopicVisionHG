import math
import re
import os

import viz
import vizact
import vizmat
import vizshape
import projector

from vizconnect.util.display.christie_autocal import auto_cal_parser
from vizconnect.util.display.christie_autocal import projector_manager


fView = viz.addView(scene=2)
fWindow = viz.addWindow()
fWindow.setSize(1, 1)
fWindow.setPosition(0, 1)
fWindow.setView(fView)
fWindow.ipd(0)
fWindow.visible(False)

with viz.cluster.MaskedContext(viz.MASTER):
	fWindow.setSize(0.1, 0.1)

IPD = 0.06

NEAR_PLANE_DIST = 0.01


class Frustum(viz.VizNode):
	def __init__(self, l, r, b, t, n, f, scene=viz.MainScene):
		viz.VizNode.__init__(self, viz.addGroup(scene=scene).id)
		self.l = l
		self.r = r
		self.b = b
		self.t = t
		self.n = n
		self.f = f

	def setNear(self, near):
		self.l *= near
		self.r *= near
		self.b *= near
		self.t *= near
		self.n = near

	def getProjectionMatrix(self):
		mat = vizmat.Transform()
		mat.makeFrustum(self.l, self.r, self.b, self.t, self.n, self.f)
		return mat

	def getMesh(self, n):
		l = self.l*n
		r = self.r*n
		b = self.b*n
		t = self.t*n

		viz.startLayer(viz.QUADS)

		viz.vertex( l, t, n)
		viz.vertex( r, t, n)
		viz.vertex( r, t, n)
		viz.vertex( r, b, n)
		viz.vertex( r, b, n)
		viz.vertex( l, b, n)
		viz.vertex( l, b, n)
		viz.vertex( l, t, n)

		object = viz.endLayer()
		return object

	def apply(self, mask=-1):
		scale = 1.0
		l = self.l*scale
		r = self.r*scale
		b = self.b*scale
		t = self.t*scale
		n = self.n*scale
		f = self.f
		euler = self.getEuler()
		pos = self.getPosition()
		scale = 1.0
		with viz.cluster.MaskedContext(mask):
			fWindow.frustum(l, r, b, t, n, f)
			fView.setEuler(euler)
			fView.setPosition(pos)


class RenderFrustum(object):
	def __init__(self, l, r, b, t, n, f, euler, pos=[0,0,0], scene=viz.MainScene):
		self.renderGroup = viz.addGroup(scene=scene)
		self._scene = scene
		self._debug = False

		self.boundingFrustum = Frustum(l, r, b, t, n, f, scene=scene)
		self.boundingFrustum.setEuler(euler)
		self.boundingFrustum.setPosition(pos)

		self.renderFrustum = Frustum(l, r, b, t, n, f, scene=scene)
		self.renderFrustum.setEuler(euler)
		self.renderFrustum.setPosition(pos)

		self.movedFrustum = Frustum(l, r, b, t, n*NEAR_PLANE_DIST, f, scene=scene)
		self.movedFrustum.setEuler(euler)
		self.movedFrustum.setPosition(pos)

		self.eightBoundingPoints = []

	def getFrustumIntersection(self, screen):
		#viz.vertex( l*f/n, t*f/n, f)
		screen.collideMesh()
		screen.disable( viz.DYNAMICS )

		# find an intersection line with the screen
		MAX_FAR = 100.0
		mat = vizmat.Transform()
		mat.setEuler(self.renderFrustum.getEuler())

		ptList = []
		distPtList = []

		pt = mat.preMultVec([self.renderFrustum.l*MAX_FAR, self.renderFrustum.t*MAX_FAR, MAX_FAR])
		info = viz.phys.intersectLine([0,0,0], pt)
		ptList.append(info.point)
		distPtList.append(pt)

		pt = mat.preMultVec([self.renderFrustum.r*MAX_FAR, self.renderFrustum.t*MAX_FAR, MAX_FAR])
		info = viz.phys.intersectLine([0,0,0], pt)
		ptList.append(info.point)
		distPtList.append(pt)

		pt = mat.preMultVec([self.renderFrustum.l*MAX_FAR, self.renderFrustum.b*MAX_FAR, MAX_FAR])
		info = viz.phys.intersectLine([0,0,0], pt)
		ptList.append(info.point)
		distPtList.append(pt)

		pt = mat.preMultVec([self.renderFrustum.r*MAX_FAR, self.renderFrustum.b*MAX_FAR, MAX_FAR])
		info = viz.phys.intersectLine([0,0,0], pt)
		ptList.append(info.point)
		distPtList.append(pt)

		if self._debug:
			for point in ptList:
				sphere = vizshape.addSphere(0.1)
				sphere.setParent(self.renderGroup)
				sphere.setPosition(point)
				sphere.color(1.0, 1.0, 0.0)

		pt = mat.preMultVec([0, 0, MAX_FAR])
		info = viz.phys.intersectLine([0,0,0], pt)

		# find a good starting reference distance
		validPoint = None
		point = vizmat.Vector(info.point)
		#print point
		if point.length() > 0.01:
			validPoint = point

		# get the a middle plane distance
		#print validPoint
		if validPoint:
			# find the min dist that still collides with the scene
			minDist = self.recursivelyFindPlane(self.renderFrustum, minDist=0.001, maxDist=point.length(), screen=screen)
			maxDist = self.recursivelyFindPlane(self.renderFrustum, minDist=point.length(), maxDist=100.0, screen=screen, near=False)
			#print minDist, maxDist, point.length()

			if self._debug:
				mesh = self.renderFrustum.getMesh(minDist)
				mesh.setEuler(self.renderFrustum.getEuler())
				mesh.setParent(self.renderGroup)
				mesh.color(1, 1, 0)
				mesh.alpha(0.3)

				mesh = self.renderFrustum.getMesh(maxDist)
				mesh.setEuler(self.renderFrustum.getEuler())
				mesh.setParent(self.renderGroup)
				mesh.color(1, 0, 1)
				mesh.alpha(0.3)

			self.boundingFrustum.setNear(minDist)
			self.boundingFrustum.f = maxDist

			self.renderFrustum.setNear(minDist)
			self.renderFrustum.f = maxDist

			self.visualizedFrustum = Frustum(	self.renderFrustum.l,
												self.renderFrustum.r,
												self.renderFrustum.b,
												self.renderFrustum.t,
												self.renderFrustum.n,
												self.renderFrustum.f,
												scene=self._scene)
			self.visualizedFrustum.setMatrix(self.renderFrustum.getMatrix())
			self.visualizedFrustum.setParent(self.renderGroup)
			self.visualizedFrustum.collideNone()
			self.visualizedFrustum.visible(False)

			# add the eight bounding points from the original frustum
			l = self.boundingFrustum.l
			r = self.boundingFrustum.r
			b = self.boundingFrustum.b
			t = self.boundingFrustum.t
			n = self.boundingFrustum.n
			f = self.boundingFrustum.f

			self.eightBoundingPoints.append(vizmat.Vector(l, t, n))
			self.eightBoundingPoints.append(vizmat.Vector(r, t, n))
			self.eightBoundingPoints.append(vizmat.Vector(l, b, n))
			self.eightBoundingPoints.append(vizmat.Vector(r, b, n))

			self.eightBoundingPoints.append(vizmat.Vector(l*f/n, t*f/n, f))
			self.eightBoundingPoints.append(vizmat.Vector(r*f/n, t*f/n, f))
			self.eightBoundingPoints.append(vizmat.Vector(l*f/n, b*f/n, f))
			self.eightBoundingPoints.append(vizmat.Vector(r*f/n, b*f/n, f))

			self.boundingCenter = vizmat.Vector(0,0,0)
			# using the eight bounding points find the center of the projection area
			for point in self.eightBoundingPoints:
				self.boundingCenter += point
			self.boundingCenter /= 8.0

		self.renderGroup.visible(False)


	def recursivelyFindPlane(self, frustum, minDist, maxDist, screen, depth=0, maxDepth=20, near=True):
		midDist = (maxDist+minDist)/2.0
		mesh = frustum.getMesh(midDist)
		mesh.collideMesh()
		mesh.setEuler(self.renderFrustum.getEuler())
		intersections = viz.phys.intersectNode(mesh)
		mesh.collideNone()
		mesh.visible(False)
		mesh.remove()

		#print depth, minDist, maxDist, midDist, intersections

		if depth > maxDepth and not (screen in intersections):
			return midDist

		# if it's found, try in the closer half
		if (near and (screen in intersections)) or (not near and not (screen in intersections)):
			return self.recursivelyFindPlane(frustum, minDist=minDist, maxDist=midDist, screen=screen, depth=depth+1, maxDepth=maxDepth, near=near)
		# if it's not found try in the farther half
		else:
			return self.recursivelyFindPlane(frustum, minDist=midDist, maxDist=maxDist, screen=screen, depth=depth+1, maxDepth=maxDepth, near=near)

	def visible(self, bool):
		self.renderGroup.visible(bool)

	def apply(self, mask):
		self.visualizedFrustum.apply(mask)

	def computeNewFrustum(self, eye):
		# get the position of the eye
		pos = eye.getPosition()

		mat = self.renderFrustum.getMatrix()
		mat = mat.inverse()

		adjPos = vizmat.Vector(mat.preMultVec(pos))

		# get the line from the eye point to the center
		eyeLine = self.boundingCenter - adjPos

		# determine the angle for each of the
		newL = 1000000
		newR = -1000000
		newB = 1000000
		newT = -1000000
		for pt in self.eightBoundingPoints:
			lr = vizmat.AngleBetweenVector([0, 0, 1], [pt[0]-adjPos[0], 0, pt[2]-adjPos[2]])
			bt = vizmat.AngleBetweenVector([0, 0, 1], [0, pt[1]-adjPos[1], pt[2]-adjPos[2]])
			# if the x value is negative then make the angle negative as well
			#print 'pt', pt, lr
			if pt[0]-adjPos[0] < 0:
				lr = -lr
			if pt[1]-adjPos[1] < 0:
				bt = -bt
			#print lr
			if lr < newL:
				newL = lr
			if lr > newR:
				newR = lr

			if bt < newB:
				newB = bt
			if bt > newT:
				newT = bt

#		self.movedFrustum = Frustum(	math.tan(newL*math.pi/180),
#										math.tan(newR*math.pi/180),
#										math.tan(newB*math.pi/180),
#										math.tan(newT*math.pi/180),
#										1.0,
#										1000.0,
#										scene=self._scene)
		self.movedFrustum.l = math.tan(newL*math.pi/180)*NEAR_PLANE_DIST
		self.movedFrustum.r = math.tan(newR*math.pi/180)*NEAR_PLANE_DIST
		self.movedFrustum.b = math.tan(newB*math.pi/180)*NEAR_PLANE_DIST
		self.movedFrustum.t = math.tan(newT*math.pi/180)*NEAR_PLANE_DIST
		self.movedFrustum.setPosition(eye.getPosition())
		self.movedFrustum.setEuler(self.renderFrustum.getEuler())

	def remove(self):
		self.boundingFrustum.remove()
		self.renderFrustum.remove()
		self.movedFrustum.remove()


class TextureProjector(object):
	def __init__(self, texture, scene=viz.MainScene):
		self._scene = scene
		self._texture = texture

		# open the fragment shader, assuming it's relative to this code file
		vertCode = ""
		with open(os.path.join(os.path.dirname(__file__), 'projective_texture.vert'), 'r') as vertFile:
			vertCode = vertFile.read()
		fragCode = ""
		with open(os.path.join(os.path.dirname(__file__), 'projective_texture.frag'), 'r') as fragFile:
			fragCode = fragFile.read()

		# Make a new shader, and assign some default values for the uniforms. These
		# will be replaced on update.
		self._shader = viz.addShader(frag=fragCode, vert=vertCode)
		matL = vizmat.Transform().get()
		self._uniformList = [	viz.addUniformFloat('line1', (matL[0:4])),
								viz.addUniformFloat('line2', (matL[4:8])),
								viz.addUniformFloat('line3', (matL[8:12])),
								viz.addUniformFloat('line4', (matL[12:16])),
								viz.addUniformFloat('pline1', (matL[0:4])),
								viz.addUniformFloat('pline2', (matL[4:8])),
								viz.addUniformFloat('pline3', (matL[8:12])),
								viz.addUniformFloat('pline4', (matL[12:16])),
								viz.addUniformInt('projection_tex', 2)]
		self._shader.attach( *self._uniformList )

	def affect(self, model):
		"""Allows a model (VizNode) to be specified as a target for texture projection.

		@model the VizNode object to texture.
		"""
		model.visible(True)

		self._model = model
		self._model.apply(self._shader)
		self._model.texture(self._texture, unit=2)

		model.visible(False)


	def update(self, mat, proj, mask):
		self._model.visible(True)

		# create a modelview matrix, converting from right to left-hand coordinates
		mvm = vizmat.Transform()
		pos = mat.getPosition()
		mvm.setPosition(pos[0], pos[1], -pos[2])
		q = mat.getQuat()
		mvm.setQuat(-q[0], -q[1], q[2], q[3])
		mvm = mvm.inverse()

		# set the modelview matrix
		# TODO: update this with newer version of vizard, should have matrix
		# set instead of neading to modify lines
		matL = mvm.get()
		line1 = (matL[0:4])
		line2 = (matL[4:8])
		line3 = (matL[8:12])
		line4 = (matL[12:16])
		with viz.cluster.MaskedContext(mask):
			self._uniformList[0].set(line1)
			self._uniformList[1].set(line2)
			self._uniformList[2].set(line3)
			self._uniformList[3].set(line4)

		# set the projection matrix
		# TODO: update this with newer version of vizard, should have matrix
		# set instead of neading to modify lines
		matL = proj.get()
		pline1 = (matL[0:4])
		pline2 = (matL[4:8])
		pline3 = (matL[8:12])
		pline4 = (matL[12:16])
		with viz.cluster.MaskedContext(mask):
			self._uniformList[4].set(pline1)
			self._uniformList[5].set(pline2)
			self._uniformList[6].set(pline3)
			self._uniformList[7].set(pline4)

	def remove(self):
		self._shader.remove()


class ChannelWrapper(object):
	"""
	"""
	def __init__(self,
					eye,
					origin,
					renderFrustumList,
					rightScreenModel,
					leftScreenModel,
					projectorList,
					scene=viz.MainScene,
					resolution=[2048, 1024]):

		self._eye = eye
		self._rightScreenModel = rightScreenModel
		self._leftScreenModel = leftScreenModel
		self._projectorList = projectorList
		self._renderFrustumList = renderFrustumList
		self._matchMainView = True

		# get the origin information
		self._origin = origin

		# make the render node that will capture the scene from the new
		# point of view/frustum defined by the moved eye position and the dynamically computed
		# screen intersection points.
		self._rightTexture = viz.addRenderTexture(wrap=viz.CLAMP_TO_BORDER, borderColor=viz.WHITE, format=viz.TEX_RGB, scene=viz.Scene2)
		node = viz.addRenderNode(size=resolution, inheritView=False, autoClip=False, scene=viz.Scene2)
		node.setRenderTexture(texture=self._rightTexture, buffer=viz.RENDER_COLOR)
		node.setScene(viz.Scene2)
#		node.setMultiSample(2)
		self._rightRenderNode = node
#		self._rightRenderNode.setParent(self._origin)
		self._rightRenderTexture = node.getRenderTexture()

		self._leftTexture = viz.addRenderTexture(wrap=viz.CLAMP_TO_BORDER, borderColor=viz.WHITE, format=viz.TEX_RGB, scene=viz.MainScene)
		node = viz.addRenderNode(size=resolution, inheritView=False, autoClip=False, scene=scene)
		node.setRenderTexture(texture=self._leftTexture, buffer=viz.RENDER_COLOR)
		node.setScene(viz.MainScene)
#		node.setMultiSample(2)
		self._leftRenderNode = node
#		self._leftRenderNode.setParent(self._origin)
		self._leftRenderTexture = node.getRenderTexture()

		# create a shader that will do the texture projection on the model
		self._rightTextureProjector = TextureProjector(self._rightRenderTexture, viz.Scene2)
		self._rightTextureProjector.affect(rightScreenModel)

		self._leftTextureProjector = TextureProjector(self._leftRenderTexture, scene)
		self._leftTextureProjector.affect(leftScreenModel)

		self._updateEvent = vizact.onupdate(0, self.update)

	def update(self):
		# update the rendering frustum and rendering window
		i = 0
		for renderFrustum in self._renderFrustumList:
			mask = self._projectorList[i].mask

			renderFrustum.apply(mask)

			rmat = self._eye.getMatrix(viz.ABS_GLOBAL)
			rmat.preTrans([IPD/2.0, 0, 0])
			renderFrustum.computeNewFrustum(rmat)
			rproj = renderFrustum.movedFrustum.getProjectionMatrix()
			rmat = renderFrustum.movedFrustum.getMatrix(viz.ABS_GLOBAL)

			lmat = self._eye.getMatrix(viz.ABS_GLOBAL)
			lmat.preTrans([-IPD/2.0, 0, 0])
			renderFrustum.computeNewFrustum(lmat)
			lproj = renderFrustum.movedFrustum.getProjectionMatrix()
			lmat = renderFrustum.movedFrustum.getMatrix(viz.ABS_GLOBAL)

			rmate = vizmat.Transform(rmat)
			lmate = vizmat.Transform(lmat)
			rmate.postMult(self._origin.getMatrix(viz.ABS_GLOBAL))
			lmate.postMult(self._origin.getMatrix(viz.ABS_GLOBAL))
#
#			lmate = self._eye.getMatrix(viz.ABS_GLOBAL)
#			lmate.preTrans([-IPD/2.0, 0, 0])
#			rmate = self._eye.getMatrix(viz.ABS_GLOBAL)
#			rmate.preTrans([IPD/2.0, 0, 0])

			with viz.cluster.MaskedContext(mask):
				self._rightRenderNode.setMatrix(rmate)
				self._rightRenderNode.setProjectionMatrix(rproj)

				self._leftRenderNode.setMatrix(lmate)
				self._leftRenderNode.setProjectionMatrix(lproj)

			self._rightTextureProjector.update(rmat, rproj, mask)
			self._leftTextureProjector.update(lmat, lproj, mask)

#			if renderFrustum.renderGroup.getVisible():
			viz.MainView.setPosition(lmate.getPosition())
			#viz.MainWindow.stereo(viz.STEREO_RIGHT)

			i+=1

	def remove(self):
		self._rightScreenModel.remove()
		self._leftScreenModel.remove()
		for projector in self._projectorList:
			projector.remove()
		for frust in self._renderFrustumList:
			frust.remove()
		self._leftRenderNode.remove()
		self._leftRenderTexture.remove()
		self._rightRenderNode.remove()
		self._rightRenderTexture.remove()
		self._leftTextureProjector.remove()
		self._rightTextureProjector.remove()
		self._updateEvent.remove()


class ProjectorConfiguration(object):
	"""Class representing a collection of projectors that make up a dome layout"""

	def __init__(self, origin):
		self.projectorList = []
		self.modelFile = ""
		self._channelWrapper = None
		self._channelToClusterMappingDict = {}
		self._eye = None
		self._origin = origin
		fWindow.visible(True)

	def parseFile(self, filename, channelToComputerMappingFilename, modelFilename="", usingStereo=True, stereoMode=viz.STEREO_VERT, scene=viz.MainScene):

		if not os.path.isfile(filename):
			viz.logWarn('** Warning: the configuration file could not be found or parsed.')
			return

		fWindow.stereo(stereoMode)
		# extract EGG definition from file
		projectorList = []
		renderFrustumList = []
		screenDistance = 1.0

		# parse the cristie auto cal file to get the settings we'll need
		configdict = auto_cal_parser.ConvertXmlToDict(filename)

		# parse the config file and split out the ip for each channel
		self._channelToClusterMappingDict = {}
		localCtr = 1
		computerList = []
		with open(channelToComputerMappingFilename, 'r') as file:
			# read the header
			file.readline()
			for line in file.readlines():
				comp, chan = line.split('\t')
				chan = int(chan)

				# if the computer name is localhost, create a valid mask ID
				if comp.lower() == 'localhost' or comp in computerList:
					mask = 1 << localCtr
				# if it's not, then get the mask ID of the specified computer name
				else:
					mask = viz.cluster.getClientID( comp )

				localCtr += 1

				# save the mask
				computerList.append(comp)
				self._channelToClusterMappingDict[chan] = mask

		# parse the cal file to get the center of the calibration relative to the model
		center = configdict['ConfigInfo']['TargetLocator']['Eye_Point']['_text']
		center = re.sub(r'\s', '', center).split(',')
		eyePoint = [float(center[0]), float(center[1]), float(center[2])]

		# get the model file from the calibration file
		if not modelFilename:
			self.modelFile = configdict['ConfigInfo']['Screen']['VRML']['_text']
			self.modelFile = os.path.normpath(os.path.join(os.path.dirname(filename), self.modelFile)).replace('\\', '/')
		else:
			self.modelFile = modelFilename

		# load the model file
		self._rightModel = viz.add(self.modelFile, scene=viz.Scene2)
		self._rightModel.renderToEye(viz.RIGHT_EYE)
		self._rightModel.setEuler([0, 90, 0])
#		self._rightModel.setScale([2, 2, 2])
#		self._rightModel.setParent(self._origin)

		self._leftModel = viz.add(self.modelFile, scene=scene)
		self._leftModel.renderToEye(viz.LEFT_EYE)
		self._leftModel.setEuler([0, 90, 0])
#		self._leftModel.setScale([2, 2, 2])
#		self._leftModel.setParent(self._origin)

		self._dataList = []

		# parse the configuration dict to get the projector information
		channel = 1
		for proj in configdict['ConfigInfo']['Projector']:
			# update the projector information

			"""
			<Name>Channel_8E-7</Name>
			<DeviceSnippet>
				<device UID="Wild***00:1A:D7:00:7A:8E" name="M-Projector" password="" type="Wild" version="1.0">
					<id>000</id>
					<connection type="ETHERNET">
						<address>192.168.1.101</address>
						<port>3002</port>
					</connection>
				</device>
			</DeviceSnippet>
			"""
			computer = proj['DeviceSnippet']['device']['connection']['address']


			channelExtents = proj['Channel_Extents']

			angL = float(channelExtents['HFOV']['Left']['_text'])
			angR = float(channelExtents['HFOV']['Right']['_text'])
			angB = float(channelExtents['VFOV']['Bottom']['_text'])
			angT = float(channelExtents['VFOV']['Top']['_text'])

			l = math.tan(angL)
			r = math.tan(angR)
			b = math.tan(angB)
			t = math.tan(angT)

			euler = [	float(channelExtents['Heading']['Yaw']['_text'])*180.0/math.pi,
						-float(channelExtents['Heading']['Pitch']['_text'])*180.0/math.pi,
						-float(channelExtents['Heading']['Roll']['_text'])*180.0/math.pi]

			mask = self._channelToClusterMappingDict[channel]

			self._dataList.append((euler, l, r, b, t, mask, channel, computer))
			# store the computer name
			computerList.append(computer)
			# increment ctr used for generating localhost mask IDs
			channel += 1

		for data in self._dataList:
			euler, l, r, b, t, mask, channel, computer = data

			renderFrustum = RenderFrustum(l, r, b, t, 1, 1000000.0, euler, eyePoint, scene=scene)
			# compute the bounding box of the rendering frustum for the channel
			# doesn't matter what model we use
			renderFrustum.getFrustumIntersection(self._rightModel)

			# create the projector set the euler and compute a "screen" for the projector
			projectorWrapper = projector_manager.Projector(channel=int(channel), mask=mask, computer=computer, usingStereo=usingStereo, stereoMode=stereoMode)
			projectorWrapper.setEuler(euler)
			projectorWrapper.offsetMat = projectorWrapper.getMatrix()
			projectorWrapper.computeScreen(l, r, b, t, screenDistance)

			# store the items in a list
			projectorList.append(projectorWrapper)
			renderFrustumList.append(renderFrustum)

		self._channelWrapper = ChannelWrapper(self._eye, self._origin, renderFrustumList, self._rightModel, self._leftModel, projectorList, scene)

		return projectorList

	def getOrigin(self):
		return self._origin

	def start(self):
		viz.ipd(0)

	def setViewpoint(self, eye):
		self._eye = eye

	def remove(self):
		self._channelWrapper.remove()
		fWindow.visible(False)

