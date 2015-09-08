#!/usr/bin/env python

import json
from urllib2 import Request, urlopen, URLError
from urllib import quote_plus
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import time
import picamera
import RPi.GPIO as GPIO
import Adafruit_DHT
import os

# start
offset = 1
register_openers()

GPIO.setmode(GPIO.BCM);
GPIO.setup(4,GPIO.OUT);
GPIO.setup(23,GPIO.OUT);
GPIO.output(4,GPIO.LOW);
GPIO.output(23,GPIO.LOW);

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ADMIN_GROUP = {add admin group id  here}
CHAT_GROUP = {add chat group id here}
memberid=[{add member id's here}]

humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 17)

if humidity is not None and temperature is not None:
        print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
else:
        print 'Failed to get reading. Try again!'

def sendLocation( chatid ):
        try:
                sendrequest = Request('https://api.telegram.org/{bot}:{api key}/sendLocation?chat_id=' + `chatid` + '&latitude=-26.711440&longitude=27.859285')
                sendresponse = urlopen(sendrequest)

                # todo read response
        except Exception, e:
                print 'send location error'
                print e

def sendMessage( chatid, msg ):
	try:
		sendrequest = Request('https://api.telegram.org/{bot}:{api key}/sendMessage?chat_id=' + `chatid` + '&text=' + quote_plus(msg))
		sendresponse = urlopen(sendrequest)

		# todo read response
	except Exception, e:
		print 'send error'
		print e

def sendPhoto( chatid, photofilename ):
	try:

		items = []
		items.append(MultipartParam('chat_id', chatid))
		items.append(MultipartParam.from_file('photo', photofilename))
		datagen, headers = multipart_encode(items)
		req = Request('https://api.telegram.org/{bot}:{api key}/sendPhoto', datagen, headers)
		print req
		rsp = urlopen(req)
		print rsp
        except Exception, e:
                print 'send photo error'
                print e
		print URLError


#camera = picamera.PiCamera()

while True:
	if not GPIO.input(22):
		sendMessage(CHAT_GROUP, "Smoke Detected in the Space. Danger Will Robinson, Danger!")
			

	try:
		request = Request('https://api.telegram.org/{bot}:{api key}/getUpdates?offset=' + `offset` + '&timeout=100')
		response = urlopen(request,timeout=120)
		data = response.read()
		result = json.loads(data)
		messages = result['result']
		msgcount =  len(messages)

		for x in xrange(msgcount):
			print messages[x]['message']
			offset = messages[x]['update_id'] + 1
			userid = messages[x]['message']['from']['id']
			fname = messages[x]['message']['from']['first_name']
			message = ''

			try:
				message = messages[x]['message']['text']
			except:
				print 'no text'		



			print message
			print userid

			# parseMessage here

			if message.upper() == '/PING':
				sendMessage( userid, 'Pong' )

			if message.upper() == '/TEMP':
				humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 17)

				if humidity is not None and temperature is not None:
        				sendMessage(userid,  'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
				else:
        				sendMessage(userid,'Failed to get reading. Try again!')

			if message.upper() == '/SPACECAM':
#				# please wait
#				camera.capture('/home/pi/binarybot/spacecam.jpg', resize=(800,600))
#				time.sleep(1)
				#sendPhoto(userid, '/home/pi/binarybot/spacecam.jpg')
 				os.system('fswebcam -r 640x480 -S 3 --jpeg 100 --save /home/pi/binarybot/spacecam.jpg')				
				sendPhoto(CHAT_GROUP, '/home/pi/binarybot/spacecam.jpg')
			
			


			if message.upper() == '/USERID':
				sendMessage(userid, "Your userid is {userid}".format(userid=userid))

			if message.upper() == '/HELP':
				sendMessage(userid, 'Commands Available /gate,/spacecam,/ping,/userid,/rabbithole - with great power comes great responsibility' )

			if message.upper() == '/RABBITHOLE':
				sendLocation(userid)

			if message.upper() == '/GATE':
				if userid in memberid:
					GPIO.output(4,GPIO.HIGH)
					time.sleep(0.5)
					GPIO.output(4,GPIO.LOW)
					sendMessage( userid, 'Welcome to BinarySpace' )
					sendMessage( ADMIN_GROUP, "Gate Triggered by {name}".format(name=fname) )
				else:
					sendMessage( userid, "I'm sorry {name}, I'm afraid I can't do that".format(name=fname))

                        if message.upper() == '/DOOR':
                                if userid in memberid:
                                        GPIO.output(23,GPIO.HIGH)
                                        time.sleep(0.5)
                                        GPIO.output(23,GPIO.LOW)
                                        sendMessage( userid, 'Welcome to BinarySpace' )
                                        sendMessage( ADMIN_GROUP, "Door Triggered by {name}".format(name=fname) )
                                else:
                                        sendMessage( userid, "I'm sorry {name}, I'm afraid I can't do that".format(name=fname))
		

	except KeyboardInterrupt:
        	raise
	except:
		print 'error'

