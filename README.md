# workload iq

`workload iq` is a Streamlit prototype for workload planning, task assignment,
and employee onboarding support.

Managers can review team capacity, estimate task effort, identify overload
risk, and assign work. Employees can review active tasks, understand how
estimates are calculated, and complete or release assigned work.

The application uses deterministic simulated data and a transparent rule-based
heuristic. It does not use a machine-learning model, database, or external
service.

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [Using the demo](#using-the-demo)
- [Demo personas](#demo-personas)
- [Workload and risk model](#workload-and-risk-model)
- [Estimation model](#estimation-model)
- [Simulated data](#simulated-data)
- [Session state](#session-state)
- [Project structure](#project-structure)
- [Configuration](#configuration)
- [Development and validation](#development-and-validation)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Responsible use](#responsible-use)

## Features

### Demo access model

The app starts with role and persona selection.

- Manager personas can access team overview, task assignment, and knowledge
  base views.
- Employee personas can access only their own tasks and estimation guidance.
- Manager personas are separate from employee workload data.
- Each manager sees and assigns work only to their own demo team.

This is a demonstration access model. It is not production authentication or
authorization.

### Manager experience

Managers can:

- review team load, capacity, remaining hours, utilisation, and risk;
- see safe, near-capacity, and overload states;
- inspect utilisation using a fixed 0-100% progress display;
- estimate task duration from task type, complexity, role, skill, and load;
- compare projected workload and skill fit across their team;
- assign a pending task to an employee;
- proceed with an assignment even when it creates overload risk;
- receive a visible warning for overload assignments; and
- explore historical completion benchmarks.

Clicking **assign task**:

1. creates a new task ID;
2. adds a pending task to the current session;
3. assigns it to the selected employee;
4. increases the employee's current load;
5. recalculates remaining capacity, utilisation, and risk; and
6. refreshes the app.

### Employee experience

Employees can:

- review current load, weekly capacity, and remaining capacity;
- inspect their skill profile and development areas;
- view pending and in-progress tasks;
- review phase-by-phase task breakdowns;
- receive guidance for tasks involving developing skills;
- mark a selected task as completed; or
- release a selected task.

Completing or releasing a task changes its status, subtracts its estimated
hours from the employee's load, and recalculates capacity and risk.

### Knowledge base

The manager knowledge base includes:

- average completion hours by task type and role level;
- average hours by task type;
- average hours by role level;
- task-type and role-level filters; and
- simulated historical completion records.

## Quick start

### Requirements

- Python 3.10 or newer
- `pip`

Runtime dependencies:

- Streamlit
- pandas
- NumPy

### 1. Clone or open the repository

Clone from GitHub:

```bash
git clone https://github.com/javen06/workload-iq.git
cd workload-iq
```

If the repository is already available locally:

```bash
cd ~/Desktop/code/workload-iq
```

### 2. Create a virtual environment

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Streamlit normally opens a browser automatically. Otherwise, visit:

```text
http://localhost:8501
```

Press `Ctrl+C` in the terminal to stop the server.

Do not use `streamlit_app.py` as the main entrypoint. It is a compatibility
shim that displays the correct launch command.

## Using the demo

### Manager workflow

1. Select `manager`.
2. Select `alice tan` or `david yeo`.
3. Click **continue**.
4. Use **team overview** to inspect the manager's assigned employees.
5. Use **assign task** to estimate and assign work.
6. Use **knowledge base** to explore historical benchmarks.

To assign work:

1. Select a task type.
2. Choose complexity from 1 to 5.
3. Select a priority.
4. Confirm or change the required skill.
5. Select an employee from the manager's team.
6. Review the estimate, recommendation, and projected utilisation.
7. Click **assign task**.

Assignments that produce overload remain allowed because urgent operational
work may still need an owner. The app displays:

```text
assignment allowed, but this creates overload risk
```

### Employee workflow

1. Select `employee`.
2. Select an employee persona.
3. Click **continue**.
4. Review capacity, skills, and active work in **my tasks**.
5. Select an active task.
6. Click **mark selected task completed** or **release selected task**.
7. Open **how estimates work** to inspect the estimation rules.

Use **sign out** to return to persona selection.

## Demo personas

### Managers and teams

| Manager | Managed employees |
| --- | --- |
| alice tan | ben lim, clara ng, evelyn koh, farah aziz |
| david yeo | gary ong, hannah soh, ivan teo, jasmine wu |

Managers do not appear in the employee dataframe and do not contribute to team
capacity.

### Employees

- ben lim
- clara ng
- evelyn koh
- farah aziz
- gary ong
- hannah soh
- ivan teo
- jasmine wu

Initial employee loads deliberately demonstrate all three risk states.

## Workload and risk model

Each employee has:

- current load in hours;
- weekly capacity, currently 40 hours;
- remaining capacity;
- utilisation; and
- risk status.

```text
remaining capacity = weekly capacity - current load
utilisation = current load / weekly capacity
```

Risk thresholds:

| Risk | Rule |
| --- | --- |
| safe | utilisation below 75% |
| near capacity | utilisation from 75% through 95% |
| overload | utilisation above 95% |

Remaining capacity can be negative when load exceeds weekly capacity. When a
task is completed or released, current load is clamped to a minimum of zero.

The initial current load is a demo aggregate. It is not reconstructed from the
generated task list.

## Estimation model

Task duration uses an explainable heuristic:

```text
estimated hours =
base hours
× role multiplier
× complexity multiplier
× skill multiplier
× workload drag
```

The app displays the calculation formula for each estimate.

### Base hours

| Task type | Base hours |
| --- | ---: |
| bug fix | 2.5 |
| feature build | 6.0 |
| data analysis | 4.5 |
| report writing | 3.5 |
| support ticket | 1.5 |
| documentation | 2.5 |

### Role multipliers

| Role level | Multiplier |
| --- | ---: |
| new hire | 1.45 |
| junior | 1.20 |
| mid | 1.00 |
| senior | 0.75 |

### Complexity multipliers

| Complexity | Multiplier |
| --- | ---: |
| 1 | 0.75 |
| 2 | 0.90 |
| 3 | 1.00 |
| 4 | 1.25 |
| 5 | 1.50 |

### Skill multiplier

Skills use a 1-10 scale, with 5 as neutral.

- Below 5: estimated time increases by 20% per level below 5.
- At 5: the multiplier is 1.00.
- Above 5: estimated time decreases by 8% per level above 5.
- The multiplier is constrained to a range of 0.50 to 2.00.

### Workload drag

Employees above 30 hours of current load receive an additional multiplier:

```text
workload drag = 1 + (hours over 30 × 0.03)
```

This adds 3% per assigned hour above 30 hours.

### Assignment ranking

Employees are ranked using projected utilisation with a small skill adjustment:

```text
fit score = projected utilisation - (skill level × 0.01)
```

Lower scores appear first. This ranking is decision support, not an automatic
assignment decision.

## Simulated data

Data generation uses a fixed random seed:

```python
numpy.random.default_rng(42)
```

This makes generated employee profiles, tasks, and history reproducible.

The initial demo includes:

- 2 manager personas;
- 8 employee personas;
- 30 generated tasks; and
- 200 historical completion records.

Initial workload values are seeded separately so the dashboard always
demonstrates safe, near-capacity, and overload conditions.

All names and records are simulated and do not represent real people or
organisations.

## Session state

Mutable data is stored in:

```python
st.session_state.emp_df
st.session_state.task_df
```

Consequences:

- assignments persist across reruns in the current session;
- completed and released statuses persist in the current session;
- signing out does not reset the demo;
- different browser sessions have separate state; and
- restarting Streamlit creates fresh demo data.

There is no database or persistence across server restarts.

To reset the demo, stop Streamlit and launch it again:

```bash
streamlit run app.py
```

## Project structure

```text
workload-iq/
├── .streamlit/
│   └── config.toml       # Native Streamlit theme
├── app.py                # Main application and prototype logic
├── streamlit_app.py      # Compatibility shim
├── requirements.txt      # Runtime dependencies
├── README.md             # Project documentation
└── LICENSE               # Repository licence
```

The single-file `app.py` structure is intentional for the current prototype.

## Configuration

The dark interface uses Streamlit's native theme configuration in
`.streamlit/config.toml`:

```toml
[theme]
base = "dark"
primaryColor = "#60a5fa"
backgroundColor = "#0b0f17"
secondaryBackgroundColor = "#111827"
textColor = "#f9fafb"
font = "sans serif"
```

The app does not load external fonts or images.

## Development and validation

### Check Python syntax

```bash
python -m py_compile app.py streamlit_app.py
```

### Run after making changes

```bash
streamlit run app.py
```

### Recommended manual checks

1. Manager selection contains only `alice tan` and `david yeo`.
2. Employee selection contains only the eight employee personas.
3. Alice and David see different employee teams.
4. Manager metrics and assignment choices use only the current manager's team.
5. Safe, near-capacity, and overload states are visible across the demo.
6. Assigning a task creates a pending task and increases employee load.
7. Completing a task reduces load and marks it completed.
8. Releasing a task reduces load and marks it released.
9. Overload assignments remain possible and display a warning.
10. Tables, progress indicators, and cards remain readable in dark mode.

Before committing changes:

```bash
git status
git diff
```

## Troubleshooting

### `streamlit: command not found`

Activate the virtual environment and reinstall dependencies:

macOS or Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### The shim warning appears

The wrong entrypoint was launched. Use:

```bash
streamlit run app.py
```

### Port 8501 is in use

Choose another port:

```bash
streamlit run app.py --server.port 8502
```

Then open:

```text
http://localhost:8502
```

### Demo changes disappeared

The app stores mutable data only in session state. Data resets when the session
or Streamlit process is recreated.

### Interface changes are not visible

Stop and restart Streamlit. If necessary, clear the Streamlit cache from the
app menu and refresh the browser.

## Limitations

This repository is a prototype. It does not provide:

- real authentication or authorization;
- persistent storage;
- audit logs;
- concurrent editing guarantees;
- integration with project-management systems;
- configurable schedules, leave, or working hours;
- task dependencies;
- confidence intervals;
- a trained prediction model; or
- production-grade employee-data controls.

The initial current load is a seeded demo aggregate rather than the sum of
generated active tasks. Treat it as a planning demonstration, not an accounting
ledger.

## Responsible use

`workload iq` is intended to support:

- transparent workload planning;
- realistic capacity discussions;
- early overload detection;
- employee onboarding and development; and
- informed manager judgement.

It should not be used as:

- an automated performance evaluation system;
- an employee surveillance tool;
- a punitive ranking mechanism;
- a source of employment decisions without human review; or
- a replacement for direct conversations with employees.

Estimates are planning benchmarks, not deadlines or measures of individual
worth.
