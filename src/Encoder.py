"""! @file Encoder.py
This program is an Encoder Reading class where the program is able
to read a quadrature encoder using a the built in counters on the STM-32.
The class initializes the Encoder's pins and Timer, and contains functionality for reading and re-zeroing the encoder value.
This class is intended to be used with a 16bit timer channel.
"""
import pyb
import utime

class Encoder:
    """!
    This class contains functionality to setup, read, and zero a quadrature encoder on a 16 bit timer channel on an STM-32.
    """
    
    def __init__ (self, ENA, ENB, timer, CHA, CHB):
        """!
        Creates an Encoder object that intializes the Encoder's
        pins and sets the set GPIO Pin Timer and respective channels.
        @param ENA GPIO pin associated with Encoder Channel A.
        @param ENB GPIO pin associated with Encoder Channel B.
        @param timer Timer object used as a counter.
        @param CHA Timer Channel corresponding to Encoder Channel A.
        @param CHB Timer Channel corresponding to Encoder Channel B.
        """
        
        # Setup the encoder pins
        self.pinENA = pyb.Pin(ENA, pyb.Pin.IN)
        self.pinENB = pyb.Pin(ENB, pyb.Pin.IN)
        
        # Create the timer and set its channels to Encoder mode
        self.tim = pyb.Timer(timer, prescaler = 0, period = 65535)
        self.ENCA = self.tim.channel(CHA, pyb.Timer.ENC_A, pin=ENA)
        self.ENCB = self.tim.channel(CHB, pyb.Timer.ENC_B, pin=ENB)
        
        # Variable to store the previous encoder count
        self.lastCount = 0
        # Variable to store the total encoder count
        self.totalCount = 0
        
    def read(self):
        """!
        Function reads the Encoder's position as a positive/negative integer.
        Accounts for under- and over-flow cases by comparing the most recent
        and current count from the Encoder.
        @returns Total encoder count as an integer
        """
        
        # Read the encoder counter
        count = self.tim.counter()
        # Compute the difference between previous and current encoder values
        d = count-self.lastCount
        
        # If difference is greater than half of the AutoReload value, over/underflow has occured
        # Compensate by adding/subtracting from the difference
        if d >= 32768:
            d = d-65536
            
        elif d <= -32768:
            d = d+65536
            
        # Add to the total count    
        self.totalCount += d
        # Update the previous encoder reading to the current encoder reading
        self.lastCount = count
        
        return self.totalCount
        
    
    def zero(self):
        """!
        Function set all Encoder counts to 0.
        """
        self.tim.counter(0)
        self.totalCount = 0
        self.lastCount = 0
        

if __name__ == "__main__":
    """!
    To test encoder functionality, create an encoder object on timer channel 4. Then print the encoder value 10 times/second
    """
    coder = Encoder(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4, 1, 2)
    while True:
        print(coder.read())
        utime.sleep(.1)
