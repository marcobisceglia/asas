from langchain_core.messages import HumanMessage
from rai.agents.langchain import create_react_runnable
from rai_whoami.models import EmbodimentInfo

from rai.agents import wait_for_shutdown

from rai.communication.ros2 import (
    ROS2Context,
    ROS2Connector,
    ROS2HRIMessage,
    wait_for_ros2_services,
    wait_for_ros2_topics
)

from turtlesim_tools import custom_tools

INPUT_TOPIC = "/from_human"
OUTPUT_TOPIC = "/to_human"

def extract_text(msg) -> str:
    """
    Extraction confirmed against real debug output:
      ROS2Message(payload=rai_interfaces.msg.HRIMessage(..., text='hello', ...), ...)
    So the real text lives at msg.payload.text (an attribute on the ROS
    message object inside .payload, not a dict key).
    """
    print(f"[DEBUG] raw message received: {msg!r}")

    payload = getattr(msg, "payload", None)
    text = getattr(payload, "text", None)
    if text:
        return text

    # Fallbacks kept just in case a different message ever reaches here
    # (e.g. if you later change msg_type or raw=True).
    text = getattr(msg, "text", None)
    if text:
        return text
    if isinstance(payload, dict) and payload.get("text"):
        return payload["text"]

    print("[WARN] Could not automatically extract text -- inspect the "
          "[DEBUG] line above and adjust extract_text() accordingly.")
    return ""

@ROS2Context()
def main() -> None:
    ros2_connector = ROS2Connector()

    required_topics = ["/turtle1/cmd_vel", "/turtle1/color_sensor", "/turtle1/pose"]
    required_services = ["/clear", "/kill", "/reset", "/spawn", "/turtle1/set_pen", "/turtle1/teleport_absolute", "/turtle1/teleport_relative"]

    # Agent will not start until the turtlesim simulation starts
    wait_for_ros2_services(ros2_connector, required_services)
    wait_for_ros2_topics(ros2_connector, required_topics)

    #tools = ROS2Toolkit(connector=ros2_connector).get_tools() + get_custom_tools(ros2_connector) # ros 2 tools + custom for turtle
    tools = custom_tools #+ get_custom_tools(ros2_connector)

    # Load the system prompt
    embodiment_info = EmbodimentInfo.from_file("turtlesim_embodiment.json")
    
    # build the agent. It will have ROS 2 tools and the turtle prompt
    # to change LLM model, updated config.toml
    agent = create_react_runnable(
        tools=tools,
        system_prompt=embodiment_info.to_langchain(),
    )

    # Conversation memory persists
    state = {"messages": []}

    def on_human_message(msg) -> None:
        text = extract_text(msg)
        if not text:
            return

        print(f"Received command: {text!r}")
        state["messages"].append(HumanMessage(content=text))
        response = agent.invoke(state)
        state["messages"] = response["messages"]  # persist full updated history

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

        reply = ROS2HRIMessage(payload={"text": reply})
        ros2_connector.send_message(
            message=reply,
            target=OUTPUT_TOPIC,
            msg_type="rai_interfaces/msg/HRIMessage",
        )

    ros2_connector.register_callback(
        INPUT_TOPIC,
        on_human_message,
        msg_type="rai_interfaces/msg/HRIMessage",
    )

    print(f"RAI HRI Agent for turtlesim is ready.")
    print(f"  Listening on: {INPUT_TOPIC}")
    print(f"  Replying on:  {OUTPUT_TOPIC}")
    print("Press Ctrl+C to stop.")

    # Start the agent and wait for shutdown signal (Ctrl+C)
    wait_for_shutdown([agent])


if __name__ == "__main__":
    main()