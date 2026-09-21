# rai-tiago

## Prerequisites

- Read instructions from tiago simulation repository (https://github.com/pal-robotics/tiago_simulation)
- Setup RAI (https://robotecai.github.io/rai/setup/install/)

## Setup
In rai folder, setup the environment:
```terminal
source ./setup_shell.sh
```

## Run
Launch gazebo simulation

```terminal
cd tiago_asas_ws/
source install/setup.bash
ros2 launch tiago_gazebo tiago_gazebo.launch.py is_public_sim:=True navigation:=True arm_type:=no-arm
```

Run the rai agent (text commands)
```terminal
cd tiago
python3 tiago_agent_local.py
```


