import win32api, win32con, json, sys, time, zmq, threading

import os

import websocket
from websocket import create_connection

addr = 'tcp://ec2-54-68-79-177.us-west-2.compute.amazonaws.com'
x = 0
y = 0


def setButtonPosition():
	print('Move Mouse to hover over the button then press enter')
	raw_input()
	x, y = win32api.GetCursorPos()
	f = open('config.txt', 'wb')
	f.write('{0},{1}'.format(x, y))

def click(x,y):
	win32api.SetCursorPos((x,y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
	time.sleep(0.1)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
		
def listenForClicks(ctx):
	socket = ctx.socket(zmq.PULL)
	socket.connect(addr + ':5557')
	cont = True
	while cont:
		doClick = socket.recv_string()
		
		if doClick == 'GO':
			cont = False
			click(x,y)

	socket.disconnect(addr + ':5557')


def RunMe():

	ctx = zmq.Context(2)

	socket = ctx.socket(zmq.SUB)
	socket.connect(addr + ':5556')



	socket.setsockopt_string(zmq.SUBSCRIBE, 'TheButton'.decode('ascii'))


	whitespacer = ' '
	lengthOfLine = 0
	printme = ''

	pullerThread = threading.Thread(None, listenForClicks, None, [ctx])
	pullerThread.start()
			
	lowestLeft = 60
	while True:
		recv = socket.recv_string()
		
		
		Sub, curTime, lowTime = recv.split()
		printme = 'Time remaining: {0} Lowest seen this run {1}'.format(curTime, lowTime)
		wps = (whitespacer*(lengthOfLine - len(printme)))
		lengthOfLine = len(printme)
		printme = printme + wps + '\r'
		
		sys.stdout.write(printme)
		sys.stdout.flush()

if os.path.isfile('config.txt'):
	f = open('config.txt', 'rb')
	ret = f.readline()

	if ret != '':
		x,y = ret.strip().split(',')
		x = int(x)
		y = int(y)
	else:
		setButtonPosition()
else:
	setButtonPosition()

		
RunMe()
