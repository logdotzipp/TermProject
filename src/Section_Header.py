"""!
\mainpage Main Page

\section Software
This section details the software used in the control and design of the
ME 405 term project turret.

\subsection subsection1 Motor Driver
The Motor Driver is a class that runs any 12 V DC motor using a L6206 H-Bridge
motor driver. The software was implemented to the control the PWM and the speed at
which the 12 V 50:1 gearmotor is to run when turning around to shoot any player on
the other side of the turret.

\subsection subsection2 Controller
This a general Proportional Controller class that can be used with any generic motor.
The class is able to output an error from a specified desired position with a specified
gain to generate an actuation value necessary for the motor to spin to get to the desired
position. The software is implemented to control how far the turret needs to turn and face
the opponent before shooting a dart.

\subsection subsection3 Encoder
The encoder class implements the STM32's quadature encoder functionality to: initlialize
encoder pins and timers, read current encoder position, and set the current encoder position to
zero.

\subsection subsection4 mlx_cam
This is a thermal imaging class that uses a MLX90640 Thermal Imaging Camera from Adafruit to take
a 32x24 sized thermal picture and return them as either a CSV file or an ASCII art. This software
was implemented to determine the horizontal position of the opponent that is 20 ft. from the turret's
position. 

\subsection subsection5 Panning
This script is a cooperative multitasking program which implements all four of the above classes
to aim and fire at a target using the MLX90640 thermal camera. See the Tasks section for more details.

\section Tasks
This section details the cooperative multitasking program in Panning.py.

Panning.py consists of three
tasks: motor_control, pusher_control, and camera. The motor_control task is used to pan the turret 180 degrees away
from the opposing turret and prepare to shoot at a location specified  by the MLX90640 camera's feedback.
\ref  subsection6 details Task 1 and the states that compose it, which allow the turret to pan, aim, and return to its home position.
The pusher_control task simply controls the timing of a pusher motor to fire a dart.
\ref subsection7 details Task 2 and the states that compose it, which push a dart from a magazine through a set of flywheels.
Finally, the camera task communicates with an MLX90640 Thermal Imaging Camera to take a picture of opponents standing opposite of
the turret and is used to determine their location.
\ref subsection8 details Task 3 and the states that compose it, which take a thermal image opposite of the turret.

The figure below shows the task diagram of the Panning.py file that is used to control movement and actions of the turret.

\image html PanningTaskDiagram.png "Figure 1. Task Diagram for panning.py that controls both movement and ability to fire." width=500 

\subsection subsection6 Task 1: motor_control
Task 1 controls the gear motor used to aim the blaster and controls the flywheels
used to fire a dart. Additionally, it homes the blaster assembly to face 180 degrees away from
the opposing team's turret.

\subsubsection sub1 State 0
Initializes gear motor by creating an object of the motor_driver and encoder classes. Initializes flywheel
motors by creating a timer channel object and a corresponding control pin. Sets up the homing
limit switch pin and the user input switch pin which begins the firing sequence. Finally, the gear motor is
turned on at a slow speed to beign homing the blaster assembly. Moves on to state 6.

\subsubsection sub2 State 1
Waits for the user input switch to be pressed before moving on to state 2 to begin the firing sequence.

\subsubsection sub3 State 2
Waits for five and a half seconds after user input button is pressed before setting a flag to tell the
camera task to take a picture. Moves on to state 3 once this flag is set.

\subsubsection sub4 State 3
Waits for the camera flag to be cleared by the camera task before calculating the desired encoder position. The desired encoder position
is determined using the target location returned by the camera task. Creates an object of the controller class to initialize step response
and aim at target. Moves on to state 4

\subsubsection sub5 State 4
Turns on the flywheel motors and runs the aiming step response while checking for steady state. Once steady state has been achieved
and the blaster assembly is aiming at the target, the doShoot flag is set to tells the pusher_control task to fire a dart.
Finally, the desired encoder position is set to a position approximately 45 degrees from home. Moves to state 5.

\subsubsection sub6 State 5
Once the doShoot flag has been cleared by the pusher_control task indicating that a dart has been fired, runs the step response to
move back to 45 degrees from the home position. Once this position has been reached, the flywheel motors are turned off, the
gear motor speed is set to slow, and the task moves on to state 6.

\subsubsection sub7 State 6
Continues moving the gear motor until the homing limit switch is pressed. When the limit switch is pressed, home position has been
reached and motor gets turned off. Moves on to state 1.

Figure 2 shown below shows the Finite State Machine of Task 1 and its various state transitions.

\image html MotorControlFSM.png "Figure 2. Finite State Machine diagram for Task 1: motor_control and its state transitions." width=500

\subsection subsection7 Task 2: pusher_control
Task 2 controls the timing of the pusher motor which pushes a dart from the magazine through the flywheels.

\subsubsection sub1 State 0
Initializes pusher motor by creating an object of the motor_driver class. Initializes the pusher motor limit switch pin.
Moves on to state 1.

\subsubsection sub2 State 1
Waits for the doShoot flag to be set by the motor_control task when the blaster assembly is aiming at the target. Once
flag is set, moves on to state 2.

\subsubsection sub3 State 2
Begins moving pusher motor. Once the pusher motor limit switch is unpressed, moves to state 3.

\subsubsection sub4 State 3
Continues moving pusher motor until the limit switch is pressed once again. Once limit switch is pressed, the pusher motor is stopped,
the doShoot flag is cleared, and the task returns to state 1.

Fiugre 3 shown below shows the Finite State Machine of Task 2 and its state transitions to push darts from a magazine to a flywheel.

\image html PusherControlFSM.png "Figure 3. Finite State Machine diagram for Task 2: pusher_control and its state transitions." width=500

\subsection subsection8 Task 3: camera
Task 3 controls the MLX90640 thermal camera to take a single picture and returns the column in which a target
is standing relative to the camera's position.

\subsubsection sub1 State 0
Initializes I2C communication with the MLX90640 camera. Creates an object of the MLX_Cam class to set up picture taking.
Moves on to state 1.

\subsubsection sub2 State 1
Waits for the camera flag to be set by the motor_control task. Once this flag is set, a thermal image is captured in the form of
a list of pixel data. This list is iterated through to determine which column the target is standing in. The column value is stored
in the share called "pixelpos", and it is returned to the motor_control task. The camera flag is then cleared and the state self
transitions to wait for another camera flag.

Figure 4 shown below shows the Finite State Machine of Task 3 and its state to take a single thermal image that will be processed for aiming.

\image html CameraFSM.png " Figure 4. Finite State Machine diagram for Task 3: camera and its state." width=500
"""


# \section {section-name} "DO NOT USE SPACES!"
# \subsection {subsection-name} {Title}
# \subsubsection {subsection-name} {Title}
#\image html {picture-name.png/.jpg} {"caption"} {widht=} "WILL NOT LOAD IMAGE UNTIL DOXY HAS AN IMAGE DIRECTORY"
