"""!
@file Panning.py
    This file contains a program that runs three separate tasks which take thermal images
    of the MLX90640 and control two motors: a positioning motor and a pusher motor. The
    program uses cotask.py and task_share.py to execute cooperative multi-tasking between
    these three tasks at different periods. The file was modified from basic_task.py from the
    ME405 library that was originally written by Dr. Ridgely.
"""

import gc
import pyb
import cotask
import task_share
import utime as time
from Encoder import Encoder
from motor_driver import MotorDriver
from controller import PController
from mlx_cam import MLX_Cam
from machine import Pin, I2C


def motor_control(shares):
    """!
    Task returns spur gear the housing blaster assembly to its home position using a limit switch. It
    subsequently awaits a button push on PC13 to begin the sequence of events which fires the
    blaster at a human target. In order, this sequence includes a state which waits for 5 seconds,
    a controller step response to aim at the target, a controller step response to turn away from
    the target, and blaster assembly homing.
    """

    statemc = 0
    doShoot, pixelpos, camflg = shares
    doShoot.put(0)
    while True:
        if (statemc == 0):
            # Setup User input switch
            triggerswitch = pyb.Pin(pyb.Pin.board.PC13, pyb.Pin.IN, pull = pyb.Pin.PULL_UP)
            # Setup the turret home position limit switch
            homeswitch = pyb.Pin(pyb.Pin.board.PC3, pyb.Pin.IN, pull = pyb.Pin.PULL_UP)
            # Setup Motor Object
            motor1 = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
            # Setup Encoder Object
            coder = Encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8, 1, 2)
            
            # Flywheel control pin
            Eme = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.OUT_PP)
            
            # Flywheel Timer & Channel
            tim4 = pyb.Timer(1, freq = 20000)
            ch3 = tim4.channel(1, pyb.Timer.PWM, pin=Eme)
            # Ensure flywheels are disabled
            ch3.pulse_width_percent(0)

            zeroreturnspeed = 10
            motor1.set_duty_cycle(zeroreturnspeed)

            # transfer to state 6 to home the turret
            statemc = 6
            
        elif(statemc == 1):
            if triggerswitch.value() == 0:
                print("Button Press")
                timestart = time.ticks_ms()
                count = 0
                statemc = 2
                
        elif(statemc == 2):
            # Stay in this state for 500 cycles to wait 5 seconds
            count+=1
            if count >= 550:
                statemc = 3
                camflg.put(1)
                print(f" {time.ticks_diff(time.ticks_ms(), timestart)} ms")

            else:
                statemc = 2
        elif(statemc == 3):
            if camflg.get() == 0:
                # Setup proportional controller for 180 degrees of rotation
                print(str(pixelpos.get()))
                desiredpos = -(pixelpos.get()-17)/0.11 + 1210 - 7
                print("\n ****************************************************"+str(desiredpos))
                cntrlr = PController(.2, desiredpos)
                
                # Rezero the encoder
                #coder.zero()
                
                # Create list of for storing time
                timeVals = []
                
                # Create a list of position values
                posVals = []
                
                # Define time period of steady state (lookback*10ms = steady state time)
                lookback = 50
                
                print("Setup Complete")
                
                # Keep track of time with tzero
                tzero = time.ticks_ms()
                
                statemc = 4
                print(f" setup complete at: {time.ticks_diff(time.ticks_ms(), timestart)} ms")
            
        elif(statemc == 4):
                
            # Run motor controller step response to look at target
            
            # Turn on flywheel motors
            ch3.pulse_width_percent(70)    
            
            # Read encoder
            currentPos = coder.read()
            
            # Store values
            posVals.append(currentPos)
            timeVals.append(time.ticks_ms()-tzero)
            
            # Run controller to get the PWM value
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
                            statemc = 5
                            print("Looking at target")
                            print(currentPos)
                            motor1.set_duty_cycle(0)
                            cntrlr.set_setpoint(300) # ~45 degrees from home
                            doShoot.put(1)
                            print(f" set doshoot at: {time.ticks_diff(time.ticks_ms(), timestart)} ms")

                            
                    else:
                        # SS not achieved, keep controlling that motor
                        break
                    
        elif(statemc == 5):
            
            # Run motor controller step response to turn away from target begin homing
            if(doShoot.get() == 0):
                # read encoder
                currentPos = coder.read()
                # Store values
                posVals.append(currentPos)
                timeVals.append(time.ticks_ms()-tzero)
                
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
                                statemc = 6
                                motor1.set_duty_cycle(zeroreturnspeed)
                                ch3.pulse_width_percent(0)
                                print("Returning home")
                                
                        else:
                            # SS not achieved, keep controlling that motor
                            break
        elif statemc == 6:
            # Homing limit switch state, motor is running, wait for switch to be pressed
            
            if homeswitch.value() == 0:
                # Home switch triggered, stop motor
                print("homing complete!")
                motor1.set_duty_cycle(0)
                coder.zero()
                # Done with state, await user input
                statemc = 1
                
        yield statemc

