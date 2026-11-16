# State-Dependent Affine Bellman Barriers, Asymptotic Equivalence, and the Institutional U-Curve

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24282792.svg)](https://doi.org/10.5281/zenodo.24282792)

**Author:** Marcelo Segura  
**Zenodo Preprint (v3.0):** [10.5281/zenodo.24282792](https://doi.org/10.5281/zenodo.24282792) · **Concept DOI (all versions):** [10.5281/zenodo.24282791](https://doi.org/10.5281/zenodo.24282791)

Bilingual working paper (English and Spanish) plus reproducible numerical and interval-arithmetic verification code extending **Milei and Reidel (2026)**, *"Minimum Viable Scale: Bellman Barriers and the Economics of Survival"*, without altering any primitive or parameter box.

---

## Main Manuscripts

- **English Working Paper (PDF, 22 pages):** [`mvs_improvements_en.pdf`](mvs_improvements_en.pdf) ([Typst source](mvs_extension_en.typ))
- **Spanish Working Paper (PDF, 25 pages):** [`mvs_mejoras_paper.pdf`](mvs_mejoras_paper.pdf) ([Typst source](mvs_extension_es.typ), [LaTeX source](mvs_mejoras_paper.tex))

---

## Summary of Contributions

1. **One-Step Affine FPBB & Interval Certification of Adverse Exits (Section 3):**
   - **Lemma 1 & Theorem 9\*:** Retains both $q(h-x)$ and $(y-b)$ simultaneously on every staying edge $(x,y)\in M\times M$ under box `(7.3)`, lowering the regional barrier ceiling from $-38.1442$ to $-43.0465$ ($-43.3556$ at $b=0.10$), raising the staying calibration margin from $>2.564$ to $>7.4665$ uniform ($>7.7755$ state-by-state), and cutting the certified entry deadline $\tau_H$ in half from $46$ to **$23$ periods** ($24$ uniformly).
   - **Proposition 1\*:** Certifies $\tau_{.1} \le 10$ periods on the anchor band $M_0 = [0.05, 0.10)$ ($\tau_H \le 33$ total).
   - **Proposition 1\*\* & Table 2:** Proves state-by-state monotonicity of adverse-exit margins via Wronskian decomposition and pure interval enclosures on $M$ and $H_1$ (no interior minima, grid-independent), collapsing the 12 finite subintervals of Table 5 to two boundary checks and lifting the global FPBB certificate margin from $0.0423$ ($0.04$) to **$>0.0571$** ($+35\%$).
2. **Asymptotic Equivalence & Finite-$A$ Isomorphism for Endogenous vs. Fixed Labor (Section 4):**
   - **Theorem 3\* & Table 3:** Resolves Footnote 1 by proving the finite-$A$ scaling isomorphism $S_A^{\mathrm{fix}}(\overline{L}) = \overline{L} S_{A\overline{L}^r}^{\mathrm{fix}}(1)$, a variational criterion for $S_A^{\mathrm{fix}}(1) < S_A$, and convergence of both rescaled frontiers to $(\delta/c_K)^{1/r}$ ($S_A / S_A^{\mathrm{fix}}(\overline{L}) \to 1$) as $A\to\infty$, backed by exact FOC evaluation and continuous-state 880-point normalized Value Function Iteration (VFI).
3. **Barro–CES Institutional U-Curve & Burden Decomposition (Section 5):**
   - **Theorem 10 & Table 4:** Microfounds Section 4.3 with balanced-budget productive public spending ($\tau_p$) and unproductive compliance overhead ($\tau_u$), cleanly separating the exact differentiable U-curve of $\overline{S}(\tau)$ and physical floor $\kappa(\tau)$ minimized uniquely at $\tau^* = \alpha/(1+\alpha)$, level-set symmetry at finite $A_0$, and the exact asymptotic $S(\tau)$ limit as $A_0 \to \infty$.
4. **Structural Extensions (Section 6):**
   - **Propositions 2\*–3\* & Theorem 11:** Formalizes monopolistic competition decentralization with exact Euler factor accounting $(\theta/\mu)Y_t$, firm fragmentation TFP loss $A/M^{\theta-1}$, unbounded balanced growth in efficiency units, and Stochastic Bellman Barriers via Doob's Optional Stopping Theorem ($\mathbb{P} \ge (1-p)^{23}$ vs. $(1-p)^{46}$).

---

## Repository Contents

| File | Description |
| :--- | :--- |
| `mvs_improvements_en.pdf` / `mvs_extension_en.typ` | Complete English manuscript and Typst source |
| `mvs_mejoras_paper.pdf` / `mvs_extension_es.typ` | Complete Spanish manuscript and Typst source |
| `mvs_mejoras_paper.tex` | Synchronized Spanish LaTeX source |
| `verify_results.py` | Standalone numerical, VFI, and interval-arithmetic verification script |
| `generate_figures.py` | Generates all 4 two-panel figures (`fig1`–`fig4`) in ES & EN (`.svg`/`.png`) |
| `fig1_*` – `fig4_*` | Vector (`.svg`) and raster (`.png`) figures embedded in the papers |
| `CITATION.cff`, `.zenodo.json`, `LICENSE`, `requirements.txt` | Citation, Zenodo archiving metadata, dual license (CC BY 4.0 / MIT), and Python dependencies |

---

## Reproduction

```bash
pip install -r requirements.txt

# 1. Verify all analytical interval bounds, Table 1-4 values, FOC, and VFI frontiers
python verify_results.py

# 2. Regenerate all figures (SVG and PNG, English and Spanish)
python generate_figures.py

# 3. Compile Typst manuscripts to PDF via Python typst package
python -c "import typst; typst.compile('mvs_extension_en.typ', output='mvs_improvements_en.pdf'); typst.compile('mvs_extension_es.typ', output='mvs_mejoras_paper.pdf')"
```

---

## Methodological & AI Disclosure

Analytical development, technical editing, and Python symbolic/numerical verification routines were assisted by AI tools under the author's direction, critical review, and sole responsibility.

---

## License

- **Manuscripts and figures:** Creative Commons Attribution 4.0 International (**CC BY 4.0**).
- **Python scripts:** **MIT License**.
