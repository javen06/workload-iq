# Workload IQ

Workload IQ is a Streamlit prototype for transparent workload planning, task
estimation, capacity tracking, and employee assignment.

It helps managers estimate task effort, identify overload risk, compare
potential assignees, and understand how new work affects team capacity.
Employees can review assigned work, inspect how estimates are calculated, and
complete or release tasks.

The project is designed as a decision-support tool, not an employee monitoring
or automated performance-evaluation system.

**Live app:** [workload-iq.streamlit.app](https://workload-iq.streamlit.app/)

**Repository:** [github.com/javen06/workload-iq](https://github.com/javen06/workload-iq)

## Features

- Manager and employee demo perspectives
- Team capacity, remaining hours, utilisation, and risk indicators
- Explainable task-duration estimates
- Assignment recommendations and projected workload impact
- Ranked employee comparisons based on capacity and skill fit
- Visible warnings for assignments that create overload risk
- Employee task completion and release workflow
- Phase-by-phase task breakdowns
- Simulated historical completion benchmarks
- Deterministic fictional demo data
- Dark Streamlit interface
- No database, external APIs, or production employee data

## Problem

Task knowledge is often transferred informally, making effort estimates
inconsistent and onboarding expectations unrealistic. Managers may also assign
work without a clear view of current capacity or the effect of another task.

Workload IQ explores a transparent planning workflow:

1. Describe the task and its required skill.
2. Estimate effort using visible rules.
3. Compare the estimate against employee capacity.
4. Review projected utilisation and overload risk.
5. Assign work while keeping human judgement in control.

## Demo Workflows

### Manager View

Managers can:

- review their team's current workload and remaining capacity;
- inspect safe, near-capacity, and overload states;
- estimate a task using type, complexity, role, skill, and current load;
- compare projected workload across potential assignees;
- assign a task and immediately update the employee's load;
- proceed with an overload assignment when operationally necessary; and
- explore simulated historical completion benchmarks.

Each demo manager sees only their assigned team.

### Employee View

Employees can:

- review current load, weekly capacity, and remaining hours;
- inspect their skill profile and development areas;
- view pending and in-progress tasks;
- review phase-by-phase task breakdowns;
- receive guidance for tasks involving developing skills;
- mark a task as completed; or
- release an assigned task.

Completing or releasing a task removes its estimated hours from the employee's
current load and recalculates capacity and risk.

## Estimation Model

Workload IQ uses an explainable rule-based heuristic rather than a trained
machine-learning model:

```text
estimated hours =
base hours
× role multiplier
× complexity multiplier
× skill multiplier
× workload drag
```

The estimate considers:

- task type;
- complexity from 1 to 5;
- employee role level;
- relevant skill level from 1 to 10; and
- current assigned workload.

The complete formula is visible in the manager interface for every estimate.

### Workload Drag

Employees with more than 30 assigned hours receive an additional multiplier:

```text
workload drag = 1 + (hours above 30 × 0.03)
```

This represents the effect of reduced available capacity. It is a planning
heuristic, not a productivity score.

### Risk Levels

| Status | Utilisation |
| --- | ---: |
| Safe | Below 75% |
| Near capacity | 75% to 95% |
| Overload | Above 95% |

### Assignment Ranking

Potential assignees are ordered using projected utilisation with a small skill
adjustment:

```text
fit score = projected utilisation - (skill level × 0.01)
```

Lower scores appear first. The ranking supports a manager's decision; it does
not assign work automatically.

## Historical Benchmarks

The knowledge-base view contains simulated historical completion records. It
shows:

- average completion hours by task type and role level;
- average hours by task type;
- average hours by role level;
- filterable raw completion records; and
- comparisons between new-hire and experienced-role benchmarks.

These records provide context for workload conversations. They are not
currently used as training data or direct inputs to the estimation formula.

## Demo Data

The app generates reproducible fictional data using:

```python
numpy.random.default_rng(42)
```

The demo includes:

- 2 manager personas;
- 8 employee personas;
- 30 generated tasks; and
- 200 historical completion records.

Initial workloads are deliberately chosen to demonstrate safe, near-capacity,
and overload conditions. No names or records represent real people or
organisations.

## Session State

Assignments and task updates are stored in Streamlit session state.

This means:

- changes persist across reruns within the current browser session;
- separate browser sessions have separate state;
- signing out does not reset the current session data; and
- restarting the Streamlit process restores the original demo data.

There is no persistent database.

## Responsible Use

Workload IQ is intended to support:

- realistic workload conversations;
- transparent capacity planning;
- early overload detection;
- employee onboarding and development; and
- informed manager judgement.

It should not be used for:

- automated performance evaluation;
- employee surveillance;
- punitive ranking;
- employment decisions without human review; or
- replacing direct conversations with employees.

Estimates are planning benchmarks, not deadlines or measures of individual
worth.

## Tech Stack

- Python
- Streamlit
- pandas
- NumPy

No external APIs, databases, or machine-learning services are required.

## Run Locally

### Requirements

- Python 3.10 or newer
- `pip`

### Installation

```bash
git clone https://github.com/javen06/workload-iq.git
cd workload-iq
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Start the App

```bash
streamlit run app.py
```

Streamlit normally opens the app automatically. Otherwise, visit:

```text
http://localhost:8501
```

`streamlit_app.py` is a compatibility shim that displays the correct launch
command. The main application entrypoint is `app.py`.

## Project Structure

```text
workload-iq/
├── .streamlit/
│   └── config.toml
├── app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── LICENSE
```

- `app.py` contains the interface, demo data, estimation logic, and session
  workflows.
- `.streamlit/config.toml` defines the native dark theme.
- `streamlit_app.py` is a compatibility entrypoint notice.
- `requirements.txt` contains the runtime dependencies.

## Validation

Check both Python entrypoints for syntax errors:

```bash
python -m py_compile app.py streamlit_app.py
```

Run the complete interface:

```bash
streamlit run app.py
```

Recommended manual checks:

1. Manager and employee persona selection works.
2. Each manager sees only their assigned team.
3. Task estimates update when task or employee inputs change.
4. Assigning work updates employee load and risk.
5. Completing or releasing a task reduces employee load.
6. Overload assignments remain possible and show a warning.
7. Historical benchmark tables and filters render correctly.

## Deployment

The app is deployed on Streamlit Community Cloud:

[https://workload-iq.streamlit.app/](https://workload-iq.streamlit.app/)

Deployment configuration:

```text
Repository: javen06/workload-iq
Branch: main
Main file path: app.py
```

No environment variables or external services are required.

## Current Limitations

- All employee, task, and history data is simulated.
- The estimator is a simplified rule-based heuristic.
- Role selection is a demo access model, not authentication.
- Data does not persist across Streamlit process restarts.
- There are no audit logs or concurrent-editing guarantees.
- The app does not account for leave, schedules, task dependencies, or
  confidence intervals.
- It is a planning prototype, not a production workforce-management system.
