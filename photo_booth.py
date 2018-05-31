# USAGE
# python photo_booth.py --output output

# import the necessary packages
from __future__ import print_function
from pyimagesearch.photoboothapp import PhotoBoothApp
from imutils.video import VideoStream
import argparse
import time
#import thread
#import multiprocessing

import os
os.system("sudo modprobe bcm2835-v4l2")

print("[INFO] warming up camera...")


def guiloop():
    vs = VideoStream(usePiCamera=-1 > 0).start()
    time.sleep(2.0)
    pba = PhotoBoothApp(vs, "output")
    pba.root.mainloop()

guiloop()

#p = multiprocessing.Process(target=guiloop, args=())

#p.start()

#thread.start_new_thread(guiloop , ())

# initialize the video stream and allow the camera sensor to warmup


# start the app
#pba = PhotoBoothApp(vs, "output")
#pba.root.mainloop()

#  sudo modprobe bcm2835-v4l2
