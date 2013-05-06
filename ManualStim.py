from psychopy import core, visual, event, misc, monitors
from pyglet.window import key
import time
import numpy
import sys

CONTROLS="""
RIGHT/LEFT: WIDTH
UP/DOWN: HEIGHT
+ / -: CONTRAST/COLOR
[ / ]: SF
; / ': TF
, / .: BG Color
MOUSE: MOVE OBJECT
MOUSEWHEEL: ROTATE
~: HOLD
NUMBERKEYS: STIMULI SELECT
M: toggle gaussian mask
T: Toggle text
"""

class ManualStim(object):
	"""docstring for ManualStim"""
	##TODO: REWRITE.  Make it more extensible.  Fix text display to not be so laggy.
	def __init__(self, *args, **kwargs):

		print CONTROLS

		self.args = args
		self.kwargs = kwargs

		self.screen=0
		self.monitor='testMonitor'

		self.tf = 0
		self.ori = 0
		self.contrast = 1
		self.phase = 0
		self.sf = 1
		self.size = (10,10)
		self.bgcolor=0
		self.textstr=""
		self.mask=None

		for k,v in self.kwargs.iteritems():
			setattr(self,k,v)

		self.window = visual.Window(units='deg', monitor=self.monitor,fullscr=True,
			screen=self.screen,waitBlanking=True)
		self.window.setColor(self.bgcolor)

		self.stimuli = [
			visual.GratingStim(self.window,tex="sin",mask='None',texRes=512,
				size=[10,10],sf=1,ori=0,name='grating',autoLog=False,units='deg',
				pos=[0,0]),
			visual.GratingStim(self.window,tex=None,mask='None',texRes=512,
				size=[10,10],ori=0,name='box',autoLog=False,units='deg',pos=[0,0])
		]

		self.text = visual.TextStim(self.window,text=self.textstr,pos=(-8,-10),wrapWidth=100)
		self.drawtext = True

		self.current = None

		self.keys = key.KeyStateHandler()
		self.window.winHandle.push_handlers(self.keys)

		self.mouse = event.Mouse(win=self.window)
		self.mouse.setVisible(0)

	def _updateText(self):
		self.textstr = "Position: " + str(self.mouse.getPos()) + " deg\n" + \
			"Size: " + str(self.size) + " deg\n" + "Contrast: " + str(self.contrast) + \
			"\n" + "SF: " + str(self.sf) + " cycles/deg\n" + "TF: " + str(self.tf) + \
			" cycles/sec\n" + "Ori: " + str(self.ori%360) + " deg"
		self.text.setText(self.textstr)


	def _handleKeys(self):
		
		if self.current is not None:
		#SIZE
			if self.keys[key.RIGHT]:
				self.stimuli[self.current].setSize([0.1,0],"+")
			elif self.keys[key.LEFT]:
				self.stimuli[self.current].setSize([0.1,0],"-")
			if self.keys[key.UP]:
				self.stimuli[self.current].setSize([0,0.1],"+")
			elif self.keys[key.DOWN]:
				self.stimuli[self.current].setSize([0,0.1],"-")
			self.size = self.stimuli[self.current].size

			if self.keys[key.BRACKETLEFT]:
				self.stimuli[self.current].setSF(0.99,"/")
			if self.keys[key.BRACKETRIGHT]:
				self.stimuli[self.current].setSF(0.99,"*")
			self.sf = self.stimuli[self.current].sf

			if self.stimuli[self.current].name in ["grating","box"]:
				if self.keys[key.EQUAL]:
					con = max(self.stimuli[self.current].contrast-0.005,-1)
					self.stimuli[self.current].setContrast(con)
				elif self.keys[key.MINUS]:
					con = min(self.stimuli[self.current].contrast+0.005,1)
					self.stimuli[self.current].setContrast(con)
				if self.keys[key.SEMICOLON]:
					self.tf += 0.005
				elif self.keys[key.APOSTROPHE]:
					self.tf -= 0.005
			self.contrast = self.stimuli[self.current].contrast

			if self.keys[key.M]:
				if self.mask == None:
					self.stimuli[self.current].setMask('gauss')
					self.mask = "gauss"
				else:
					self.stimuli[self.current].setMask(None)
					self.mask = None
				time.sleep(0.1)

			if self.keys[key.T]:
				if self.drawtext:
					self.drawtext=False
				else:
					self.drawtext=True
				time.sleep(0.1)

		#STIMULUS #
		if self.keys[key.NUM_0]:
			self.current = 0
		elif self.keys[key.NUM_1]:
			self.current = 1

		#ESCAPE
		if self.keys[key.ESCAPE]:
			self._cleanup()

	def _handleMouse(self):
		#POSITION
		pos = self.mouse.getPos()
		wheel = self.mouse.getWheelRel()
		if self.current is not None:
			self.stimuli[self.current].setPos(pos)
			if wheel[1] != 0:
				self.stimuli[self.current].setOri(wheel[1]*15,"+")
			self.ori = self.stimuli[self.current].ori

	def _update(self):
		pass

	def _cleanup(self):
		self.window.close()
		sys.exit()

	def run(self):
		t = core.Clock()
		while 1:

			self._handleKeys()
			self._handleMouse()
			if self.drawtext: self._updateText()
			if self.current is not None:
				self.stimuli[self.current].draw()
				self.stimuli[self.current].setPhase(t.getTime()*self.tf)
				if self.drawtext: self.text.draw()
			self.window.flip()



	
def main(*args,**kwargs):
		ms = ManualStim(*args,**kwargs)
		ms.run()

if __name__ == '__main__':
	main(screen=1)
