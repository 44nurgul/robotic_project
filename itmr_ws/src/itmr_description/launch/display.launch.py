
import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():

    # ITMR description package path
    pkg_path = get_package_share_directory("itmr_description")

    # Robot Xacro file
    xacro_file = os.path.join(
        pkg_path,
        "urdf",
        "robot.urdf.xacro"
    )

    # Convert Xacro to URDF
    robot_description = xacro.process_file(xacro_file).toxml()

    # Publish robot TF transforms
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description
        }]
    )

    # Publish joint states
    joint_state_publisher = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen"
    )

    # Open RViz2
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="screen"
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz
    ])
