import RPi.GPIO as GPIO
import time
import sys
import time
import Adafruit_DHT
import Adafruit_CharLCD as LCD
import microgear.client as microgear
import logging
import os
from time import sleep
from datetime import datetime

appid = "EmbeddedProject"
gearkey = "j4TKxK545VAcQi1"
gearsecret =  "eVyq1xTR4EvQ5DnW8JkYE0rwR"

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_BACKLIGHT = 4

LCD_COLS = 16
LCD_ROWS = 2

lcd = LCD.Adafruit_CharLCD(LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
                           LCD_COLS, LCD_ROWS, LCD_BACKLIGHT)

# Define sensor dht - gpio
sensor = Adafruit_DHT.DHT22
pin = 4

# Define button gpio pin
BUTTON_PIN = 21

temp_current = 0.0
humid_current = 0.0

TEMP_TOP_LIMIT = 100
TEMP_DOWN_LIMIT = -50
HUMID_TOP_LIMIT = 100
HUMID_DOWN_LIMIT = 0
 
microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
  print "Now I am connected with netpie"

def subscription(topic, message):
  if topic == "/EmbeddedProject/SmartSensor/temp":
    lcd.set_cursor(0, 0)
    temp = "{0:.2f}".format(float(message))
    global temp_current
    temp_current = temp
    print "Temp: " + temp + " C"
    lcd.message("Temp:  " + temp + " C")
    createlog("Temp", temp)
  if topic == "/EmbeddedProject/SmartSensor/humid":
    lcd.set_cursor(0, 1)
    humid = "{0:.2f}".format(float(message))
    global humid_current
    humid_current = humid
    print "Humid: " + humid + "%"
    lcd.message("Humid: " + humid + " %")
    createlog("Humid", humid)
	
def disconnect():
    logging.debug("disconnected")

def createlog(topic ,value):
    file = open("/home/pi/data_log.csv", "a")
    if topic == "Temp":
      file.write("Temp: "+value+"\n")
    else:
      file.write("Humid: "+value +"\n")
    file.close()
	
def main():
  # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

  GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  microgear.setalias("pi")
  microgear.on_connect = connection
  microgear.on_message = subscription
  microgear.on_disconnect = disconnect
  microgear.subscribe("/SmartSensor/temp")
  microgear.subscribe("/SmartSensor/humid")
  microgear.connect(False)

  lcd_state = 1
  
  while True:
    button_input = GPIO.input(BUTTON_PIN)
    if button_input == True:
      print "Button pressed"
      if lcd_state == 1:
        lcd.set_backlight(0)
        lcd_state = 0
      else:
        lcd.set_backlight(1)
        lcd_state = 1
      time.sleep(0.2)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd.clear()
    lcd.message("Goodbye :)")
    time.sleep(3)
    GPIO.cleanup()
	

