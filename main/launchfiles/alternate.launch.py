import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


MODEL_PACKAGE = "main"
MODEL_NAME = "youbot.urdf.xacro"
WORLD_NAME = "model.sdf"
WORLD_CONFIG = "model.config"
RVIZ_CONFIG = "config.rviz"

def generate_launch_description():

    # set LaunchConfiguration variables
    use_sim_time = LaunchConfiguration("use_sim_time")
    rviz = LaunchConfiguration("rviz")

    # get Packages
    package_model = get_package_share_directory(MODEL_PACKAGE)
    package_gazebo = get_package_share_directory("simulation")   #! ToDo: new Structure
    package_config = get_package_share_directory("main")     #! ToDo: new Structure
    package_gazebo_ros = get_package_share_directory("gazebo_ros")
    package_slam = get_package_share_directory("slam_toolbox")
    package_nav = get_package_share_directory("nav2_bringup")

    # get Paths
    model_file = os.path.join(package_model, "youbot_model_description", "urdf", MODEL_NAME)
    world_file = os.path.join(package_gazebo, "world", "maze", WORLD_NAME)
    world_config = os.path.join(package_gazebo, "world", "maze", WORLD_CONFIG)

    # convert xacro files to xml
    model_config = xacro.process_file(model_file)
    mdoel_xml = model_config.toxml()
    params = {"robot_description": mdoel_xml, "use_sim_time": use_sim_time}

    slam_toolbox_params = os.path.join(get_package_share_directory("main"), "config", "slam_config", "mapper_params_online_async.yaml")

    return LaunchDescription([

        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="true if Simulation is used, false if Robot is used"
        ),

        DeclareLaunchArgument(
            "rviz",
            default_value="true",
            description="Wheter to start RVIZ or not"
        ),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[params]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(package_gazebo_ros, "launch", "gazebo.launch.py")
            ])
        ),

        

        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", os.path.join(package_config, "config","rviz_config", RVIZ_CONFIG)], #! ToDo: new Structure
            condition=IfCondition(rviz)
        ),

        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-topic", "robot_description", 
                "-entity", "Youbot"     #! ToDo: Variable bauen
                ],
            output="screen"
        ),

        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-entity", "Maze", 
                "-file", world_file, 
                "-x", "25.0",
                "-y", "19.0",
                "-z", "0.0",
                ],
            output="screen"
        ),

        #
        #Node(
        #    package = "slam_toolbox",
        #    executable="async_slam_toolbox_node",
        #    parameters=[slam_toolbox_params, {"use_sim_time": True}],
        #)

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(package_slam, "launch", "online_async_launch.py")
            ]),
            launch_arguments={"my_parameters":slam_toolbox_params}.items(),
        ),
      

        #IncludeLaunchDescription(
        #    PythonLaunchDescriptionSource([
        #        os.path.join(package_nav, "launch", "navigation_launch.py")
        #    ])
        #)
#
    ])