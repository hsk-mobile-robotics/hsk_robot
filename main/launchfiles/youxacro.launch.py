import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node

import xacro

def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")
    pkg_youbot_model_description = get_package_share_directory('main')
    pkg_youbot_gazebo = get_package_share_directory('simulation')

    # Get paths
    xacro_file =  os.path.join(pkg_youbot_model_description, 'youbot_model_description','urdf', 'youbot.urdf.xacro')
    gazebo_maze_world_path = os.path.join(pkg_youbot_gazebo,'world','maze','model.sdf')
    gazebo_maze_world_config_path = os.path.join(pkg_youbot_gazebo,'world','maze','model.config')
    
    #Gazebo
    pkg_youbot_model_description = get_package_share_directory('main')
    
    
    #RVIZ
    pkg_youbot_rviz = get_package_share_directory('main')

    #Get xacro file and transform it into xml 
    robot_description_config = xacro.process_file(xacro_file)
    robot_description_xml = robot_description_config.toxml()
    params = {"robot_description": robot_description_xml, "use_sim_time": use_sim_time}

   
    robot_state_publisher = Node(
        #namespace="/youbot",
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

     # Visualize in RViz
    rviz = Node(
       # namespace="/youbot",
       package='rviz2',
       executable='rviz2',
       arguments=['-d', os.path.join(pkg_youbot_rviz, 'config', 'rviz_config', 'config.rviz')],
       condition=IfCondition(LaunchConfiguration('rviz'))
    )

     # Setup to launch the simulator and Gazebo world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory("gazebo_ros"),"launch","gazebo.launch.py")]),

    )


    spawn_entity = Node(package="gazebo_ros", executable="spawn_entity.py",
                        arguments=["-topic", "robot_description",
                                   "-entity", "Youbot"],
                                   output="screen")
    
    spawn_entity_world = Node(package="gazebo_ros", executable="spawn_entity.py",
                        arguments=[
                                   "-entity", "Maze",
                                   '-file', gazebo_maze_world_path,
                                   '-x', '30.0',
                                   '-y', '18.0',
                                   '-z', '0.0',],
                                   output="screen")
 

    return LaunchDescription([
            
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='use sim time if true'),
        DeclareLaunchArgument(
            'rviz', 
            default_value='true',
            description='Open RViz.'),
            
        robot_state_publisher,
    
        rviz,
        gazebo,
        #bridge,
        spawn_entity,
        spawn_entity_world
        
    ])
