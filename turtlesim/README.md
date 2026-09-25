# RAI-TurtleSim

This directory contains a small demonstration of **RAI** integration with **ROS 2 TurtleSim**.

The demo was developed as a preliminary environment for experimenting with RAI, ROS 2 tools, and natural-language robot control before moving to the main TIAGo implementation.

Both **textual** and **vocal** interaction are supported.

## Prerequisites

Before running the demo, install and configure:

1. **ROS 2**

2. **TurtleSim**

   Follow the official ROS 2 TurtleSim tutorial:

   https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html

3. **RAI**

   Follow the RAI installation instructions:

   https://robotecai.github.io/rai/setup/install/

## Setup

Navigate to the RAI repository and initialize the RAI environment:

```bash
cd rai/
source setup_shell.sh
cd ..
```

## Running the Demo

### Start TurtleSim

In a terminal, launch the TurtleSim node:

```bash
ros2 run turtlesim turtlesim_node
```

### Text Interaction

In another terminal, navigate to the `turtlesim` directory and run the local RAI agent:

```bash
cd turtlesim/
python3 turtlesim_agent_local.py
```

Natural-language commands can then be entered directly through the terminal.

### Voice Interaction

Alternatively, the demo can be controlled using vocal commands.

Run the HRI agent in one terminal:

```bash
cd turtlesim/
python3 turtlesim_agent_hri.py
```

Then run the speech-to-text agent in another terminal:

```bash
cd turtlesim/
python3 turtlesim_s2t_agent.py
```

The speech-to-text component processes vocal commands, which are then used by the RAI agent to interact with TurtleSim.

## Project Context

This demo was developed as a preliminary step to become familiar with RAI and its integration with ROS 2.

It is included as supplementary material and is **not part of the main experimental evaluation**. The main implementation and replication package are available in the [`../tiago/`](../tiago/) directory.