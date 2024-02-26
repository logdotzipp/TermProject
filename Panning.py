"""!
@file main.py
    This file contains a program that runs two separate tasks that controls two motors:
    a positioning motor and a pusher motor. The program uses cotask.py and task_share.py
    to execute cooperative multi-tasking between these two task at different periods.
    The file was modified from basic_task.py from the ME405 library that was originally
    written by Dr. Ridgely.
"""

import gc
import pyb
import cotask
import task_share
import utime
from Encoder import Encoder
from motor_driver import MotorDriver
from controller import PController


def motor_control(shares):
    """!
    Task awaits a proportional gain to arrive over serial, and then drives a 12V Pololu 37Dx70L 50:1 Gear motor
    connected to a nerf turret term project 180 degrees using a closed loop proportional controller class.
    The response is recorded and sent back over Serial to be plotted on a PC side GUI.
    """

    statemc = 0
    doShoot = shares
    doShoot.put(0)
    while True:
        if (statemc == 0):
            # Setup User input switch
            triggerswitch = pyb.Pin(pyb.Pin.board.PC13, pyb.Pin.IN, pull = pyb.Pin.PULL_UP)
            # Setup Motor Object
            motor1 = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
            # Setup Encoder Object
            coder = Encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8, 1, 2)
            
            # Flywheel control pin
            Eme = pyb.Pin(pyb.Pin.board.PB8, pyb.Pin.OUT_PP)
            
            # Flywheel Timer & Channel
            tim4 = pyb.Timer(4, freq = 20000)
            ch3 = tim4.channel(3, pyb.Timer.PWM, pin=Eme)
            ch3.pulse_width_percent(0)
            
            statemc = 1
            
        elif(statemc == 1):
            if triggerswitch.value() == 0:
                
                # Setup proportional controller for 180 degrees of rotation
                cntrlr = PController(.16, 1200)
                
                # Rezero the encoder
                coder.zero()
                
                # Create list of for storing time
                timeVals = []
                
                # Create a list of position values
                posVals = []
                
                # Define time period of steady state (lookback*10ms = steady state time)
                lookback = 50
                
                print("Setup Complete")
                
                # Keep track of time with tzero
                tzero = utime.ticks_ms()
                
                statemc = 2
            
        elif(statemc == 2):
                
            # Run motor controller step response
            ch3.pulse_width_percent(80)   
            # read encoder
            currentPos = coder.read()
            
            # Store values
            posVals.append(currentPos)
            timeVals.append(utime.ticks_ms()-tzero)
            
            # Run controller to get the pwm value
            pwm = cntrlr.run(currentPos)
            
            
            # Send signal to the motor
            motor1.set_duty_cycle(-pwm)
            
            # Check if steady state was achieved
            if(len(posVals) > lookback):
                
                for i in range(1, lookback+1):
                    if(posVals[-i-1] == currentPos):
                        if(i == lookback):
                            timeVals = []
                            posVals = []
                            # SS achieved, exit all loops
                            statemc = 3
                            motor1.set_duty_cycle(0)
                            cntrlr.set_setpoint(0)
                            doShoot.put(1)
                            
                    else:
                        # SS not achieved, keep controlling that motor
                        break
                    
        elif(statemc == 3):
            # Run motor controller step response
            if(doShoot.get() == 0):
                # read encoder
                currentPos = coder.read()
                # Store values
                posVals.append(currentPos)
                timeVals.append(utime.ticks_ms()-tzero)
                
                # Run controller to get the pwm value
                pwm = cntrlr.run(currentPos)
                
                
                # Send signal to the motor
                motor1.set_duty_cycle(-pwm)
                
                # Check if steady state was achieved
                if(len(posVals) > lookback):
                    
                    for i in range(1, lookback+1):
                        if(posVals[-i-1] == currentPos):
                            if(i == lookback):
                                # SS achieved, exit all loops
                                statemc = 1
                                motor1.set_duty_cycle(0)
                                ch3.pulse_width_percent(0)
                                
                        else:
                            # SS not achieved, keep controlling that motor
                            break
                    
        yield statemc

def pusher_control(shares):
    """!
    Task that controls a pusher motor that pushes darts from a magazine to a flywheel. Motor is triggered when
    the PC13 button is pressed on the STM32 MCU and stops moving after setting pin PB6 low.  
    """
    
    statepc = 0
    doShoot = shares
    while True:
        if(statepc == 0):
            #init
            # Setup Motor Object
            pusher = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
            pusher.set_duty_cycle(0)
            
            # Setup Pusher Limit Switch
            trigger = pyb.Pin(pyb.Pin.board.PC3, pyb.Pin.OUT)
            pusherswitch = pyb.Pin(pyb.Pin.board.PB3, pyb.Pin.IN, pull = pyb.Pin.PULL_UP)
            
            
            statepc = 1
            
        elif(statepc == 1):
            if doShoot.get() == 1:
                statepc = 2
                
        elif(statepc == 2):
            
            pusher.set_duty_cycle(50)
            if(pusherswitch.value() == 1):
                statepc = 3
           
        elif(statepc == 3):
            if pusherswitch.value() == 1:
                pusher.set_duty_cycle(50)
            else:
                print('Click')
                pusher.set_duty_cycle(0)
                doShoot.put(0)
                statepc = 1

        yield statepc
# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":


    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")
    
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    
    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('H', thread_protect=False, name="Share 0")

    motor_control = cotask.Task(motor_control, name="Motor Control Task", priority=2, period=10,
                        profile=True, trace=False, shares = (share0))
    
    pusher_control = cotask.Task(pusher_control, name="Pusher Motor Control Task", priority=1, period=10,
                        profile=True, trace=False, shares = (share0))
    
    cotask.task_list.append(motor_control)
    cotask.task_list.append(pusher_control)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(motor_control.get_trace())
    print('')
