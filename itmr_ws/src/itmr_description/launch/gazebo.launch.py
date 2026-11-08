import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

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

    # Dunya dosyasinin yolu 
    world_path = os.path.join(
        pkg_path,
        "worlds",
        "itmr_world.sdf"
    )

    # Convert Xacro to URDF
    robot_description = xacro.process_file(xacro_file).toxml()

    # Publish robot TF transforms
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }]
    )
    gz_resource_path = AppendEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        os.path.dirname(pkg_path)
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            # --- DEGISTI: empty.sdf yerine kendi dunyamiz ---
            "gz_args": f"-r {world_path}",
            "on_exit_shutdown": "true"
        }.items()
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        parameters=[{
            "topic": "robot_description",
            "name": "itmrbot",
            #YENI: dogma konumu
            "x": 0.0,
            "y": 0.0,
            "z": 0.1
        }]
    )

    # Gazebo <-> ROS 2 koprusu (topic esleme tablosu config/gz_bridge.yaml icinde)
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        parameters=[{
            "config_file": os.path.join(pkg_path, "config", "gz_bridge.yaml")
        }]
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", os.path.join(pkg_path, "rviz", "default.rviz")],
        parameters=[{
            "use_sim_time": True
        }]
    )

    # Engelden kacinma davranisi: sadece "behavior:=true" verilirse baslar
    behavior_arg = DeclareLaunchArgument(
        "behavior",
        default_value="false",
        description="true ise obstacle_avoider node'u da baslatilir"
    )

    obstacle_avoider = Node(
        package="itmr_behavior",
        executable="obstacle_avoider",
        output="screen",
        parameters=[{
            "use_sim_time": True
        }],
        condition=IfCondition(LaunchConfiguration("behavior"))
    )

    return LaunchDescription([
        behavior_arg,
        robot_state_publisher,
        gz_resource_path,
        gazebo,
        spawn_robot,
        bridge,
        rviz,
        obstacle_avoider
    ])
