# State-Dependent Affine Bellman Barriers, Asymptotic Equivalence, and the Institutional U-Curve

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24340962.svg)](https://doi.org/10.5281/zenodo.24340962)

**Author:** Marcelo Segura  
**Zenodo Preprint (v5.1; v5.2 release pending archive):** [10.5281/zenodo.24340962](https://doi.org/10.5281/zenodo.24340962) · **Concept DOI (all versions):** [10.5281/zenodo.24282791](https://doi.org/10.5281/zenodo.24282791)

Bilingual working paper (English and Spanish) plus reproducible numerical and interval-arithmetic verification code extending **Milei and Reidel (2026)**, *"Minimum Viable Scale: Bellman Barriers and the Economics of Survival"* (October 2026 edition), without altering any primitive or parameter box.

---

## Main Manuscripts

- **English Working Paper (PDF, 37 pages):** [`mvs_improvements_en.pdf`](mvs_improvements_en.pdf) ([Typst source](mvs_extension_en.typ))
- **Spanish Working Paper (PDF, 40 pages):** [`mvs_mejoras_paper.pdf`](mvs_mejoras_paper.pdf) ([Typst source](mvs_extension_es.typ), [LaTeX source](mvs_mejoras_paper.tex))

---

## Summary of Contributions

1. **One-Step Affine FPBB, Restricted-$M$ Slack Decomposition, & Interval Certification (Section 3):**
   - **Lemma 1 & Theorem 9\* (Table 1):** Retains both $q(h-x)$ and $(y-b)$ simultaneously on every staying edge $(x,y)\in M\times M$ under box `(7.3)` and the baseline `MR-Table 4` / $\Psi^\sharp$ bounds, lowering the regional barrier ceiling from $-38.1442$ to $-43.0465$ ($-43.3556$ at $b=0.10$), raising the staying calibration margin from $>2.564$ to $>7.4665$ uniform ($>7.7755$ state-by-state), and cutting the certified entry deadline $\tau_H$ in half from $46$ to **$23$ periods** ($24$ uniformly). Exact restricted-$M$ DP and continuous VFI (`verify_restricted_M_vfi`) decompose the remaining slack ($46 \to 23 \to 9 \to 4$).
   - **Proposition 1\* & Corollary 1\*:** Proposition 1\* certifies $\tau_{.1} \le 10$ periods on the anchor band $M_0 = [0.05, 0.10)$ ($\tau_H \le 33$ total). Corollary 1\* sharpens the three-step $M_0$ witness ($W_{M_0}(0.05) = -43.540132$ with the `MR-Table 4` tail / $-43.500107$ with the 25-step stationary tail $W_M^{(0)}$) and certifies a single $\Psi^{(0)}$ super-barrier per subinterval across an 8-subinterval partition of the continuum $[\beta_-, \beta_+] = [0.9699, 0.9701]$ ($\min\text{gap} = +0.028216$, outward-rounded `Interval` lower bound $+0.028216$), tightening the certified deadlines to **$\tau_{.1} \le 9$** and **$\tau_H \le 22$** box-uniform (**$\tau_H \le 21$** across the matched-$\beta$ continuum).
   - **Proposition 1\*\* & Table 2:** Proves state-by-state monotonicity and concavity of adverse-exit margins via Wronskian decomposition and outward-rounded 50-digit interval arithmetic (`decimal` `ROUND_FLOOR`/`ROUND_CEILING` + `math.nextafter`, cross-certifying Lemma 1, Theorem 9\*, Proposition 1\*, Corollary 1\*, and Proposition 1\*\* with $Q_M \le -0.04375$, $\Delta_M' \ge 0.0723$, $\Delta_M'' \le -2.5107$, $Q_{H_1} \le -0.13124$, $\Delta_{H_1}' \ge 0.0095$, $\Delta_{H_1}'' \le -0.1889$, and boundary margins $0.094717$ / $0.057148$ for $\Psi^\sharp$ and $0.062495$ / $0.024926$ for $\Psi$), incorporating the $c_M'' > 0$ ($\eta_+$) sign fix on $[0.10, 0.17)$, interior tangent share $u^*(K) \in [0.4301, 0.6808] < 1$, and variational $l_0$ alignment—collapsing the 12 finite subintervals of `MR-Table 5` to two boundary checks and lifting the global FPBB certificate margin from $0.0423$ ($0.04$) to **$>0.0571$** ($+35\%$, and $>0.0947$ on $M$).
2. **Asymptotic Equivalence, Weak Patience, & Finite-$A$ Isomorphism (Section 4):**
   - **Theorem 3\*, Corollary 2\*, & Table 3:** Resolves Footnote 1 by proving the finite-$A$ scaling isomorphism $S_A^{\mathrm{fix}}(\overline{L}) = \overline{L} S_{A\overline{L}^r}^{\mathrm{fix}}(1)$, establishing a rigorous three-phase escape proof (Phases I–III cancelling Lemma 9's bound via $\beta\theta > 1$, with sub-logarithmic escape times $T_{\mathrm{esc}}(A) \in [102, 121]$ so $\beta^{T_{\mathrm{esc}}} \gg A^{-1}$ for large $A$ while the optimal value gap $\Delta W_A^+ := V_A^{\mathrm{fix}}(S_A; 1) - V_A(S_A) \to 0^+$) for convergence of both rescaled frontiers to $(\delta/c_K)^{1/r}$ ($S_A / S_A^{\mathrm{fix}}(\overline{L}) \to 1$ as $A\to\infty$), extending equivalence via **Corollary 2\*** to weak patience $\beta\theta > 1$ without requiring `(2.3)` ($\beta[q+\theta\delta] > 1$), and formulating a variational ordering criterion for $S_A^{\mathrm{fix}}(1) < S_A$ over optimal/confined extinct paths $\mathcal{O}_-^{\mathrm{fix}}$ ($\chi_p^{\mathrm{fix}} = \Omega(1) > 0$). Verified up to $A = 10^8$ via exact FOC evaluation and continuous-state 880-point normalized Value Function Iteration (VFI, at both $\beta = 0.97$ and $\beta = 0.90$).
3. **Barro–CES Institutional U-Curve & Burden Decomposition (Section 5):**
   - **Theorem 10 & Table 4:** Microfounds Section 4.3 with balanced-budget productive public spending ($\tau_p$) and unproductive compliance overhead ($\tau_u$), deriving the Barro–CES Institutional U-Curve minimized uniquely at $\tau^* = \alpha/(1+\alpha) = \gamma = 0.20$ (for illustrative $A_0 = 1.45, \alpha = 0.25, \theta_0 = 1.20$). Cleanly separates physical extinction traps ($(\tau_{\min}, \tau_{\max}) = (6.60\times 10^{-6}, 0.948649)$ at $A_{\mathrm{rep}} = 0.073485$), the saddle-node threshold $A_{\mathrm{SN}} = 0.0995245$ with $(\tau_{1,\mathrm{SN}}, \tau_{2,\mathrm{SN}}) = (2.219660\times 10^{-5}, 0.930108)$, the global economic viability interval $(\tau_{1,*}, \tau_{2,*}) = (2.227217\times 10^{-5}, 0.930047)$ above $A_* = 0.0996091$ ($A_{\mathrm{rep}} < A_{\mathrm{SN}} < A_*$, with economic extinction occurring on $(A_{\mathrm{rep}}, A_*]$), the Theorem 3 asymptotic envelope $\overline{S}_{\mathrm{asy}}(\tau)$ ($A_e \ge A_{\mathrm{cross}} = 0.110038$, $(\tau_{c1}, \tau_{c2}) = (3.317089\times 10^{-5}, 0.922567)$), Theorem 8's finite-$A$ certified upper bound $\overline{S}_{\mathrm{cert}}(\tau)$ ($A_e \ge 0.749$, $\tau \in [0.117245, 0.304799]$), finite-$A_0$ level-set symmetry $S(\tau_-) = S(\tau_+)$, and the exact asymptotic $S(\tau)$ limit as $A_0 \to \infty$ (noting that global monotonicity of $A \mapsto S_A$ is **not** proved analytically—only asymptotic scaling and finite-$A_0$ level-set symmetry $S(\tau_-) = S(\tau_+)$ are proved).
4. **Structural Extensions & Stochastic Bellman Barriers (Section 6 & Appendix A):**
   - **Propositions 2\*–3\* & Footnote 2:** Formalizes monopolistic competition decentralization with exact factor accounting $(\theta/\mu)Y_t$, a persistent $1/\theta < 1$ marginal wedge opening a decentralized trap already at $\mu = \theta$, and verified $2\times 2$ Jacobian stability across $\mu \in \{1.5, 1.8, 2.0\}$ (both overhead and rebate: $K_{\mathrm{lo}}$ is an unstable spiral source with $|\lambda| \in [1.0694, 1.1412] > 1$, and $K_{\mathrm{hi}}$ is a saddle with $0 < \lambda_1 < 1 < \lambda_2$); firm fragmentation TFP loss $A/N_f^{\theta-1}$ (distinguishing economic extinction at $N_{f,*} = 56.69$ and saddle-node $N_{f,\mathrm{SN}} = 56.79$ from physical extinction at $N_{f,\mathrm{rep}} = 104.17$); unbounded balanced growth in efficiency units eliminating $K_p^+$ (with Red-Queen $\partial Y_t/\partial E_t < 0$ near $S_A$); and continuous piecewise $AK$ Footnote 2 ($V_{\mathrm{AK}}(0.28) \ge +240.76 \gg \Psi^\sharp(0.28) = -27.870334$, invalidating stationary continuation ceilings on $H$).
   - **Lemma 2, Proposition 4\*, & Table 5 (Stochastic FPBB & VFI):** Separates the stochastic framework into **Lemma 2** (pure Doob stopped-supermartingale certificate, $B$ bounded on $[b,\infty)$), **Proposition 4\*** (IEEE-754 `log-PWL` branch-and-bound Doob bounds: box-uniform ruin $T^*(0) = 22$ to $T^*(2\%) = 84$, $p_{\mathrm{cert}} = 2.0434\%$, local patience limit $p_{\mathrm{pat}} = 0.8723\%$, $x^{-1/2}$ tail singularity $p_{\mathrm{sing}} = 1.1217\%$; and coupled $2\times 2$ Markov certificates $(B_G, B_B)$ across $p \in \{0\%, 0.5\%, 1\%, 1.5\%, 2\%, 5\%, 8\%, 12\%\}$ with $p_{\mathrm{cert}}^{\mathrm{Markov}} = 15.45\%$, certified across an 8-subinterval outer $[\beta_-,\beta_+]$ continuum and all $32$ $(4\times 2\times 2\times 2)$ subboxes $\times [\beta_-,\beta_+]$ with positive `B_32bx` margins $\ge +0.0000\text{–}+0.0063$, plus `certify_psi_centered` $x_{\mathrm{lo}}$ discrepancy $\le 0$, $\Psi_\omega' \ge m_\omega$ on every $M$ segment, and uniform Markov escape $\varepsilon_0 = \inf_{x_0 \in M, \omega \in \{G,B\}} \mathbb{P}(\tau \le T_0) \ge 0.0329\text{–}0.0070 > 0$ over $T_0 = 49\text{–}93$ proving $\mathbb{P}(\tau=\infty)=0$ and $\mathbb{E}[\tau]<\infty$), exact $H$-exit and $<b/<h$ scope (Ruin verifies $<b/<h$ slopes, 50-interval $H_1 = [0.28, 0.80)$ covers $\ge +0.338$, and global $H_2 = [0.80, \infty)$ bounds $\ge +2.637$ since $l_0 = 0.57 \ge K/2$ fails for $K > 1.14$; Markov verifies $<b/<h$ slopes for $G,B$, 50-interval $H_1 \ge +0.46$ and $H_2 \ge +2.99$ for $G$, and 32-subbox $\times [\beta_-,\beta_+]$ at $K=0.28$ plus pointwise `ks_wit` over $H_1$ for $B$ due to $(E_B^+)'(0.28) = 14.1259$), and the 880-point continuous golden-section Stochastic VFI policy dichotomy ($S^{\mathrm{ruin}}(p)$ vs. $S_G(p), S_B^{\mathrm{kink}}(p), K_B^*(p)$ and $p_{\mathrm{rec}}$ sensitivity).
   - **Technical Appendix (`A.1–A.4`):** Provides the collision-free notation disambiguation table ($N_f, \mathcal{S}, S^{\mathrm{ruin}}, \varrho, R_t^K, p_{\mathrm{rec}}, \Lambda_a, \Gamma_t$, `MR-Table 4/5`) and explicit numerical reproducibility certificates.

---

## Repository Contents

| File | Description |
| :--- | :--- |
| `mvs_improvements_en.pdf` / `mvs_extension_en.typ` | Complete English manuscript (Sections 1–7 & Technical Appendix A.1–A.4) and Typst source |
| `mvs_mejoras_paper.pdf` / `mvs_extension_es.typ` | Complete Spanish manuscript (Sections 1–7 & Technical Appendix A.1–A.4) and Typst source |
| `mvs_mejoras_paper.tex` | Fully synchronized Spanish LaTeX source (including Technical Appendix A.1–A.4) |
| `verify_results.py` | Standalone numerical, VFI, interval-arithmetic, and stochastic Doob/Markov verification script |
| `generate_figures.py` | Generates all 4 two-panel figures (`fig1`–`fig4`) in ES & EN (`.svg`/`.png`) |
| `fig1_*` – `fig4_*` | Vector (`.svg`) and raster (`.png`) figures embedded in the papers |
| `CITATION.cff`, `.zenodo.json`, `LICENSE`, `requirements.txt` | Citation, Zenodo archiving metadata, dual license (CC BY 4.0 / MIT), and Python dependencies |

---

## Reproduction

```bash
pip install -r requirements.txt

# 1. Verify all analytical interval bounds, Table 1-5 values, FOC, VFI, and stochastic barriers
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
