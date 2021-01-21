#Transmitter Code:

import time
import Adafruit_BBIO.GPIO as GPIO
import socket

pin = "P9_42"
GPIO.setup(pin, GPIO.IN)    

def wait_for_keydown(pin):
	while GPIO.input(pin):
		time.sleep(0.01)

def wait_for_keyup(pin):
	while not GPIO.input(pin):
		time.sleep(0.01)
        
DOT = "."
DASH = "-"

key_down_time = 0
key_down_length = 0
key_up_time = 0

print("Ready")

s = socket.socket()
host = "10.100.70.192"
port = 43
s.bind((host, port))
s.listen(1000)

while True:
	wait_for_keydown(pin)
	key_down_time = time.time()	# record the time when the key was pressed
	wait_for_keyup(pin)
	key_up_time = time.time()		# record the time when the key was released
	key_down_length = key_up_time - key_down_time
	# get the length of time it was held down for
	c, addr = s.accept()
	msg = str(key_down_length)
	c.send(msg)
	print "Connected!"
	c.close()
	time.sleep(0.1)


#Receiver Code:

import time
import Adafruit_BBIO.GPIO as GPIO
import thread
import socket
import sys

pin = "P9_42"
GPIO.setup(pin, GPIO.OUT)

morse_code_lookup = {
	".-":	"A",
	"-...":	"B",
	"-.-.":	"C",
	"-..":	"D",
	".":	"E",
	"..-.":	"F",
	"--.":	"G",
	"....":	"H",
	"..":	"I",
	".---":	"J",
	"-.-":	"K",
	".-..":	"L",
	"--":	"M",
	"-.":	"N",
	"---":	"O",
	".--.":	"P",
	"--.-":	"Q",
	".-.":	"R",
	"...":	"S",
	"-":	"T",
	"..-":	"U",
	"...-":	"V",
	".--":	"W",
	"-..-":	"X",
	"-.--":	"Y",
	"--..":	"Z",
	".----":	"1",
	"..---":	"2",
	"...--":	"3",
	"....-":	"4",
	".....":	"5",
	"-....":	"6",
	"--...":	"7",
	"---..":	"8",
	"----.":	"9",
	"-----":	"0",
	"-.-.--":   "!"
}


def try_decode(bit_string):
	if bit_string in morse_code_lookup.keys():
		ch = morse_code_lookup[bit_string]
		sys.stdout.write(ch)
		if ch != ' ':
			stack.append(ch)
			if len(stack) >= 5: #1000:
				stack.pop(0)
		if ''.join(stack) == "SOS!":
			thread.start_new_thread(sosbeep, ())
			del stack[:]
		sys.stdout.flush()


def sosbeep():
	GPIO.output(pin, GPIO.HIGH)
	time.sleep(3)
	GPIO.output(pin, GPIO.LOW)


def decoder_thread():
	global offset
	global start
	global stack
	global buffer
	new_word = False
	while True:
		time.sleep(.01)
		key_up_length = time.time() - offset
		if len(buffer) > 0 and key_up_length >= 1.5:
			new_word = True
			bit_string = "".join(buffer)
			try_decode(bit_string)
			del buffer[:]
		elif new_word and key_up_length >= 4.5:
			new_word = False
			sys.stdout.write(" ")
			sys.stdout.flush()

DASH = '-'
DOT = '.'

key_down_length = 0
offset = 0
start = 0
buffer = []
stack = []

thread.start_new_thread(decoder_thread, ())

while True:
	s = socket.socket()
	host = "10.100.70.192"
	port = 43
	s.connect((host,port))
	key_down_length = float(s.recv(1024))
	offset = time.time()
	buffer.append(DASH if key_down_length > 0.15 else DOT)
	s.close()
