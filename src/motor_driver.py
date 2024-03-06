"""! @file motor_driver.py
This program is a motor driving class that runs a 12V Brushed DC Motor
using a L6206 H-Bridge Motor Driver. The class initializes the motor
driver pins, and then allows the motor duty cycle to be updated from
-100% to 100%.
"""
import pyb
import micropython

class MotorDriver:
    """! 
    This class implements a L6206 H-Bridge Motor Controller Shield
    """

    def __init__ (self, en_pin, in1pin, in2pin, timer):
        """! 
        Creates a motor driver by initializing GPIO
        pins and turning off the motor for safety. 
        @param en_pin Pin that enables the motor.
        @param in1pin First pin used for input to Motor's H-bridge.
        @param in2pin Second pin used for input to Motor's H-bridge.
        @param timer Timer channel used to drive PWM.
        """
        print ("Creating a motor driver")
        
        # Setup Enable Pin
        self.pinEN = pyb.Pin(en_pin, pyb.Pin.OUT_OD, pyb.Pin.PULL_UP)
        # Disable Motor For Safety
        self.pinEN.value(0)
        
        # Setup H-Bridge Swtitching Pins
        pinIN1A = pyb.Pin(in1pin, pyb.Pin.OUT_PP)
        pinIN2A = pyb.Pin(in2pin, pyb.Pin.OUT_PP)
    
        # Setup PWM Timers
        self.chIN1A = timer.channel(1, pyb.Timer.PWM, pin=pinIN1A)
        self.chIN2A = timer.channel(2, pyb.Timer.PWM, pin=pinIN2A)
        
        

    def set_duty_cycle (self, level):
        """!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction. Input levels less than -100
        or greater than 100 automatically saturate
        @param level A signed integer for the percent duty cycle sent to the motor. Ideally between -100 and 100.
        """
        print (f"Setting duty cycle to {level}")
        
        if level >= 0:
            # Forward Direction
            if level > 100:
                level = 100
            
            self.pinEN.value(1) # Enable motor
        
            self.chIN1A.pulse_width_percent(0)
            self.chIN2A.pulse_width_percent(level)
            
        else:
            # Backwards Direction
            if level < -100:
                level = -100
            
            self.pinEN.value(1) # Enable motor
        
            self.chIN1A.pulse_width_percent(abs(level))
            self.chIN2A.pulse_width_percent(0)
            
            