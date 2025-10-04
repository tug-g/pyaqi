import time
import serial
import aqi
import pytz
from datetime import datetime
# sds011 sensor
from sds011lib import SDS011QueryReader
import board
import adafruit_dht
# Setup a query-mode reader on /dev/ttyUSB0
pmsensor = SDS011QueryReader('/dev/ttyUSB0')
tempsensor = adafruit_dht.DHT11(board.D4)
lcd_port = '/dev/ttyAMA0'
lcd = serial.Serial(lcd_port, baudrate=9600, timeout=1)

# Setup time & date
loctime = pytz.timezone('Placeholder')

# Define a function to log information
def save_log(current_time, pm25, pm10, aqi25, aqi10, temperature_c, humidity):
    with open("air_quality.csv", "a") as log:
        dt = datetime.now()
        log.write("{},{},{},{},{},{},{}\n".format(current_time, pm25, pm10, aqi25, aqi10, temperature_c, humidity))
    log.close()

def clear_screen():
    lcd.write(b'\xFE\x51')  # Clear the display
    time.sleep(0.5)         # Allow the display to process

def next_line():
    lcd.write(b'\xFE\x45\x40')  # Clear the display
    time.sleep(0.1)         # Allow the display to process

# This code was written using a 2-line display, hence the two lines
def write_to_line1(text):
    lcd.write(text.encode())

def write_to_line2(text):
    next_line()
    lcd.write(text.encode())

while True:
    try:
        res = pmsensor.query() # Read data
        # Format AQI data
        pm25 = round(res.pm25, 1)
        pm10 = round(res.pm10, 1)
        myaqi25 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pm25))
        myaqi10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pm10))
        # Temp & Humidity data
        temperature_c = tempsensor.temperature
        humidity = tempsensor.humidity
        # Time format
        current_time = datetime.now(loctime).strftime("%Y-%m-%d %H:%M")
        # Output
        print(f"{current_time}: pm2.5: {pm25}μg/m³, pm10: {pm10}μg/m³, aqi2.5: {myaqi25}, aqi10: {myaqi10}, temp: {temperature_c}ºC, humidity: {humidity}%")
        save_log(current_time, pm25, pm10, myaqi25, myaqi10, temperature_c, humidity)
		# Misc AQI
        if myaqi25 <= 9.0:
            status25 = 'G'
        elif myaqi25 > 9 & myaqi25 <= 35.4:
            status25 = 'M'
        elif myaqi25 > 35.4 & myaqi25 <= 55.4:
            status25 = 'S'
        elif myaqi25 > 55.4 & myaqi25 <= 125.4:
            status25 = 'U'
        elif myaqi25 > 125.4 & myaqi25 <= 225.4:
            status25 = 'V'
        elif myaqi25 > 225.4:
            status25 = 'H'
        if myaqi10 <= 54:
            status10 = 'G'
        elif myaqi10 > 54 & myaqi10 <= 154:
            status10 = 'M'
        elif myaqi10 > 154 & myaqi10 <= 254:
            status10 = 'S'
        elif myaqi10 > 254 & myaqi10 <= 354:
            status10 = 'U'
        elif myaqi10 > 354 & myaqi10 <= 454:
            status10 = 'V'
        elif myaqi10 > 454:
            status10 = 'H'
        # Screen
        clear_screen()
        write_to_line1(f"{current_time}")
        write_to_line2(f"{myaqi25}{status25} {myaqi10}{status10} {temperature_c}C {humidity}%")
        # Let the sensor sleep
        time.sleep(60)
        
    except Exception as e:
        print (e)
        time.sleep(12)



