# RAI-TIAGo

This repository contains the implementation and replication package for experiments using RAI to control a TIAGo robot in a ROS 2 Gazebo simulation through natural-language commands.

The agent interprets user instructions and executes robot actions through RAI tools. Both textual and vocal interaction modes are supported.

## Repository Structure

```text
tiago/
├── experiments_logs/
├── prompts/
├── config.toml
├── tiago_agent.py
└── tiago_embodiment.json
```

- `experiments_logs/` — logs collected during the experimental evaluation.
- `prompts/` — natural-language prompts used in the experiments.
- `config.toml` — RAI configuration, including the Ollama model configuration.
- `tiago_agent.py` — main script implementing the RAI agent and TIAGo interaction.
- `tiago_embodiment.json` — embodiment description, capabilities, behaviors, and rules provided to the agent.

## Prerequisites

1. **TIAGo simulation environment**

   Follow the instructions provided by PAL Robotics:

   https://github.com/pal-robotics/tiago_simulation

2. **RAI environment**

   Follow the RAI developer environment setup instructions:

   https://robotecai.github.io/rai/setup/install/#setting-up-developer-environment

3. **Ollama**

   The experiments use locally deployed language models through Ollama. Make sure Ollama is installed and that the model specified in `config.toml` is available locally.

## Configuration

Open a terminal, navigate to the RAI repository, and initialize the RAI environment:

```bash
cd rai/
source setup_shell.sh
cd ..
```

The language model used by the agent can be changed in config.toml under the Ollama configuration section.

Make sure the selected model has already been downloaded with Ollama before running the agent.

For example:

```bash
ollama pull qwen2.5:14b
```

## Running the TIAGo Simulation

In a second terminal, navigate to the TIAGo workspace and source the ROS 2 environment:

```bash
cd tiago_asas_ws/
source install/setup.bash
```

Launch the TIAGo Gazebo simulation with navigation enabled:

```bash
ros2 launch tiago_gazebo tiago_gazebo.launch.py \
    is_public_sim:=True \
    navigation:=True \
    arm_type:=no-arm
```

This launches the Gazebo simulation and RViz.


## Running the RAI Agent

Return to the terminal in which the RAI environment was initialized.

Navigate to the `tiago` directory of this repository and start the agent:

```bash
cd tiago/
python3 tiago_agent.py
```

At startup, select the desired interaction mode:

```text
1 - Text
2 - Voice
```

- `1` enables textual interaction through the terminal.
- `2` enables vocal commands through the configured speech-recognition pipeline.

## Replication Package

The `experiments_logs/` and `prompts/` directories contain the material required to inspect and replicate the experimental evaluation.

### Experimental Models

The following locally deployed Ollama models were evaluated:

- `gpt-oss:20b`
- `llama3.1:8b`
- `mistral-nemo:12b`
- `qwen2.5:7b`
- `qwen2.5:14b`

The model can be selected by modifying the corresponding Ollama configuration in `config.toml`.

### Experimental Prompts

Three natural-language prompts of increasing specificity were evaluated.

The exact prompts used during the experiments are available in the `prompts/` directory.

Each prompt was executed **five times for each model**.

### Simulation Speed

To reduce the wall-clock time required to execute the experiments, the Gazebo simulation was run with an increased real-time factor.

During our experiments, an observed real-time factor of approximately **7.82×** was obtained.

The simulation rate can be configured by modifying:

```text
src/pal_gazebo_worlds/worlds/pal_office.world
```

in the TIAGo workspace.

For our experiments, the following Gazebo physics parameter was used:

```xml
<real_time_update_rate>10000</real_time_update_rate>
```

The same simulation configuration was maintained across all experimental trials.

Note that setting `real_time_update_rate` to `10000` does not imply an exact 10× real-time factor. The effective real-time factor depends on the computational load and hardware performance.

### Experiment Logging

Each experimental run was recorded by redirecting both standard output and standard error to a log file using `tee`.

The general command was:

```bash
python3 -u tiago_agent.py 2>&1 | tee experiments_logs/{model}/T-P{prompt}-{iteration}.txt
```

where:

- `{model}` identifies the evaluated Ollama model;
- `{prompt}` is the prompt identifier (`1`, `2`, or `3`);
- `{iteration}` is the repetition number (`1` to `5`).


For example:

```bash
python3 -u tiago_agent.py 2>&1 | tee experiments_logs/qwen2.5-14b/T-P3-1.txt
```

This command executes the first repetition of Prompt 3 using the model configured in `config.toml` and saves the complete execution trace.

### Experimental Protocol

For each model:

1. Configure the desired Ollama model in `config.toml`.
2. Start the TIAGo Gazebo simulation.
3. Start `tiago_agent.py`.
4. Select text interaction mode.
5. Submit one of the prompts from the `prompts/` directory.
6. Record the interaction using the logging command above.
7. Reset the simulation and restart the agent before the next trial.
8. Repeat each prompt five times.

To ensure comparability across models, the same agent implementation, embodiment configuration, tools, prompts, simulation environment, semantic locations, and experimental procedure were maintained across trials.

## Experiment Overview

With five models, three prompts, and five repetitions per prompt, the replication package contains:

```text
5 models × 3 prompts × 5 repetitions = 75 experimental trials
```

These experiments evaluate the ability of different locally deployed language models to execute multi-step natural-language robotic missions through the same RAI-based agent architecture.

## Contributors
- _Nunzio Marco BISCEGLIA_ — Gran Sasso Science Institute, Italy
- _Elham KARGARI JAM_ — Gran Sasso Science Institute, Italy
- _Gianluca FILIPPONE_ — Gran Sasso Science Institute, Italy
- _Sara PETTINARI_ — Gran Sasso Science Institute, Italy
- _Gian Luca SCOCCIA_ — Gran Sasso Science Institute, Italy
- _Martina DE SANCTIS_ — Gran Sasso Science Institute, Italy