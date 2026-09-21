# rai-turtlesim

## Prerequisites

- ROS 2
- Install turtlesim (https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html)
- Setup RAI (https://robotecai.github.io/rai/setup/install/)

## Setup
In rai folder, setup the environment
```terminal
cd turtlesim/
source ./setup_shell.sh
```

## Run
In one terminal, launch the turtlesim simulation

```terminal
ros2 run turtlesim turtlesim_node
```

In another termina, run the local agent and insert textual commands through the terminal
```
cd turtlesim/
python3 turtlesim_agent_local.py
```

In alternative, you can use vocal commands running two agents in two different terminals

```
cd turtlesim/
python3 turtlesim_agent_hri.py
```

```
cd turtlesim/
python3 turtlesim_s2t_agent.py
```
