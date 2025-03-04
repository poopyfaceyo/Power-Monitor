import time 

import smbus2  # For I2C communication 

import json 

import os 

from gpiozero import Button, LED 

from datetime import datetime 

from PIL import Image, ImageDraw, ImageFont 

import Adafruit_SSD1306 

  

# Constants 

VOLTAGE_SENSOR_ADDRESS = 0x40  # Example I2C address 

CURRENT_SENSOR_ADDRESS = 0x41 

DATA_FILE = "/home/pi/power_data.json" 

  

# Initialize I2C bus 

bus = smbus2.SMBus(1) 

  

# Initialize buttons and LEDs 

btn_on = Button(2) 

btn_off = Button(3) 

btn_low_power = Button(4) 

led_green = LED(17) 

led_yellow = LED(27) 

led_red = LED(22) 

  

# Initialize display (128x32 OLED using I2C) 

display = Adafruit_SSD1306.SSD1306_128_32(rst=None) 

display.begin() 

display.clear() 

display.display() 

  

# Function to read sensor values (mocked for now) 

def read_voltage(): 

    return 220.0  # Simulated voltage reading 

  

def read_current(): 

    return 0.5  # Simulated current reading 

  

# Function to calculate power 

def calculate_power(): 

    voltage = read_voltage() 

    current = read_current() 

    return voltage * current 

  

# Function to log power data 

def log_power_data(power): 

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

    data = {"timestamp": timestamp, "power": power} 

     

    if os.path.exists(DATA_FILE): 

        with open(DATA_FILE, "r") as file: 

            logs = json.load(file) 

    else: 

        logs = [] 

     

    logs.append(data) 

  

    with open(DATA_FILE, "w") as file: 

        json.dump(logs, file, indent=4) 

  

# Function to display data on OLED 

def display_message(message): 

    display.clear() 

    image = Image.new("1", (display.width, display.height)) 

    draw = ImageDraw.Draw(image) 

    font = ImageFont.load_default() 

    draw.text((0, 0), message, font=font, fill=255) 

    display.image(image) 

    display.display() 

  

# Function for normal operation 

def normal_operation(): 

    led_green.on() 

    led_yellow.off() 

    led_red.off() 

     

    while True: 

        power = calculate_power() 

        log_power_data(power) 

        display_message(f"Power: {power:.2f}W") 

        time.sleep(5) 

  

# Function for low power mode 

def low_power_mode(): 

    led_green.off() 

    led_yellow.on() 

    led_red.off() 

     

    outage_start = None 

    while btn_low_power.is_pressed: 

        power = calculate_power() 

        if power < 10:  # Threshold for detecting an outage 

            if not outage_start: 

                outage_start = time.time() 

        else: 

            if outage_start: 

                outage_duration = time.time() - outage_start 

                log_outage(outage_duration) 

                outage_start = None 

  

        display_message("Low Power Mode") 

        time.sleep(10) 

  

# Function to log outages 

def log_outage(duration): 

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

    data = {"timestamp": timestamp, "outage_duration": duration} 

  

    if os.path.exists(DATA_FILE): 

        with open(DATA_FILE, "r") as file: 

            logs = json.load(file) 

    else: 

        logs = [] 

  

    logs.append(data) 

  

    with open(DATA_FILE, "w") as file: 

        json.dump(logs, file, indent=4) 

  

# Shutdown function 

def shutdown(): 

    display_message("Shutting down...") 

    time.sleep(2) 

    display.clear() 

    display.display() 

    os.system("sudo shutdown -h now") 

  

# Button event handlers 

btn_on.when_pressed = normal_operation 

btn_off.when_pressed = shutdown 

btn_low_power.when_pressed = low_power_mode 

  

# Start normal mode on boot 

normal_operation() 

 