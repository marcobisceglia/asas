"""
RAI + turtlesim demo -- LOCAL variant.

Run:
  ros2 run turtlesim turtlesim_node
  python3 turtlesim_agent_local.py
"""

import time

from langchain_core.messages import HumanMessage
from rai.tools.ros2 import (
    ROS2Toolkit,
    PublishROS2MessageTool,
    ReceiveROS2MessageTool,
    CallROS2ServiceTool,
    GetROS2ServicesNamesAndTypesTool,
    GetROS2ActionsNamesAndTypesTool,
    StartROS2ActionTool,
    GetROS2ActionResultTool
)
 
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from rai.agents import BaseAgent

from rai.communication.ros2 import (
    ROS2Context,
    ROS2Connector,
    ROS2HRIConnector,
)

from rai.communication.ros2 import wait_for_ros2_services, wait_for_ros2_topics, ROS2Connector, ROS2Message

from rai.agents.langchain import create_react_runnable
from rai_whoami.models import EmbodimentInfo

from langchain_core.tools import tool

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

INPUT_TOPIC = "/from_human"
OUTPUT_TOPIC = "/to_human"

# QoS esplicito per garantire la compatibilità con il subscriber RELIABLE di turtlesim
CMD_VEL_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)

@ROS2Context() # run rclpy.init() before main and rclpy.shutdown() after
def main():
    ros2_connector = ROS2Connector()

    #tools = ROS2Toolkit(connector=ros2_connector).get_tools() + get_custom_tools(ros2_connector) # ros 2 tools + custom for turtle

    required_topics = ["/turtle1/cmd_vel", "/turtle1/color_sensor", "/turtle1/pose"]
    required_services = ["/clear", "/kill", "/reset", "/spawn", "/turtle1/set_pen", "/turtle1/teleport_absolute", "/turtle1/teleport_relative"]

    # Agent will not start until the turtlesim simulation starts
    wait_for_ros2_services(ros2_connector, required_services)
    wait_for_ros2_topics(ros2_connector, required_topics)
    

    @tool
    def publish_cmd_vel(linear_x: float, angular_z: float, duration: float = 1.0, turtle_name: str = "turtle1") -> str:
        """
        Publish a velocity command to /turtleX/cmd_vel, repeating it for `duration` seconds, then stop.
        """
        turtle_name = turtle_name.strip("/")
        target_topic = f"/{turtle_name}/cmd_vel"

        move_msg = ROS2Message(payload={
            "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": angular_z}
        })
        stop_msg = ROS2Message(payload={
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
        })

        rate_hz = 5  # well under the ~1s watchdog timeout
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
        return f"{turtle_name} moved for {duration:.1f}s and stopped."

    custom_tools = [
        publish_cmd_vel,

        #PublishROS2MessageTool(
        #    connector=ros2_connector,
        #    readable=["/turtle1/cmd_vel"],
        #    name="publish_cmd_vel",
        #    description=("Call /turtle1/cmd_vel [geometry_msgs/msg/Twist] to move the turtle1. The linear and angular command velocity for turtle1. The turtle will execute a velocity command for 1 second then time out. Twist.linear.x is the forward velocity, Twist.linear.y is the strafe velocity, and Twist.angular.z is the angular velocity.'")
        #),

        ReceiveROS2MessageTool(
            connector=ros2_connector,
            readable=["/turtle1/pose"],
            name="get_turtle_pose",
            description="Call /turtle1/pose [turtlesim/Pose] to get the x, y, theta, linear velocity, and angular velocity of turtle1"
        ),

        CallROS2ServiceTool(
            connector=ros2_connector,
            writable=["/clear", "/reset", "/kill", "/turtle1/set_pen", "/turtle1/teleport_absolute", "/turtle1/teleport_relative"],
            name="manage_simulation",
            description=(
                "Call /clear [std_srvs/srv/Empty] to clear the turtlesim background and sets the color to the value of the background parameters. Takes NO arguments (empty service_args)."
                "Call /reset [std_srvs/srv/Empty] to reset the turtlesim to the start configuration and sets the background color to the value of the background. Takes NO arguments." 
                "Call /kill [turtlesim/srv/Kill] to kill a turtle by name. args: {name: str}."
                "Call /turtle1/set_pen [turtlesim/srv/SetPen] to set the pen's color (r g b), width (width), and turns the pen on and off (off). args: {r: int, g: int, b: int, width: int, off: int(0 or 1)}." 
                "Call /turtle1/teleport_absolute [turtlesim/srv/TeleportAbsolute] to teleport the turtle1 to (x, y, theta). args: {x: float, y: float, theta: float}."
                "Call /turtle1/teleport_relative [turtlesim/srv/TeleportRelative] to teleport the turtle1 a linear and angular distance from the turtles current position. args: {linear: float, angular: float}." 
            ),
        ),
    ]

    tools = custom_tools #+ get_custom_tools(ros2_connector)

    #print(tools)

    
    #system_prompt = SystemMultimodalMessage()
    #input_topic = INPUT_TOPIC
    #output_topic = OUTPUT_TOPIC

    # Initialize the ROS 2 HRI (Human-Robot Interface) connector
    # This handles bidirectional communication with human-facing topics
    hri_connector = ROS2HRIConnector()


    # Load the system prompt
    embodiment_info = EmbodimentInfo.from_file(
        "turtlesim_embodiment.json"
    )

    # Create a ReAct agent with the provided tools and system prompt
    # It will have ROS 2 tools and the turtle prompt
    # to change LLM model, updated config.toml
    agent = create_react_runnable(
        tools=tools,
        system_prompt=embodiment_info.to_langchain(),
        #system_prompt=TURTLESIM_SYSTEM_PROMPT,
    )

    # Initialize the agent's state with an empty message history
    # state = {"messages": []}
    # state = ReActAgentState(messages=[])
    state = {'messages': []}

    # Set up the callback handler to route agent outputs to ROS 2 topics
    #callback_handler = HRICallbackHandler(
    #    connectors={output_topic: hri_connector},
    #)

    # Register the input callback for distributed operation
    # For simpler setups, you can directly call self.agent.invoke() in a loop
    # hri_connector.register_callback(input_topic, input_callback)

    print("LangChain/LangGraph Agent (Local Setup)) for turtlesim is ready.")

    while True:
        input_text = input("> ")
        state["messages"].append(HumanMessage(content=input_text))
        response = agent.invoke(state)
        state["messages"] = response["messages"]  # persist full updated history
        
        #print(response)
        
        # Print the last real reply (skip intermediate tool-call-only messages).
        reply = ""
        for m in reversed(response["messages"]):
            if m.__class__.__name__ == "AIMessage" and getattr(m, "content", None):
                reply = m.content
                break
        if reply:
            print(f"\nAgent: {reply}")
        else:
            print("\nAgent: [Tools executed, no final text reply]")


if __name__ == "__main__":
    main()