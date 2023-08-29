from coralScopeLabLib import *
import time
import logging
import subprocess

main_folder = '/home/pi/coralscope/'
# logging.basicConfig(filename='/tmp/myapp.log', level=logging.DEBUG, 
#                     format='%(asctime)s %(levelname)s %(name)s %(message)s')
logging.basicConfig(filename=main_folder+'coralScope_gui.log', level=logging.DEBUG) 
logger=logging.getLogger(__name__)

# wait for desktop to stabilize
# cnt = 0
# while(cnt<5):
# 	print(cnt)
# 	cnt = cnt+1
# 	time.sleep(1)

# first run at the beginning
try:
	app = coralScopeLabApp(main_folder)
	app.GPIOinit()
	app.sensorsInit()
	app.runGUI(logo_dir="coralscope_logo.png" )
except Exception as err: 
	print(err)
	# log error to file
	logger.error(err)

# after the end of the first run, check whether 
# push[0] and [1] -> Shutdown
# push[0] only -> restart GUI
# push[1] -> wait
# No push -> end program (not shutdown)
# cnt_restart = 0
# cnt_close = 0
# cnt_shdn = 0
# while(True):
# 	if app.checkPush(0) and app.checkPush(1):
# 		if cnt_shdn >= 5:
# 			subprocess.Popen(['shutdown','-h','now'])
# 		else:
# 			print("Waiting Shutdown %d"%cnt_shdn)
# 			cnt_shdn = cnt_shdn + 1
# 	# elif app.checkPush(0) and not app.checkPush(1):
# 	# 	if cnt_restart >= 5:
# 	# 		app.runGUI(logo_dir="coralscope_logo.png" )
# 	# 	else:
# 	# 		print("Waiting restart %d"%cnt_shdn)
# 	# 		cnt_restart = cnt_restart + 1
# 	elif not app.checkPush(0) and not app.checkPush(1):
# 		if cnt_close >= 5:
# 			break
# 		else:
# 			print("Waiting close %d"%cnt_shdn)
# 			cnt_close = cnt_close + 1
# 	else:
# 		if cnt_close > 0 or cnt_shdn > 0 or cnt_restart > 0:
# 			cnt_close = 0
# 			cnt_shdn = 0
# 			cnt_restart = 0
# 			print("Restart all counts")
# 	time.sleep(1)

print("End of program...")