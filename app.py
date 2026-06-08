# app.py - workload iq
# run with: streamlit run app.py

import numpy as np
import pandas as pd
import streamlit as st

# Page config must be the first Streamlit call.
st.set_page_config(
    page_title="workload iq",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimal styling for app-specific HTML. Native Streamlit components inherit the
# coordinated dark theme from .streamlit/config.toml.
st.markdown("""
<style>
html, body, main {
    background: #0b0f17;
    color: #f9fafb;
}
main {
    padding-bottom: 1.5rem;
}
.wordmark {
    color: #94a3b8;
    border-bottom: 1px solid #273244;
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
}
.pill {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.pill-safe { background: #123524; color: #86efac; }
.pill-near { background: #422006; color: #fbbf24; }
.pill-over { background: #450a0a; color: #fca5a5; }
.result-block {
    background: #111827;
    border: 1px solid #273244;
    border-radius: 0.75rem;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
}
.result-block.safe { border-left: 4px solid #22c55e; }
.result-block.near { border-left: 4px solid #f59e0b; }
.result-block.over { border-left: 4px solid #ef4444; }
.section-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}
.mono-note {
    font-family: monospace;
    font-size: 0.8rem;
    color: #cbd5e1;
    background: #151b26;
    border: 1px solid #273244;
    border-radius: 0.5rem;
    padding: 0.65rem 0.8rem;
    margin: 0.75rem 0;
}
.phase-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #273244;
    font-size: 0.85rem;
}
.phase-name { flex: 1; color: #e5e7eb; font-weight: 500; }
.phase-hrs { color: #f9fafb; font-weight: 600; min-width: 40px; text-align: right; }
.phase-pct { color: #94a3b8; min-width: 30px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# constants
# ─────────────────────────────────────────────
ROLE_LEVELS   = ["new hire", "junior", "mid", "senior"]
ROLE_FAMILIES = ["engineering", "data", "support", "product"]
MANAGERS      = {"alice tan": "M01", "david yeo": "M02"}
EMPLOYEE_NAMES = [
    "ben lim", "clara ng", "evelyn koh", "farah aziz",
    "gary ong", "hannah soh", "ivan teo", "jasmine wu",
]
TASK_TYPES    = ["bug fix", "feature build", "data analysis",
                 "report writing", "support ticket", "documentation"]
SKILLS        = ["frontend", "backend", "debugging",
                 "data analysis", "writing", "stakeholder support"]
PRIORITY      = ["low", "medium", "high"]

BASE_HOURS = {
    "bug fix": 2.5, "feature build": 6.0, "data analysis": 4.5,
    "report writing": 3.5, "support ticket": 1.5, "documentation": 2.5,
}
ROLE_MULT = {"new hire": 1.45, "junior": 1.20, "mid": 1.00, "senior": 0.75}
COMP_MULT = {1: 0.75, 2: 0.90, 3: 1.00, 4: 1.25, 5: 1.50}
TASK_SKILL = {
    "bug fix": "debugging", "feature build": "backend",
    "data analysis": "data analysis", "report writing": "writing",
    "support ticket": "stakeholder support", "documentation": "writing",
}
TASK_PHASES = {
    "bug fix":          [("triage", 0.25), ("fix", 0.50), ("verify", 0.25)],
    "feature build":    [("design", 0.20), ("build", 0.55), ("review & test", 0.25)],
    "data analysis":    [("explore", 0.30), ("analyse", 0.50), ("summarise", 0.20)],
    "report writing":   [("draft", 0.50), ("edit", 0.30), ("review", 0.20)],
    "support ticket":   [("diagnose", 0.35), ("respond", 0.45), ("document", 0.20)],
    "documentation":    [("outline", 0.20), ("write", 0.60), ("review", 0.20)],
}


# ─────────────────────────────────────────────
# estimation logic — transparent heuristic
# ─────────────────────────────────────────────
def estimate(task_type: str, complexity: int, role_level: str,
             skill_level: int, current_load: float) -> dict:
    base   = BASE_HOURS[task_type]
    r_m    = ROLE_MULT[role_level]
    c_m    = COMP_MULT[complexity]
    # skill 1–10, neutral at 5
    if skill_level < 5:
        s_m = 1.0 + (5 - skill_level) * 0.20
    else:
        s_m = 1.0 - (skill_level - 5) * 0.08
    s_m = max(0.50, min(s_m, 2.0))
    # drag: +3 % per hour over 30 h already loaded
    d_m  = 1.0 + max(0, current_load - 30) * 0.03
    hrs  = base * r_m * c_m * s_m * d_m
    formula = (
        f"base {base}h  ×  role ({role_level}) {r_m}  ×  "
        f"complexity {c_m}  ×  skill ({skill_level}/10) {s_m:.2f}  ×  "
        f"load drag {d_m:.2f}"
    )
    return {"hours": round(hrs, 1), "formula": formula}


def risk(utilisation: float) -> str:
    if utilisation > 0.95: return "overload"
    if utilisation >= 0.75: return "near"
    return "safe"


def pill(r: str) -> str:
    labels = {"safe": "safe", "near": "near capacity", "overload": "overload"}
    return f'<span class="pill pill-{r}">{labels[r]}</span>'


def recalculate_employee(emp_df: pd.DataFrame, employee_id: str) -> None:
    mask = emp_df["id"] == employee_id
    load = emp_df.loc[mask, "load (h)"].clip(lower=0).round(1)
    capacity = emp_df.loc[mask, "capacity (h)"]
    utilisation = (load / capacity).round(3)
    emp_df.loc[mask, "load (h)"] = load
    emp_df.loc[mask, "remaining (h)"] = (capacity - load).round(1)
    emp_df.loc[mask, "utilisation"] = utilisation
    emp_df.loc[mask, "risk"] = utilisation.apply(risk)


def next_task_id(task_df: pd.DataFrame) -> str:
    numbers = pd.to_numeric(
        task_df["task id"].str.removeprefix("T"),
        errors="coerce",
    )
    return f"T{int(numbers.max()) + 1:03d}"


# ─────────────────────────────────────────────
# demo data — deterministic seed
# ─────────────────────────────────────────────
@st.cache_data
def build_data():
    rng = np.random.default_rng(42)
    demo_loads = [18.0, 31.0, 39.0, 42.0, 27.0, 34.0, 12.0, 37.0]
    emps = []
    for i, name in enumerate(EMPLOYEE_NAMES):
        rl  = rng.choice(ROLE_LEVELS, p=[0.2, 0.3, 0.3, 0.2])
        rf  = rng.choice(ROLE_FAMILIES)
        load = demo_loads[i]
        sk  = {s: int(rng.integers(2, 10)) for s in SKILLS}
        emps.append({"id": f"E{i+1:02d}", "name": name,
                     "role level": rl, "family": rf,
                     "load (h)": load, "capacity (h)": 40.0, **sk})
    emp = pd.DataFrame(emps)
    emp["remaining (h)"] = (emp["capacity (h)"] - emp["load (h)"]).round(1)
    emp["utilisation"]   = (emp["load (h)"] / emp["capacity (h)"]).round(3)
    emp["risk"]          = emp["utilisation"].apply(risk)

    # active tasks
    tasks = []
    for j in range(30):
        e   = emp.sample(1, random_state=int(rng.integers(9999))).iloc[0]
        tt  = rng.choice(TASK_TYPES)
        cp  = int(rng.integers(1, 6))
        sk  = TASK_SKILL[tt]
        sv  = int(e[sk])
        hrs = estimate(tt, cp, e["role level"], sv, e["load (h)"])["hours"]
        tasks.append({
            "task id": f"T{j+1:03d}", "title": f"{tt} #{j+1}",
            "type": tt, "complexity": cp, "required skill": sk,
            "priority": rng.choice(PRIORITY),
            "assigned to": e["id"],
            "status": rng.choice(["pending", "in progress", "completed"], p=[0.4, 0.4, 0.2]),
            "est. hours": hrs,
        })
    task_df = pd.DataFrame(tasks)

    # history
    hist = []
    for _ in range(200):
        e   = emp.sample(1, random_state=int(rng.integers(9999))).iloc[0]
        tt  = rng.choice(TASK_TYPES)
        cp  = int(rng.integers(1, 6))
        sk  = TASK_SKILL[tt]
        sv  = int(e[sk])
        est_h = estimate(tt, cp, e["role level"], sv, float(rng.uniform(5, 35)))["hours"]
        actual = round(max(0.5, est_h * float(rng.normal(1.0, 0.18))), 1)
        hist.append({
            "task type": tt, "complexity": cp, "skill": sk,
            "role level": e["role level"], "actual (h)": actual,
            "family": e["family"], "quality": int(rng.integers(3, 6)),
        })
    hist_df = pd.DataFrame(hist)

    return emp, task_df, hist_df


initial_emp_df, initial_task_df, hist_df = build_data()


# ─────────────────────────────────────────────
# session state — role-based access
# ─────────────────────────────────────────────
if "emp_df" not in st.session_state:
    st.session_state.emp_df = initial_emp_df.copy(deep=True)
if "task_df" not in st.session_state:
    st.session_state.task_df = initial_task_df.copy(deep=True)
if "role" not in st.session_state:
    st.session_state.role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

emp_df = st.session_state.emp_df
task_df = st.session_state.task_df


# ─────────────────────────────────────────────
# login gate
# ─────────────────────────────────────────────
if st.session_state.role is None:
    st.title("workload iq")
    st.caption("select a demo persona")

    role_choice = st.radio("role", ["manager", "employee"], horizontal=True)
    people = list(MANAGERS) if role_choice == "manager" else EMPLOYEE_NAMES
    who = st.selectbox(
        "user",
        people,
        placeholder="select a user",
    )

    if st.button("continue"):
        st.session_state.user_name = who
        st.session_state.role = role_choice
        if role_choice == "manager":
            st.session_state.user_id = MANAGERS[who]
        else:
            emp_row = emp_df[emp_df["name"] == who].iloc[0]
            st.session_state.user_id = emp_row["id"]
        st.rerun()

    st.markdown("""
    <div class="mono-note" style="margin-top:1.5rem">
    demo prototype — no authentication.<br>
    role selection controls which views are shown.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# top bar
# ─────────────────────────────────────────────
top_left, top_right = st.columns([4, 1])
with top_left:
    st.markdown(
        f'<div class="wordmark">workload iq &nbsp;/&nbsp; {st.session_state.user_name} '
        f'&nbsp;·&nbsp; {st.session_state.role}</div>',
        unsafe_allow_html=True
    )
with top_right:
    if st.button("sign out"):
        st.session_state.role      = None
        st.session_state.user_id   = None
        st.session_state.user_name = None
        st.rerun()


# ─────────────────────────────────────────────
# MANAGER VIEW
# ─────────────────────────────────────────────
if st.session_state.role == "manager":

    tab1, tab2, tab3 = st.tabs(["team overview", "assign task", "knowledge base"])

    # ── tab 1: team overview ──────────────────
    with tab1:
        st.markdown("## team overview")
        st.markdown(
            '<div class="section-label">current workload — simulated demo data</div>',
            unsafe_allow_html=True
        )

        total_used = emp_df["load (h)"].sum()
        total_cap  = emp_df["capacity (h)"].sum()
        near_n     = (emp_df["risk"] == "near").sum()
        over_n     = (emp_df["risk"] == "overload").sum()
        avg_rem    = emp_df["remaining (h)"].mean()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("capacity used", f"{total_used/total_cap*100:.0f}%",
                  f"{total_used:.0f} / {total_cap:.0f} h")
        c2.metric("near capacity", int(near_n), help="75–95% utilised")
        c3.metric("overload risk", int(over_n))
        c4.metric("avg remaining", f"{avg_rem:.1f} h")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.subheader("employee workload")

        show = emp_df[[
            "id", "name", "role level", "family",
            "load (h)", "capacity (h)", "remaining (h)", "utilisation", "risk"
        ]].copy()
        show["utilisation"] = (show["utilisation"] * 100).round(1).astype(str) + "%"

        def _risk_color(val):
            if val == "overload": return "color: #fca5a5"
            if val == "near":     return "color: #fbbf24"
            return "color: #86efac"

        st.dataframe(
            show.style.map(_risk_color, subset=["risk"]),
            width="stretch", hide_index=True
        )

        st.subheader("utilisation by employee")
        for _, employee in emp_df.sort_values("utilisation", ascending=False).iterrows():
            name_col, progress_col, status_col = st.columns([2, 5, 2])
            utilisation = float(employee["utilisation"])
            with name_col:
                st.write(employee["name"])
            with progress_col:
                st.progress(min(utilisation, 1.0))
            with status_col:
                st.write(f'{utilisation * 100:.0f}% | {employee["risk"]}')

    # ── tab 2: assign task ────────────────────
    with tab2:
        st.markdown("## assign task")
        if "assignment_message" in st.session_state:
            st.success(st.session_state.pop("assignment_message"))
        st.markdown(
            '<div class="section-label">'
            'estimate duration and check workload impact before assigning'
            '</div>', unsafe_allow_html=True
        )

        col_l, col_r = st.columns([1, 1], gap="large")

        with col_l:
            st.markdown('<div class="section-label">task details</div>', unsafe_allow_html=True)
            sel_type  = st.selectbox("task type", TASK_TYPES)
            sel_comp  = st.slider("complexity", 1, 5, 3,
                                  help="1 = trivial, 5 = highly complex")
            sel_pri   = st.selectbox("priority", PRIORITY, index=1)
            sel_skill = st.selectbox(
                "required skill",
                SKILLS,
                index=SKILLS.index(TASK_SKILL[sel_type])
            )

        with col_r:
            st.markdown('<div class="section-label">potential assignee</div>',
                        unsafe_allow_html=True)
            sel_name = st.selectbox("select employee", emp_df["name"].tolist())
            emp_row  = emp_df[emp_df["name"] == sel_name].iloc[0]

            # show quick profile
            st.markdown(f"""
            <div class="result-block">
              <div class="section-label">{sel_name}</div>
              <div style="font-size:12px; color:#94a3b8; margin-top:4px">
                {emp_row['role level']} &nbsp;·&nbsp; {emp_row['family']}
              </div>
              <div style="font-size:12px; margin-top:8px">
                current load &nbsp;<strong>{emp_row['load (h)']}h</strong>
                &nbsp;of&nbsp;
                <strong>{emp_row['capacity (h)']}h</strong>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        sv      = int(emp_row[sel_skill])
        result  = estimate(sel_type, sel_comp, emp_row["role level"],
                           sv, emp_row["load (h)"])
        est_h   = result["hours"]
        proj    = emp_row["load (h)"] + est_h
        util_a  = proj / emp_row["capacity (h)"]
        rem_a   = emp_row["capacity (h)"] - proj
        r       = risk(util_a)

        risk_css = {"safe": "safe", "near": "near", "overload": "over"}
        rec_text = {
            "safe":     "assign",
            "near":     "assign — monitor closely",
            "overload": "assign only if operationally necessary",
        }

        # find best alternative
        cands = emp_df[emp_df["name"] != sel_name].copy()
        cands["proj"]   = cands["load (h)"] + est_h
        cands["util_p"] = cands["proj"] / cands["capacity (h)"]
        cands["score"]  = cands["util_p"] - cands[sel_skill].astype(int) * 0.01
        best_alt        = cands.sort_values("score").iloc[0]

        st.markdown(f"""
        <div class="result-block {risk_css[r]}">
          <div style="display:flex; justify-content:space-between; align-items:center">
            <div>
              <div class="section-label">recommendation</div>
              <div style="font-size:15px; font-weight:500; margin-top:4px">{rec_text[r]}</div>
            </div>
            {pill(r)}
          </div>
          <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-top:1rem">
            <div><div class="section-label">estimate</div><strong>{est_h}h</strong></div>
            <div><div class="section-label">projected load</div><strong>{proj:.1f}h</strong></div>
            <div><div class="section-label">remaining after</div><strong>{rem_a:.1f}h</strong></div>
            <div><div class="section-label">utilisation after</div><strong>{util_a*100:.0f}%</strong></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if r == "overload":
            st.warning("assignment allowed, but this creates overload risk")
            st.markdown(
                f'<div class="mono-note">'
                f'suggested alternative: <strong>{best_alt["name"]}</strong> — '
                f'{best_alt["role level"]} &nbsp;·&nbsp; '
                f'{TASK_SKILL[sel_type]} skill {int(best_alt[sel_skill])}/10 &nbsp;·&nbsp; '
                f'{best_alt["remaining (h)"]:.1f}h remaining'
                f'</div>',
                unsafe_allow_html=True
            )

        if st.button("assign task", type="primary"):
            task_id = next_task_id(task_df)
            new_task = pd.DataFrame([{
                "task id": task_id,
                "title": f"{sel_type} #{task_id[1:]}",
                "type": sel_type,
                "complexity": sel_comp,
                "required skill": sel_skill,
                "priority": sel_pri,
                "assigned to": emp_row["id"],
                "status": "pending",
                "est. hours": est_h,
            }])
            st.session_state.task_df = pd.concat(
                [task_df, new_task],
                ignore_index=True,
            )
            employee_mask = st.session_state.emp_df["id"] == emp_row["id"]
            st.session_state.emp_df.loc[employee_mask, "load (h)"] += est_h
            recalculate_employee(st.session_state.emp_df, emp_row["id"])
            st.session_state.assignment_message = (
                f"{task_id} assigned to {sel_name}. "
                f"new load: {proj:.1f}h"
            )
            st.rerun()

        with st.expander("how this estimate was calculated"):
            st.markdown(
                f'<div class="mono-note">{result["formula"]}</div>',
                unsafe_allow_html=True
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ranked alternatives
        st.markdown('<div class="section-label">all employees — ranked by fit</div>',
                    unsafe_allow_html=True)
        st.subheader("assignment ranking - lowest projected risk first")

        ranked = emp_df.copy()
        ranked["proj load"]    = (ranked["load (h)"] + est_h).round(1)
        ranked["util after"]   = (ranked["proj load"] / ranked["capacity (h)"]).round(3)
        ranked["rem after"]    = (ranked["capacity (h)"] - ranked["proj load"]).round(1)
        ranked["risk after"]   = ranked["util after"].apply(risk)
        ranked["skill match"]  = ranked[sel_skill].astype(int)
        ranked["fit score"]    = ranked["util after"] - ranked["skill match"] * 0.01
        ranked = ranked.sort_values("fit score")[[
            "name", "role level", "skill match", "proj load", "rem after", "util after", "risk after"
        ]].copy()
        ranked["util after"] = (ranked["util after"] * 100).round(1).astype(str) + "%"
        ranked = ranked.reset_index(drop=True)
        ranked.index += 1

        st.dataframe(
            ranked.style.map(_risk_color, subset=["risk after"]),
            width="stretch"
        )

    # ── tab 3: knowledge base ─────────────────
    with tab3:
        st.markdown("## knowledge base")
        st.markdown(
            '<div class="section-label">'
            'historical completion benchmarks from past tasks — simulated demo data'
            '</div>', unsafe_allow_html=True
        )

        st.markdown("""
        <div class="mono-note">
        when experienced staff complete tasks, their actual durations become institutional memory.
        new hires are estimated with a role multiplier (1.45×) — not expected to match senior pace from day one.
        </div>
        """, unsafe_allow_html=True)

        # pivot: avg actual hours by task type × role level
        pivot = (
            hist_df.groupby(["task type", "role level"])["actual (h)"]
            .mean().round(1).unstack("role level")
        )
        ordered = [c for c in ROLE_LEVELS if c in pivot.columns]
        pivot = pivot[ordered]

        st.subheader("average hours by task type and role level")
        st.dataframe(
            pivot.style.format("{:.1f}", na_rep="—")
                 .highlight_min(axis=1, color="#123524")
                 .highlight_max(axis=1, color="#450a0a"),
            width="stretch"
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("average hours by task type")
            by_type = (
                hist_df.groupby("task type")["actual (h)"].mean().round(1)
                .sort_values(ascending=False).reset_index()
                .rename(columns={"actual (h)": "avg hours"})
                .set_index("task type")
            )
            st.bar_chart(by_type, height=220)

        with col_b:
            st.subheader("average hours by role level")
            by_role = (
                hist_df.groupby("role level")["actual (h)"].mean().round(1)
                .reindex(ROLE_LEVELS).reset_index()
                .rename(columns={"actual (h)": "avg hours"})
                .set_index("role level")
            )
            st.bar_chart(by_role, height=220)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-label">raw records</div>', unsafe_allow_html=True)
        f_tt = st.multiselect("filter by task type", TASK_TYPES, default=TASK_TYPES)
        f_rl = st.multiselect("filter by role level", ROLE_LEVELS, default=ROLE_LEVELS)
        filtered = hist_df[
            hist_df["task type"].isin(f_tt) & hist_df["role level"].isin(f_rl)
        ]
        st.subheader(f"completion records - {len(filtered)} rows")
        st.dataframe(filtered, width="stretch", hide_index=True)

        st.markdown(
            '<div class="mono-note" style="margin-top:1.5rem">'
            'this prototype uses decision support, not automated evaluation. '
            'estimates support fair planning and manager judgement — not surveillance.'
            '</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────
# EMPLOYEE VIEW
# ─────────────────────────────────────────────
else:
    uid   = st.session_state.user_id
    uname = st.session_state.user_name
    me    = emp_df[emp_df["id"] == uid].iloc[0]

    tab1, tab2 = st.tabs(["my tasks", "how estimates work"])

    # ── tab 1: my tasks ───────────────────────
    with tab1:
        st.markdown(f"## {uname}")
        if "task_update_message" in st.session_state:
            st.success(st.session_state.pop("task_update_message"))
        st.markdown(
            f'<div class="section-label">'
            f'{me["role level"]} &nbsp;·&nbsp; {me["family"]}'
            f'</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("current load", f"{me['load (h)']:.1f}h")
        c2.metric("weekly capacity", f"{me['capacity (h)']:.1f}h")
        c3.metric("remaining", f"{me['remaining (h)']:.1f}h")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">skill profile</div>', unsafe_allow_html=True)
        st.subheader("skills - 1 to 10")
        skill_chart = pd.DataFrame({
            "skill": [s.title() for s in SKILLS],
            "level": [int(me[s]) for s in SKILLS]
        }).set_index("skill")
        st.bar_chart(skill_chart, height=180)

        # top/dev areas
        skdf = pd.Series({s: int(me[s]) for s in SKILLS})
        top2 = skdf.nlargest(2).index.tolist()
        dev2 = skdf.nsmallest(2).index.tolist()
        st.markdown(
            f'<div class="mono-note">'
            f'strengths: {", ".join(top2)}&nbsp;&nbsp;·&nbsp;&nbsp;'
            f'development areas: {", ".join(dev2)}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # assigned tasks
        my_tasks = task_df[
            (task_df["assigned to"] == uid) &
            (task_df["status"].isin(["pending", "in progress"]))
        ].copy()

        st.markdown('<div class="section-label">active tasks</div>', unsafe_allow_html=True)

        if my_tasks.empty:
            st.markdown(
                '<div class="mono-note">no active tasks assigned to you.</div>',
                unsafe_allow_html=True
            )
        else:
            total_est = my_tasks["est. hours"].sum()
            rem       = me["remaining (h)"]

            ta1, ta2 = st.columns(2)
            ta1.metric("total assigned", f"{total_est:.1f}h")
            ta2.metric("remaining capacity", f"{rem:.1f}h")

            if total_est > rem:
                st.markdown(
                    '<div class="mono-note" style="border-left:3px solid #ff3b30">'
                    'assigned hours exceed remaining capacity — flag this with your manager.'
                    '</div>', unsafe_allow_html=True
                )

            st.subheader("assigned tasks")
            st.dataframe(
                my_tasks[["task id", "title", "type", "complexity",
                           "required skill", "priority", "status", "est. hours"]],
                width="stretch", hide_index=True
            )

            selected_task_id = st.selectbox(
                "selected task",
                my_tasks["task id"].tolist(),
                format_func=lambda task_id: (
                    f'{task_id} | '
                    f'{my_tasks.loc[my_tasks["task id"] == task_id, "title"].iloc[0]}'
                ),
            )
            complete_col, release_col = st.columns(2)

            def update_selected_task(new_status: str) -> None:
                task_mask = st.session_state.task_df["task id"] == selected_task_id
                task_hours = float(
                    st.session_state.task_df.loc[task_mask, "est. hours"].iloc[0]
                )
                st.session_state.task_df.loc[task_mask, "status"] = new_status
                employee_mask = st.session_state.emp_df["id"] == uid
                st.session_state.emp_df.loc[employee_mask, "load (h)"] -= task_hours
                recalculate_employee(st.session_state.emp_df, uid)
                st.session_state.task_update_message = (
                    f"{selected_task_id} marked {new_status}. "
                    f"{task_hours:.1f}h removed from your load."
                )

            with complete_col:
                if st.button("mark selected task completed", width="stretch"):
                    update_selected_task("completed")
                    st.rerun()
            with release_col:
                if st.button("release selected task", width="stretch"):
                    update_selected_task("released")
                    st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">task breakdown</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="mono-note">each task type has typical phases. '
                'use these as checkpoints.</div>',
                unsafe_allow_html=True
            )

            for _, row in my_tasks.iterrows():
                phases   = TASK_PHASES[row["type"]]
                req_sk   = row["required skill"]
                sk_val   = int(me[req_sk])

                with st.expander(f'{row["title"]} — {row["est. hours"]}h'):
                    # phase rows via HTML for cleaner look
                    phase_html = ""
                    for ph, pct in phases:
                        h = round(row["est. hours"] * pct, 1)
                        phase_html += (
                            f'<div class="phase-row">'
                            f'<span class="phase-name">{ph}</span>'
                            f'<span class="phase-pct">{int(pct*100)}%</span>'
                            f'<span class="phase-hrs">{h}h</span>'
                            f'</div>'
                        )
                    st.markdown(phase_html, unsafe_allow_html=True)

                    if sk_val < 5:
                        st.markdown(
                            f'<div class="mono-note" style="margin-top:0.75rem; border-left:3px solid #ff9f0a">'
                            f'{req_sk} skill: {sk_val}/10 — '
                            f'consider pairing with a senior colleague for this task. '
                            f'break it into smaller checkpoints and check in after each phase. '
                            f'the estimate already accounts for your current level.'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    elif sk_val >= 8:
                        st.markdown(
                            f'<div class="mono-note" style="border-left:3px solid #30d158">'
                            f'{req_sk} skill: {sk_val}/10 — well positioned for this task.'
                            f'</div>',
                            unsafe_allow_html=True
                        )

    # ── tab 2: how estimates work ─────────────
    with tab2:
        st.markdown("## how estimates work")
        st.markdown(
            '<div class="section-label">no black-box model — every estimate is explainable</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="mono-note">
        estimated hours  =  base hours  ×  role multiplier  ×  complexity  ×  skill level  ×  load drag
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-label">base hours by task type</div>',
                        unsafe_allow_html=True)
            base_df = pd.DataFrame(
                list(BASE_HOURS.items()), columns=["task type", "base hours"]
            )
            st.dataframe(base_df, width="stretch", hide_index=True)

            st.markdown('<div class="section-label" style="margin-top:1rem">role multipliers</div>',
                        unsafe_allow_html=True)
            role_df = pd.DataFrame(
                list(ROLE_MULT.items()), columns=["role level", "multiplier"]
            )
            st.dataframe(role_df, width="stretch", hide_index=True)

        with col_r:
            st.markdown('<div class="section-label">complexity multipliers</div>',
                        unsafe_allow_html=True)
            comp_df = pd.DataFrame(
                list(COMP_MULT.items()), columns=["complexity (1–5)", "multiplier"]
            )
            st.dataframe(comp_df, width="stretch", hide_index=True)

            st.markdown(
                '<div class="section-label" style="margin-top:1rem">skill multiplier logic</div>',
                unsafe_allow_html=True
            )
            st.markdown("""
            <div class="mono-note">
            skill 1–4 : adds up to +80% (lower skill → more time)<br>
            skill 5   : neutral, ×1.0<br>
            skill 6–10: reduces by up to −40% (higher skill → less time)<br><br>
            load drag : +3% per hour over 30h already assigned
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<div class="mono-note">'
            'estimates are benchmarks, not targets. '
            'if a task takes significantly longer, that is useful signal — '
            'flag it so the team can refine future estimates.'
            '</div>',
            unsafe_allow_html=True
        )
