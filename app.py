# app.py — workload iq
# run with: streamlit run app.py

import numpy as np
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────
# page config — must be first st call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="workload iq",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# global css — apple-adjacent: neutral, tight, rounded, small type
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@300;400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: #1a1a1a;
    background: #f5f5f7;
}

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem 2.5rem; max-width: 1200px; }

/* page wordmark */
.wordmark {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: lowercase;
    color: #6e6e73;
    margin-bottom: 2rem;
    border-bottom: 1px solid #e0e0e5;
    padding-bottom: 0.75rem;
}

/* section headers */
h1, h2, h3 { font-family: 'DM Sans', sans-serif; font-weight: 500; letter-spacing: -0.01em; }
h1 { font-size: 22px; color: #1d1d1f; }
h2 { font-size: 15px; color: #1d1d1f; }
h3 { font-size: 13px; color: #3a3a3c; }

/* metric cards */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e0e0e5;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] > div:first-child { font-size: 10px; letter-spacing: 0.08em; text-transform: lowercase; color: #6e6e73; }
[data-testid="metric-container"] > div:nth-child(2) { font-size: 22px; font-weight: 500; color: #1d1d1f; }

/* tab strip */
[data-baseweb="tab-list"] {
    background: #e8e8ed;
    border-radius: 10px;
    padding: 3px;
    gap: 2px;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: lowercase !important;
    letter-spacing: 0.04em !important;
    color: #6e6e73 !important;
    padding: 6px 16px !important;
}
[aria-selected="true"] {
    background: #ffffff !important;
    color: #1d1d1f !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10) !important;
}
[data-baseweb="tab-highlight"] { display: none !important; }
[data-baseweb="tab-border"] { display: none !important; }

/* data panel — the "code block" treatment for tables/charts */
.data-panel {
    background: #1d1d1f;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0 1.5rem 0;
    border: 1px solid #2d2d2f;
}
.data-panel-header {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: lowercase;
    color: #6e6e73;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2d2d2f;
}
.data-panel table { color: #f5f5f7; }

/* dataframe override — dark */
[data-testid="stDataFrame"] {
    background: #1d1d1f !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #2d2d2f !important;
}

/* inputs / selects */
[data-baseweb="select"] > div, [data-baseweb="input"] > div {
    border-radius: 8px !important;
    border-color: #d0d0d5 !important;
    background: #ffffff !important;
    font-size: 12px !important;
}
[data-baseweb="slider"] { padding: 0 !important; }

/* buttons */
[data-testid="stButton"] button {
    border-radius: 8px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: lowercase;
    background: #1d1d1f;
    color: #f5f5f7;
    border: none;
    padding: 0.4rem 1.2rem;
    transition: opacity 0.15s;
}
[data-testid="stButton"] button:hover { opacity: 0.8; }

/* pills for risk status */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: lowercase;
}
.pill-safe   { background: #d4edda; color: #155724; }
.pill-near   { background: #fff3cd; color: #856404; }
.pill-over   { background: #f8d7da; color: #721c24; }

/* expander */
[data-testid="stExpander"] {
    border: 1px solid #e0e0e5 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}

/* result block */
.result-block {
    background: #ffffff;
    border: 1px solid #e0e0e5;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.result-block.safe   { border-left: 3px solid #34c759; }
.result-block.near   { border-left: 3px solid #ff9f0a; }
.result-block.over   { border-left: 3px solid #ff3b30; }

/* login screen */
.login-wrap {
    max-width: 360px;
    margin: 5rem auto;
    background: #ffffff;
    border: 1px solid #e0e0e5;
    border-radius: 16px;
    padding: 2.5rem;
}
.login-title {
    font-size: 18px;
    font-weight: 500;
    color: #1d1d1f;
    margin-bottom: 0.25rem;
}
.login-sub {
    font-size: 11px;
    color: #6e6e73;
    margin-bottom: 2rem;
}

/* section label */
.section-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.10em;
    text-transform: lowercase;
    color: #6e6e73;
    margin-bottom: 0.5rem;
}

/* mono annotation */
.mono-note {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #8e8e93;
    background: #f5f5f7;
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    margin: 0.5rem 0;
}

/* divider */
hr { border: none; border-top: 1px solid #e0e0e5; margin: 1.5rem 0; }

/* phase row */
.phase-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f0f0f2;
    font-size: 12px;
}
.phase-name { flex: 1; color: #3a3a3c; font-weight: 500; }
.phase-hrs { color: #1d1d1f; font-weight: 600; min-width: 40px; text-align: right; }
.phase-pct { color: #8e8e93; font-size: 10px; min-width: 30px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# constants
# ─────────────────────────────────────────────
ROLE_LEVELS   = ["new hire", "junior", "mid", "senior"]
ROLE_FAMILIES = ["engineering", "data", "support", "product"]
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


# ─────────────────────────────────────────────
# demo data — deterministic seed
# ─────────────────────────────────────────────
@st.cache_data
def build_data():
    rng = np.random.default_rng(42)
    names = [
        "alice tan", "ben lim", "clara ng", "david yeo", "evelyn koh",
        "farah aziz", "gary ong", "hannah soh", "ivan teo", "jasmine wu",
    ]
    emps = []
    for i, name in enumerate(names):
        rl  = rng.choice(ROLE_LEVELS, p=[0.2, 0.3, 0.3, 0.2])
        rf  = rng.choice(ROLE_FAMILIES)
        load = round(float(rng.uniform(5, 36)), 1)
        sk  = {s: int(rng.integers(2, 10)) for s in SKILLS}
        emps.append({"id": f"E{i+1:02d}", "name": name,
                     "role level": rl, "family": rf,
                     "load (h)": load, "capacity (h)": 40.0, **sk})
    emp = pd.DataFrame(emps)
    emp["remaining (h)"] = emp["capacity (h)"] - emp["load (h)"]
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


emp_df, task_df, hist_df = build_data()


# ─────────────────────────────────────────────
# session state — role-based access
# ─────────────────────────────────────────────
if "role" not in st.session_state:
    st.session_state.role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


# ─────────────────────────────────────────────
# login gate
# ─────────────────────────────────────────────
if st.session_state.role is None:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">workload iq</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">sign in to continue</div>', unsafe_allow_html=True)

    who = st.selectbox("who are you?", emp_df["name"].tolist(), label_visibility="collapsed",
                       placeholder="select your name")
    role_choice = st.radio("your role", ["i'm a manager", "i'm a team member"],
                           horizontal=True, label_visibility="collapsed")

    if st.button("continue"):
        emp_row = emp_df[emp_df["name"] == who].iloc[0]
        st.session_state.user_name = who
        st.session_state.user_id   = emp_row["id"]
        st.session_state.role      = "manager" if "manager" in role_choice else "member"
        st.rerun()

    st.markdown("""
    <div class="mono-note" style="margin-top:1.5rem">
    demo prototype — no authentication.<br>
    role selection controls which views are shown.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
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

        # dark data panel
        st.markdown('<div class="data-panel">', unsafe_allow_html=True)
        st.markdown('<div class="data-panel-header">employee workload</div>', unsafe_allow_html=True)

        show = emp_df[[
            "id", "name", "role level", "family",
            "load (h)", "capacity (h)", "remaining (h)", "utilisation", "risk"
        ]].copy()
        show["utilisation"] = (show["utilisation"] * 100).round(1).astype(str) + "%"

        def _risk_color(val):
            if val == "overload": return "color: #ff6b6b"
            if val == "near":     return "color: #ffd60a"
            return "color: #30d158"

        st.dataframe(
            show.style.applymap(_risk_color, subset=["risk"]),
            width=1100, hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # utilisation bar chart — dark panel
        st.markdown('<div class="data-panel">', unsafe_allow_html=True)
        st.markdown('<div class="data-panel-header">utilisation by employee</div>',
                    unsafe_allow_html=True)
        chart_data = emp_df.set_index("name")[["utilisation"]].rename(
            columns={"utilisation": "utilisation %"})
        chart_data["utilisation %"] = (chart_data["utilisation %"] * 100).round(1)
        st.bar_chart(chart_data, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── tab 2: assign task ────────────────────
    with tab2:
        st.markdown("## assign task")
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
              <div style="font-size:12px; color:#3a3a3c; margin-top:4px">
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
            "overload": "split, defer, or reassign",
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
            st.markdown(
                f'<div class="mono-note">'
                f'suggested alternative: <strong>{best_alt["name"]}</strong> — '
                f'{best_alt["role level"]} &nbsp;·&nbsp; '
                f'{TASK_SKILL[sel_type]} skill {int(best_alt[sel_skill])}/10 &nbsp;·&nbsp; '
                f'{best_alt["remaining (h)"]:.1f}h remaining'
                f'</div>',
                unsafe_allow_html=True
            )

        with st.expander("how this estimate was calculated"):
            st.markdown(
                f'<div class="mono-note">{result["formula"]}</div>',
                unsafe_allow_html=True
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ranked alternatives
        st.markdown('<div class="section-label">all employees — ranked by fit</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="data-panel">', unsafe_allow_html=True)
        st.markdown('<div class="data-panel-header">assignment ranking — lowest projected risk first</div>',
                    unsafe_allow_html=True)

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
            ranked.style.applymap(_risk_color, subset=["risk after"]),
            width=1100
        )
        st.markdown('</div>', unsafe_allow_html=True)

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

        st.markdown('<div class="data-panel">', unsafe_allow_html=True)
        st.markdown('<div class="data-panel-header">avg hours — task type × role level</div>',
                    unsafe_allow_html=True)
        st.dataframe(
            pivot.style.format("{:.1f}", na_rep="—")
                 .highlight_min(axis=1, color="#1a3a1f")
                 .highlight_max(axis=1, color="#3a1a1a"),
            width=1100
        )
        st.markdown('</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="data-panel">', unsafe_allow_html=True)
            st.markdown('<div class="data-panel-header">avg hours by task type</div>',
                        unsafe_allow_html=True)
            by_type = (
                hist_df.groupby("task type")["actual (h)"].mean().round(1)
                .sort_values(ascending=False).reset_index()
                .rename(columns={"actual (h)": "avg hours"})
                .set_index("task type")
            )
            st.bar_chart(by_type, height=220)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="data-panel">', unsafe_allow_html=True)
            st.markdown('<div class="data-panel-header">avg hours by role level</div>',
                        unsafe_allow_html=True)
            by_role = (
                hist_df.groupby("role level")["actual (h)"].mean().round(1)
                .reindex(ROLE_LEVELS).reset_index()
                .rename(columns={"actual (h)": "avg hours"})
                .set_index("role level")
            )
            st.bar_chart(by_role, height=220)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-label">raw records</div>', unsafe_allow_html=True)
        f_tt = st.multiselect("filter by task type", TASK_TYPES, default=TASK_TYPES)
        f_rl = st.multiselect("filter by role level", ROLE_LEVELS, default=ROLE_LEVELS)
        filtered = hist_df[
            hist_df["task type"].isin(f_tt) & hist_df["role level"].isin(f_rl)
        ]
        st.markdown('<div class="data-panel">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="data-panel-header">completion records — {len(filtered)} rows</div>',
            unsafe_allow_html=True
        )
        st.dataframe(filtered, width=1100, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="mono-note" style="margin-top:1.5rem">'
            'this prototype uses decision support, not automated evaluation. '
            'estimates support fair planning and manager judgement — not surveillance.'
            '</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────
# MEMBER VIEW
# ─────────────────────────────────────────────
else:
    uid   = st.session_state.user_id
    uname = st.session_state.user_name
    me    = emp_df[emp_df["id"] == uid].iloc[0]

    tab1, tab2 = st.tabs(["my tasks", "how estimates work"])

    # ── tab 1: my tasks ───────────────────────
    with tab1:
        st.markdown(f"## {uname}")
        st.markdown(
            f'<div class="section-label">'
            f'{me["role level"]} &nbsp;·&nbsp; {me["family"]}'
            f'</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("current load", f"{me['load (h)']}h")
        c2.metric("weekly capacity", f"{me['capacity (h)']}h")
        c3.metric("remaining", f"{me['remaining (h)']}h")

        # skill bar
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">skill profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-panel">', unsafe_allow_html=True)
        st.markdown('<div class="data-panel-header">skills — 1 to 10</div>',
                    unsafe_allow_html=True)
        skill_chart = pd.DataFrame({
            "skill": [s.title() for s in SKILLS],
            "level": [int(me[s]) for s in SKILLS]
        }).set_index("skill")
        st.bar_chart(skill_chart, height=180)
        st.markdown('</div>', unsafe_allow_html=True)

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

            st.markdown('<div class="data-panel">', unsafe_allow_html=True)
            st.markdown('<div class="data-panel-header">assigned tasks</div>',
                        unsafe_allow_html=True)
            st.dataframe(
                my_tasks[["task id", "title", "type", "complexity",
                           "required skill", "priority", "status", "est. hours"]],
                width=1100, hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

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
            st.markdown('<div class="data-panel">', unsafe_allow_html=True)
            st.markdown('<div class="data-panel-header">base hours</div>', unsafe_allow_html=True)
            st.dataframe(base_df, width=500, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-label" style="margin-top:1rem">role multipliers</div>',
                        unsafe_allow_html=True)
            role_df = pd.DataFrame(
                list(ROLE_MULT.items()), columns=["role level", "multiplier"]
            )
            st.markdown('<div class="data-panel">', unsafe_allow_html=True)
            st.markdown('<div class="data-panel-header">role multipliers</div>',
                        unsafe_allow_html=True)
            st.dataframe(role_df, width=500, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="section-label">complexity multipliers</div>',
                        unsafe_allow_html=True)
            comp_df = pd.DataFrame(
                list(COMP_MULT.items()), columns=["complexity (1–5)", "multiplier"]
            )
            st.markdown('<div class="data-panel">', unsafe_allow_html=True)
            st.markdown('<div class="data-panel-header">complexity multipliers</div>',
                        unsafe_allow_html=True)
            st.dataframe(comp_df, width=500, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

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