"""
RAI + TIAGo Gazebo simulation agent -- mobile base only (velocity teleop + Nav2).

Run:
  ros2 launch tiago_gazebo tiago_gazebo.launch.py is_public_sim:=True navigation:=True arm_type:=no-arm
  python3 tiago_agent_local.py
"""

import math
import time

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from rai.agents.langchain import create_react_runnable
from rai.tools.ros2 import (
    PublishROS2MessageTool,
    ReceiveROS2MessageTool,
    CallROS2ServiceTool,
    GetROS2ActionsNamesAndTypesTool,
    StartROS2ActionTool,
    GetROS2ActionResultTool,
)
from rai.communication.ros2 import (
    ROS2Context,
    ROS2Connector,
    ROS2HRIConnector,
    wait_for_ros2_services,
    wait_for_ros2_topics,
    ROS2Message,
)
from rai_whoami.models import EmbodimentInfo
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

CMD_VEL_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)


@ROS2Context()
def main():
    ros2_connector = ROS2Connector()

    required_topics = [
        "/mobile_base_controller/cmd_vel_unstamped",
        "/amcl_pose",
        "/initialpose",
    ]
    wait_for_ros2_topics(ros2_connector, required_topics)

    @tool
    def publish_cmd_vel(linear_x: float, angular_z: float, duration: float = 1.0) -> str:
        """
        Drive the TIAGo base directly by publishing Twist commands to
        /mobile_base_controller/cmd_vel_unstamped, repeating at 5 Hz for `duration`
        seconds so the command doesn't go stale, then stopping.
        linear_x is forward velocity (m/s), angular_z is rotational velocity (rad/s).
        """
        target_topic = "/mobile_base_controller/cmd_vel_unstamped"
        move_msg = ROS2Message(payload={
            "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": angular_z}
        })
        stop_msg = ROS2Message(payload={
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
        })

        rate_hz = 5
        interval = 1.0 / rate_hz
        elapsed = 0.0
        while elapsed < duration:
            ros2_connector.send_message(
                message=move_msg, target=target_topic,
                msg_type="geometry_msgs/msg/Twist",
                qos_profile=CMD_VEL_QOS, auto_qos_matching=False
            )
            time.sleep(interval)
            elapsed += interval

        ros2_connector.send_message(
            message=stop_msg, target=target_topic,
            msg_type="geometry_msgs/msg/Twist",
            qos_profile=CMD_VEL_QOS, auto_qos_matching=False
        )
        return f"Base moved for {duration:.1f}s and stopped."

    custom_tools = [
        publish_cmd_vel,

        ReceiveROS2MessageTool(
            connector=ros2_connector,
            readable=["/amcl_pose"],
            name="get_robot_pose",
            description=(
                "Call /amcl_pose [geometry_msgs/msg/PoseWithCovarianceStamped] to get the "
                "robot's current localized position and orientation (quaternion) in the map frame."
            )
        ),

        PublishROS2MessageTool(
            connector=ros2_connector,
            readable=["/initialpose"],
            name="set_initial_pose",
            description=(
                "Publish to /initialpose [geometry_msgs/msg/PoseWithCovarianceStamped] to tell "
                "AMCL where the robot currently is in the map. Required once before Nav2 goals "
                "will navigate correctly, if the robot hasn't been localized yet. "
                "Fields: pose.pose.position {x, y, z}, pose.pose.orientation {x, y, z, w}."
            )
        ),

        StartROS2ActionTool(connector=ros2_connector),
        GetROS2ActionResultTool(connector=ros2_connector),
        GetROS2ActionsNamesAndTypesTool(connector=ros2_connector),
    ]

    hri_connector = ROS2HRIConnector()
    embodiment_info = EmbodimentInfo.from_file("tiago_embodiment.json")

    agent = create_react_runnable(
        tools=custom_tools,
        system_prompt=embodiment_info.to_langchain(),
    )

    state = {'messages': []}
    print("LangChain/LangGraph Agent (Local Setup) for TIAGo simulation is ready.")

    while True:
        input_text = input("> ")
        state["messages"].append(HumanMessage(content=input_text))
        response = agent.invoke(state)
        state["messages"] = response["messages"]

        reply = ""
        for m in reversed(response["messages"]):
            if m.__class__.__name__ == "AIMessage" and getattr(m, "content", None):
                reply = m.content
                break
        print(f"\nAgent: {reply}" if reply else "\nAgent: [Tools executed, no final text reply]")


if __name__ == "__main__":
    main()