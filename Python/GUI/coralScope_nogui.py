from coralScopeLib import *

app = coralScopeApp('/home/pi/coralscope/')
app.GPIOinit()

print('Set mode to highres')
app.setMode('highres')
print('Take video')
app.takeVideo(20000)
print('Done')