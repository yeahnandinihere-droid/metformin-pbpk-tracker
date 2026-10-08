import pytest
from src.model import PatientProfile, MetforminPKModel

def test_renal_clearance_scaling():
    healthy = PatientProfile(weight_kg=70.0, egfr_ml_min=100.0, age=35)
    impaired = PatientProfile(weight_kg=70.0, egfr_ml_min=30.0, age=65)
    m_healthy = MetforminPKModel(healthy)
    m_impaired = MetforminPKModel(impaired)
    assert m_impaired.cl < m_healthy.cl

def test_simulation_shape():
    patient = PatientProfile(weight_kg=75.0, egfr_ml_min=90.0, age=40)
    model = MetforminPKModel(patient)
    t, conc = model.simulate(dose_mg=500.0, duration_hours=12.0, steps=100)
    assert len(t) == 100
    assert len(conc) == 100
    assert conc[0] == 0.0
    assert max(conc) > 0.1
