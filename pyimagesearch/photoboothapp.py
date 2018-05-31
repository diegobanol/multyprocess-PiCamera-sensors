# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
from math import ceil
import Tkinter as tki
import tkFont
import threading
import datetime
import imutils
import cv2
import time
import csv
#import os

import mysql.connector as mariadb

import RPi.GPIO as GPIO
import Adafruit_DHT

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

from multiprocessing import Process, Queue

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)

def temp(q):

	# keep looping over frames until we are instructed to stop
	while True:
		# Try to grab a sensor reading.  Use the read_retry method which will retry up
		# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
		#humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 18)
		humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22, 4)
		# Note that sometimes you won't get a reading and
		# the results will be null (because Linux can't
		# guarantee the timing of calls to read the sensor).
		# If this happens try again!
		if humidity is not None and temperature is not None:
			#print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
			q.put(temperature)
			#q.send(temperature)

def termo(q2, q):
    
        CONSECUTIVO = 0
        
	CLK = 25
	CS  = 24
	DO  = 18
	sensor = MAX31855.MAX31855(CLK, CS, DO)
	
	mariadb_connection = mariadb.connect(user='salamanca', password='salamanca', database='SENSORS')
	cursor = mariadb_connection.cursor()
	
	cont_to_store = 0

	while True:
		temp = sensor.readTempC() - 30
		#print('Thermocouple Temperature: {0:0.3F}*C '.format(temp))
		q2.put(temp)
		#q.get()
		time.sleep(1)
		cont_to_store = cont_to_store + 1
		if cont_to_store == 60:
			try:
				cursor.execute("INSERT INTO temperature (consecutive, temperature_hot, temperature_cold) VALUES (%s, %s,%s)", (CONSECUTIVO, temp, ceil(q.get()*100)/100))
				mariadb_connection.commit()
				#print "The last inserted id was: ", cursor.lastrowid
				#cursor.execute("INSERT INTO employees (first_name,last_name) VALUES (%s,%s)", ('Maria','DB'))
				#INSERT INTO products_tbl (product_name,product_manufacturer) VALUES ('6789','Orbitron 4010')", ('6789','Orbitron 4010')
			except mariadb.Error as error:
				print("Error: {}".format(error))
			cont_to_store = 0
			
			myFile = open('/home/pi/SENSORS.csv', 'a')
			with myFile:
                            writer = csv.writer(myFile)
                            myData = [[CONSECUTIVO, temp, ceil(q.get()*100)/100, time.strftime("%x") + " " + time.strftime("%X")]]
                            writer.writerows(myData)


