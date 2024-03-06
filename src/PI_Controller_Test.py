
import pyb
import utime
from Encoder import Encoder
from motor_driver import MotorDriver
from controller import PIController






def motor_control():
    
    """! 
    Sets motor speed using closed loop proportional postion control implemented with the PController class.
    Stores the encoder values of each step response in a list, and terminates the test when
    steady state has been achieved.
    """
    while True:
        # read encoder
        currentPos = coder.read()
        print(currentPos)
        
        
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
                        raise ValueError("Steady State Achieved")
                else:
                    # SS not achieved, keep controlling that motor
                    break
        
        # Check if we've ran longer than 5 seconds (infinite oscillation)
        if(timeVals[-1] > 5000):
            raise ValueError("Steady State Timeout")
        
        # Run control loop at ~100Hz
        utime.sleep_ms(10)







# Setup Motor Object
motor1 = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, pyb.Timer(5, freq=20000))
    
# Setup Encoder Object
coder = Encoder(pyb.Pin.board.PC6, pyb.Pin.board.PC7, 8, 1, 2)

Kp = 0.125;
Ki = 0;

cntrlr = PIController(Kp, Ki, 1210)
coder.zero()

# Create list of for storing time
timeVals = []
            
# Create a list of position values
posVals = []
            
# Define time period of steady state (lookback*10ms = steady state time)
lookback = 50

print("Setup Complete")
utime.sleep(0.5)


tzero = utime.ticks_ms()
try:
    # Run motor controller step response
    motor_control()
except ValueError as e:
    print(e)
    # Steady state achieved, turn motor off

motor1.set_duty_cycle(0)