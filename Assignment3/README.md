# Assignment 3
**Group number**: 10

**Members**: Ege Postacioglu, Gianluca Privitelli, Nikita Shuvaev, Valentyn Prianikov

## Repository overview
- `assignment3.ipynb` — notebook with the normal network, mutations A–D, scenario analysis and attractor analysis
- `KEN3170_BooleanModeling-2026-27.ipynb` — practical notebook we started from

**How to run**:
```bash
pip install numpy pandas matplotlib seaborn networkx sympy
jupyter notebook assignment3.ipynb
```

## Mutations
- **A** — p53 knockout: p53 always OFF
- **B** — MYC amplification: MYC always ON
- **C** — MDM2 overexpression: MDM2 always ON
- **D** — p21 knockout (our choice): p21 always OFF

## Scenario analysis
Final state after simulation (Growth / Death / p53):

| Network | Healthy Cell | Stressed Cell | Oncogene Hijacked Cell |
|---------|--------------|---------------|------------------------|
| Normal | 1 / 0 / 0 | 0 / 1 / 1 | 1 / 0 / 0 |
| A — p53 KO | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| B — MYC amp | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| C — MDM2 over | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| D — p21 KO | 1 / 0 / 0 | 0 / 1 / 1 | 1 / 0 / 0 |

The normal network kills the stressed cell. A, B and C keep growing even with DNA damage. D behaves like
the normal network.

## Attractor analysis
We tested all 2⁸ = 256 starting states. We call an attractor **cancerous** when DNA damage is ON, Growth
is ON and Death is OFF (growth without DNA damage is just a healthy dividing cell).

| Network | Attractors | Cancerous states | Cancerous % |
|---------|------------|------------------|-------------|
| Normal | 3 | 8 | 3.1% |
| A — p53 KO | 2 | 128 | 50.0% |
| B — MYC amp | 2 | 128 | 50.0% |
| C — MDM2 over | 2 | 128 | 50.0% |
| D — p21 KO | 5 | 8 | 3.1% |

## Questions

### Which mutation is most dangerous and why?
A, B and C are all much more dangerous than the normal network: 50% of all starting states end up
cancerous, compared with 3.1% normally. That is 16 times more. In all three, every state with DNA damage
ends up growing instead of dying.

Between the three, we think **Mutation A (p53 knockout)** is the most dangerous. The numbers are the same,
but A reaches the cancerous state faster in the Stressed Cell scenario (4 steps, against 7 for B and C).
Also, B and C only stop p53 through MDM2, so p53 itself still works. If MDM2 were blocked (for example by a
drug), p53 could come back. In A, p53 is gone, so nothing further down the pathway can bring cell death back.

Mutation D has no effect on the cancer percentage (3.1%, same as normal), because p21 just copies p53 in
this model, so p53 can still stop MYC on its own.

### Role of feedback loops
The main loop is **MYC → MDM2 ⊣ p53 ⊣ MYC**: MYC turns on MDM2, MDM2 turns off p53, and p53 turns off
MYC (directly and through p21). This is a negative feedback loop, and it decides between growth and death.
When there is DNA damage, p53 wins, MYC is shut down and the cell dies.

Mutations B and C break this loop by fixing MYC or MDM2 ON, so p53 can never turn on and the cell keeps
growing. Mutation A breaks it at p53 itself.

In Mutation D we can see the loop directly. Without p21 holding MYC down, p53 and MYC keep switching each
other on and off, which gives two 3-state limit cycles (96 of 256 states, 37.5%). In the normal network,
p21 keeps MYC off for an extra step, which stops these oscillations.

### Limitations of the model
1. **Only ON or OFF.** Real proteins have levels. A little MYC and a lot of MYC are the same here, so we
   cannot model partial effects or dose.
2. **Synchronous updating.** All nodes update at the same time, but real reactions happen at different
   speeds. This can create cycles that would not happen in a real cell, like the ones in Mutation D.
3. **Very small network.** Only 8 nodes. Real cancer involves many more genes, and there is no DNA repair
   in the model: DNA damage stays ON forever once it is there, so a damaged cell can only die or keep
   growing.
