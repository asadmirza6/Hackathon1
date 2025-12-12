---
title: Locomotion & Planning
description: Algorithms and techniques for robot locomotion and motion planning
keywords: [locomotion, motion planning, path planning, gait, bipedal walking, trajectory]
sidebar_position: 2
---

# Locomotion & Planning

## Introduction to Locomotion

Locomotion is the ability to move from one place to another. For humanoid robots, this primarily means walking on two legs in human environments. This is fundamentally different from wheeled robots and presents unique challenges.

## Bipedal Walking Principles

### Support Polygon

The support polygon is the region on the ground enclosed by the contact points of the feet.

**Dynamic Stability**: Maintaining balance requires the center of mass (COM) projection to stay within the support polygon

### Walking Cycle

A typical walking cycle consists of:

1. **Stance Phase**: One leg supports the body while the other swings forward (~60% of cycle)
2. **Double Support Phase**: Both feet contact ground (~10% of cycle)
3. **Swing Phase**: Free leg moves forward without support (~30% of cycle)

### Gait Patterns

**Normal Walking Gait**
- Comfortable, energy-efficient
- Double support phase provides stability
- Suitable for most situations

**Running Gait**
- Flight phase where both feet leave ground
- Faster but requires more power
- Less stable than walking

**Crawling Gait**
- Continuous ground contact
- Very stable
- Slower movement

## Motion Planning

### Path Planning

Planning a collision-free path from start to goal:

**Graph-Based Methods**
- **Roadmap**: Create graph of free space
- **A* Search**: Find shortest path through graph
- **Dijkstra**: Find optimal path
- Good for known environments

**Sampling-Based Methods**
- **Rapidly Exploring Random Trees (RRT)**: Incrementally build tree toward goal
- **Probabilistic Roadmaps (PRM)**: Sample configuration space
- Good for high-dimensional spaces and unknown environments

**Potential Field Methods**
- Goal attracts robot, obstacles repel
- Simple and fast
- Can get stuck in local minima

### Trajectory Planning

Given a path, plan smooth, feasible trajectories:

**Joint Space Trajectories**
- Plan in joint angle space
- Simpler computation
- Respects joint limits automatically

**Cartesian Space Trajectories**
- Plan in 3D end-effector space
- More intuitive
- Requires inverse kinematics

**Time-Optimal Trajectories**
- Minimize execution time
- Subject to actuator limits
- Computationally intensive

## Walking Pattern Generation

### Zero Moment Point (ZMP)

ZMP is a critical concept in bipedal walking:

**Definition**: The point on the ground where the net moment (torque) about that point is zero

**Stability Condition**: For stable walking, ZMP must remain within the support polygon

**Control Strategy**: Adjust COM acceleration to keep ZMP in feasible region

### Inverted Pendulum Model

Simplified model for bipedal walking:

```
     COM (center of mass)
      |
      |
      | (height h)
      |
    /---\ (foot/support point)
```

- Body modeled as point mass at COM
- Inverted pendulum dynamics govern motion
- Natural frequency increases with leg length

### Gait Optimization

Finding efficient walking patterns:

**Energy Efficiency**
- Minimize total energy consumption
- Balance speed and power usage
- Important for battery-powered robots

**Stability Margins**
- Larger margins more stable but slower
- Smaller margins faster but riskier
- Optimize based on environment

## Obstacle Avoidance

### Reactive Obstacle Avoidance
- Respond to immediately detected obstacles
- Quick decision making
- Limited planning horizon

### Predictive Obstacle Avoidance
- Predict future obstacles
- Plan around them in advance
- Requires motion prediction of moving obstacles

### Dynamic Window Approach
- Sample command velocities
- Forward simulate trajectories
- Choose safest and most efficient option

## Terrain Adaptation

### Uneven Terrain

**Detection**:
- Use foot sensors to detect terrain height
- Computer vision for terrain classification

**Adaptation**:
- Adjust step height for stairs
- Modify gait for slopes
- Increase caution for uncertain terrain

### Different Surfaces

| Surface | Challenge | Adaptation |
|---------|-----------|-----------|
| Stairs | Large height changes | Increased step height |
| Slopes | Loss of stability | COM adjustment |
| Ice | Low friction | Slower movement |
| Sand | Energy loss | Modified gait |

## Real-Time Constraints

### Computational Latency

- Walking at 1 m/s requires decisions every ~0.3 seconds
- Must balance planning horizon and computation time
- Hierarchical planning: long-term path, short-term trajectory

### Sensory Delays

- Camera latency: 30-100 ms
- IMU latency: 5-20 ms
- Motor response time: 10-50 ms
- Must predict future states

## Challenges in Real-World Locomotion

### Unstructured Environments
- Real environments are messy and unpredictable
- Requires robust perception and adaptation
- Edge cases are common

### Dynamic Obstacles
- Moving obstacles (people, vehicles)
- Prediction of future positions
- Safety margins needed

### Uncertainty
- Sensor noise and inaccuracy
- Model mismatch between simulation and reality
- Adaptation and learning needed

### Energy Constraints
- Limited battery capacity
- Efficiency critical for long operation
- Trade-offs between speed and endurance

## Planning for Manipulation While Walking

### Multi-Task Planning
- Simultaneously walk to location and manipulate
- Requires coordinated upper and lower body control
- Balance maintenance while manipulating

### Grasp-and-Move Tasks
- Identify object location
- Plan walking path
- Plan grasping trajectory
- Execute task
- Execute return journey

## Key Takeaways

- Bipedal walking requires maintaining balance through ZMP control
- Path planning finds collision-free routes; trajectory planning creates smooth motions
- Multiple planning methods exist with different trade-offs
- Real-world deployment requires handling uneven terrain and dynamic obstacles
- Computational and sensory latency must be considered
- Energy efficiency becomes critical for practical systems

## Further Reading

- Kajita, S., & Espiau, B. (2008). Legged robots. In Springer handbook of robotics (pp. 519-547)
- Khatib, O. (1985). Real-time obstacle avoidance for manipulators and mobile robots. The International Journal of Robotics Research, 5(1), 90-98
- Thrun, S., Burgard, W., & Fox, D. (2005). Probabilistic Robotics

---

**Previous Lesson**: [Humanoid Mechanical Design](lesson-1.md)

**Next Chapter**: [Human-AI Collaboration](../chapter-4/lesson-1.md)
