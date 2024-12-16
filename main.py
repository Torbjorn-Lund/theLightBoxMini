"""
This is the main document for the LED matrix project
"""

# Importing required modules
from machine import Pin
import time
import machine

# Importing custom modules
from lib.lightbox_functionality import my_lightbox
import events as ev

# Hardware setup
button_pin = Pin(15, Pin.IN, Pin.PULL_DOWN) # Pin for physical button
reset_button_pin = Pin(0, Pin.IN, Pin.PULL_UP) # Pin for reset button

# Constants for button behavior
LONG_PRESS_TIME = 5000 # 5 seconds
press_start_time = 0
debounce_time = 100

def start_event_loop():
    """ 
    Function to start the event loop 
    This function continuously runs event_loop() from the events module
    """
    while True:
        try:
            my_lightbox.clear() # Clear buffer
            loop = ev.event_loop()
            if loop == "button_count_error":
                my_lightbox.button_count = 1 # Reset button count on error
            time.sleep(1)
            
        except Exception as e:
            print(f"ERR, an exception occurred: {e}")

def button_callback(pin):
    """ 
    Callback function for the physical button 
    This function handles button press and release events
    """
    global debounce_time, press_start_time

    if pin.value():
        press_start_time = time.ticks_ms() # Record button press start time
    else:
        if (time.ticks_ms()-debounce_time) > 500:
            press_duration = time.ticks_ms() - press_start_time # Calculates the time the button has been pressed

            # Long press action
            if press_duration > LONG_PRESS_TIME:
                print("Entering sleep mode")
                my_lightbox.set_button_count(0)
                my_lightbox.clear()
                my_lightbox.show()

            # Normal press action
            else:
                my_lightbox.change_button_count(1)
            
        debounce_time=time.ticks_ms()

def main():
    global core0_task
    """
    Main loop, this is where the program start
    """

    # Try/except/finnaly for error handling 
    try:
        print("Initializing startup proces...")
        
        button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_callback)
        start_event_loop()

    # In the case of an error
    except Exception as e:
        print(f"An error occurred: {e} - Device restarting")
        max_lines = 20

        # Getting data
        with open("data/logg.txt", "r") as file:
            data = file.read()

        data = data.split("\n")

        # Checking length
        if len(data) > max_lines:
            data.pop(0)
        
        data.append(f"ERROR at {time.localtime()}: {e} - Device restarting")
            
        # Logging error
        with open("data/logg.txt", "w") as file:
            for line in data:
                if line != "":
                    file.write(line + "\n")

        time.sleep(1)
        machine.reset() # Reset device

# Calling the main loop
main()