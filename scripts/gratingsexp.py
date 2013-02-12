from aibs.SweepStim import SweepStim
from psychopy import visual, core, event, logging, misc, monitors

"""
This is a sample script that sets up a basic gratings experiment.  This should be performed by the GUI eventually.
"""


#GENERIC PARAMETERS (should be passed by GUI, some of which have been read from config file)
params = {}
params['runs'] = 1 #number of runs
params['shuffle'] = False #shuffle sweep tables
params['preexpsec'] = 2 #seconds at the start of the experiment
params['postexpsec'] = 2 #seconds at the end of the experiment
params['sweeplength'] = 2 #length of sweeps
params['postsweepsec'] = 1 #black period after sweeps (foreground remains)
params['logdir'] = "C:\\ExperimentLogs\\" #where to put the log
params['backupdir'] = "" #backup to network
params['mousename'] = "Spock" #name of the mouse
params['userid'] = "derricw" #name of the user
params['task'] = "" #task type
params['stage'] = "idkwhatthismeans" #stage
params['protocol'] = "" #implemented later
params['nidevice']='Dev1' #NI device name
params['blanksweeps']=3 #blank sweep every x sweeps
params['bgcolor']='gray' #background color
params['syncsqr']=True #display a flashing square for synchronization
params['syncsqrloc']=(-600,-350)


#SET CONSOLE OUTPUT LEVEL, INITIALIZE WINDOWS
#logging.console.setLevel(logging.DEBUG) #uncommet for diagnostics
window = visual.Window(units='norm',monitor='testMonitor', fullscr = True, screen = 0, waitBlanking=False)
window.setColor(params['bgcolor'])

#CREATE BACKGROUND STIMULUS

grating = visual.GratingStim(window,tex="sin",mask="None",texRes=64,
       size=[80,80], sf=1, ori = 0, name='grating', autoLog=False, units = 'deg')
       
#CREATE BACKGROUND FRAME PARAMETERS (what changes between frames and how much)
bgFrame = {}

#CREATE BACKGROUND SWEEP PARAMETERS (what changes between sweeps, and in what order)
bgSweep = {}

bgSweep['Ori'] = ([0,45],1)
bgSweep['SF'] = ([0.5,1],3)
bgSweep['Contrast'] = ([0.5,1],0)
bgSweep['TF'] = ([1],2)

#CREATE FOREGROUND STIMULUS (none for basic gratings experiment)


#CREATE FOREGROUND STIMULUS FRAME PARAMETERS (what changes between frames and how much (BESIDES XPOSITITON WHICH IS AUTOMATIC FOR THIS EXPERIMENT)
fgFrame = {}

#CREATE FOREGROUND SWEEP PARAMETERS (what changes between sweeps)
fgSweep = {}

#CREATE FORAGING CLASS INSTANCE
g = SweepStim(window = window, params = params, bgStim = grating, bgFrame = bgFrame, bgSweep = bgSweep, fgStim = None)
#RUN IT
g.run()