def pusher_control(shares):
    """!
    Task that controls a pusher motor which pushes darts from a magazine into flywheels. Pusher motor is triggered when 
    the doShoot flag is set in the motor_control task. Motor turns off when the pusher motor limit switch is triggered so
    that only one dart is fired. 
    """
    
    statepc = 0
    doShoot, pixelpos, camflg = shares
    while True:
        if(statepc == 0):
            #init
            # Setup Motor Object
            pusher = MotorDriver(pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5, pyb.Timer(3, freq=20000))
            pusher.set_duty_cycle(0)
            
            # Setup Pusher Limit Switch
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
                print('Pusher psh')
                pusher.set_duty_cycle(0)
                doShoot.put(0)
                statepc = 1

        yield statepc
        
def camera(shares):
    """!
    Task that uses the MLX90640 thermal camera driver classes to take an image. The get_csv function of the
    mlx_cam class has been modified to store all pixel data in a list. In state 1, this list is iterated through,
    determining which column of pixels in the thermal image has the highest total temperature. The majority of code
    implemented in this task has been implemented from the test script in the mlx_cam class written by Dr. Ridgely.
    """
    statecam = 0
    doShoot, pixelpos, camflg = shares
    while True:
        if statecam == 0:
            
            import gc

            # The following import is only used to check if we have an STM32 board such
            # as a Pyboard or Nucleo; if not, use a different library
            try:
                from pyb import info

            # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
            except ImportError:
                # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
                i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))

            # OK, we do have an STM32, so just use the default pin assignments for I2C1
            else:
                i2c_bus = I2C(1)

            print("MXL90640 Easy(ish) Driver Test")

            # Select MLX90640 camera I2C address, normally 0x33, and check the bus
            i2c_address = 0x33
            scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
            print(f"I2C Scan: {scanhex}")

            # Create the camera object and set it up in default mode
            camera = MLX_Cam(i2c_bus)
            print(f"Current refresh rate: {camera._camera.refresh_rate}")
            camera._camera.refresh_rate = 10.0
            print(f"Refresh rate is now:  {camera._camera.refresh_rate}")
            
            statecam = 1
            
        elif statecam == 1:
            if camflg.get() == 1:
                
                # Get an image and see how long it takes to grab that image
                print("Click.", end='')
                begintime = time.ticks_ms()

                # Keep trying to get an image; this could be done in a task, with
                # the task yielding repeatedly until an image is available
                image = None
                while not image:
                    image = camera.get_image_nonblocking()
                    time.sleep_ms(50)

                print(f" {time.ticks_diff(time.ticks_ms(), begintime)} ms")

                # Can show image.v_ir, image.alpha, or image.buf; image.v_ir best?
                # Display pixellated grayscale or numbers in CSV format; the CSV
                # could also be written to a file. Spreadsheets, Matlab(tm), or
                # CPython can read CSV and make a decent false-color heat plot.
                show_image = False
                show_csv = True
                data = []
                if show_image:
                    camera.ascii_image(image)
                elif show_csv:
                    maxcolumn = []
                    columntotals = []
                    coltotal = 0
                    
                    # Create list called data which stores all pixel values in a list
                    for line in camera.get_csv(image, data, limits=(0, 99)):
                        pass
                    
                    # Iterate through data to find the column with the highest total temperature
                    for n in range(28):
                        for i in range(5, 23):
                            coltotal += data[n+i*32]
                        if n <= 8:
                            columntotals.append(0)
                        else:
                            columntotals.append(coltotal)
                        coltotal = 0
                    #print("\n" + str(columntotals))
                    #camera.ascii_art(image)

                    ind = columntotals.index(max(columntotals))
                    pixelpos.put(ind)
                    camflg.put(0)
                    print("Flg clr")
                    print(ind)
                       
                else:
                    camera.ascii_art(image)
                gc.collect()
                print(f"Memory: {gc.mem_free()} B free")
        yield statecam
            
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
    share1 = task_share.Share('H', thread_protect=False, name="Share 1")
    share2 = task_share.Share('H', thread_protect=False, name="Share 2")

    motor_control = cotask.Task(motor_control, name="Motor Control Task", priority=2, period=10,
                        profile=True, trace=False, shares = (share0, share1, share2))
    
    pusher_control = cotask.Task(pusher_control, name="Pusher Motor Control Task", priority=1, period=10,
                        profile=True, trace=False, shares = (share0, share1, share2))
    
    camera = cotask.Task(camera, name="Camera Task", priority=3, period=20,
                        profile=True, trace=False, shares = (share0, share1, share2))
    
    cotask.task_list.append(motor_control)
    cotask.task_list.append(pusher_control)
    cotask.task_list.append(camera)


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


