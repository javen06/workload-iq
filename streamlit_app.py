# app.py
import numpy as np, pandas as pd, streamlit as st
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ---------------------------
# Task classifier
# ---------------------------
train_examples = [
    ("fix login bug","BugFix"),("patch security issue","BugFix"),
    ("resolve crash error","BugFix"),("implement new feature","Feature"),
    ("add api endpoint","Feature"),("build signup ui","Feature"),
    ("analyze sales data","Analysis"),("research customer behavior","Analysis"),
    ("explore dataset trends","Analysis"),("write monthly report","Report"),
    ("prepare presentation slides","Report"),("document system architecture","Report"),
    ("answer customer ticket","Support"),("handle incident request","Support"),
    ("provide technical support","Support"),
]
X_texts=[t for t,_ in train_examples]
y_labels=[lab for _,lab in train_examples]
vec=TfidfVectorizer()
clf=LogisticRegression(max_iter=500).fit(vec.fit_transform(X_texts),y_labels)

# ---------------------------
# Globals
# ---------------------------
TASK_TYPES=["BugFix","Feature","Analysis","Report","Support"]
SKILL_CATEGORIES=["Frontend","Backend","Debugging","DataAnalytics","Writing","Support"]
RNG=np.random.default_rng(42)

# Map task types → skill weights
TASK_SKILLS={
    "Feature":{"Frontend":0.5,"Backend":0.5},
    "BugFix":{"Debugging":1.0},
    "Analysis":{"DataAnalytics":1.0},
    "Report":{"Writing":1.0},
    "Support":{"Support":1.0},
}

# Learning resources with summaries if skill < 5
RESOURCES = {
    "Frontend": [
        ("https://developer.mozilla.org/en-US/docs/Learn/Front-end_web_developer",
         "MDN guide for learning HTML, CSS, and JavaScript from scratch"),
        ("https://www.freecodecamp.org/learn/front-end-development-libraries/",
         "FreeCodeCamp interactive front-end development libraries course")
    ],
    "Backend": [
        ("https://roadmap.sh/backend",
         "Comprehensive backend developer roadmap with technologies and paths"),
        ("https://www.geeksforgeeks.org/backend-development/",
         "GeeksforGeeks backend development tutorials and articles")
    ],
    "Debugging": [
        ("https://developer.chrome.com/docs/devtools/",
         "Chrome DevTools official guide for debugging front-end applications"),
        ("https://www.geeksforgeeks.org/debugging-tips-techniques/",
         "General debugging tips and techniques with examples")
    ],
    "DataAnalytics": [
        ("https://www.kaggle.com/learn",
         "Kaggle Learn micro-courses for data analytics and machine learning"),
        ("https://www.coursera.org/specializations/data-analytics",
         "Coursera Data Analytics specialization for beginners to intermediate")
    ],
    "Writing": [
        ("https://owl.purdue.edu/owl/general_writing/academic_writing/index.html",
         "Purdue OWL guide to academic and professional writing"),
        ("https://writingcenter.unc.edu/tips-and-tools/",
         "UNC Writing Center tips and strategies for effective writing")
    ],
    "Support": [
        ("https://www.zendesk.com/blog/customer-service-skills/",
         "Zendesk blog post on key customer service skills"),
        ("https://www.helpscout.com/blog/customer-service-skills/",
         "HelpScout article on improving customer service skills")
    ]
}

@dataclass
class Employee:
    id:str
    role:str
    skills:dict
    current_load_hours:float
    weekly_capacity_hours:float

def simulate_employees(n=5):
    rows=[]
    for i in range(n):
        skills={cat:int(RNG.integers(2,10)) for cat in SKILL_CATEGORIES}
        rows.append({
            "employee_id":chr(65+i),
            "role":RNG.choice(["FrontendDev","BackendDev","FullStack","DataSci","SupportEng"]),
            **skills,
            "current_load_hours":float(np.round(RNG.uniform(2,16),1)),
            "weekly_capacity_hours":float(np.round(RNG.uniform(25,38),1)),
        })
    return pd.DataFrame(rows)

def simulate_history(employees,n_rows=300):
    rows=[]
    for _ in range(n_rows):
        e=employees.sample(1).iloc[0]
        task=RNG.choice(TASK_TYPES)
        comp=int(RNG.integers(1,6))
        base={"BugFix":2,"Feature":4,"Analysis":3.5,"Report":3,"Support":1.5}[task]*(0.7+0.4*comp)

        required=TASK_SKILLS[task]
        weighted=sum(w*e[cat] for cat,w in required.items())
        avg_skill=weighted/sum(required.values())
        skill_factor=1-(avg_skill-5)*0.07
        skill_factor=max(0.4,skill_factor)

        drag=1+max(0,(e.current_load_hours-10))*0.02
        actual=base*skill_factor*drag*RNG.normal(1.0,0.15)

        rows.append({
            "employee_id":e.employee_id,"task_type":task,"complexity":comp,
            **{cat:e[cat] for cat in SKILL_CATEGORIES},
            "current_load_hours":e.current_load_hours,
            "time_taken_hours":max(0.5,round(actual,2))
        })
    return pd.DataFrame(rows)

