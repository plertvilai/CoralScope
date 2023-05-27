from coralScopeLib import *
import time
import logging
main_folder = '/home/pi/coralscope/'
# logging.basicConfig(filename='/tmp/myapp.log', level=logging.DEBUG, 
#                     format='%(asctime)s %(levelname)s %(name)s %(message)s')
logging.basicConfig(filename=main_folder+'coralScope_gui.log', level=logging.DEBUG) 
logger=logging.getLogger(__name__)

# wait for desktop to stabilize
cnt = 0
while(cnt<5):
	print(cnt)
	cnt = cnt+1
	time.sleep(1)

try:
	app = coralScopeApp(main_folder)
	app.GPIOinit()
	app.sensorsInit()
	app.runGUI(logo_dir="coralscope_logo.png" )
except Exception as err: 
	print(err)
	# log error to file
	logger.error(err)

print("End of program...")