from coralScopeLib import *

app = coralScopeApp('/home/pi/coralscope/')
app.GPIOinit()
app.sensorsInit()
app.runGUI(logo_dir="coralscope_logo.png" )