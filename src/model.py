from dataclasses import dataclass
import numpy as np
from scipy.integrate import odeint

@dataclass
class PatientProfile:
    weight_kg: float
    egfr_ml_min: float
    age: int

class MetforminPKModel:
    def __init__(self, patient: PatientProfile):
        self.patient = patient
        self.ka = 0.85
        self.f = 0.55
        self.v_central = 0.7 * patient.weight_kg
        self.v_periph = 2.5 * patient.weight_kg
        self.q = 12.0
        scaled_clr_l_hr = (patient.egfr_ml_min / 100.0) * 30.0
        self.cl = max(scaled_clr_l_hr, 1.5)

    def _ode_system(self, y, t):
        a_gut, a_central, a_periph = y
        c_central = a_central / self.v_central
        c_periph = a_periph / self.v_periph
        d_gut = -self.ka * a_gut
        d_central = (self.ka * a_gut * self.f) - (self.cl / self.v_central) * a_central - self.q * (c_central - c_periph)
        d_periph = self.q * (c_central - c_periph)
        return [d_gut, d_central, d_periph]

    def simulate(self, dose_mg: float, duration_hours: float = 24.0, steps: int = 500):
        t = np.linspace(0, duration_hours, steps)
        initial_conditions = [dose_mg, 0.0, 0.0]
        solution = odeint(self._ode_system, initial_conditions, t)
        plasma_conc_mg_l = solution[:, 1] / self.v_central
        return t, plasma_conc_mg_l
