---
title: 'Wildflower Seeds'
date: 2024-10-17
permalink: /posts/2024/10/wildflower_seeds/
tags:
  - Hardware
  - drones
  - flowers
  - Biohacking
---

We moved to PA in 2023 and our property has a rather large and very plain looking power line easement. Previous owners had been mowing it every few months and as a result the plant biodiversity is pretty low consisting of mostly [Timothy Grass](https://www.inaturalist.org/taxa/57190-Phleum-pratense) with a few blackberry bushes spreading out of the woods. 

Inspiration
======
I like to look at wildflowers damn it. Going outside and collecting seed heads from wild plants on the roadside while effective still means I need to spread them on the easement somehow. I figured why not make something airborne? Enter the seed drone!

Hardware
======
The drone is a pretty common custom made 5 inch prop FPV drone, its running a [betaflight](https://betaflight.com/) firmware (4.5.1). The seed deployment mechanism consists of a 9g servo and a rubber band. The servo proved to be the most frustrating part of this build.
The drone flight controller is a [SpeedyBee F7 V3](https://www.speedybee.com/speedybee-f7-v3-bl32-50a-30x30-stack/) with the servo signal line going to motor pad 5 (M5) with the ground and +5v to their pads.
![Drone Electronics](/images/DroneElectronics.jpg)
The motor controller outputs more than enough power for a 9g servo, that servo rotates the control horn releasing the rubber band and flinging seeds. Depending on the type of seeds they can be wind dispersed or scattered by gravity alone, below is an example of wind dispersed [Joe Pye weed](https://www.inaturalist.org/taxa/132717-Eutrochium-fistulosum) and wild lettuces.
![Wild Lettuce](/images/WildflowerSeeds.jpg)
![Wind Dispersed Seeds](/images/WindDispersedSeeds.jpg)
![Joe Pye Weed](/images/JoePyeWeed1.jpg)
![Joe Pye Weed](/images/JoePyeWeed2.jpg)

Other seeds like to be in a soil seed bank and they can be packed into "seed balls" made of clay and compost.
![Seed Balls](/images/SeedBalls.jpg)

Still others are perfect for dropping loose but packed for flight using "natural materials" found around the forest.
![Seed Packet](/images/DroneSeedPacket.jpg)

Demonstration of the loose seed deployer in action.
[![Drone Servo](https://img.youtube.com/vi/q6Zp8Fsnwuo/0.jpg)](https://www.youtube.com/watch?v=q6Zp8Fsnwuo)

Software
======
By default `Motor 5` is mapped to output `B07`, since I'm not using motor 5 for a flight motor we can redefine `Servo 1` to use that output.
```
# resources
resource MOTOR 5 NONE
resource SERVO 1 B07
```
Next we need to make sure that CHANNEL_FORWARDING is enabled in betaflight, I'm using channel `AUX 1` for the seed deployer Servo 1 with that mapped to a pushbutton on the radio transmitter. By default the `channel_forwarding_start` param maps `AUX 1` to `Servo 1`
References: 
https://betaflight.com/docs/wiki/guides/current/servos-and-servo_tilt-for-3-1
https://youtu.be/L-6r2iX1p6s?t=804
[![Drone Servo](https://img.youtube.com/vi/9vQyFJy8Ob8/0.jpg)](https://www.youtube.com/watch?v=9vQyFJy8Ob8)
