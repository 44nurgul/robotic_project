# ITMR-Bot

ITMR-Bot is a differential-drive mobile robot that we designed ourselves and simulated in Gazebo,
controlled through ROS 2. Its task is **exploration and detection** in an indoor area with obstacles:
it drives around while avoiding obstacles with a 2D LiDAR, detects colored objects with an RGB camera, spots warm objects and a human model with a thermal camera, and measures its own motion with an IMU.

## Team

| Member                | Sensor responsibility                                           | Other work                                                              |
| --------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Zeynep Sude Akyüz     | IMU                                                             | Simulation world, `obstacle_avoider` behavior node                      |
| Nurgül Gün            | LiDAR, thermal camera (integration)                             | Diff drive, ROS–Gazebo bridge, joint states, `color_detector` node      |
| Muaz Hamza Leventoğlu | RGB camera, thermal camera (visualization, thermal world setup) | Robot model, launch files, RViz configuration, system integration tests |


## Environment

- Ubuntu 26.04 LTS
- ROS 2 Lyrical
- Gazebo Jetty (gz-sim) with `ros_gz`
- RViz2

## Installation

1. Install ROS 2 Lyrical and Gazebo Jetty, then install the packages the project needs:

   ```bash
   sudo apt install \
     ros-lyrical-ros-gz \
     ros-lyrical-xacro \
     ros-lyrical-robot-state-publisher \
     ros-lyrical-joint-state-publisher-gui \
     ros-lyrical-rviz2 \
     ros-lyrical-rviz-imu-plugin \
     ros-lyrical-rqt-plot \
     ros-lyrical-rqt-image-view \
     ros-lyrical-teleop-twist-keyboard \
     python3-opencv python3-numpy
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/44nurgul/robotic_project.git
   cd robotic_project/itmr_ws
   ```

3. Install any missing dependencies with rosdep (optional if step 1 is done):

   ```bash
   source /opt/ros/lyrical/setup.bash
   rosdep install --from-paths src --ignore-src -y
   ```

4. Build the workspace and source it:

   ```bash
   colcon build --symlink-install
   source install/setup.bash
   ```

Run `source install/setup.bash` again in every new terminal you open before using `ros2` commands.

## Running

**Simulation only.** This starts the Gazebo world, spawns the robot, and starts the ROS–Gazebo bridge,
RViz and the `color_detector` node:

```bash
ros2 launch itmr_description gazebo.launch.py
```

**Simulation with obstacle avoidance.** This also starts the `obstacle_avoider` node, so the robot
drives on its own:

```bash
ros2 launch itmr_description gazebo.launch.py behavior:=true
```

**Manual driving.** Run this in a second terminal, with `behavior:=false`:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# or send a single command:
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}"
```

**Robot model only.** This opens RViz with joint sliders and does not start Gazebo:

```bash
ros2 launch itmr_description display.launch.py
```

## Sensors

| Sensor         | Topic                | Message type                | Visualization        |
| -------------- | -------------------- | --------------------------- | -------------------- |
| 2D LiDAR       | `/scan`              | `sensor_msgs/msg/LaserScan` | RViz LaserScan       |
| RGB camera     | `/camera/image_raw`  | `sensor_msgs/msg/Image`     | RViz Camera          |
| IMU            | `/imu`               | `sensor_msgs/msg/Imu`       | RViz Imu, `rqt_plot` |
| Thermal camera | `/thermal/image_raw` | `sensor_msgs/msg/Image`     | RViz Camera          |

To check a sensor, run `ros2 topic echo <topic> --once` or `ros2 topic hz <topic>`.

## Nodes (`itmr_behavior`)

- **`obstacle_avoider`**: subscribes to `/scan` and publishes `/cmd_vel`. If the closest obstacle in the
  front ±45° is nearer than 1.0 m, the robot turns in place toward the more open side. It drives forward
  again once the front is clear beyond 1.4 m.
- **`color_detector`**: subscribes to `/camera/image_raw` and publishes `/detected_color`
  (`std_msgs/msg/String`) when a red, green or blue object is visible.

## Repository Structure

```
itmr_ws/src/
├── itmr_description/   # robot model (URDF/Xacro, sensors), world, bridge config, launch, RViz
└── itmr_behavior/      # obstacle_avoider and color_detector nodes
```

## Troubleshooting

- If `ros2` cannot find a package, the terminal is not sourced. Run `source install/setup.bash`.
- If Gazebo misbehaves after a crash, stop any leftover processes with `pkill -f "gz sim"` and launch again.

## Credits and License

The Rescue Randy human model is from OpenRobotics on Gazebo Fuel, and a copy is included in the repository. The project is licensed under Apache-2.0.
