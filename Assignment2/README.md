# Assignment 2
**Group number**: 10

**Members**: Ege Postacioglu, Gianluca Privitelli, Nikita Shuvaev, Valentyn Prianikov

## Repository overview
- `assignment2.ipynb` — notebook with all parts (1–4)
- `e_coli_core-1.json` 
- `KEN3170_Assignment_2026_e_coli_core_expression.csv` — maximal reaction activities (mmol/gDW/h)
- `saved_map.png` — Escher map
- `requirements.txt` — Python dependencies

**How to run**:
```bash
pip install -r requirements.txt
jupyter notebook assignment2.ipynb
```

## Part 1 — Escher map
Data loaded through - Load reaction data, screenshot `saved_map.png`.

- a) Reactions in a linear pathway do not have equal values any more. The numbers are upper bounds not fluxes, so mass balance does not apply to them.
- b) Grey arrows are either nd or 0.00 (measured, but the enzyme is not expressed, so the reaction cannot carry flux).

## Part 2 — Constraining the model
Loop over the csv and set bounds per reaction:

- reversible  (-value, value)
- irreversible  (0, value)
- `nd` default bounds kept
- `ATPM` lower bound left alone
- `EX_glc__D_e` lower bound reset to -1000

Then all reaction bounds are printed as a table.

## Part 3 — FBA

| Setup | Max biomass (h⁻¹) |
|-------|-------------------|
| a) enzyme constraints only | 0.8733 |
| c) + glucose uptake ≤ 5 | 0.4156 |

- b) The -5 bound is an environmental limit, while Part 2 bounds are internal limits.
- c) Growth drops by more than half, because less glucose means less carbon and energy for biomass.

## Part 4 — Glucose scan
- a) Glucose bound scanned from 1 to 15 in steps of 0.1, biomass plotted against it.
- b) No. Growth rises linearly, bends around 10, and is flat at 0.8733 from ~10.6 onwards. Oxygen uptake hits its cap first, then acetate export hits its cap, after which extra glucose can't be used. The limit comes from the enzyme constraints, not from glucose.
- c) EX_ac_e — acetate secretion starts in the second segment (0 at bound 9.0 and 1.25 at 10.0).
