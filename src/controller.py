"""! @file controller.py
This program contains a general purpose proportional controller class. The class initializes a gain constant, Kp,
and a desired set point. When run() is repeatedly called, it calculates the error in the system and applies the
proportional gain to it.
"""

class PController:
    """!
    The class initializes a proportional gain constant, Kp,
    and a desired setpoint for a system.
    When feedback is applied through the run() method, the error in the system is calculated,
    and the proportional gain is applied. Rapidly and repeatedly calling run() enables one to
    create a closed loop proportional controller.
    """
    def __init__(self, Kp, setPoint):
        """! 
        This function initializes the proportional gain constant and desired setpoint
        @param Kp User specified proportional gain constant.
        @param setPoint Desired setpoint for the system to be driven to.
        """

        self.Kp = Kp
        self.setPoint = setPoint
        
    def run(self, actualVal):
        """!
        This function handles proportional control by comparing the current system value
        to the desired set point, and then computing the error. The error is then multiplied by
        the gain Kp to obtain proportional control.
        @param actualVal The measured current value of the system.
        @returns The output to be sent to the system driver as a float. (For a motor system, this is the PWM duty cycle percentage to be sent to the motor)
        """    
       
        # Compare actual to setpoint to find the error
        # Multiply by Kp
        outputVal = self.Kp * (self.setPoint - actualVal)
        
        
        return outputVal

    def set_setpoint(self, setPt):
        """!
        This function sets the desired setpoint.
        @param setPt The new desired setpoint of the system.
        """ 
        self.setPoint = setPt
        
    def set_Kp(self, Kp):
        """!
        This function sets the user input gain.
        @param Kp The new proportional gain value.
        """ 
        self.Kp = Kp
        
        
class PIController:
    """!
    The class initializes a proportional gain constant, Kp, an integral gain Ki
    and a desired setpoint for a system.
    When feedback is applied through the run() method, the error in the system is calculated,
    and the proportional and integral gain is applied. Rapidly and repeatedly calling run() enables one to
    create a closed loop proportional controller.
    """
    def __init__(self, Kp, Ki, setPoint):
        """! 
        This function initializes the proportional and integral gain constants and desired setpoint
        @param Kp User specified proportional gain constant.
        @param Ki User specified integral gain constant
        @param setPoint Desired setpoint for the system to be driven to.
        """

        self.Kp = Kp
        self.Ki = Ki
        self.setPoint = setPoint
        self.totalE = 0
        
    def run(self, actualVal):
        """!
        This function handles control by comparing the current system value
        to the desired set point, and then computing the error. The error is then multiplied by
        the gain Kp to obtain proportional control. The total error is integrated by summing it, and then
        Ki is applied to obtain integral control. Together, this creates a PI controller.
        @param actualVal The measured current value of the system.
        @returns The output to be sent to the system driver as a float. (For a motor system, this is the PWM duty cycle percentage to be sent to the motor)
        """    
       
        # Compare actual to setpoint to find the error        
        error = (self.setPoint - actualVal)
        # Sum the total error
        totalE += error
        # Multiply by Kp and Ki to get the output signal
        outputVal = self.Kp * error + self.Ki * totalE
        
        
        return outputVal

    def set_setpoint(self, setPt):
        """!
        This function sets the desired setpoint.
        @param setPt The new desired setpoint of the system.
        """ 
        self.setPoint = setPt
        
    def set_Kp(self, Kp):
        """!
        This function sets the proportional gain.
        @param Kp The new proportional gain value.
        """ 
        self.Kp = Kp
        
    def set_Ki(self, Ki):
        """!
        This function sets the intergral gain.
        @param Ki The new integral gain value.
        """ 
        self.Ki = Ki