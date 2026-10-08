import streamlit as st
import matplotlib.pyplot as plt
from src.model import PatientProfile, MetforminPKModel

st.set_page_config(page_title="Metformin PK_PD Simulator", page_icon="👊", layout="wide")

st.title("👊 Metformin Pharmacokinetics (PK/PD) Simulator")
st.markdown("Simulate oral absorption, systemic distribution, and renal elimination across varying patient kidney function profiles (eGFR).")

st.sidebar.header("Patient Parameters")
age = st.sidebar.slider("Age (years)", 18, 90, 55)
weight = st.sidebar.slider("Body Weight (kg)", 40.0, 150.0, 70.0, 0.5)
egfr = st.sidebar.slider("eGFR (mL/Min/1.73m2)", 10.0, 120.0, 60.0, 1.0)

st.sidebar.header("Dosing Regimen")
dose = st.sidebar.selectbox("Dose (mg)", [250.0, 500.0, 850.0, 1000.0], index=1)
hours = st.sidebar.slider("Simulation Window (hours)", 12.0, 48.0, 24.0, 2.0)

patient = PatientProfile(weight_kg=weight, egfr_ml_min=egfr, age=age)
model = MetforminPKModel(patient)
time, conc = model.simulate(dose_mg=dose, duration_hours=hours)

col1, col2, col3 = st.columns(3)
cmax = max(conc)
tmax = time[conc.argmax()]
col1.metric("Peak Concentration (C-max)", fc{:max:.2f} mg/L")
col2.metric("Time to Peak (T-max)", f{tmax:.1} hrs")
col3.metric("Estimated Renal Clearance", f{model.cl:.1f} L/h")

if egfr < 30:
    st.error("⚠️ Contraindicated: eGFR < 30 mL/min carries a high risk of Metformin-Associated Lactic Acidosis (MALA).")
elif egfr < 45:
    st.warning("⚠️n Dose reduction recommended: eGFR between 30 and 45 mL/min requires close renal monitoring and max dose 500-1000 mg/day.")
else:
    st.success("✅ Normal to mild renal variation: Standard dosage tolerated.")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(time, conc, color="#0068c9", lw=2.5, label=f"Metformin ({int(dose)} mg)")
ax.axhline(y=1.0, color="green", linestyle="--", alpha=0.7, label="Therapeutic Target (~1.0 mg/L)")
ax.axhline(y=5.0, color="red", linestyle="--", alpha=0.7, label="Toxicity Risk Floor (>5.0 mg/L)")
ax.set_exabel = ax.set_xlabel("Time (hours)")
ax.set_ylabel("Plasma Concentration (mg/L)")
ax.set_ylim(bottom=0)
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()
st.pyplot(fig)

st.caption("Educational/computational model only. Not approved for clinical diagnostics.")