def simulate_pending_tasks(n=6):
    return pd.DataFrame([{
        "task_id":f"T{i+1:02d}",
        "task_type":RNG.choice(TASK_TYPES),
        "complexity":int(RNG.integers(1,6))
    } for i in range(n)])

def build_model(hist):
    feats=["employee_id","task_type","complexity","current_load_hours"]+SKILL_CATEGORIES
    X,y=hist[feats],hist["time_taken_hours"]
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=7)
    pre=ColumnTransformer([
        ("cat",OneHotEncoder(handle_unknown="ignore"),["employee_id","task_type"]),
        ("num",StandardScaler(),["complexity","current_load_hours"]+SKILL_CATEGORIES)
    ])
    model=RandomForestRegressor(n_estimators=300,random_state=7,n_jobs=-1)
    pipe=Pipeline([("pre",pre),("rf",model)]).fit(Xtr,ytr)
    return pipe,{"mae":mean_absolute_error(yte,pipe.predict(Xte)),"r2":r2_score(yte,pipe.predict(Xte))}

# ---------------------------
# Sidebar data
# ---------------------------
st.sidebar.header("📥 Data")
use_sim=st.sidebar.toggle("Use simulated demo data",True)
if use_sim:
    employees_df=simulate_employees()
    history_df=simulate_history(employees_df,400)
    pending_df=simulate_pending_tasks()
else:
    up_emp=st.sidebar.file_uploader("Employees CSV",type=["csv"])
    up_hist=st.sidebar.file_uploader("History CSV",type=["csv"])
    up_tasks=st.sidebar.file_uploader("Tasks CSV",type=["csv"])
    if not(up_emp and up_hist and up_tasks): st.stop()
    employees_df=pd.read_csv(up_emp)
    history_df=pd.read_csv(up_hist)
    pending_df=pd.read_csv(up_tasks)

pipe,metrics=build_model(history_df)

# ---------------------------
# Mode switch
# ---------------------------
mode=st.sidebar.radio("Choose Mode:",["Manager Dashboard","Employee Task Planner"])

# === MANAGER VIEW ===
if mode=="Manager Dashboard":
    st.title("📊 Manager Dashboard — Curate Skills & Predict Durations")
    st.subheader("👥 Employee Skills")
    edited=st.data_editor(employees_df,use_container_width=True,num_rows="dynamic")
    employees_df=edited

    st.metric("MAE",f"{metrics['mae']:.2f}")
    st.metric("R²",f"{metrics['r2']:.2f}")

    st.subheader("🧾 Pending Tasks")
    st.dataframe(pending_df,use_container_width=True)

# === EMPLOYEE VIEW ===
elif mode=="Employee Task Planner":
    st.title("⏱️ Onborn — Personal Task Planner")

    who=st.selectbox("Who are you?",employees_df.employee_id)
    emp=employees_df[employees_df.employee_id==who].iloc[0]
    task_text=st.text_input("Describe your task")

    if st.button("Get Plan"):
        if not task_text.strip():
            st.warning("Please enter a task description.");st.stop()

        task_type=clf.predict(vec.transform([task_text]))[0]
        avg_complexity=history_df[history_df.task_type==task_type]["complexity"].mean()
        complexity=int(round(avg_complexity)) if not np.isnan(avg_complexity) else 3

        x=pd.DataFrame([{
            "employee_id":who,"task_type":task_type,"complexity":complexity,
            "current_load_hours":emp.current_load_hours,
            **{cat:emp[cat] for cat in SKILL_CATEGORIES}
        }])
        est=float(pipe.predict(x)[0])

        st.success(f"Estimated total time: {est:.2f} hours for a **{task_type}** task")

        st.markdown("### 📋 Breakdown")
        if task_type=="Feature": phases=[("Design",.25),("Build",.55),("Test",.20)]
        elif task_type=="BugFix": phases=[("Triage",.3),("Resolve",.5),("Test",.2)]
        elif task_type=="Analysis": phases=[("Research",.5),("Modeling",.3),("Review",.2)]
        elif task_type=="Report": phases=[("Draft",.5),("Edit",.3),("Review",.2)]
        else: phases=[("Handle",.8),("Document",.2)]
        for name,p in phases: st.write(f"- **{name}**: {est*p:.2f}h")

        # show resources if weak in needed skills
        weak_skills=[cat for cat in TASK_SKILLS[task_type] if emp[cat]<5]
        if weak_skills:
            st.markdown("### 💡 Helpful Resources to Improve Skills")
            for cat in weak_skills:
                st.write(f"**{cat} (your level: {emp[cat]})**")
                for url, desc in RESOURCES.get(cat, []):
                    st.write(f"- [{url}]({url}) — {desc}")

        st.markdown(f"""
        ---
        **Why this plan?**  
        - Task detected as **{task_type}**  
        - Complexity estimated from history → {complexity}  
        - Relevant skills: {TASK_SKILLS[task_type]}  
        - Your profile: {[f"{cat}:{emp[cat]}" for cat in TASK_SKILLS[task_type]]}  
        - Model adjusted time based on these skills + workload  
        """)
