---
title: Sensors & Actuators
description: Overview of sensors and actuators used in physical AI and robotics systems
keywords: [sensors, actuators, motors, feedback devices, robotics hardware]
sidebar_position: 2
---

# Sensors & Actuators

## Introduction

Sensors and actuators are the "eyes, ears, and hands" of robots. Sensors provide information about the environment and the robot's state, while actuators translate control signals into physical action.

## Sensors in Robotics

### Vision Sensors

**Cameras**
- RGB cameras for color vision
- Depth cameras (RGB-D) for 3D information
- Thermal cameras for temperature sensing
- High resolution for detailed analysis
- Computationally intensive processing

**LiDAR (Light Detection and Ranging)**
- Creates 3D point clouds of environment
- Active sensing (emits laser light)
- Good in low-light conditions
- Limited by range and field of view

### Inertial Sensors

**Accelerometers**
- Measure acceleration in three axes
- Essential for balance control in walking robots
- Sensitive to vibration and noise

**Gyroscopes**
- Measure angular velocity
- Critical for orientation tracking
- Helps maintain balance during motion

**Inclinometers**
- Measure tilt and orientation relative to gravity
- Used for postural control

### Position and Motion Sensors

**Encoders**
- Measure joint position (angle)
- Rotary encoders for revolute joints
- Linear encoders for prismatic joints
- Essential feedback for joint control

**IMU (Inertial Measurement Unit)**
- Combines accelerometer, gyroscope, sometimes magnetometer
- Provides comprehensive motion and orientation data
- Fusion of multiple sensors for robust estimation

### Force and Touch Sensors

**Force/Torque Sensors**
- Measure forces and torques
- Critical for safe human-robot interaction
- Enable compliant manipulation
- Used in wrist and joint sensing

**Pressure Sensors**
- Detect contact and pressure distribution
- Important for grasping feedback
- Can be integrated into robotic skin

**Proximity Sensors**
- Detect nearby objects
- Ultrasonic or infrared based
- Used for collision avoidance

### Environmental Sensors

**Temperature Sensors**
- Monitor environment and robot internal temperature
- Important for thermal management

**Humidity Sensors**
- Measure ambient moisture
- Relevant for outdoor operation

**Air Quality Sensors**
- Detect gases and pollutants
- Used in hazardous environment inspection

## Actuators in Robotics

### Electric Motors

**DC Motors**
- Simple control via voltage
- Good speed-torque characteristics
- Commonly used for mobile robots

**Stepper Motors**
- Precise position control
- Good for load holding
- Limited speed and smoothness

**AC Motors**
- High power density
- Used in industrial applications
- Complex control requirements

**Brushless DC (BLDC) Motors**
- High efficiency
- Long lifespan
- Better control than brushed DC
- Common in modern robotics

### Servomotors

- Integrated motor with gearbox and controller
- Feedback control built-in
- Wide range of speeds and torques
- Popular for humanoid robots

### Actuator Types

**Revolute (Rotational) Actuators**
- Produce rotational motion
- Most common in humanoid robots
- Joints like shoulder, hip, knee

**Prismatic (Linear) Actuators**
- Produce linear motion
- Linear actuators or hydraulic cylinders
- Less common in humanoid design

### Power Transmission

**Gearboxes**
- Increase torque, reduce speed
- Essential for strong joints with reasonable power
- Add compliance and damping

**Timing Belts and Pulleys**
- Transmit motion over distance
- Lower friction than gears
- Useful for wrist mechanisms

**Direct Drive**
- No gearbox, motor directly drives joint
- Lower backlash and latency
- Requires high-torque motor

## Sensor-Actuator Integration

### Feedback Control Loop

```
Desired Position → Controller → Motor Command
                                       ↓
                                    Motor
                                       ↓
                                  Joint Movement
                                       ↓
                                  Position Sensor (Encoder)
                                       ↓
                              Back to Controller (Feedback)
```

### Multi-Sensor Fusion

Real robots often combine multiple sensors:
- **Vision + Depth**: Better 3D understanding
- **IMU + Encoders**: Robust state estimation
- **Force + Position**: Safe compliant control

Sensor fusion algorithms (like Kalman filters) combine information from multiple sources for robust estimation.

## Power Considerations

### Energy Efficiency
- Motor selection affects battery life
- Gearing impacts power consumption
- Control algorithms can reduce wasted energy

### Power Supply Requirements
- Peak power for acceleration
- Sustained power for continuous operation
- Battery capacity and recharge time

## Practical Challenges

### Sensor Noise and Drift
- All real sensors have imperfect measurements
- Filtering and fusion reduce noise
- Calibration needed periodically

### Latency
- Time delay between measurement and response
- Critical for stability and responsiveness
- Must be minimized in feedback loops

### Environmental Factors
- Temperature affects sensor calibration
- Vibration causes noise
- Electromagnetic interference affects sensors
- Weather impacts outdoor operation

### Reliability and Redundancy
- Sensors and actuators can fail
- Critical systems need redundant sensors
- Graceful degradation important

## Selection Criteria

When choosing sensors and actuators, consider:

| Factor | Consideration |
|--------|---------------|
| Accuracy | How precise does measurement need to be? |
| Speed | How fast must measurements be taken? |
| Range | What range of values must be measured? |
| Power | How much power can system provide? |
| Cost | Budget constraints for components? |
| Reliability | How critical is failure tolerance? |
| Size | Space constraints on robot? |

## Key Takeaways

- Sensors provide environmental and state information
- Actuators convert control signals to physical action
- Feedback from sensors enables closed-loop control
- Proper selection of sensors and actuators is critical for performance
- Multi-sensor fusion improves robustness
- Real systems must handle noise, delays, and component failure

## Further Reading

- Siciliano, B., & Khatib, O. (Eds.). (2016). Springer Handbook of Robotics (2nd ed.)
- Liphardt, A. M. (2018). Robotic Systems: Design, Control, and Implementation
- Everett, H. R. (1995). Sensors for Mobile Robots: Theory and Application

---

**Previous Lesson**: [Control Systems](lesson-1.md)

**Next Chapter**: [Mechanical Design & Motion](../chapter-3/lesson-1.md)
