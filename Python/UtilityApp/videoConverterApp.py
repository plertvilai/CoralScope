import tkinter as tk
from tkinter import filedialog 
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime
import glob
import subprocess
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def h264toMp4(fullfilename,mp4path,fps=30):
	'''Simple conversion from raw h264 videos from RPi to MP4 format with 30fps'''
	#use os.path.basename to extract only filename without path and extension
	filename =os.path.basename(fullfilename).split('.')[0]
	# print('%s/%s.mp4'%(mp4path,filename))
	command = 'ffmpeg -framerate %d -i %s -qscale:v 0 -vcodec copy -acodec copy %s%s.mp4' %(fps,fullfilename,mp4path,filename)
	subprocess.call(command,shell=True) #run command
	return

class videoApp():
    def __init__(self,w=600,h=480):
        self.w = w # window width
        self.h = h # window height
        
        try:
            bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            logo_file = "logo_bw.png"
            self.logo_dir = os.path.abspath(os.path.join(bundle_dir,logo_file))
            print(self.logo_dir)
        except Exception:
            print("Failed to get local path")
            self.logo_dir = ""
        self.root = tk.Tk() # main GUI object
        
    def runGUI(self):
        #---------- App Components ---------#
        self.root.title("coralScope")
        # create a full screen window
        self.root.geometry('%dx%d+%d+%d' % (self.w, self.h, 0, 0))
        
        # display logo
        try:
            load = Image.open(resource_path(self.logo_dir))
            resize_image  = load.resize((100,100))
            render = ImageTk.PhotoImage(resize_image)
            img = tk.Label(image=render)
            img.image = render
            img.place(x=25, y=25)
        except Exception:
            print('Load logo failed.')

        # Logo Text Label
        self.logo_label = tk.Label(text="CoralScope",font=("Arial", 25))
        self.logo_label.place(x=150, y=25)
        
        # Version Text Label
        self.version_label = tk.Label(text="v1.0",font=("Arial", 15))
        self.version_label.place(x=50, y=400)
        
        # Title Text Label
        self.title_label = tk.Label(text="Video Processing App",font=("Arial", 25))
        self.title_label.place(x=150, y=75)
        
        # Message label
        self.sv = tk.StringVar()
        self.message_label = tk.Label(textvariable=self.sv,font=("Arial", 15),bg='green', fg='white')
        self.message_label.place(x=100, y=175)
        self.sv.set('STATUS: OK')
        
        # Browse input folder
        self.input_folder_button = tk.Button(self.root, text ="Input Folder",font=("Arial", 15), command = self.browseInputFolderCallBack)
        self.input_folder_button.place(x=100, y=250)
        
        # Browse output folder
        self.output_folder_button = tk.Button(self.root, text ="Output Folder",font=("Arial", 15), command = self.browseOutputFolderCallBack)
        self.output_folder_button.place(x=100, y=300)
        
        # Run program
        self.run_button = tk.Button(self.root, text ="RUN",font=("Arial", 20), command = self.runProgram)
        self.run_button.place(x=150, y=350)
        
        #  output folder label
        self.output_folder_label = tk.Label(text=" ",font=("Arial", 15))
        self.output_folder_label.place(x=250, y=300)
        
        # Detected video labels
        self.vidnum_label = tk.Label(text=" ",font=("Arial", 15))
        self.vidnum_label.place(x=250, y=250)
        
        #self.updateApp()
        self.root.mainloop()
    
    def errorMessage(self,e):
        s=str(e)
        # update message
        self.sv.set('ERROR: %s'%s)
        self.message_label.config(bg= "red", fg= "white")
        
    def browseInputFolderCallBack(self):
        try:
            filepath = filedialog.askdirectory() 
            filepath = filepath + '/'
            vidpath = filepath+'*.h264'
            # print(vidpath)
            #get the list of filenames of all videos
            vid_list0 = glob.glob(vidpath) #windows outputs incorrect format
            self.vid_list = [filepath + os.path.basename(name) for name in vid_list0] #format the name to correct one
            # update message
            self.vidnum_label.config(text='%d h264 videos detected'%len(vid_list0))
            self.sv.set('Status: Input Loaded')
            self.message_label.config(bg= "green", fg= "white")

        except Exception as e:
            self.errorMessage(e)
            
    def browseOutputFolderCallBack(self):
        try:
            filepath = filedialog.askdirectory()
            self.output_path = filepath + '/'
            # update message
            self.output_folder_label.config(text=self.output_path)
            self.sv.set('Status: Output Selected')
            self.message_label.config(bg= "green", fg= "white")

        except Exception as e:
            self.errorMessage(e)
    
    def runProgram(self):
        try:
            self.sv.set('Status: Working')
            self.message_label.config(bg= "orange", fg= "white")
            time.sleep(1)
            for filename in self.vid_list:
                # print(filename)
                h264toMp4(filename,self.output_path)
            self.sv.set('Status: DONE')
            self.message_label.config(bg= "green", fg= "white")
        except Exception as e:
            self.errorMessage(e)

app = videoApp()
app.runGUI()