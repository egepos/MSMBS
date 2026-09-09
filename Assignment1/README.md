# Epidemiological Model Assignment — Parameter Exploration

**Course**: KEN3170 — Multi-scale modeling of biological systems
**Group number**: 10
**Members**: Ege Postacioglu, Gianluca Privitelli, Nikita Shuyaev, Valentyn Prianikov

---

## 1. Repository overview
- `analysis.ipynb` — main notebook containing all required sections (Setup, Part 1–3, Conclusions)
- `requirements.txt` — Python dependencies (numpy, matplotlib, pandas, scipy, seaborn)
- `README.md` — this file

**How to run**:
```bash
pip install -r requirements.txt
jupyter notebook analysis.ipynb
```
Then run the notebook from top to bottom. No extra data files are needed.

---

## 2. Part 1 — Parameter analysis function

**Function**: `analyze_recovery_rates(beta, mu, N, I0, simulation_days, display_plots=False)`

We use the SIRD model from the practical, which adds a deaths compartment D to the SIR model. We need
this because the assignment asks for `total_deaths`, and the SIR model does not track deaths.

The function runs the model for each γ in `[0.05, 0.1, 0.15, 0.2, 0.25]` using `odeint`, and stores the
peak number of infectious people, the day of that peak, the total deaths at the end, and R₀ = β/γ. The
results are returned as a DataFrame. The `display_plots` option turns the S/I/R/D plots on or off, so
the function can also be used in Part 2 without making extra figures.

**Output** (β = 0.3, μ = 0.01, N = 1000, I₀ = 10, 100 days):

| gamma | R0 | peak_infected | peak_day | total_deaths |
|-------|-----|---------------|----------|--------------|
| 0.05 | 6.0 | 479.7 | 26 | 163.7 |
| 0.10 | 3.0 | 269.1 | 27 | 83.4 |
| 0.15 | 2.0 | 136.8 | 30 | 47.6 |
| 0.20 | 1.5 | 57.4 | 33 | 25.8 |
| 0.25 | 1.2 | 18.0 | 30 | 11.1 |

---

## 3. Part 2 — Scenario comparison

Both scenarios use N = 1000, I₀ = 5 and 200 days.

**Scenario A — "High Transmission"** (β = 0.4, μ = 0.02):

| gamma | R0 | peak_infected | peak_day | total_deaths |
|-------|------|---------------|----------|--------------|
| 0.05 | 8.00 | 520.6 | 21 | 284.8 |
| 0.10 | 4.00 | 340.1 | 22 | 159.9 |
| 0.15 | 2.67 | 213.5 | 24 | 102.6 |
| 0.20 | 2.00 | 123.9 | 27 | 67.4 |
| 0.25 | 1.60 | 63.1 | 30 | 42.7 |

**Scenario B — "Low Transmission"** (β = 0.2, μ = 0.005):

| gamma | R0 | peak_infected | peak_day | total_deaths |
|-------|------|---------------|----------|--------------|
| 0.05 | 4.00 | 371.4 | 44 | 88.2 |
| 0.10 | 2.00 | 139.3 | 52 | 36.7 |
| 0.15 | 1.33 | 31.3 | 67 | 13.6 |
| 0.20 | 1.00 | 5.0 | 0 | 1.8 |
| 0.25 | 0.80 | 5.0 | 0 | 0.4 |

**Scenario A is worse for public health.** At every recovery rate it has a higher peak and more deaths.
At γ = 0.10 it causes 159.9 deaths against 36.7 in Scenario B. It is also faster: Scenario A peaks
around day 21–30, Scenario B around day 44–67, so the same number of patients arrives in a shorter
time.

Scenario B can also be stopped completely. At γ = 0.20 its R₀ is 1.0 and at γ = 0.25 it is 0.8, so the
epidemic never grows. Scenario A never goes below R₀ = 1.6, so a better recovery rate makes it smaller
but cannot stop it.

---

## 4. Part 3 — Policy recommendations

- **4.1 Parameter impact analysis** — A higher recovery rate lowers the peak, the total deaths and R₀.
  In Scenario A, going from γ = 0.05 to 0.25 drops the peak from 521 to 63 and deaths from 285 to 43.
  It also makes the peak come later, and once R₀ ≤ 1 there is no peak at all.
- **4.2 Intervention analysis** — Baseline Scenario A at γ = 0.10. A 50% increase gives γ = 0.15.
  Deaths go from 159.89 to 102.61, so 57.28 deaths are avoided. That is a 35.8% reduction.
- **4.3 Real-world application** — Antibiotics for bacterial infections. They clear the infection
  faster, which shortens the infectious period and raises γ. How well they work depends on the
  infection and the antibiotic, and antibiotic resistance can reduce the effect.

Full answers are in the notebook.

---

## 5. Conclusions

- **A higher recovery rate is better in every way.** Going from γ = 0.05 to 0.25 lowers the peak from
  480 to 18 people and deaths from 164 to 11, and it also delays the peak, which gives hospitals more
  time.
- **R₀ = 1 is the important line.** Scenario B drops below it at γ = 0.20 and the epidemic never
  starts. Scenario A stays above 1.6, so treatment can only make it smaller.
- **Better treatment is not always enough.** In Scenario A a 50% higher recovery rate saves 57 lives
  (35.8% fewer deaths), but the epidemic still happens. It has to be combined with something that
  lowers β.
- **Limitations.** Closed population, no births, everyone mixes equally, and the parameters never
  change during the simulation. Real epidemics are not like this, so these numbers compare scenarios
  rather than predict real outbreaks.
