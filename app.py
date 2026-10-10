import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="Metformin PK | Clinical Pharmacokinetics Engine",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💊 Metformin PK: Renal Elimination & Steady-State Engine")
st.caption("One-compartment pharmacokinetic simulation modeling renal clearance, eGFR dose adjustments, and steady-state plasma concentrations.")
st.markdown("---")

st.sidebar.header("📋 Patient Clinical Parameters")

col_p1, col_p2 = st.sidebar.columns(2)
with col_p1:
    age = st.sidebar.number_input("Age (years)", min_value=18, max_value=95, value=58, step=1)
    weight = st.sidebar.number_input("Weight (kg)", min_value=35.0, max_value=160.0, value=74.0, step=0.5)
with col_p2:
    egfr = st.sidebar.number_input("eGFR (mL/min/1.73m²)", min_value=10.0, max_value=130.0, value=48.0, step=1.0)
    dose_mg = st.sidebar.selectbox("Dose (mg)", [500, 850, 1000], index=0)

dosing_interval_hr = st.sidebar.selectbox("Dosing Frequency", [12, 24], index=0, format_func=lambda x: "Every 12 hrs (BID)" if x == 12 else "Every 24 hrs (Daily)")

# Metformin pharmacokinetic model
f_bioavail = 0.55
vd = 3.0 * weight
ka = 0.8

cl_base = (egfr / 100.0) * 30.0
ke = cl_base / vd
half_life = np.log(2) / ke if ke > 0 else 0

if egfr >= 60:
    safety_tier = "Normal / Mild"
    guideline_status = "Safe for Standard Dosing (Max 2000-2550 mg/day)"
    dose_alert_type = "success"
elif 45 <= egfr < 60:
    safety_tier = "Moderate Impairment (Stage 3a)"
    guideline_status = "Dose Capped at 1000 mg/day (Monitor eGFR Q3-6M)"
    dose_alert_type = "info"
elif 30 <= egfr < 45:
    safety_tier = "Substantial Impairment (Stage 3b)"
    guideline_status = "Dose Capped at 500 mg/day (Risk of Lactic Acidosis; initiation not recommended)"
    dose_alert_type = "warning"
else:
    safety_tier = "Severe Impairment (Stage 4/5)"
    guideline_status = "CONTRAINDICATED (eGFR < 30 mL/min/1.73m²)"
    dose_alert_type = "error"

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("eGFR Function", f"{egfr:.0f} mL/min", delta=safety_tier, delta_color="normal" if egfr >= 45 else "inverse")
col_m2.metric("Apparent Clearance (CL)", f"{cl_base:.2f} L/hr")
col_m3.metric("Elimination Half-Life (t½)", f"{half_life:.1f} hrs")
col_m4.metric("Steady-State AUC₂₄", f"{round((dose_mg * (24 / dosing_interval_hr) * f_bioavail) / cl_base, 1)} mg·h/L")

if dose_alert_type == "success":
    st.success(f"**Guideline Recommendation:** {guideline_status}")
elif dose_alert_type == "info":
    st.info(f"**Guideline Recommendation:** {guideline_status}")
elif dose_alert_type == "warning":
    st.warning(f"**Guideline Recommendation:** {guideline_status}")
else:
    st.error(f"**Guideline Recommendation:** {guideline_status}")

st.markdown("---")
st.subheader("📈 Plasma Concentration-Time Profile (0 – 48 Hours)")

t = np.linspace(0, 48, 200)
conc = np.zeros_like(t)
doses = np.arange(0, 48, dosing_interval_hr)

for d_time in doses:
    mask = t >= d_time
    dt = t[mask] - d_time
    conc[mask] += (dose_mg * f_bioavail * ka / (vd * (ka - ke))) * (np.exp(-ke * dt) - np.exp(-ka * dt))

chart_df = pd.DataFrame({"Time (Hours)": t, "Plasma Concentration (mg/L)": np.round(conc, 3)})
chart_df = chart_df.set_index("Time (Hours)")
st.line_chart(chart_df)

st.caption("Reference Therapeutic Window: 0.5 – 2.0 mg/L | Trough > 5.0 mg/L indicates substantial risk of Metformin-Associated Lactic Acidosis (MALA).")