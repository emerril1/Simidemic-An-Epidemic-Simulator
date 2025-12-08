import os, time, json, csv
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt

from Population import Population
from Virus import Virus
from Intervention import Intervention
from EnumeratedTypes import State

class Simulation:
    """ Runs the epidemic simulation, logs all data, and exports summary statistics."""

    RESULTS_DIR = "Simulator/results/"

    def __init__(self, config):
        """ Initialize the simulation and all subsystems."""

        self.config = config
        os.makedirs(self.RESULTS_DIR, exist_ok = True)

        # Extracts and validates config file parameters
        sim_cfg = config.get("simulation", {})
        virus_cfg = config.get("virus", {})
        pop_cfg = config.get("population", {})

        self.duration = sim_cfg.get("duration", 60)
        self.purpose = sim_cfg.get("purpose", "Baseline")
        self.params_changed = sim_cfg.get("params_changed", "All defaults")

        # Creates a unique Run ID
        self.run_id = self.get_next_run_id()

        # Initializes the Virus, Population, and Intervention parameters from the config
        self.virus = Virus(
            name = virus_cfg.get("name", "T-Virus"),
            infect_rate = virus_cfg.get("infect_rate", 0.7),
            cure_rate = virus_cfg.get("cure_rate", 0.05),
            infection_time = virus_cfg.get("infection_time", 2),
        )
        self.population = Population(
            size = pop_cfg.get("size", 100),
            avg_degree = pop_cfg.get("avg_degree", 6),
            rewire_prob = pop_cfg.get("rewire_prob", 0.1),
            risk_factors = pop_cfg.get("risk_factors", {}),
        )
        self.intervention = Intervention(self.population, config)

        # Runtime tracking utilities
        self.history, self.event_log = [], []
        self.runtime_ms = 0.0

    @classmethod
    def get_next_run_id(cls):
        """ Generate the next run ID based on previous log entries."""

        os.makedirs(cls.RESULTS_DIR, exist_ok=True)
        log_file = os.path.join(cls.RESULTS_DIR, "log.csv")
        if not os.path.exists(log_file):
            return "001"

        with open(log_file, "r", newline = "") as f:
            rows = list(csv.reader(f))
            last = next((r for r in reversed(rows) if r and r[0].isdigit()), None)
            return f"{int(last[0]) + 1:03d}" if last else "001"

    def run(self):
        """ Execute the full simulation across the configured duration."""

        # Start simulation runtime tracking
        start = time.time()

        # Infects patient zero
        if not self.population.population:
            raise RuntimeError("Population is empty — cannot start simulation.")
        self.population.population[0].state = State.INFECTED

        for day in range(1, self.duration + 1):
            self.simulate_day(day)

        # Converts runtime to ms
        self.runtime_ms = (time.time() - start) * 1000

        # Export data, log run, and plot results
        summary_file, config_file = self.export_run_data()
        self.log_run(summary_file)
        self.plot_curve(f"{self.RESULTS_DIR}run_{self.run_id}_curve.png")

    def simulate_day(self, day):
        """ Simulate a single day of spread, interventions, and transitions."""

        prev_states = [p.state for p in self.population.population]

        # Apply interventions and update states
        self.intervention.apply_vaccine(day)
        self.intervention.apply_social_distancing(day)
        self.intervention.apply_quarantine(day)
        self.population.update(self.virus, day)

        # Record daily totals
        counts = Counter(p.state for p in self.population.population)
        ordered = {s.name[0]: counts.get(s, 0) for s in State}
        self.history.append(ordered)

        # Track state changes
        for i, person in enumerate(self.population.population):
            old, new = prev_states[i], person.state
            if old != new:
                self.event_log.append({
                    "day": day,
                    "PersonID": getattr(person, "id", i),
                    "Age": getattr(person, "age", "Unknown"),
                    "AgeGroup": getattr(person, "age_group", "Unknown"),
                    "Event": f"{old.name} → {new.name}"
                })

    def export_run_data(self):
        """ Export timeseries, events, summary, and config data."""

        base = os.path.join(self.RESULTS_DIR, f"run_{self.run_id}")
        files = {
            "timeseries": f"{base}_timeseries.csv",
            "events": f"{base}_events.csv",
            "summary": f"{base}_summary.json",
            "config": f"{base}_config.json",
        }

        # Create timeseries CSV
        with open(files["timeseries"], "w", newline = "") as f:
            writer = csv.writer(f)
            writer.writerow(["Day", "Susceptible", "Exposed", "Infected", "Recovered"])
            for day, c in enumerate(self.history, 1):
                writer.writerow([day, c["S"], c["E"], c["I"], c["R"]])

        # Creates events CSV
        with open(files["events"], "w", newline = "", encoding = "utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Day", "PersonID", "Age", "AgeGroup", "Event"])
            for ev in self.event_log:
                writer.writerow([
                    ev.get("day", ""), ev.get("PersonID", ""), ev.get("Age", ""),
                    ev.get("AgeGroup", ""), ev.get("Event", "")
                ])

        # Calculates various metrics
        final_counts = self.history[-1] if self.history else {"S": 0, "E": 0, "I": 0, "R": 0}
        total_counts = {k: sum(day[k] for day in self.history) for k in final_counts}
        avg_counts = {k: sum(day[k] for day in self.history) / self.duration for k in final_counts}
        throughput = total_counts["I"] / self.runtime_ms if self.runtime_ms > 0 else 0
        age_dist = Counter(p.age_group for p in self.population.population)

        # Creates summary JSON
        summary = {
            "RunID": self.run_id,
            "Purpose": self.purpose,
            "ParametersChanged": self.params_changed,
            "Virus": self.virus.name,
            "PopulationSize": len(self.population.population),
            "DurationDays": self.duration,
            "Runtime_ms": round(self.runtime_ms, 4),
            "Timestamp": datetime.now().isoformat(),
            "FinalState": final_counts,
            "TotalCounts": total_counts,
            "AvgCounts": avg_counts,
            "Throughput": round(throughput, 4),
            "AgeDistribution": dict(age_dist)
        }
        with open(files["summary"], "w") as f:
            json.dump(summary, f, indent = 4)

        # Crestes config JSON
        with open(files["config"], "w") as f:
            json.dump(self.config, f, indent = 4)

        print("Data exported:")
        for name, path in files.items():
            print(f"   ├─ {path}")
        return files["summary"], files["config"]

    def log_run(self, summary_file):
        """ Append this run to the cumulative results log."""

        log_file = os.path.join(self.RESULTS_DIR, "log.csv")
        new_file = not os.path.exists(log_file)
        with open(log_file, "a", newline = "") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["Run ID", "Purpose", "Parameters Changed", "Duration (ms)", "Data File"])
            writer.writerow([self.run_id, self.purpose, self.params_changed, round(self.runtime_ms, 4), summary_file])
        print(f"Logged Run {self.run_id} → {log_file}")

    def plot_curve(self, save_path = None):
        """ Plot epidemic curve and optionally save to file."""

        if not self.history:
            print("Warning: No history to plot.")
            return

        days = range(1, len(self.history) + 1)
        S, E, I, R = ([h[k] for h in self.history] for k in ["S", "E", "I", "R"])

        plt.figure(figsize = (10, 6))
        plt.plot(days, S, label = "Susceptible")
        plt.plot(days, E, label = "Exposed")
        plt.plot(days, I, label = "Infected")
        plt.plot(days, R, label = "Recovered")
        plt.title(f"Epidemic Simulation: {self.virus.name}")
        plt.xlabel("Day")
        plt.ylabel("Individuals")
        plt.legend()
        plt.grid(True)

        # Saves figure to results path
        if save_path:
            plt.savefig(save_path)
            print(f"Figure saved → {save_path}")
        plt.close()

if __name__ == "__main__":
    """ Load config, create a Simulation, and run it."""

    # Safely open config file and start simulation
    try:
        with open("Simulator/config.json") as f:
            config = json.load(f)
        sim = Simulation(config)
        sim.run()
    except FileNotFoundError:
        print("Error: Config file not found: 'config.json'")
    except json.JSONDecodeError:
        print("Error: Config file is not valid JSON.")
    except Exception as e:
        print(f"Error: Simulation failed: {e}")