from aibs.Terrain import Terrain
from aibs.Foraging import Foraging
from psychopy import visual, core, event, logging, misc, monitors

"""
This is a sample script that sets up a basic Foraging experiment.  This should be performed by the GUI.
"""

#GENERIC PARAMETERS (should be passed by GUI, some of which have been read from config file)
params = {}
params['runs'] = 4 #number of runs
params['shuffle'] = False #shuffle sweep tables
params['preexpsec'] = 10 #seconds at the start of the experiment
params['postexpsec'] = 2 #seconds at the end of the experiment
params['sweeplength'] = 5 #length of sweeps
params['postsweepsec'] = 0 #black period after sweeps (foreground remains)
params['rewardtime'] = 0.03 #length of reward for mouse
params['logdir'] = "C:\\ForagingLogs\\" #where to put the log
params['backupdir'] = "" #backup to network
params['mousename'] = "test" #id of mouse
params['userid'] = "derricw" #name of the user
params['task'] = "Virtual Foraging" #task type
params['stage'] = "Disk, Plexi" #stage
params['protocol'] = "" #implemented later
params['nidevice']='Dev2' #NI device name
params['rewardline']=0 #NI DO line
params['rewardport']=1 #NI DO port
params['encodervinchannel']=1 #NI Vin channel
params['encodervsigchannel']=2 #NI Vsig channel
params['blanksweeps']=7 #blank sweep e                if self.fgStim is not None: 
params['bgcolor']='gray' #background color
params['syncsqr']= True
params['syncsqrloc']=(900,500) #(900,500) upper right corner
params['comments']="SOME COMMENTS FROM THE USER"
params['script']=__file__

#TERRAIN CREATION AND PARAMETERS (see Terrain for additional parameters)
terrain = Terrain(['color','orientation'])
terrain.colormatters = True
terrain.orientation = 45
terrain.correctfreq = 1
terrain.lapdistance = 3500
terrain.windowwidth = 200
terrain.selectiontime = 25
terrain.speedgain = 4
terrain.colorrandom = True
terrain.oriarray = [0,45]
terrain.oricorrect = 0
terrain.objectwidthDeg = 23
terrain.colorcorrect = terrain.black
terrain.color = terrain.white


#SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
#logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0, waitBlanking = False)
window.setColor(params['bgcolor'])

#CREATE BACKGROUND STIMULUS

grating = visual.GratingStim(window,tex="sin",mask="None",texRes=64,
       size=[160,160], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
       
#CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
bgFrame = {}

#CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)  
bgSweep = {}

bgSweep['Ori'] = (range(0,360,45),0)
bgSweep['SF'] = ([0.1,0.2],1)
bgSweep['Contrast'] = ([1],3)
bgSweep['TF'] = ([1,2,3],2)
bgSweep['Phase'] = ([0],4)

#CREATE FOREGROUND STIMULUS
monitor = monitors.Monitor('testMonitor')
target = visual.Rect(window,width = misc.deg2pix(terrain.objectwidthDeg,monitor), height = misc.deg2pix(terrain.objectwidthDeg,monitor), units = 'pix', fillColor = 'black', lineColor = 'black', autoLog=False)
#img = visual.ImageStim(window, image = "C:\\Users\\derricw\\Pictures\\facepalm.jpg", size = [450,300], units = 'pix', autoLog=False) #creates an image from an image in specified directory
#CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much (BESIDES XPOSITITON WHICH IS AUTOMATIC FOR THIS EXPERIMENT)
fgFrame = {}

#CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
fgSweep = {}

#CREATE FORAGING CLASS INSTANCE
f = Foraging(window = window, terrain = terrain, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = target)
#RUN IT
f.run()