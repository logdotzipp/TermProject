# TermProject
## ME 405 Bin 9 Term Project - Heat Seeking Nerf Turret

 This repository contains code used to create a turret capable of launching foam darts at targets with a thermal signature. This device has been purpose built to compete in the Cal Poly ME 405 Term project duel. This means that it rotates 180 degrees after 5 seconds and then shoots at targets that are located in an approximately 15 degree cone. It only shoots a single dart before reseting itself. The goal was to create a turret that is accurate, consistent, and fast in order to consitently hit targets without incurring penalties for missed shots.

 ## Hardware Overview

 The turret itself consists of a [Pololu 37D 70L 12V 50:1 Gearmotor](https://www.pololu.com/product/4753/resources) which drives a 50 tooth pinion gear. The pinion gear then drives the 75 tooth turret platter, for an overall gear ratio of 75:1. Upon the platter sits a custom built dart launcher which uses 2 [OOD Loki 130 3s Motors](https://outofdarts.com/products/loki-130-3s-high-rpm-neo-motor-for-nerf-blasters) with [Worker Nightingale Flywheels](https://outofdarts.com/products/nightingale-flywheel-pair?_pos=6&_sid=e8fd52227&_ss=r). These motors spin up to approximately 60,000 rpm at 12V, providing more than enough kinetic energy to launch the [Worker Half Darts](https://outofdarts.com/products/worker-short-darts-200-pack-gen3-glow-tip) across the ~20ft gap between the turret and target. The darts are fed into the flywheels from a [10 Round Magazine](https://outofdarts.com/products/worker-10-round-talon-short-dart-magazine) by a [N20 Micro Gearmotor](https://outofdarts.com/products/n20-metal-gear-motor-micro-size-300-3000rmp-multiple-options) which drives a simple crank slider mechanism.

 A STM32 Nucleo MCU is used to control the system, and a L6206 H-Bridge Motor Controller Shield is used to control the pusher motor and turret motor. An additional custom N-Channel MOSFET circuit is used to drive the flywheel motors due to their unidirectional functionality and high current draw. An [Adafruit MLX90640 Thermal Camera](https://www.adafruit.com/product/4407) is used to detect targets with a relatively high heat signature. 12V Power is wired through a large red E-Stop button to allow the user to shut off motor power in the event of rapid unscheduled dissasembly or targeting of innocent bystanders. Limit switches are also used by the pusher motor and turret platter in order to home the motors between targeting cycles.  

## Software Implementation
The software for this project is constructed in a cotasking setup whereing tasks are assigned to each mechanism, and said tasks are given a priority and frequency at which to run. Each task contains a finite state machine in order to control the functionality of each mechanism.
 
After the user presses the input button on the STM32, the MCU waits 5.5 seconds before polling the thermal camera for targeting information. The blaster then rotates ~180 degrees to face the target. This rotation is done by a closed loop proportional controller using the optical encoder built into the Pololu Gearmotor. The pusher then forces a dart into the flywheels, sending it on a rapid flight towards the target. The turret then rotates back around homes itself to prepare for another duel. Detailed information on the software implementation can be viewed on the [Bin 9 Term Project Documentation Page](https://logdotzipp.github.io/TermProject/)

## Testing

