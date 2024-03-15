"""!
\mainpage Main Page

\section Software
This section details the software used in the control and design of the
ME 405 term project Nerf turrent.

\subsection subsection1 Motor Driver
The Motor Driver is a class that runs any 12 V DC motor using a L6206 H-Bridge
motor driver. The software was implemented to the control the PWM and the speed at
which the 12 V 60:1 gearmotor is to run when turning around to shoot any player on
the other side of the turrent.

\subsection subsection2 Controller
This a general Proportional Controller class that can be used with any generic motor.
The class is able to output an error from a specified desired position with a specified
gain to generate an actuation value necessary for the motor to spin to get to the desired
position. The software is implemented to control how far the turrent needs to turn and face
the opponent before shooting a dart.

\subsection subsection3 mlx_cam
This a thermal imaging class that uses a MLX90640 Thermal Imaging Camera from Adafruit to take
a 32x24 sized thermal picture and return them as either a CSV file or an ASCII art. This software
was implemented to determine the horizontal position of the opponent that is 20 ft. from the turrent's
position.

\section Tasks
This section details the Tasks, as well as the states that composes them, that comprises the software used to both run and control the firing and turning
of the turrent in the duel.

\subsection subsection4 Task 1: motor_control
Task 1 controls the behavior of the motor used to turn the turrent to face the opposing player and the flywheels
used to shoot the dart. Task 1 also controls the turrent to position itself facing 180 degrees away when the
software is ran.

\subsubsection sub1 State 0

\subsubsection sub2 State 1

\subsubsection sub3 State 2

\subsubsection sub4 State 3

\subsubsection sub5 State 4

\subsubsection sub6 State 5

\subsubsection sub7 State 6



\subsection subsection 5 Task 2: pusher_control
Task 2 controls the timing of the pusher motors that are stationed in the back of the turrent that pushes
a dart from a magazine to the flywheels.

\subsubsection sub1

\subsubsection sub2


\subsection subsection6 Task 3: camera
Task 3 controls the MLX90640 thermal camera to take a single picture and return the position a player
is standing relative to the camera's position.

\subsubsection sub1

\subsubsection sub2
"""

# \section {section-name} "DO NOT USE SPACES!"
# \subsection {subsection-name} {Title}
# \subsubsection {subsection-name} {Title}
#\image html {picture-name.png/.jpg} "WILL NOT LOAD IMAGE UNTIL DOXY HAS AN IMAGE DIRECTORY"

