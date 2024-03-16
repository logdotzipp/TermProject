# TermProject
## ME 405 Bin 9 Term Project - Heat Seeking Nerf Turret

 This repository contains code used to create a turret capable of launching foam darts at targets with a thermal signature. This device has been purpose built to compete in the Cal Poly ME 405 Term project duel. This means that it rotates 180 degrees after 5 seconds and then shoots at targets that are located in an approximately 15 degree cone. It only shoots a single dart before reseting itself. The goal was to create a turret that is accurate, consistent, and fast in order to consitently hit targets without incurring penalties for missed shots.

 ## Hardware Overview

 The turret itself consists of a [Pololu 37D 70L 12V 50:1 Gearmotor](https://www.pololu.com/product/4753/resources) which drives a 50 tooth pinion gear. The pinion gear then drives the 75 tooth turret platter, for an overall gear ratio of 75:1. Each large gear is 3D printed, and rides on a large ball bearing. Upon the platter sits a custom built dart launcher which uses 2 [OOD Loki 130 3s Motors](https://outofdarts.com/products/loki-130-3s-high-rpm-neo-motor-for-nerf-blasters) with [Worker Nightingale Flywheels](https://outofdarts.com/products/nightingale-flywheel-pair?_pos=6&_sid=e8fd52227&_ss=r). These motors spin up to approximately 60,000 rpm at 12V, providing more than enough kinetic energy to launch the [Worker Half Darts](https://outofdarts.com/products/worker-short-darts-200-pack-gen3-glow-tip) across the ~20ft gap between the turret and target. The darts are fed into the flywheels from a [10 Round Magazine](https://outofdarts.com/products/worker-10-round-talon-short-dart-magazine) by a [N20 Micro Gearmotor](https://outofdarts.com/products/n20-metal-gear-motor-micro-size-300-3000rmp-multiple-options) which drives a simple crank slider mechanism.

![image](https://github.com/logdotzipp/TermProject/assets/156237159/e5302574-3454-4f97-afdf-9873803fa1d0)
Figure 1: Overall Turret System CAD Model

![image](https://github.com/logdotzipp/TermProject/assets/156237159/77e55e58-a68a-4516-87a7-fda8671a1469)
Figure 2: Cross section of turret and blaster

![image](https://github.com/logdotzipp/TermProject/assets/156237159/32b3f3bb-f522-43a9-8e5d-9203a71ff7c9)

Figure 3: Internal view of blaster 

![IMG_4116](https://github.com/logdotzipp/TermProject/assets/156237159/b9ac9375-cfd0-4a7d-afe3-e8eb7e5399b6)
Figure 4: Completed Term Project Assembly

 A STM32 Nucleo MCU is used to control the system, and a L6206 H-Bridge Motor Controller Shield is used to control the pusher motor and turret motor. An additional custom N-Channel MOSFET circuit is used to drive the flywheel motors due to their unidirectional functionality and high current draw. An [Adafruit MLX90640 Thermal Camera](https://www.adafruit.com/product/4407) is used to detect targets with a relatively high heat signature. 12V Power is wired through a large red E-Stop button to allow the user to shut off motor power in the event of rapid unscheduled dissasembly or targeting of innocent bystanders. Limit switches are also used by the pusher motor and turret platter in order to home the motors between targeting cycles.

![CircuitDiagram](https://github.com/logdotzipp/TermProject/assets/156237159/68f6903b-5e8b-48e6-8b94-cce51bf90c21)
Figure 5: Circuit Diagram

## Software Implementation
The software for this project is constructed in a cotasking setup whereing tasks are assigned to each mechanism, and said tasks are given a priority and frequency at which to run. Each task contains a finite state machine in order to control the functionality of each mechanism.
 
After the user presses the input button on the STM32, the MCU waits 5.5 seconds before polling the thermal camera for targeting information. The blaster then rotates ~180 degrees to face the target. This rotation is done by a closed loop proportional controller using the optical encoder built into the Pololu Gearmotor. The pusher then forces a dart into the flywheels, sending it on a rapid flight towards the target. The turret then rotates back around homes itself to prepare for another duel. Detailed information on the software implementation can be viewed on the [Bin 9 Term Project Documentation Page](https://logdotzipp.github.io/TermProject/)

## Testing
The software was implemented in phases in order to verify each function of the system. Firstly, a P controller was implemented on the turret platter, which allowed for angular control in order to aim the blaster. The pusher and flywheels were also verified to ensure that darts could be consitently and accurately fed and launched. The thermal camera was also verified for functionality separately from the rest of system. Upon vertification of each subsystem, the entire system was integrated so as to compete ion the duel.

The thermal camera is fixed onto the frame of the project, meaning that it does not rotate with the turret. This means that targets identified by the camera must be mapped to a position of the turret. To additionally complicate matters, the camera is offset from the center of rotation. Some rough geometry was used to approximately map pixels to encoder ticks which provided a good starting point for our tuning. Repeated tests were then done to further refine our gain and offset values for accurate target tracking. 

## Learnings and Issues
The primary issue with our system is that there is no feedback at the output of the system (Direction of the barrel). Instead, feedback is given at the input of the system by the motor's encoder. This means that backlash is a big issue, since the position of the motor may not necessarily align with the position of the platter in all cases. This can be especially problematic when setting up the turret by hand, since it's relatively impercise and the direction of backlash unknown. For this reason, we implemented a homing sequence in which the turret uses a limit switch to locate itself before the start of every duel. This means that the turret setup is essentially the exact same for all duels, giving a more consistent result. While homing does not necessarily remove backlash from the system, homing the turret requently does help combat its effects.

A more robust solution to this problem would be to mount the camera on the blaster such that it rotates with the turret. This would provide direct feedback from the output, thereby removing backlash from being a consideration. However, we found that the camera refresh rate was much to slow to do closed loop camera feedback. The fastest we could get the camera to update was every 400ms, which is not nearly fast enough to provide closed loop control over a ~10 second duel. Using closed loop camera feedback would also be advatageous in that it would allow for more imprecise placement of the turret project, since the camera would be able to correct the turrets aim. In our project, slight misalignment of the turret on the table would cause large inacurracies since the connection between the camera and turret is essentially running in open loop.

Lastly, the addition of a PI controller could also help the turret system be more accurate. Our strictly P controller always had some steady state error, but this steady state error was always less that the angular backlash of the system. This means that adding integral control would likely not have helped boost our system accuracy in this case. However, if a system with less backlash and runnout was used, a PI controller could help maintain the accuracy of the system between duels.


