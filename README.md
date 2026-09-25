# Autonomous Self-Adaptive Systems — RAI Robotics Project

Project developed for the **Autonomous Self-Adaptive Systems** course at the **Gran Sasso Science Institute (GSSI)**.

This repository explores the integration of AI agents with ROS 2 robots using **RAI**, an agentic framework for Embodied AI and robotic systems.

The project contains two implementations:

```text
asas/
├── tiago/
└── turtle_sim/
```

## TIAGo

The [`tiago/`](tiago/) directory contains the main project and experimental evaluation.

It integrates RAI with a simulated **TIAGo robot** in ROS 2 and Gazebo, allowing an LLM-based agent to interpret natural-language missions and execute them through robotic tools.

The project includes:

* text and voice interaction with the robot;
* semantic navigation through ROS 2/Nav2;
* multi-step and conditional mission execution;
* human–robot interaction during mission execution;
* evaluation of multiple locally deployed LLMs through Ollama;
* experimental prompts, execution logs, and replication instructions.

Five models were evaluated:

* `qwen2.5:7b`
* `qwen2.5:14b`
* `llama3.1:8b`
* `mistral-nemo:12b`
* `gpt-oss:20b`

See [`tiago/README.md`](tiago/README.md) for the complete setup, execution, and experiment replication instructions.

## TurtleSim Demo

The [`turtlesim/`](turtlesim/) directory contains a small preliminary demo developed to become familiar with RAI and its integration with ROS 2.

It provides a simpler environment for experimenting with natural-language agent interaction and robotic tools before moving to the TIAGo simulation.

This demo is provided as supplementary material and is not part of the main experimental evaluation.

## RAI

The project uses **RAI (RobotecAI)**, an agentic framework for integrating AI capabilities with robotic systems and ROS 2.

For installation instructions and documentation, see the official RAI documentation.

## Contributors
- _Nunzio Marco BISCEGLIA_ — Gran Sasso Science Institute, Italy
- _Elham KARGARI JAM_ — Gran Sasso Science Institute, Italy
- _Gianluca FILIPPONE_ — Gran Sasso Science Institute, Italy
- _Sara PETTINARI_ — Gran Sasso Science Institute, Italy
- _Gian Luca SCOCCIA_ — Gran Sasso Science Institute, Italy
- _Martina DE SANCTIS_ — Gran Sasso Science Institute, Italy