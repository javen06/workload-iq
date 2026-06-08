# workload iq

> AI-assisted onboarding and workload planning for enterprise teams.

---

## Problem

When a new hire joins or a team member is promoted, managers often have no reliable way to estimate how long tasks will take for someone at that experience level. This can lead to overloaded new hires, unrealistic deadlines, and poor handover when staff rotate or leave.

## Solution

workload iq uses historical task completion data — contributed by existing staff over time — to produce transparent, explainable task duration estimates.

These estimates account for:

- role level
- skill profile
- task complexity
- current workload

Managers get a clear overload warning system, while new hires get a realistic and supportive view of their ramp-up expectations.

---

## Features

### Manager Console

- Team workload overview with risk status:
  - Safe
  - Near Capacity
  - Overload Risk
- Summary metrics:
  - team capacity used
  - employees near capacity
  - overload count
- Task assignment simulator:
  - select task type
  - select complexity
  - select required skill
  - select assignee
- Transparent estimate with a human-readable explanation of every multiplier
- Ranked list of recommended assignees by:
  - workload risk
  - skill match
  - remaining capacity

### New Hire Planner

- Employee profile with skill levels and development areas
- Assigned task list with estimated hours and remaining capacity
- Phase-by-phase breakdown for each task type
  - example: Triage → Fix → Test
- Skill-gap guidance with supportive coaching notes when the required skill is below 5/10

### Task Knowledge Base

- Historical average completion times by task type and role level
- Charts:
  - average hours by task type
  - average hours by role level
- Filterable historical completion records
- Explains how senior task history anchors estimates for new hires

---

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- NumPy

No database.  
No external APIs.  
No ML model.

Estimation uses a transparent rule-based heuristic.

---

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/javen06/workload-iq.git
cd workload-iq
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

The app will open at:

```text
http://localhost:8501
```

---

## Project Structure

```text
workload-iq/
├── app.py              # Main Streamlit application
├── streamlit_app.py    # Compatibility shim pointing users to app.py
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## Notes on Simulated Data

All data is generated with:

```python
numpy.random.default_rng(seed=42)
```

This makes the demo data deterministic.

The prototype includes:

- 2 demo manager personas
- 8 simulated employees
- 30 active tasks
- 200 historical completions

None of this data represents any real person or organisation.

---

## Estimation Logic

workload iq uses a transparent heuristic:

```text
estimated_hours =
base_hours[task_type]
× role_multiplier[role_level]
× complexity_multiplier[complexity]
× skill_multiplier(skill_level)
× workload_drag(current_load)
```

### Multipliers

Role multipliers:

```text
New Hire: 1.45×
Junior:   1.20×
Mid:      1.00×
Senior:   0.75×
```

Complexity multipliers:

```text
1 → 0.75×
2 → 0.90×
3 → 1.00×
4 → 1.25×
5 → 1.50×
```

Skill multiplier:

```text
Low skill increases estimated time.
High skill reduces estimated time.
```

Workload drag:

```text
+3% per hour over 30h current load
```

Every estimate is accompanied by a human-readable formula.

There is no black-box model.

---

## Responsible AI Note

This prototype is decision support, not automated employee evaluation.

It is intended to support:

- fair workload planning
- transparent expectations
- onboarding support
- manager judgment

It must not be used as:

- a surveillance tool
- a punitive mechanism
- a replacement for honest conversations between managers and their teams

---

## Future Improvements

- Connect to real project management systems such as Jira, Asana, or Linear
- Allow managers to log actual task completion times to improve estimates over time
- Add role-specific skill taxonomies
- Add multi-team and cross-department workload views
- Add exportable reports for sprint planning or onboarding documentation
- Add persistent storage with a database
- Add proper authentication and role-based access control
