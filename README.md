# Optimized Power Flow (OPF) for PV Generation and Voltage Regulation

## Project Description

This project implements an Optimized Power Flow (OPF) model focusing on maximizing photovoltaic (PV) generation while managing overvoltage issues within a power distribution network. The model employs Pyomo, a Python-based, open-source optimization modeling language, to solve the OPF problem, ensuring that PV generation is maximized under the constraints of network voltage limits and other operational conditions.

## Features

- **PV Generation Maximization**: Enhances renewable energy utilization by optimizing the output of PV units within network constraints.
- **Voltage Regulation**: Incorporates voltage constraints to prevent overvoltages, ensuring that the voltage at every node in the distribution network remains within safe and predefined limits.
- **Configuration Parameters**: Allows users to easily adjust key parameters such as PV generation limits, voltage thresholds, and network topology through a simple configuration file.

## Installation

Ensure you have Python 3.6 or later installed on your system. The project depends on several external libraries, which can be installed using pip:
 **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Execute the OPF model from the project root directory:

```bash
python src/main.py
```
## Configuration

The optimization model is highly configurable to adapt to different network scenarios and requirements. Configuration is managed through the config/settings.json file, where you can specify:

- `scaling_factor`, `size`: Load and generation scaling.
- `Sbase`, `V_base`: Base power and voltage for per-unit calculations.
- `PV_threshold`, `PV_pu`: PV generation curtailment limits.
- Additional customizable parameters.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details [here](https://www.gnu.org/licenses/)

## Acknowledgments