class PhotoBoothApp:
	def __init__(self, vs, outputPath):
		# store the video stream object and output path, then initialize
		# the most recently read frame, thread for reading frames, and
		# the thread stop event
		self.vs = vs
		self.outputPath = outputPath
		self.frame = None
		self.frame1 = None
		self.thread = None
		self.stopEvent = None

		# initialize the root window and image panel
		self.root = tki.Tk()
		self.root.attributes("-fullscreen",True)
		self.panel = None
		self.panel1 = None

		self.data = None
		self.humidity = None
		self.temperature = 0
		self.temperature2 = 0

		self.q = Queue()
		self.q2 = Queue()
		#self.parent_conn, self.child_conn = Pipe()

		# Sensor variables
		# Define GPIO to use on Pi
		#GPIO.setmode(GPIO.BCM)
		#self.GPIO_TEMP = 18
		#self.sensor = Adafruit_DHT.DHT22
		#self.GPIO_BUZZ = 4
		#GPIO.setup(self.GPIO_TEMP,GPIO.IN)      # Temperature

		#helv12 = tkFont.Font(family='Helvetica', size=12, weight=tkFont.BOLD)

		# create a button, for suspend camera and sensors operation
		# btn1 = tki.Button(self.root, text="Suspender",
		# 	command=self.takeSnapshot,  height = 2, width = 10, font=helv12)
		# #btn.pack(side="bottom", fill="both", expand="no", padx=10,
		# #	pady=10)
		# btn1.grid(row=5,column=0, padx=5, pady=5)

		# create a button, for display new window to show inventory
		# btn = tki.Button(self.root, text="Inventario",
		# 	command=self.takeSnapshot,  height = 2, width = 10, font=helv12)
		# #btn.pack(side="bottom", fill="both", expand="no", padx=10,
		# #	pady=10)
		# btn.grid(row=5,column=1, padx=5, pady=5)
		#
		# # create a button, for display window to show "itinerario"
		# btn1 = tki.Button(self.root, text="Itinerario",
		# 	command=self.takeSnapshot,  height = 2, width = 10, font=helv12)
		# #btn.pack(side="bottom", fill="both", expand="no", padx=10,
		# #	pady=10)
		# btn1.grid(row=5,column=2, padx=5, pady=5)

		# #Put the Logo of the client
		# #f = open('/home/pi/TkinterExamples/tkinter-photo-booth/pyimagesearch/logoSalamanca.png', 'r+')
		# self.frame1  = cv2.imread("/home/pi/TkinterExamples/tkinter-photo-booth/pyimagesearch/logoSalamanca.png")
		# #self.frame1 = f.read()
		# #f.close()
		#
		# self.frame1 = imutils.resize(self.frame1, width=200)

		# OpenCV represents images in BGR order; however PIL
		# represents images in RGB order, so we need to swap
		# the channels, then convert to PIL and ImageTk format
		# image1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2RGB)
		# image1 = Image.fromarray(image1)
		# image1 = ImageTk.PhotoImage(image1)
		#
		# if self.panel1 is None:
		# 	self.panel1 = tki.Label(image=image1)
		# 	self.panel1.image = image1
		# 	#self.panel.pack(side="left", padx=10, pady=10)
		# 	self.panel1.grid(row=4, column=3, padx=30, pady=5, rowspan=2, sticky=tki.E+tki.S)
		# 	#sticky=tki.W+tki.E+tki.N+tki.S
		# # otherwise, simply update the panel
		# else:
		# 	self.panel.configure(image=image1)
		# 	self.panel.image = image

		#thread.start_new_thread(self.temp , ())
		p = Process(target=temp, args=(self.q,))
		p.start()

		p2 = Process(target=termo, args=(self.q2,self.q,))
		p2.start()


		# start a thread that constantly pools the video sensor for
		# the most recently read frame
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()
		#self.thread.join()
		# start a thread for getting data from the sensors
		# the most recently read frame
		#self.stopEvent1 = threading.Event()
		#self.thread1 = threading.Thread(target=self.temp_update, args=())
		#self.thread1.start()



		#f = Process(target=self.temp_update, args=())
		#f.start()

		#self.temp_update()

		# set a callback to handle when the window is closed
		self.root.wm_title("Frente de las neveras")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	# def temp_update(self):
	# 	try:
	# 		while not self.stopEvent.is_set():
	# 			print(len(self.q.get()))
	# 			self.panel1 = tki.Label(self.root, text="Hello, world!" + self.q.get())
	# 			self.panel1.grid(row=0,column=3, padx=5, pady=5)
	# 	except RuntimeError, e:
	# 		print("[INFO] caught a RuntimeError")


	def videoLoop(self):
		# DISCLAIMER:
		# I'm not a GUI developer, nor do I even pretend to be. This
		# try/except statement is a pretty ugly hack to get around
		# a RunTime error that Tkinter throws due to threading
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():
			#while True:
				#print(self.q)
				# grab the frame from the video stream and resize it to
				# have a maximum width of 300 pixels
				#self.temp_update()
				#print(self.q.get())
				if not self.q.empty():
					self.temperature = self.q.get()

				if not self.q2.empty():
					self.temperature2 = self.q2.get()

				#	print(self.q.qsize())
				#if(self.parent_conn.recv()):
				#print(self.parent_conn.recv())
				#if self.q.get()==None:
				#	continue
				#else:
				#	self.temperature = self.q.get()
				#try:
				#	self.q.get_nowait()
				#	print("find")
				#except:
				#	pass
				#self.frame = imutils.resize(self.frame, width=500, height=600)
				self.frame = self.vs.read()
				# OpenCV represents images in BGR order; however PIL
				# represents images in RGB order, so we need to swap
				# the channels, then convert to PIL and ImageTk format
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = cv2.resize(image, (790, 470))
				cv2.putText(image, "Temperatura Frio: {0:0.1f}*C".format(self.temperature), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				#cv2.putText(image, "Temperatura Calor: {}".format("-15"), (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
				cv2.putText(image, "Temperatura Calor: {0:0.1f}*C".format(self.temperature2), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
				#'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
				image = imutils.rotate(image , 180)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)

				# if the panel is not None, we need to initialize it
				if self.panel is None:
					self.panel = tki.Label(image=image)
					self.panel.image = image
					#self.panel.pack(side="left", padx=10, pady=10)
					#self.panel.grid(row=0, column=0, columnspan=4, rowspan=4, padx=5, pady=5)
					self.panel.pack(fill="both", expand=1)
				# otherwise, simply update the panel
				else:
					self.panel.configure(image=image)
					self.panel.image = image

		except RuntimeError, e:
			print("[INFO] caught a RuntimeError")

	def takeSnapshot(self):
		# grab the current timestamp and use it to construct the
		# output path
		ts = datetime.datetime.now()
		filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
		#p = os.path.sep.join((self.outputPath, filename))

		# save the file
		# cv2.imwrite(p, self.frame.copy())
		print("[INFO] saved {}".format(filename))

	def onClose(self):
		# set the stop event, cleanucp the camera, and allow the rest of
		# the quit process to continue
		print("[INFO] cerrando...")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()
