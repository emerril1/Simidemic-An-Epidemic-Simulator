# Simidemic: An Epidemic Simulator

“Simidemic: An Epidemic Simulator” falls within the domain of epidemiology and computational modeling. Specifically, it focuses on simulating infectious disease spread within a controlled, virtual population to study dynamics of transmission and intervention strategies.

Understanding how infectious diseases spread and how intervention strategies can mitigate outbreaks is critical for public health planning not just locally, but globally. However, real-world experimentation is often impractical, unethical, or even highly unfeasible. Therefore, computational simulations are needed that model disease transmission, evaluate infection rates, and assess the effectiveness of intervention strategies in a controlled environment.

The simulation will:
* Model infection dynamics using a compartmental approach (e.g., susceptible, exposed, infected, recovered).
* Track infection rates over time.
* Evaluate the effectiveness of basic intervention strategies (e.g., social distancing, vaccination, quarantine).

The simulation will not:
* Differentiate between types of pathogens such as bacteria, parasites, or fungi.
* Model complex social, environmental, or biological factors beyond random interactions within the population.

By focusing on a simplified virus model, this simulation aims to provide insights into disease propagation and containment strategies, offering a foundation for understanding more complex epidemiological scenarios.

# Installation Instructions

This simulation was developed using Python version 3.13. While this is not the absolute latest release, it was chosen to ensure compatibility with the NetworkX package. NetworkX is supported on Python versions 3.11 and above, making 3.13 a stable and reliable choice for this project.

The latest Python version can always be downloaded from the official Python website: https://www.python.org/downloads/

The NetworkX library is required to generate and manage the population contact graph within the simulation.
* In this project, NetworkX was installed directly through the Visual Studio Code terminal, but it can be installed in any IDE or editor that supports Python.
* If the terminal installation does not work, NetworkX can also be downloaded and unpacked manually.

1.Standard Installation (recommended)

From a terminal or command prompt, run:
- `pip install networkx`

Official installation instructions are available here: https://networkx.org/documentation/stable/install.html

2.Manual Installation (alternative method)

If direct installation fails, the package can be downloaded and installed manually:
* GitHub release page: https://github.com/networkx/networkx/releases
* PyPI package page: https://pypi.python.org/pypi/networkx

This ensures the simulation has all the necessary dependencies to run properly, regardless of environment or editor.

3.Running the Simulation

Once Python and NetworkX are installed:
1. Open a terminal in the project folder.
2. Run the main script:
- `python Simulation.py`
3. The simulation will load the default parameters and produce output directly in the terminal.
4. To run a different scenario or modify settings, edit the JSON parameter file (e.g., config.json) and re-run the command above.

# Usage

All key parameters for the simulator are defined in the config.json file located in the project root. This file allows users to adjust settings such as population size, virus characteristics, intervention strategies, and simulation duration without changing the source code. Each value can be modified to test different outbreak conditions and intervention effects.

Once the configuration file is updated and placed in the correct directory, the simulation can be run from any environment or IDE that supports Python. The simulator will automatically read the configuration, initialize all components, and begin execution.

After completion, several output files are generated automatically. These include:
* timeseries.csv – Daily counts of Susceptible, Exposed, Infected, and Recovered individuals.
* events.csv – Detailed logs of individual transitions, including infection and recovery events.
* summary.json – Key statistics and metadata for the entire simulation run.
* curve.png - Detailed plot curve of each compartmen of the SEIR model.

These files provide a complete record of the simulation’s behavior and can be used for further analysis or reporting.

# Parameter Explanations

Simulation
* duration – Total timesteps the simulation runs.
* initial_infected – Number of starting infected individuals.
* purpose – Label for the scenario (e.g., Baseline).
* params_changed – Notes which parameters differ from defaults.

Population
* size – Number of individuals in the network.
* avg_degree – Average number of connections per person.
* rewire_prob – Probability of creating long-range shortcuts in the Watts–Strogatz network.
* risk_factors – Infection risk multipliers by age group (child, adult, senior).

Virus
* name – Virus identifier.
* infect_rate – Probability of transmission per contact.
* cure_rate – Probability of recovery per timestep.
* infection_time – Fixed number of timesteps someone remains infected.

Interventions
* social_distancing – Reduces contact rate after a start day.
* vaccination – Immunizes a percentage of the population after a start day.
* quarantine – Removes a portion of infected individuals from contact after a start day.