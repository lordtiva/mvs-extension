#set page(
  paper: "us-letter",
  margin: (x: 1.05in, y: 1.0in),
  numbering: "1",
)
#set text(
  font: "New Computer Modern",
  size: 10.5pt,
  lang: "en",
)
#set par(
  justify: true,
  leading: 0.62em,
  first-line-indent: 1.4em,
)
#show table: set par(justify: false)
#show table: set text(hyphenate: false)
#set heading(numbering: "1.1")
#show heading: it => {
  set text(weight: "bold")
  if it.level == 1 {
    v(1.15em, weak: true)
    block(text(size: 12.5pt, it))
    v(0.55em, weak: true)
  } else if it.level == 2 {
    v(0.9em, weak: true)
    block(text(size: 11pt, it))
    v(0.45em, weak: true)
  }
}

#let thm_box(title, body) = {
  v(0.65em, weak: true)
  block(width: 100%, breakable: true)[
    #set par(first-line-indent: 0pt)
    *#title.* #emph(body)
  ]
  v(0.65em, weak: true)
}

#let proof_block(title: "Proof", body) = {
  v(0.45em, weak: true)
  block(width: 100%, breakable: true)[
    #set par(first-line-indent: 0pt)
    #emph(title + ".") #body #h(1fr) $square.stroked$
  ]
  v(0.65em, weak: true)
}

#align(center)[
  #v(0.15in)
  #text(size: 16.5pt, weight: "bold")[State-Dependent Affine Bellman Barriers, Asymptotic Equivalence, and the Institutional U-Curve]
  #v(0.75em)
  #text(size: 11.5pt)[Analytical Extensions, Sharper Certificates, and Microfoundations on _Minimum Viable Scale_ (Milei and Reidel, 2026)]
  #v(1.1em)
  #text(size: 12pt, weight: "semibold")[Marcelo Segura#footnote[Working Paper (preprint). Analytical development, technical editing, and Python symbolic/numerical verification routines were assisted by AI tools under the author's direction, critical review, and sole responsibility.]]
  #v(0.45em)
  #text(size: 10pt)[November 2026]
  #v(1.1em)
]

#pad(x: 2.0em)[
  #align(center)[*Abstract*]
  #v(0.3em)
  #set text(size: 9.5pt)
  #set par(first-line-indent: 0pt)
  We develop four analytical extensions and quantitative strengthenings for the nonconcave optimal growth model with increasing returns to scale, gross complementarity, and endogenous labor of Milei and Reidel (2026, _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, October 2026 Working Paper). *First*, in the First Passage Bellman Barrier (FPBB) certificate of Section 7.2, we identify an unexploited algebraic slack in their two-period block construction: comparing any staying transition $(x, y) in M times M$ against the reference pair $(h, b)$ at identical labor retains both the initial capital difference $q(h - x)$ and the terminal saving difference $(y - b)$ on _every single edge_. Using a state-dependent one-step affine barrier $B_1 (x)$, we lower the barrier ceiling by nearly five welfare units ($-43.0465$ vs. $-38.1442$), *nearly triple the staying calibration margin* (from $2.564$ to $7.4665$ uniformly and $7.7756$ at $b = 0.10$), and *cut the certified productive entry deadline in half* from $46$ to *$23$ periods* ($24$ uniformly) under the baseline MR-Table 4 / $Psi^sharp$ bounds. We further extend the certificate to the preceding anchor band $M_0 = lr([0.05, 0.10))$ with an explicit bound $tau_(.1) <= 10$ periods (and tighten both bounds via a sharpened $M_0$ witness and continuous $Psi^((0))$ unification to $tau_(.1) <= 9$ and $tau_H <= 21$–$22$ periods), and prove analytically via a Wronskian ratio decomposition and interval arithmetic that the $12$ finite origin subintervals in MR-Table 5 collapse to two boundary checks with no interior minima, raising the adverse-exit margin on $M$ from $0.0436$ to $> 0.0947$ and the global FPBB certificate margin from $0.0423$ ($0.04$) to *$> 0.0571$* ($+35\%$). *Second*, we resolve Footnote 1 of the original paper asymptotically ($A -> infinity$) by proving the finite-$A$ isomorphism $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, formulating a sharp variational condition for $S_A^("fix") (1) < S_A$, and proving under the patience condition that as $A -> infinity$ both endogenous- and fixed-labor rescaled frontiers converge to $s_infinity^* = (delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), corroborated up to $A = 10^8$ by direct value function iteration (VFI). *Third*, we microfound Section 4.3 with productive public spending in the spirit of Barro (1990) ($tau^* = gamma$) and unproductive compliance costs $(tau_p, tau_u)$, separating the physical floor $kappa(tau)$, the Theorem 3 asymptotic envelope $overline(S)_("asy")(tau)$ (empirically valid for $A_e >= A_("cross") = 0.110038$ and violated near economic extinction), Theorem 8's finite-$A$ certified upper bound ($A_e >= 0.749$), level-set symmetry of $S(tau)$ at finite $A_0$, and its asymptotic limit as $A_0 -> infinity$. *Fourth*, we formalize firm decentralization with persistent marginal wedge $1\/mu <= 1\/theta < 1$ (showing that a decentralized underinvestment trap opens already at $mu = theta$ and that fragmenting into $N_f$ units depresses TFP to $A\/N_f^(theta-1)$), unbounded balanced growth in efficiency units, and Stochastic Bellman Barriers via Doob's Optional Stopping Theorem (*Lemma 2* and *Proposition 4\**) over continuous log-PWL super-barriers, deriving the endogenous risk-adjusted deadline $T^*(p)$ (reaching $84$ periods at $p = 2\%$, $bb(P)_("Doob") = 0.1832$, with breakdown at $p_("cert") = 2.0434\%$, vs. the myopic deterministic $23$-period bound), an explicit coupled Markov system $(B_G, B_B)$ certified over 32 parameter sub-boxes across $p in {0\%, dots, 12\%}$, and forward-looking 880-point continuous golden-section Stochastic VFI policy responses. Technical Appendix A compiles the disambiguated notation and IEEE-754 double-precision reproducible certificates.
  #v(0.65em)
  *Keywords.* minimum viable scale; First Passage Bellman Barriers; entry time bounds; endogenous labor; institutional U-curve. \
  *JEL codes.* C61, D24, D61, H21, O41.
]

#v(0.7em)

= Introduction

In _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_ (October 2026 edition; all theorem numbers, constants, and baseline tables cited herein refer to that edition), Milei and Reidel (2026) develop a unified theory of optimal economic survival when aggregate production exhibits increasing returns to scale ($1 < theta < 2$), gross complementarity between capital and labor ($rho = -d < 0$), and endogenous labor supply with logarithmic consumption–leisure preferences ($L in [0, 1]$). Their core classification result shows that under a patience condition ($beta[q + theta delta] > 1$) and sufficiently high productivity ($A > A_*$), a unique Minimum Viable Scale $S_p$ separates optimal extinction from productive survival strictly above the physical maintenance boundary $kappa_p$ (*Theorem 1*). In the intermediate band $(kappa_p, S_p)$, sustaining capital forever with positive consumption and leisure is physically feasible, yet every optimal path depletes capital toward zero because preservation does not repay current consumption and leisure costs. At $S_p$, extinct and productive optima coexist with identical total welfare, producing a strict upward kink in the value function (*Theorem 2*). Moreover, because postponed-liquidation paths approximate optimal initial welfare arbitrarily closely (*Proposition 3*), the authors introduce *First Passage Bellman Barriers* (FPBB) to certify finite entry into a target productive region $H$ and permanence thereafter without solving for the exact value function $V_p (K)$.

While Milei and Reidel (2026) provide a rigorous foundation and a computer-assisted rational verification in Section 7 and Appendix F, close examination of their proofs and explicitly stated open questions uncovers four analytical gaps that can be closed precisely without altering any primitive or assumption of their model:

1. *Joint sharpening of the staying barrier, initial crossing bound, and interval certification of adverse exits (Section 3):* In Theorem 9 of Milei and Reidel (2026), on parameter box (7.3) with staging region $M = lr([0.10, 0.28))$ and target region $H = lr([0.28, infinity))$, no constant regional barrier can satisfy calibration because choosing $b = 0.10$ from near $h = 0.28$ yields higher period reward than optimal lifetime welfare at $b$. To bypass this obstruction, the authors construct a two-period ($N = 2$) block barrier giving $B(K) <= -38.144176$, staying margin $> 2.564$, entry deadline $tau_H <= 46$, and global margin $0.04$ (governed by a minimum of $0.0423$ across Table 5 of Milei and Reidel (2026), hereafter *MR-Table 5*). We prove in *Lemma 1* and *Theorem 9\** that Equation (7.6) discards roughly half of per-edge resource dissipation on every transition $(x, y) in M times M$: a *one-step* affine barrier $B_1 (x)$ retains both terms simultaneously, lowers the barrier ceiling to $-43.046512$, raises the staying margin to *$> 7.4665$* ($> 7.7755$ at $b = 0.10$), and halves the certified entry deadline to *$tau_H <= 23$ periods* ($24$ uniformly). We also close the unbounded initial delay of Figure 6 on $M_0 = lr([0.05, 0.10))$ with *$tau_(.1) <= 10$ periods* (*Proposition 1\**), further unify both intervals via a sharpened $M_0$ witness and continuously certified super-barrier $Psi^((0))$ to *$tau_(.1) <= 9$* and *$tau_H <= 21$–$22$ periods* (*Corollary 1\**), and establish via an analytical interval certificate on the Wronskian and second derivative (*Proposition 1\*\**) that no interior minima exist on $M$ and $H_1$, collapsing the $12$ finite subintervals of MR-Table 5 into two boundary evaluations and lifting the global FPBB certificate margin from $0.0423$ ($0.04$) to *$> 0.0571$* ($+35\%$).
2. *Asymptotic resolution ($A -> infinity$), variational ordering, and finite-productivity isomorphism between endogenous and fixed labor (Section 4):* In Footnote 1 (p. 2), Milei and Reidel (2026) note that comparing the endogenous-labor frontier $S_A$ with the frontier $S_A^("fix") (overline(L))$ of an otherwise identical fixed-labor economy remains open. *Theorem 3\** proves the exact finite-$A$ scaling isomorphism $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, states the precise variational condition under which $S_A^("fix") (1) < S_A$, and proves under the patience condition (2.3) (which implies $beta theta > 1$) that both $A^(1\/r) S_A$ and $A^(1\/r) S_A^("fix") (overline(L))$ converge to the common physical limit $(delta\/c_K)^(1\/r)$, settling $S_A \/ S_A^("fix") (overline(L)) -> 1$ asymptotically as $A -> infinity$, corroborated numerically up to $A = 10^8$ by continuous-state VFI.
3. *Institutional microfoundation and fiscal–regulatory U-curve (Section 5):* In Section 4.3, Milei and Reidel (2026) represent efficiency distortions via an exogenous wedge $A_e = (1 - tau) A$, explicitly cautioning that applying this experiment to taxes or regulation requires accounting for returned revenue and productive benefits. Coupling their CES technology with balanced-budget productive public infrastructure and property-rights enforcement in the spirit of Barro (1990) alongside unproductive compliance waste ($tau = tau_p + tau_u$), *Theorem 10* establishes twin physical extinction traps ($tau < tau_(min)$ and $tau > tau_(max)$) as well as economic extinction regimes ($A_("rep") < A_e < A_* = A_("SN")$), separates the differentiable U-curve of the physical floor $kappa(tau)$ and Theorem 3 asymptotic envelope $overline(S)_("asy")(tau)$ (violated below $A_("cross") = 0.110038$) from Theorem 8's finite-$A$ certified upper bound ($A_e >= 0.749$) minimized uniquely at Barro's rule $tau^* = alpha\/(1+alpha) = gamma$, characterizes level-set symmetry of $S(tau)$ at finite $A_0$ and its exact asymptotic U-profile as $A_0 -> infinity$, and preserves strict monotonicity in unproductive bureaucracy $tau_u$.
4. *Decentralization, unbounded growth, and Stochastic Bellman Barriers (Section 6):* Finally, we extend the deterministic planner framework with stationary ceiling $K_p^+$ along three axes: (i) decentralization under monopolistic competition (Dixit and Stiglitz, 1977) with consistent Euler factor accounting $(theta\/mu) Y_t$ and scale externalities (Romer, 1986), showing that a persistent $1\/mu <= 1\/theta < 1$ marginal wedge opens a decentralized trap already at $mu = theta$ and that fragmenting firms into $N_f$ isolated units reduces aggregate TFP to $A\/N_f^(theta-1)$ (*Proposition 2\**); (ii) labor-augmenting technical progress ($g > 0$), eliminating $K_p^+$ to generate unbounded "hockey-stick" exponential growth while preserving every FPBB certificate in efficiency units (*Proposition 3\**); and (iii) a complete probabilistic FPBB formulation via Doob's Optional Stopping Theorem (*Lemma 2*) and continuously certified log-PWL super-barriers (*Proposition 4\**), replacing fixed deterministic $23$-period bounds with endogenous risk-adjusted Doob deadlines $T^*(p)$ (breaking down at $p_("cert") = 2.0434\%$), a coupled 2-state Markov barrier system $(B_G, B_B)$ certified across $p in {0\%, dots, 12\%}$, and a continuous golden-section stochastic VFI experiment showing how investment, labor supply, and survival thresholds ($S^("ruin")(p)$ vs. $S_G (p), S_B^("kink")(p), K_B^*(p)$) respond differently to irreversible ruin hazard versus recoverable recessions.

The remainder of the paper is organized as follows. Section 2 positions our contributions within the related literature. Section 3 develops the one-step affine barrier, the anchor crossing bound, and the MR-Table 5 reduction. Section 4 resolves Footnote 1 asymptotically ($A -> infinity$) and reports VFI numerical verification. Section 5 derives the institutional U-curve and the $(tau_p, tau_u)$ decomposition. Section 6 presents structural extensions on firm scale, unbounded growth, and stochastic barriers. Section 7 concludes, and Technical Appendix A consolidates our disambiguated notation and numerical reproducibility certificates.

= Related Literature and Theoretical Positioning

Our contributions sit at the intersection of four strands of economic theory and verified optimal control, closing concrete analytical gaps relative to prior work and Milei and Reidel (2026).

== Non-Concave Optimal Growth, Skiba Thresholds, and Poverty Traps

Since the foundational contributions of Skiba (1978), Majumdar and Mitra (1982), and Dechert and Nishimura (1983), non-concave optimal growth theory has shown that increasing returns or convex–concave technologies generate critical indifference thresholds dividing optimal trajectories toward extinction or prosperity. Subsequent work by Mitra and Ray (1984), Kamihigashi and Roy (2007), and Akao, Kamihigashi, and Nishimura (2011) generalized global monotonicity and existence results to non-smooth and non-convex settings in discrete time, later extended to continuous-time Ramsey models by Akao, Ishii, Kamihigashi, and Nishimura (2022). In development macroeconomics, Azariadis and Drazen (1990) and Galor and Zeira (1993) linked threshold externalities and indivisible investments to persistent poverty traps, while Wagener (2020) analyzed tipping-point geometry through indifference manifolds and envelope conditions. Yet as Kraay and McKenzie (2014) emphasize in assessing empirical evidence on poverty traps, classical threshold models typically assume inelastic labor and prove only qualitative asymptotic convergence without bounding finite transition durations. Our *Theorem 9\** and *Proposition 1\** supply explicit finite-time capture deadlines ($tau_(.1) <= 10$ and $tau_H <= 23$ periods, sharpened to $<= 9$ and $<= 21$–$22$ in *Corollary 1\**) for an endogenous-labor economy.

== Endogenous Labor Supply and Factor Complementarity under Increasing Returns

The constant elasticity of substitution (CES) aggregate introduced by Arrow, Chenery, Minhas, and Solow (1961) plays a decisive role when capital and labor are gross complements ($rho < 0$), a regime empirically supported for aggregate production by Klump, McAdam, and Willman (2007). When CES production interacts with endogenous leisure choice, de Hek (1998) proved that consumption–leisure preferences can induce multiple steady states and poverty traps even under convex technology, while Benhabib and Farmer (1994) demonstrated indeterminacy under increasing returns. In Milei and Reidel (2026), combining $1 < theta < 2$, $rho = -d < 0$, and logarithmic leisure utility left the comparison between endogenous-labor and fixed-labor thresholds open (Footnote 1). *Theorem 3\** resolves this comparison analytically via an exact finite-$A$ isomorphism and a singular-scaling proof showing that optimal labor vanishes slower than capital ($K_t\/L_t -> 0$), causing the leisure cost to disappear algebraically as $A -> infinity$.

== Bellman Barriers, Duality, and Stochastic First-Passage Certificates

The FPBB methodology of Milei and Reidel (2026) bridges classical dynamic programming (Bellman, 1957; Stokey, Lucas, and Prescott, 1989) and nonsmooth envelope theorems (Milgrom and Segal, 2002) with finite-time reachability (Bertsekas, 1972), storage functions in dissipative systems (Willems, 1972; Grüne, Müller, Kellett, and Weller, 2021), finite-step Lyapunov iterates (Geiselhart, Gielen, Lazar, and Wirth, 2014; Noroozi, Geiselhart, Grüne, and Wirth, 2020), and American option duality and linear programming optimality (Haugh and Kogan, 2004; Gaitsgory, Parkinson, and Shvartsman, 2019). However, the analytical application in Section 7.2 of Milei and Reidel (2026) relies on $N = 2$ block comparisons with a constant reference—discarding half of per-edge resource dissipation—and discretizes $M union H$ into twelve subintervals in MR-Table 5 to verify adverse-exit bounds. Replacing constant blocks with our one-step affine barrier and proving state-by-state monotonicity (*Proposition 1\*\**) halves the entry deadline and widens the global certificate margin by $35\%$. Moreover, *Lemma 2* and *Proposition 4\** complete the stochastic FPBB program via supermartingales and Doob's Optional Stopping Theorem (Doob, 1953), delivering anticipation-adjusted analytical certificates ($T^*(p)$ and coupled Markov barriers), complemented by continuous stochastic VFI policy experiments.

== Productive Public Goods, Regulatory Distortions, and Market Structure

Section 4.3 of Milei and Reidel (2026) draws on the misallocation and compliance-cost literature—where Restuccia and Rogerson (2008), Hsieh and Klenow (2009), Garicano, Lelarge, and Van Reenen (2016), and Trebbi, Zhang, and Simkovic (2026) document how size-dependent regulations and compliance burdens depress aggregate TFP. As Milei and Reidel explicitly note (p. 10), modeling wedges solely as $A_e = (1 - tau) A$ omits the productive returns of public infrastructure and property-rights enforcement (Barro, 1990; Futagami, Morita, and Shibata, 1993; Acemoglu, Johnson, and Robinson, 2005). *Theorem 10* unifies both mechanisms in $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$, preserving unconditional monotonicity in unproductive waste $tau_u$ while deriving the institutional U-curve in productive taxation $tau_p$. Section 6 further clarifies how decentralization under monopolistic competition (Dixit and Stiglitz, 1977) or aggregate spillovers (Romer, 1986) retains a $1\/theta$ marginal wedge and shows that regulatory fragmentation into $N_f$ isolated firms maps directly into a TFP loss $A\/N_f^(theta-1)$.

= One-Step Affine Bellman Barriers, Entry Deadlines, and Global Certificate Sharpening

== Parameter box and unexploited slack in two-period blocks

Following Section 7 of Milei and Reidel (2026), consider the harmonic CES technology $(theta, rho, w) = (3\/2, -1, 1\/2)$ with production and period utility:
$ F_A (K, L) = A ( (2 K L) / (K + L) )^(3/2), quad u(C, L) = eta log C + (1 - eta) log(1 - L), quad C + K' <= q K + F_A (K, L), $
over parameter box (7.3) of the original paper:
$ A in [0.749, 0.751], quad beta in [0.9699, 0.9701], quad q in [0.9199, 0.9201], quad eta in [0.6999, 0.7001]. $
For staging region $M = lr([b, h)) = lr([0.10, 0.28))$ and target region $H = lr([h, infinity)) = lr([0.28, infinity))$, let $rho.alt(K, s) = max_(0 <= L < 1) {eta log(q K + F_A (K, L) - s) + (1 - eta) log(1 - L)}$ be the reduced one-period return. The rationally verified constants in Equation (7.5) and page 59 of Milei and Reidel (2026) are:
$ hat(R) = -0.996 > rho.alt(h, b), quad Delta_2 = 0.2997 < (eta_- beta_- q_- (h - b)) / (q_+ h + F_(A_+) (h, 1) - b) = 0.2997787, $
with maximal feasible consumption $C_(max) = q h + F_A (h, 1) - b <= C_(max)^+ = 0.37495167$, staging witness floor $W_M (K) >= W_M (b) > -35.579855 > -35.58$, and unrestricted continuation ceiling $Psi^sharp (K) = Psi(K) - 10\/301 >= V(K)$ satisfying $Psi(h) < -27.83$ (and more precisely $Psi(0.28) = -27.837112$, $Psi^sharp (0.28) = -27.870334$).

On page 22 of Milei and Reidel (2026), for two staying transitions $x -> y -> z$ in $M$, the authors bound each edge separately:
$ rho.alt(x, y) <= rho.alt(h, b) - (eta (y - b)) / C_(max), quad rho.alt(y, z) <= rho.alt(h, b) - (eta q (h - y)) / C_(max), $
summing both to obtain $[hat(R) - rho.alt(x, y)] + beta [hat(R) - rho.alt(y, z)] >= Delta_2$ and defining the two-period barrier $B_0 = hat(R)\/(1 - beta) - Delta_2\/(1 - beta^2) <= -38.144176$.

Observe, however, what happens on *any single transition* $(x, y) in M times M$. Let $L in lr([0, 1))$ be the labor level attaining $rho.alt(x, y)$, with consumption $c_0 = q x + F_A (x, L) - y > 0$. Evaluating utility at $(h, b)$ with the exact *same* labor $L$ yields consumption $c_1 = q h + F_A (h, L) - b <= C_(max)$. The exact consumption difference between $(h, b)$ and $(x, y)$ at identical labor is:
$ c_1 - c_0 = q(h - x) + [F_A (h, L) - F_A (x, L)] + (y - b). $
Since $x < h$ and $F_A (dot, L)$ is nondecreasing in capital for all $L in [0, 1]$, $F_A (h, L) - F_A (x, L) >= 0$. Therefore, *both* terms $q(h - x) > 0$ and $(y - b) >= 0$ are present simultaneously on every individual edge $(x, y) in M times M$. By discarding $q(h - x)$ on the first edge and $(z - b)$ on the second, the $N = 2$ disjoint block construction forfeits roughly half of the accumulated dissipation along staying trajectories.

== One-step affine barrier and halved entry deadline

The following lemma formalizes the single-edge loss bound and constructs an explicit affine regional barrier satisfying the Bellman inequality in one step across all of $M$.

#thm_box("Lemma 1 (Unified single-edge loss bound and affine regional barrier on M)")[
  Under parameter box (7.3), every staying transition $(x, y) in M times M = lr([b, h)) times lr([b, h))$ satisfies:
  $ rho.alt(x, y) <= rho.alt(h, b) - eta / C_(max) [q(h - x) + (y - b)] <= hat(R) - eta / C_(max) [q(h - x) + (y - b)]. $
  Consequently, the state-dependent affine function on $M = lr([b, h))$ defined by:
  $ B_1 (x) = B_* - (eta q (h - x)) / C_(max), quad B_* = (hat(R) - Delta_2) / (1 - beta), $
  is a bounded regional Bellman barrier on $M$, i.e., $B_1 (x) >= rho.alt(x, y) + beta B_1 (y)$ for all $x, y in M$. Moreover, uniformly on (7.3):
  $ B_1 (x) <= B_* <= -43.0465116, quad B_1 (b) <= -43.355594, $
  and the calibration margin against the feasible witness $W_M (x)$ satisfies $W_M (x) - B_1 (x) >= W_M (b) - B_1 (b) > 7.7755$ (and uniformly $W_M (x) - B_* > 7.4665$).
]

#proof_block[
  For any $(x, y) in M times M$, let $L in lr([0, 1))$ attain $rho.alt(x, y)$ with consumption $c_0 = q x + F_A (x, L) - y > 0$, and put $c_1 = q h + F_A (h, L) - b <= C_(max)$. Since $(h, b, L)$ is feasible at $(h, b)$ and the leisure term $(1 - eta) log(1 - L)$ cancels, concavity of the logarithm ($log(c_1\/c_0) >= (c_1 - c_0)\/c_1$) and monotonicity $F_A (h, L) >= F_A (x, L)$ give:
  $ rho.alt(h, b) - rho.alt(x, y) >= eta log(c_1 / c_0) >= eta (c_1 - c_0) / c_1 >= eta / C_(max) [q(h - x) + (y - b)]. $
  Substituting $rho.alt(h, b) <= hat(R)$ yields the first inequality. Evaluating $rho.alt(x, y) + beta B_1 (y)$ for any $x, y in M$:
  $ rho.alt(x, y) + beta B_1 (y) &<= hat(R) - (eta q (h - x)) / C_(max) - (eta (y - b)) / C_(max) + beta B_* - (eta beta q (h - y)) / C_(max) \
  &= hat(R) + beta B_* - (eta q (h - x)) / C_(max) - eta / C_(max) [(y - b) + beta q (h - y)]. $
  Because $y in lr([b, h))$ and $beta q < 1$, we have $(y - b) + beta q (h - y) = (1 - beta q)(y - b) + beta q (h - b) >= beta q (h - b)$, bounding the last bracket below by $(eta beta q (h - b))\/C_(max) > Delta_2$. Since $hat(R) - Delta_2 + beta B_* = B_*$ by definition of $B_*$, we conclude $rho.alt(x, y) + beta B_1 (y) <= B_* - (eta q (h - x))\/C_(max) = B_1 (x)$ for all $x, y in M$. On box (7.3), $hat(R) - Delta_2 = -1.2957 < 0$ and $beta >= 0.9699$, yielding $B_* <= -1.2957 \/ 0.0301 = -43.04651162...$ and $(eta q)\/C_(max) >= (0.6999 times 0.9199)\/0.37495167 = 1.717123$, so $B_1 (b) <= -43.0465116 - 1.717123(0.18) = -43.355594$. Finally, since the first-step witness consumption $c_M (x) = q x + F_A (x, 0.68) - 0.135$ satisfies $0 < c_M (x) < C_(max)$ and $F_(A,K) (x, 0.68) > 0$, we have $W'_M (x) = eta[q + F_(A,K) (x, 0.68)]\/c_M (x) > (eta q)\/C_(max) = B'_1 (x)$ on $M$. Hence $W_M (x) - B_1 (x)$ is strictly increasing on $lr([b, h))$ and attains its infimum at $x = b$, giving $inf_(x in M)[W_M (x) - B_1 (x)] = W_M (b) - B_1 (b) > -35.58 - (-43.355594) = 7.775594$.
]

With Lemma 1 established, we prove our sharpened version of Theorem 9 in Milei and Reidel (2026), cutting the certified entry deadline from $46$ to $23$ periods ($24$ under uniform endpoint bounds), as summarized in Table 1.

#thm_box("Theorem 9* (Sharpened CES first passage certificate and halved entry deadline)")[
  Under parameter box (7.3), set $M = lr([0.10, 0.28))$ and $H = lr([0.28, infinity))$.
  1. The affine regional barrier $B_1 (K)$ of Lemma 1 and the feasible witnesses of Table 4 of Milei and Reidel (2026) (hereafter *MR-Table 4*) form a strict First Passage Bellman Barrier (FPBB) certificate with uniform staying margin $> 7.4665$ ($7.7755$ state-by-state) and adverse-exit margin $> 0.0423$ under the original partition (sharpened to $> 0.0571$ in Proposition 1\*\*).
  2. Every optimal history starting in $M$ enters the productive target $H = lr([0.28, infinity))$ by date *$tau_H <= 23$* (or $tau_H <= 24$ using only uniform bounds independent of $K_0$) and remains in $H$ forever. If $K_0 in [0.10, 0.105]$, its first entry date satisfies:
  $ 3 <= tau_H <= 23. $
]

#proof_block[
  Adverse-departure comparisons from $M$ and $H$ into actions below $b$ and $h$ depend only on $W_M, W_H$ and the ceiling $Psi^sharp$, preserving the MR-Table 5 uniform margin $> 0.0423$ (which Proposition 1\*\* improves to $> 0.0571$). By Theorem 5 (global FPBB selection), no optimizer from $M union H$ ever takes an adverse exit or remains forever in $M$.

  To bound the entry deadline $tau_H$, consider any feasible path staying in $M$ for $T >= 1$ consecutive transitions $x_0 -> x_1 -> dots.c -> x_T$ with $x_t in M$ for $0 <= t <= T$, followed by any feasible continuation from $x_T$. Iterating $rho.alt(x_t, x_(t+1)) <= B_1 (x_t) - beta B_1 (x_(t+1))$ for $t = 0, dots, T - 1$ and bounding continuation at $x_T$ via $V(x_T) <= Psi^sharp (x_T) <= Psi(x_T)$ gives:
  $ J_(x_0) (pi) <= B_1 (x_0) + beta^T [Psi^sharp (x_T) - B_1 (x_T)]. $
  On $x in lr([0.10, 0.28))$, the derivative of $Psi^sharp (x) = 0.4 x - 5 x^(-1\/2) - 18.5 - 10\/301$ satisfies $(Psi^sharp)'(x) = 0.4 + 2.5 x^(-3\/2) >= 17.272 > 2 > (eta q)\/C_(max) = B'_1 (x)$, so $Psi^sharp (x_T) - B_1 (x_T)$ is strictly increasing on $lr([b, h))$ and bounded above by $Psi^sharp (h) - B_* < -27.83 - B_*$.
  *Uniform bound ($T = 24$):* Using $B_1 (x_0) <= B_* <= -43.0465116$ and $Psi(h) < -27.83$ from page 59 of Milei and Reidel (2026), at $T = 24$:
  $ J_(x_0) (pi) <= -43.0465116 + (0.9701)^24 (-27.83 - (-43.0465116)) = -43.0465116 + 7.34364 = -35.70287 < -35.58 <= W_M (x_0). $
  *State-matched bound ($T = 23$):* Since $W_M (x_0) - B_1 (x_0)$ is strictly increasing on $lr([b, h))$ by Lemma 1, for all $x_0, x_T in M$:
  $ W_M (x_0) - J_(x_0) (pi) >= [W_M (b) - B_1 (b)] - beta_+^T [Psi(h) - B_*]. $
  At $T = 23$ (exactly half the $46$-period bound of the original paper), we obtain:
  $ W_M (x_0) - J_(x_0) (pi) >= 7.775594 - (0.9701)^23 (15.2165116) = 7.775594 - 7.569980 = +0.205614 > 0. $
  (Using the exact verified values $hat(R) = -0.996799$, $Delta_2 = 0.299778$, and $Psi^sharp (0.28) = -27.870334$ from pages 57–59 of Milei and Reidel, the gap is positive even at $T = 22$ with $+0.0073$). Thus no optimal path can remain in $M$ for $23$ periods, certifying $tau_H <= 23$. The lower bound $tau_H >= 3$ on $[0.10, 0.105]$ follows directly from $Phi(0.105) < 0.16$ and $Phi(0.16) < 0.26 < 0.28$.
]

#figure(
  image("fig1_barrier_en.svg", width: 100%),
  caption: [Comparison between the two-period block barrier of Milei and Reidel (2026) and our one-step affine barrier $B_1 (K)$ on $M = lr([0.10, 0.28))$ under MR-Table 4 and $Psi^sharp$. Panel (a) shows the calibration gain of nearly $5$ welfare units; Panel (b) illustrates the halving of the certified entry deadline from $tau_H <= 46$ to $tau_H <= 23$–$24$ periods.],
)

== Explicit crossing deadline on the anchor band $M_0 = lr([0.05, 0.10))$ and continuous unification

In Figure 6 (p. 21) of Milei and Reidel (2026), crossing from $K_0 > S_A$ to $0.10$ is guaranteed only in finite time ($tau_(.1) < infinity$) with no quantitative bound. Although no uniform deadline can reach $K_0 -> S_A^+$ due to hyperbolic slowdown near the coexistence frontier $S_A$, our one-step affine barrier extends directly to the anchor interval $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, where Theorem 8 already excludes downward exits ($G(K) > K$).

#thm_box([Proposition 1\* (Explicit crossing bound on the preceding anchor band $M_0 = lr([0.05, 0.10))$)])[
  Under parameter box (7.3), set $M_0 = lr([0.05, 0.10))$. Using the MR-Table 4 tail $W_M (0.10) > -35.58$, every optimal history with $K_0 in M_0$ crosses $0.10$ within *$tau_(.1) <= 10$ periods* and enters the productive target $H = lr([0.28, infinity))$ within $tau_H <= 33$ total periods.
]

#proof_block[
  On $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, direct maximization over $L in lr([0, 1))$ gives $rho.alt(0.10, 0.05) <= -1.827072 < hat(R)_0 := -1.827$ (using exact $hat(R)_0 = -1.827072$ yields $B_0^* = -71.048986 <= -71.046512$), maximum consumption $C_(max,0) <= q_+(0.10) + F_(A_+) (0.10, 1) - 0.05 = 0.100233$, and per-step loss bound $Delta^(0) := 0.3115 < (eta_- beta_- q_- (0.05))\/C_(max,0) = 0.311503$. Applying Lemma 1 to $M_0$ yields $B^(0) (x) = B_*^(0) - (eta q (h_0 - x))\/C_(max,0)$ with $B_*^(0) = (hat(R)_0 - Delta^(0))\/(1 - beta) <= -2.1385 \/ 0.0301 = -71.046512$.

  As a feasible witness from any $K_0 in M_0$, we prepend to $W_M (0.10) = -35.579855 > -35.58$ the three-step transition $K_0 -> 0.065 -> 0.0845 -> 0.100$ at constant labor $L = 0.75$ (corresponding to the progression $0.05 -> 0.065 -> 0.0845 -> 0.100$ on p. 46 of Milei and Reidel, extended to all $K_0 in [0.065, 0.10)$ via *temporary liquidation* down to $0.065$ on step 1). Because first-step consumption $c_0 (K_0) = q_- K_0 + F_(A_-) (K_0, 0.75) - 0.065$ is strictly positive and strictly increasing on $[0.05, 0.10)$, the worst-case stage payoffs across box (7.3) occur at $(K_0, A_-, q_-, eta_+)$ with consumptions $(0.002495, 0.006286, 0.022068)$ and exact utilities $(-4.611772, -3.964892, -3.085659)$ (on step 1 from $0.05 -> 0.065$, maximum feasible consumption as $L -> 1$ is $0.003009$ and $max_L u = -4.597860 < -4.59$). Discounting at $beta_+ = 0.9701$ with $W_M (0.10) = -35.579855$ yields a valid strictly increasing witness floor:
  $ W_(M_0) (K_0) >= W_(M_0) (0.05) = -43.844826 > -43.845, quad forall K_0 in lr([0.05, 0.10)). $
  Since $Psi(0.10) < -34.271388$ at $h_0 = 0.10$, after $T_0 = 10$ steps in $M_0$:
  $ B_*^(0) + (0.9701)^10 [Psi(0.10) - B_*^(0)] = -71.046512 + (0.9701)^10 (36.775124) = -43.8997 < -43.845 < W_(M_0) (K_0). $
  Since monotone successor order (F.1) rules out downward exits below $0.05$ from $M_0$, every optimal history from $M_0$ enters $lr([0.10, infinity))$ within $tau_(.1) <= 10$ periods, and by Theorem 9\* reaches $H$ within $10 + 23 = 33$ periods.
]

To tighten both bounds beyond the MR-Table 4 / $Psi^sharp$ baseline without modifying any model primitive, the following corollary replaces the $L = 0.75$ progression with an optimized $M_0$ witness and unifies $M_0$ and $M$ under a single 25-step stationary witness $W_M^((0))$ and a continuously certified global super-barrier $Psi^((0))$ across all $(0, infinity)$.

#thm_box([Corollary 1\* (Sharpened $M_0$ witness and continuous $Psi^((0))$ unification)])[
  Under parameter box (7.3):
  1. Using the three-step feasible path $K_0 -> 0.0595 -> 0.0755 -> 0.100$ with labor $(0.45, 0.50, 0.60)$ (extended over $[0.05, 0.10)$ by temporary liquidation to $0.0595$), the worst-case witness floor improves to $W_(M_0) (K_0) >= -43.540132$ under the MR-Table 4 tail $W_M (0.10) = -35.579855$, and to $-43.500107$ under the 25-step stationary witness $W_M^((0))(0.10; beta_+) = -35.536014$.
  2. The analytical barrier $Psi^((0))(x) = 0.45 x - 5.0 x^(-1\/2) + c_0$ is continuously certified to satisfy $T Psi^((0)) <= Psi^((0))$ on all $(0, infinity)$ across box (7.3) with box-uniform shift $c_(0,"unif") = -18.713835$ ($Psi_("unif")^((0))(0.10) = -34.480223$, $Psi_("unif")^((0))(0.28) = -28.036947$), tightening the certified deadlines to *$tau_(.1) <= 9$* periods uniformly on $M_0$ (via state-to-state comparison against $B^(0)(0.05) = -71.367682$, since $W_(M_0)^("af")(K_0) - B^(0)(K_0)$ strictly increases on $M_0$) and *$tau_H <= 22$* periods on $M$ under independent box endpoints (and *$tau_H <= 21$* periods when $B_1$, $W_M^((0))$, and $Psi^((0))(beta)$ are matched at a common $beta in [0.9699, 0.9701]$), for a combined $0.05 -> H$ deadline of $30$–$31$ periods.
]

#proof_block[
  Evaluating $(0.05 -> 0.0595 -> 0.0755 -> 0.100)$ with $(0.45, 0.50, 0.60)$ at $(A_-, q_-, eta_+)$ gives stage payoffs $(-3.681867, -3.888538, -3.828711)$, whose discounted sum at $beta_+$ yields $-43.540132$ with $W_M (0.10)$ and $-43.500107$ with the 25-step optimal grid witness $W_M^((0))(0.10; beta_+) = -35.536014$ (all stage payoffs negative). Because $c_0 (K_0)$ is strictly increasing on $[0.05, 0.10)$, temporary liquidation gives $W_(M_0) (K_0) >= -43.540132$ uniformly. Next, exact 3D centered-form and monotone interval branch-and-bound on $[8 times 10^(-5), 45.0]$ (giving discrepancy $d(beta_+) in [-0.564473, -0.564273]$), combined with the analytical contraction tail on $(0, 8 times 10^(-5)]$ and upper-tail verification on $[45.0, infinity)$ (margin $>= 1.0433$), certifies $Psi^((0))(x) = 0.45 x - 5.0 x^(-1\/2) + c_0 (beta)$ at $c_0 (beta_+) = -18.855281$ and uniformly across $[beta_-, beta_+]$ at $c_(0,"unif") = -18.713835$ (since $Psi^((0)) < 0$ makes the residual largest at $beta_-$). On $M_0$ at $T_0 = 9$, because $c_0^("af")(K_0) <= 0.0822 < C_(max,0)^+$ implies $W_(M_0)^("af")(K_0) - B^(0)(K_0)$ strictly increases on $[0.05, 0.10)$, state-to-state comparison with $B^(0)(0.05) = -71.367682$ yields $J(9; 0.05) = -43.543050 < -43.540132$, leaving a positive minimum margin $+0.0029$ across all $K_0 in [0.05, 0.10)$ and certifying $tau_(.1) <= 9$. On $M$ using box-uniform independent endpoints ($B_* (beta_-) = -43.0465116$, $B_1 (0.10; beta_-) = -43.355594$), the $T = 21$ slack is $-0.114831$ whereas $T = 22$ gives $+0.122408 > 0$, certifying $tau_H <= 22$; matching $beta in {0.9699, 0.9700, 0.9701}$ consistently across $B_1 (beta)$, $W_M^((0))(beta)$, and $c_0 (beta)$ (e.g., $B_* (0.9701) = -43.339148$, $B_1 (0.10; 0.9701) = -43.648230$) yields $T = 21$ gaps $+0.070042$, $+0.083959$, and $+0.097882$, certifying $tau_H <= 21$.
]

#v(0.3em)
#figure(
  text(size: 9.0pt, table(
    columns: (2.35fr, 1.4fr, 1.4fr, 1.55fr),
    align: (left, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Certified metric on box (7.3)*], [*Milei & Reidel (2026)*], [*Baseline $B_1$ (MR-Tab. 4 / $Psi^sharp$)*], [*U1 Unification ($W_M^((0)), Psi^((0))$)*],
    table.hline(stroke: 0.6pt),
    [Regional reference on $M = lr([0.10, 0.28))$], [Constant ($N = 2$)], [Affine in $K$ ($N = 1$)], [Affine $B_1$ + cont. $Psi^((0))$],
    [Barrier upper bound $B(K)$ on $M$], [$-38.144176$], [$-43.046512$ \ (to $-43.3556$)], [$-43.046512$ \ (to $-43.3556$)],
    [Staying calibration margin ($W_M - B$)], [$> 2.564$], [$> 7.4665$ \ ($> 7.7755$ at $b$)], [$> 7.820$ at $b$ \ ($W_M^((0)) = -35.5360$)],
    [Certified entry deadline from $M$ to $H$ ($tau_H$)], [$<= 46$ periods], [*$<= 23$ periods* \ ($24$ unif.)], [*$<= 21$ (matched $beta$)* \ *$<= 22$ (indep. box)*],
    [Entry window from $K_0 in [0.10, 0.105]$], [$3 <= tau_H <= 46$], [*$3 <= tau_H <= 23$*], [*$3 <= tau_H <= 21$–$22$*],
    [Crossing deadline from $lr([0.05, 0.10))$ to $0.10$], [Finite \ (unbounded)], [*$<= 10$ periods* \ ($W_(M_0) >= -43.8448$)], [*$<= 9$ periods* \ ($W_(M_0) >= -43.5401$)],
    [Total deadline from $K_0 = 0.05$ to $H = lr([0.28, infinity))$], [Finite \ (unbounded)], [*$<= 33$ periods*], [*$<= 30$–$31$ periods*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Quantitative synthesis of analytical improvements over Section 7.2 and Theorem 9 of Milei and Reidel (2026) under identical parameters (7.3): baseline $B_1$ with MR-Table 4 / $Psi^sharp$ (Theorem 9\* and Proposition 1\*) and sharpened U1 unification (Corollary 1\*).],
)

*Exact slack decomposition against the restricted $M$-staying problem (VFI):* To measure how much slack remains between the certified worst-case deadline ($tau_H <= 23$) and optimal dynamics, `verify_restricted_M_vfi` solves the exact $T$-step dynamic program restricted to $M = [0.10, 0.28)$ under the identical MR-Table 4 / $Psi^sharp$ outer bounds. The restricted staying gap $J_T^(*, Psi^sharp)(x_0) - W_M (x_0)$ turns from $+0.028144$ at $T = 8$ to $-0.556742$ at $T = 9$, matching the optimal regional fixed-point barrier $B_("opt")(x) = max_(y in M) {rho.alt^+ (x, y) + beta_- B_("opt")(y)}$ ($B_("opt")(0.10) = -56.794979$, $B_("opt")(0.28^-) = -52.457990$, gap $+0.472857$ at $T = 9$ evaluated at the uniform / worst-case initial state $x_0 = 0.28^-$, where $inf_M (W_M - B_("opt")) = 19.1824$ vs. $21.2151$ at $0.10$). Meanwhile, unrestricted continuous VFI at the box center ($A = 0.75, beta = 0.97, q = 0.92, eta = 0.70$, $V(0.10) = -35.597030$) enters $H$ within *$max_(K_0 in M) tau_H^("VFI")(K_0) = 4$ periods*, and the true restricted DP gap $J_T^(*, "VFI")(x_0) - V(x_0)$ turns strictly negative at $T = 4$ ($-0.173124$, vs. $-0.752234$ at $T = 5$). Thus, out of Milei and Reidel's $46$-period bound, our closed-form affine barrier $B_1$ removes $23$ periods ($46 -> 23$), affine linearization—which drops $F_A (h, L) - F_A (x, L)$ and uses global $C_("max")$—accounts for $14$ periods to the regional optimum ($23 -> 9$), and the outer $(W_M, Psi^sharp)$-to-$V$ wedge accounts for the remaining $5$ periods ($9 -> 4$).

== State-by-state monotonicity of adverse exits and MR-Table 5 reduction

Because $B_1 (K)$ raises the staying calibration margin to $> 7.4665$ ($> 7.7755$ at $b = 0.10$) and the staying prefix margin at $T = 23$ to $+0.2056$, staying transitions on $M$ cease to bind. In MR-Table 5 (Milei and Reidel, 2026, p. 23 and Appendix F.3), adverse-departure comparisons across $M = [0.10, 0.28)$ and $H_1 = [0.28, 0.80)$ partition those domains into $12$ finite subintervals $[k_-, k_+]$, evaluating $underline(W)_X (k_-)$ at the left endpoint against $E^+ (k_+, a; l_0) + beta_- Psi^sharp (a)$ at the right endpoint to obtain a global margin of $0.0423$ (reported as $.04$).

We now prove that interval discretization is unnecessary: evaluated at the *same* state $K$, the witness advantage over the tangent upper bound is strictly increasing in $K$ across all of $M$ and $H_1$, collapsing the $12$ finite rows of MR-Table 5 to just two boundary checks at $K = 0.10$ and $K = 0.28$ and expanding the global certificate margin by $35\%$ (summarized in Table 2).

#thm_box([Proposition 1\*\* (Analytical interval certification of monotonicity and MR-Table 5 collapse)])[
  Under box (7.3), take the MR-Table 4 witnesses of Milei and Reidel (2026) given by $(l_M, s_M, underline(T)_M, a, l_0) = (0.68, 0.135, -33.103, 0.10, 0.44)$ on $M = lr([0.10, 0.28))$ and $(l_H, s_H, underline(T)_H, a, l_0) = (0.72, 0.375, -27.164, 0.28, 0.57)$ on $H_1 = lr([0.28, 0.80))$. The pointwise witness advantage over the adverse-exit envelope (F.19)–(F.20),
  $ Delta_X (K) := underline(W)_X (K) - [E^+ (K, a; l_0) + beta_- Psi^sharp (a)], $
  is strictly increasing across both intervals with no interior minima, and its nonsmooth switches over $eta in [eta_-, eta_+]$ induce only downward kinks in $Delta'_(H_1)$ preserving global concavity. Specifically:
  1. An analytical interval certificate (evaluated in IEEE-754 double precision) on the ratio $R_X (K) = (cal(S)(K) - a)\/c_X (K)$ across $4$ subintervals of $M$ and $6$ of $H_1$ suffices on its own to guarantee uniformly $Delta'_M (K) >= +0.0723 > 0$ on $M$ and $Delta'_(H_1) (K) >= +0.0095 > 0$ on $H_1$ (excluding interior minima); additionally, accounting for the positive curvature $c''_M > 0$ on $[0.10, 0.17)$ ($l_M\/4 = 0.17 in M$), second-derivative interval enclosures verify strict concavity $Delta''_M (K) <= -2.5107 < 0$ (on $8$ subintervals) and $Delta''_(H_1) (K) <= -0.1889 < 0$ (on $10$ subintervals), placing the infimum of $Delta'_X$ at the right boundary:
     $ inf_(K in M) Delta'_M (K) = Delta'_M (0.28^-) = +0.502666, quad inf_(K in H_1) Delta'_(H_1) (K) = Delta'_(H_1) (0.80^-) = +0.100489. $
  2. Consequently, $inf Delta_X$ is attained at the left boundary of each domain, collapsing the $12$ finite subintervals of MR-Table 5 into two boundary evaluations at $K = 0.10$ and $K = 0.28$:
     - On $M = lr([0.10, 0.28))$, the certified adverse-exit margin rises from $> 0.0436$ to *$> 0.0947$* ($+117\%$).
     - On $H_1 = lr([0.28, 0.80))$, the certified margin rises from $> 0.0423$ to $> 0.0561$ ($l_0 = 0.60$) and *$> 0.0571$* ($l_0 = 0.57$), lifting the global FPBB certificate margin across $M union H$ from $0.0423$ ($.04$) to *$> 0.0571$* ($+35\%$).
]

#proof_block[
  Following Appendix F.3 (Equations F.19–F.20 of Milei and Reidel), for each region $X in {M, H_1}$ with witness labor $l_X$, successor $s_X$, tail floor $underline(T)_X$, exit threshold $a$, and tangent labor $l_0 >= sup(X)\/2$, minimum witness consumption is $c_X (K) = q_- K + F_(A_-) (K, l_X) - s_X > 0$, tangent slope is $t(K) = partial_L F_(A_+) (K, l_0)$, and the virtual majorant resource is $cal(S)(K) = q_+ K + F_(A_+) (K, l_0) + (1 - l_0) t(K)$. Notice why $l_0 >= sup(X)\/2$ is exact for global tangency dominance: by homogeneity, $F_A (K, l_0) - l_0 partial_L F_A (K, l_0) = F_A (K, l_0)(l_0 - K\/2)\/(K + l_0) >= 0$ iff $l_0 >= K\/2$, which ensures that the tangent line on the strictly concave region $L > K\/4$ passes above $F_A (K, 0) = 0$ at $L = 0$ and majorizes $F_A (K, L)$ across all $L in [0, 1]$ despite S-shaped convexity on $(0, K\/4)$. At $(K, a, l_0) = (0.28, 0.28, 0.57)$, $l_0 = 0.57 >= 0.80\/2$ holds throughout $H_1$ and $beta_- Psi'(0.28) = beta_- (Psi^sharp)'(0.28) = 16.7535 > 4.6539 = 1\/(cal(S)(0.28) - 0.28)$, so the envelope over $[0.05, a]$ attains its maximum at $s = a$ (the $s = 0$ branch is lower by over $5.37$ on $M$ and $11.77$ on $H_1$). Moreover, the tangent-envelope interior consumption share $u^*(K) = (1 - eta)(cal(S)(K) - a)\/t(K)$ satisfies $u^*(K) in [0.5662, 0.6808] < 1$ on $M$ (implying $L^* >= 0.3192 > 0$) and $u^*(K) in [0.4301, 0.5427] < 1$ on $H_1$ ($L^* >= 0.4573 > 0$), so $u^*(K) in [0.4301, 0.6808] < 1$ everywhere on $M union H_1$. By the variational envelope first-order condition $partial_(l_0) E^+ (K, a; l_0) = 0 <=> l_0 = L_("tan")(K; l_0)$, MR-Table 4's choices $l_0 = 0.57$ on $H_1$ and $l_0 = 0.44$ on $M$ closely track the exact adverse-exit optimizers $L^*(0.28) = 0.569743$ and $L^*(0.10) = 0.437261$ (with $L_("tan")(0.10; 0.44) in [0.433462, 0.433840]$).

  *Exact decomposition of $Delta'_X (K)$ and exclusion of interior minima:* The tangent slope obeys the exact logarithmic identities:
  $ (t'(K)) / (t(K)) = (5 l_0) / (2 K (K + l_0)) > 0, quad ((t'\/t)')(K) = - (5 l_0 (2 K + l_0)) / (2 K^2 (K + l_0)^2) < 0. $
  Differentiating each branch of $underline(W)_X$ and $E^+ (K, a; l_0)$ and setting $R_X (K) := (cal(S)(K) - a)\/c_X (K) > 1$ yields the exact lower bound (valid at smooth points and for both one-sided derivatives at kink points of $min\/max$):
  $ Delta'_X (K) >= (eta_- c'_X (K) R_X (K) - cal(S)'(K)) / (cal(S)(K) - a) + (1 - eta_+) (5 l_0) / (2 K (K + l_0)). $
  To certify $R'_X (K) < 0$, write $R'_X (K) = Q_X (K)\/c_X (K)^2$ with Wronskian $Q_X (K) := cal(S)'(K) c_X (K) - c'_X (K)(cal(S)(K) - a)$, whose derivative cancels $cal(S)' c'$ identically: $Q'_X (K) = cal(S)''(K) c_X (K) - c''_X (K)(cal(S)(K) - a)$. Since $partial_K F_(A,K)(K, L) prop (L - 4K) K^(-1\/2)(K + L)^(-7\/2)$ and $t''(K) prop (3 l_0\/2 - 2K) K^(1\/2)(K + l_0)^(-9\/2)$, both $F_(A,K)$ (unique peak at $L\/4$) and $t'$ (unique peak at $3 l_0\/4$) have no interior minima, while $|Q'_X|$ is bounded on each subinterval $[k_L, k_R]$ by endpoint envelopes of $|F_(A, K K)|$ and $|t''|$. The midpoint Lipschitz bound $Q_X (K) <= Q_X (k_m) + (k_R - k_L)|Q'_X|_([k_L, k_R])\/2$ gives:
  - across the $4$ equal subintervals of $M$ (`[0.100, 0.145, 0.190, 0.235, 0.280]`): $Q_M (K) <= -0.06341, -0.05880, -0.05061, -0.04375 < 0$;
  - across the $6$ subintervals of $H_1$ (`[0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80]`): $Q_(H_1) (K) <= -0.18976, -0.16941, -0.15171, -0.13844, -0.13124, -0.13540 < 0$.
  Thus $R_X (K)$ strictly decreases throughout $M$ and $H_1$, satisfying $R_X (K) >= R_X (k_R)$ on every $[k_L, k_R]$. Bounding $c'_X (K) >= min{c'_X (k_L), c'_X (k_R)}$, $cal(S)'(K) <= cal(S)'_([k_L, k_R], max)$ via unimodality of $F_(A,K)$ and $t'$, and $cal(S)(K) - a$ by its appropriate monotone endpoint yields exact analytical interval lower bounds:
  - on $M$ ($4$ subintervals): $Delta'_M (K) >= +3.0288, +0.3955, +0.1252, +0.0723 > 0$;
  - on $H_1$ ($6$ subintervals): $Delta'_(H_1) (K) >= +1.4675, +0.3243, +0.1022, +0.0348, +0.0095, +0.0119 > 0$.
  This eliminates any grid dependence and rules out interior minima of $Delta_X (K)$. For the second derivative, note that because $l_M \/ 4 = 0.17 in M$, $c''_M (K) = F_(A_-, K K)(K, 0.68) > 0$ on $[0.10, 0.17)$: the worst-case upper bound on $eta c''_X \/ c_X$ therefore uses $eta_+ c''_X \/ c_X (k_L)$ whenever $c''_X > 0$ (on the first four subintervals of $M$) and $eta_- c''_X \/ c_X (k_R)$ whenever $c''_X <= 0$ (for $k_L >= l_X \/ 4$). Incorporating this sign rule into $Delta''_X (K) <= [(cal(S)')^2 - eta_- (c'_X R_X)^2]\/(cal(S) - a)^2 + (eta c''_X\/c_X)^+ - cal(S)''\/(cal(S) - a) + (1 - eta_+)(t'\/t)'(K)$ over $8$ equal subintervals of $M$ and $10$ of $H_1$ certifies $Delta''_M (K) <= -421.1331, -107.5343, -42.3434, -21.2734, dots, -2.5107 < 0$ (uniform max $-2.5107$) and $Delta''_(H_1) (K) <= -40.4320, -12.4955, -5.3078, -2.6661, dots, -0.1889 < 0$ (uniform max $-0.1889$). Moreover, the two nonsmooth $eta$-branch switches inside $H_1$—at $k_W = 0.406819$ ($c_(H_1) = 1 - l_H$, where $W'_(H_1)$ jumps downward from $3.954006$ to $3.952877$) and at $k_E = 0.573570$ ($E^+$ branch switch, where $(-E^+)'$ jumps downward from $-1.652310$ to $-1.652744$)—produce strictly downward kinks in $Delta'_(H_1)$, preserving global concavity. Hence $Delta'_X$ attains its infimum at the right boundary ($Delta'_M (0.28^-) = +0.502666$, $Delta'_(H_1) (0.80^-) = +0.100489$), and $Delta_X$ attains its infimum at the left boundary:
  - At $K = 0.10$: $underline(W)_M (0.10) - [E^+ (0.10, 0.10; 0.44) + beta_- Psi^sharp (0.10)] = 0.094717 > 0.0947$ (and $0.062495 > 0.0624$ using $Psi$).
  - At $K = 0.28$: with $l_0 = 0.60$, $underline(W)_H (0.28) - [E^+ (0.28, 0.28; 0.60) + beta_- Psi^sharp (0.28)] = 0.056121 > 0.0561$; optimizing $l_0 = 0.57$ increases it to $0.057148 > 0.0571$ (and $0.024926 > 0.0249$ using $Psi$).
  Combined with Equation (F.21) on $H_2 = [0.80, infinity)$ ($> 2.2984$), the global certified margin across $M union H$ rises to $> 0.0571$.
]

#v(0.3em)
#figure(
  text(size: 9.2pt, table(
    columns: (1.45fr, 1.85fr, 1.35fr, 1.35fr),
    align: (left, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Region & domain*], [*Comparison method*], [*Margin using $Psi$*], [*Margin using $Psi^sharp$*],
    table.hline(stroke: 0.6pt),
    [$M = lr([0.10, 0.28))$], [Original MR-Table 5 ($4$ intervals)], [$> 0.0114$], [$> 0.0436$],
    [$M = lr([0.10, 0.28))$], [*Prop. 1\*\* at $K = 0.10$* \ *($l_0 = 0.44$)*], [*$> 0.0624$*], [*$> 0.0947$*],
    [$H_1 = lr([0.28, 0.80))$], [Original MR-Table 5 ($8$ intervals)], [$> 0.01008$], [$> 0.0423$],
    [$H_1 = lr([0.28, 0.80))$], [*Prop. 1\*\* at $K = 0.28$* \ *($l_0 = 0.57$)*], [*$> 0.0249$*], [*$> 0.0571$*],
    [$H_2 = lr([0.80, infinity))$], [Global bound Eq. (F.21)], [$> 2.2662$], [$> 2.2984$],
    table.hline(stroke: 0.6pt),
    [*Global FPBB margin*], [*Minimum over $M union H$*], [*$> 0.0249$* \ (vs. $0.01008$)], [*$> 0.0571$* \ (vs. $0.0423$)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Collapse of the $12$ finite subintervals in MR-Table 5 (Milei and Reidel, 2026) via the state-by-state monotonicity of Proposition 1\*\*.],
)

= Asymptotic Equivalence of Endogenous and Fixed Labor (Footnote 1 and Theorem 3)

Footnote 1 of Milei and Reidel (2026, p. 2) notes that comparing the endogenous-labor frontier $S_A$ with the frontier $S_A^("fix") (overline(L))$ of an otherwise identical economy with exogenously fixed labor $L_t equiv overline(L) in lr((0, 1])$ (where period utility is $eta log C_t$) remains an open question. In Section 4.2 (*Theorem 3*, Eq. 4.6), the authors establish that as $A -> infinity$ with $r = theta - 1$ and $c_K = w^(theta\/rho)$:
$ (delta / c_K)^(1/r) <= liminf_(A -> infinity) A^(1/r) S_A <= limsup_(A -> infinity) A^(1/r) S_A <= (D / c_K)^(1/r), quad D = delta + (1 - beta) / beta. $

== Finite-$A$ isomorphism and asymptotic equivalence as $A -> infinity$

We show below that this open question admits an exact asymptotic resolution as $A -> infinity$ for every $overline(L) in lr((0, 1])$, together with a finite-$A$ scaling isomorphism and a sharp comparison condition against full capacity.

#thm_box("Theorem 3* (Fixed-labor isomorphism and asymptotic frontier convergence)")[
  Fix the six primitives other than $A$ in the patient region $E = D - theta delta < 0$, with $d = -rho > 0$ and $r = theta - 1 in (0, 1)$.
  1. *High-productivity regime ($A -> infinity$) and frontier convergence:* Rescaling capital and consumption on the critical scale of Theorem 3, $K_t = A^(-1\/r) k_t$ and $C_t = A^(-1\/r) c_t$ with $k_t, c_t = Theta(1)$, along every interior optimal action at that scale optimal labor and the capital–labor ratio satisfy:
  $ L_t = Theta( A^(- d / (r (1 + d))) ) -> 0, quad K_t / L_t = Theta( A^(- 1 / (r (1 + d))) ) -> 0 quad (A -> infinity). $
  Consequently, on compacts of $(k, L)$, the leisure utility loss vanishes as $(1 - eta)|log(1 - L_t)| = O(A^(-d\/[r(1+d)])) -> 0$ and rescaled output converges uniformly to the same convex limit $c_K k^theta$ as fixed labor $overline(L) in lr((0, 1])$. Moreover, because the patience condition (2.3) necessarily implies $beta theta > beta [q + theta delta] > 1$, for every $overline(L) in lr((0, 1])$ both rescaled frontiers converge to the common physical limit and satisfy strict asymptotic equivalence:
  $ lim_(A -> infinity) A^(1/r) S_A = lim_(A -> infinity) A^(1/r) S_A^("fix") (overline(L)) = ( delta / c_K )^(1/r), quad lim_(A -> infinity) S_A / (S_A^("fix") (overline(L))) = 1. $
  2. *Exact finite-$A$ isomorphism and variational ordering criterion:* For any finite $A$ and fixed labor $overline(L) in lr((0, 1])$, rescaling $tilde(K)_t = K_t \/ overline(L)$ induces an exact isomorphism with the full-capacity economy ($overline(L) = 1$) at productivity $A overline(L)^r$:
  $ S_A^("fix") (overline(L)) = overline(L) dot S_(A overline(L)^r)^("fix") (1), quad kappa_A^("fix") (overline(L)) = overline(L) dot kappa_(A overline(L)^r) >= kappa_A^("fix") (1) = kappa_A. $
  Relative to endogenous labor, full-capacity fixed labor ($overline(L) = 1$ with no leisure cost) strictly dominates in welfare ($V_A^("fix") (K; 1) > V_A (K)$ for all $K > 0$). At $S_A$, let $Delta W_A^+ := J_A^("fix") (pi^+ |_(L=1)) - V_A (S_A) > 0$ be the surplus gained by setting $L equiv 1$ along a productive optimal trajectory $pi^+$ from $S_A$, and let $cal(O)_(-)^("fix")$ denote the class of optimal extinct fixed-labor paths from $S_A$ (or feasible extinct paths confined in $(0, S_A]$ satisfying the uniform consumption floor $C_t^("f") >= chi_p^("fix") K_t^("f")$ with $chi_p^("fix") = Omega(1) > 0$ independent of $A$, excluding deferred-liquidation paths mimicking $pi^+$), with $Delta W_A^- := sup_(pi^- in cal(O)_(-)^("fix")) [J_A^("fix") (pi^-) - V_A (S_A)]$. Then $Delta W_A^- = O(A^(-d\/[r(1+d)]))$, and the strict ordering $S_A^("fix") (1) < S_A$ holds at every $A$ satisfying $Delta W_A^+ > Delta W_A^-$.
]

#proof_block[
  *Part 1 (Operator scaling and frontier convergence).* Set $K = A^(-1\/r) k$ and $C = A^(-1\/r) c$. Using $1 - theta\/r = -1\/r$ and $rho = -d < 0$:
  $ f_A (k, L) := A^(1/r) F_A (A^(-1\/r) k, L) = c_K k^theta [1 + c_w (k / (A^(1\/r) L))^d]^(-theta/d), quad c_w = (1 - w) / w. $
  With fixed labor $L equiv overline(L) in lr((0, 1])$, $(A^(1\/r) overline(L))^(-d) = O(A^(-d\/r)) -> 0$ and $f_A (k, overline(L)) -> c_K k^theta$. With endogenous labor, multiplying the interior first-order condition $F_(A,L)(K, L) = nu C\/(1 - L)$ ($nu = (1 - eta)\/eta$) by $A^(1\/r)$ yields:
  $ theta c_K c_w k^(theta + d) A^(-d/r) L^(-1 - d) [1 + c_w (A^(1/r) L / k)^(-d)]^(-1 - theta/d) = nu c / (1 - L), $
  requiring $L = [theta c_K c_w k^(theta + d)\/(nu c)]^(1\/(1+d)) A^(-d\/[r(1+d)])(1 + o(1)) -> 0$ and $K\/L = Theta(A^(-1\/[r(1+d)])) -> 0$, so $f_A (k, L) = c_K k^theta [1 + O(A^(-d\/[r(1+d)]))]$, $(1 - eta)log(1 - L) = -O(A^(-d\/[r(1+d)]))$ and the normalized Bellman operator converges on compacts to the fixed-labor limit.

  To prove convergence of the frontiers themselves, observe that for $q in (0, 1)$ and $theta > 1$, $theta - (q + theta delta) = q(theta - 1) > 0$. Hence patience condition (2.3), $beta[q + theta delta] > 1$, necessarily implies $beta theta > 1$. Fix any rescaled stock $k_0 > (delta\/c_K)^(1\/r)$ and set $K_0 = A^(-1\/r) k_0$. Construct a feasible expansion at constant labor $L_0 = 3\/4$ in the endogenous-labor model and $L_0 = 1$ in the fixed-labor full-capacity economy ($overline(L) = 1$, and analogously for any $overline(L) in (0, 1)$ via the finite-$A$ isomorphism):
  - Choose $epsilon_1 in (0, 1)$ with $c_K (1 - epsilon_1) k_0^r > delta$ and a small fixed macroscopic threshold $K_("esc") > 0$ (independent of $A$) such that $[1 + c_w (K_("esc")\/L_0)^d]^(-theta\/d) >= 1 - epsilon_1\/2$, ensuring $f_A (k, L_0) >= c_K (1 - epsilon_1\/2) k^theta$ whenever $K_t <= K_("esc")$.
  - *Phase I (bottleneck escape):* Consuming half of net surplus above $k_t$ reaches in $T_1 (k_0) < infinity$ periods (independent of $A$) a fixed level $k_1 >= max{2, (2 \/ [c_K (1 - epsilon_1\/2)])^(1\/(theta - tilde(theta)))}$, having fixed $tilde(theta) in (beta^(-1), theta)$ (possible since $beta theta > 1$).
  - *Phase II (superexponential climb):* Saving half of total resources ($C_t = K_(t+1) = [q K_t + F_A (K_t, L_0)]\/2$) yields $k_(t+1) >= k_t^(tilde(theta))$ while $k_t <= A^(1\/r) K_("esc")$, reaching $K_(T_1 + J) >= K_("esc")$ within $J(A) <= (log log A)\/(log tilde(theta)) + O(1)$ steps, and stepping down on date $T_1 + J$ to $K_("esc")$ (absorbing any excess into consumption).
  - *Phase III (macroscopic plateau):* For $t >= T_1 + J$, holding $K_("esc")$ yields consumption $A f_1 (K_("esc"), L_0) - delta K_("esc") = Omega(A)$, delivering discounted payoff at least $beta^(T_1 + J) (eta\/(1 - beta)) log A - O(1)$.

  On dates $0 <= t < T_1 + J(A)$, $C_t = A^(-1\/r) c_t$ with $c_t = Omega(1)$ yields $u(C_t, L_0) >= -(eta\/r) log A - O(1)$, so Phase I and Phase II sum to $-(1 - beta^(T_1 + J)) (eta\/[r(1 - beta)]) log A - O(1)$ (with error uniformly bounded in $J(A)$ since $sum_(t=0)^infinity beta^t = 1\/(1 - beta)$). Adding Phase III and subtracting Lemma 9's resource upper bound on $(0, K_0]$ (with growth factor $G_A (K_0) = q + F_A (K_0, 1)\/K_0 -> q + c_K k_0^r = O(1)$, bounding every path confined to $(0, K_0]$ from above by $-(eta\/[r(1 - beta)]) log A + O(1)$) cancels the $-(eta\/[r(1 - beta)]) log A$ term identically. Using $1 + 1\/r = theta\/r$ and $beta^(J(A)) >= c_0 (log A)^(-|log beta|\/log tilde(theta))$, the net surplus over any extinct optimum scales at least as:
  $ beta^(T_1 + J(A)) (theta eta) / (r(1 - beta)) log A - O(1) >= c_1 (log A)^(1 - |log beta|\/log tilde(theta)) - O(1) -> +infinity $
  because $beta tilde(theta) > 1 => 1 - |log beta|\/log tilde(theta) > 0$. By Theorem 1, no optimum can become extinct from $K_0 = A^(-1\/r) k_0$ for large $A$, so $limsup_(A -> infinity) A^(1\/r) S_A <= (delta\/c_K)^(1\/r)$ (and identically for $S_A^("fix") (overline(L))$). Combined with the lower physical bound (4.5) in Theorem 3 and (2.4) for $kappa_A^("fix") (overline(L))$, both frontiers converge to $(delta\/c_K)^(1\/r)$ and their ratio tends to $1$.

  *Part 2 (Finite-$A$ isomorphism and variational criterion).* Degree-$theta = 1 + r$ homogeneity implies $F_A (overline(L) tilde(K), overline(L)) = overline(L) F_(A overline(L)^r) (tilde(K), 1)$ and $eta log(overline(L) tilde(C)_t) = eta log tilde(C)_t + eta log overline(L)$, establishing the exact isomorphism. By Theorem 1, at $K_0 = S_A$ a productive optimum $pi^+$ and an extinct optimum attain $V_A (S_A)$. Setting $L equiv 1$ (without leisure disutility) along $pi^+$ is feasible under fixed labor and yields $V_A^("fix") (S_A; 1) >= J_A^("fix") (pi^+ |_(L=1)) = V_A (S_A) + Delta W_A^+$. Conversely, for any optimal (or confined) decreasing extinct path $pi^- = (C_t^("f"), K_(t+1)^("f"))_(t>=0) in cal(O)_(-)^("fix")$ with $K_t^("f") <= S_A <= c_+ A^(-1\/r)$ for all $t >= 0$, consumption for $s >= t + 1$ satisfies $C_s^("f") <= G_("max") K_t^("f")$ with $G_("max") = q + c_K c_+^r <= 1\/beta + o(1)$. Hence $V_A^("fix")(K_t^("f"); 1) <= eta log C_t^("f") + frac(beta eta, 1 - beta) log(G_("max") K_t^("f"))$, whereas the feasible cake-eating policy delivers $V_("cake")(K_t^("f")) = frac(eta, 1 - beta) log((1 - beta) q K_t^("f")) + frac(beta eta, (1 - beta)^2) log(beta q)$. Comparing $V_A^("fix")(K_t^("f"); 1) >= V_("cake")(K_t^("f"))$ cancels $log K_t^("f")$ identically and establishes the uniform lower bound $C_t^("f") \/ K_t^("f") >= chi_p^("fix") := [(1 - beta) q]^(1\/(1 - beta)) (beta q)^(beta\/(1 - beta)^2) G_("max")^(-beta\/(1 - beta)) approx 2.07 times 10^(-106) > 0$ at $G_("max") = 1\/beta$ (or, tightening the continuation bound via the linear-$A K$ problem with return $G_("max")$ on $K_(t+1)^("f") <= K_t^("f")$, $chi_p^("fix") := (1 - beta) q (beta q)^(beta\/(1 - beta)) (q\/G_("max"))^(beta\/(1 - beta)^2) approx 3.60 times 10^(-57) > 0$), both strictly positive and independent of $A$ ($Omega(1)$). Pairing $(K_t^("f"))$ with endogenous labor $tilde(L)_t = c_0 A^(-d\/[r(1+d)])$ and consumption $tilde(C)_t = C_t^("f") - [F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)] > 0$ bounds the relative output shortfall at every date $t >= 0$ by:
  $ (F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)) / C_t^("f") <= C_1 A (K_t^("f"))^r (K_t^("f") / tilde(L)_t)^d = O(A^(- d / (r(1+d)))), $
  with $C_1 = O(1)$, matching the order of the leisure cost $(1 - eta)|log(1 - tilde(L)_t)| = O(tilde(L)_t)$. Discounting and summing gives $V_A (S_A) >= J_A^("endo") (pi^- |_(tilde(L))) >= J_A^("fix") (pi^-) - C_2 A^(-d\/[r(1+d)])$, hence $Delta W_A^- = O(A^(-d\/[r(1+d)]))$. Whenever $Delta W_A^+ > Delta W_A^-$, $J_A^("fix") (pi^+ |_(L=1)) > sup_(cal(O)_(-)^("fix")) J_A^("fix") (pi^-)$, ruling out optimal extinction at $S_A$ and forcing $S_A^("fix") (1) < S_A$.
]

#thm_box([Corollary 2\* (Weakening patience condition (2.3) to $beta theta > 1$)])[
  Assume only $beta in (0, 1)$ and *$beta theta > 1$*, without requiring the stronger condition (2.3) ($beta[q + theta delta] > 1$). Defining the general survival and extinction thresholds $S_A^- := inf{K_0 > 0 : "some optimum from " K_0 " survives"}$ and $S_A^+ := sup{K_0 > 0 : "some optimum from " K_0 " becomes extinct"}$ (and analogously $S_A^("fix", plus.minus) (overline(L))$), we have $kappa_A <= S_A^- <= S_A^+$ and both converge asymptotically to the same physical limit:
  $ lim_(A -> infinity) A^(1/r) S_A^- = lim_(A -> infinity) A^(1/r) S_A^+ = lim_(A -> infinity) A^(1/r) S_A^("fix", plus.minus) (overline(L)) = (delta / c_K)^(1/r). $
]

#proof_block[
  With $L_t <= 1$ and $rho < 0$, the bounded production asymptote $F_A (K, 1) < A (1 - w)^(theta\/rho)$ confines all feasible capital to a compact interval $[0, K_("max")]$ and guarantees existence of optimal policies for every $beta in (0, 1)$. By supermodularity of $rho.alt(x, y)$ (Dechert and Nishimura, 1983; Lemma 5 of Milei and Reidel, 2026), which does not depend on (2.3), every optimal sequence $(K_t^*)$ is monotone in time. Hence any optimal path that extinguishes ($K_t^* -> 0$) from $K_0$ is monotone nonincreasing and confined to $(0, K_0]$, obeying Lemma 9's resource bound. Since the three-phase expansion in Theorem 3\*(1) requires only $tilde(theta) in (beta^(-1), theta)$—feasible under $beta theta > 1$—for every $k_0 > (delta\/c_K)^(1\/r)$ and sufficiently large $A$ it strictly outperforms all paths confined to $(0, A^(-1\/r) k_0]$, ruling out optimal extinction and proving $limsup_(A -> infinity) A^(1\/r) S_A^+ <= (delta\/c_K)^(1\/r)$. The physical lower bound $liminf_(A -> infinity) A^(1\/r) S_A^- >= lim_(A -> infinity) A^(1\/r) kappa_A = (delta\/c_K)^(1\/r)$ is purely technological (independent of $beta$), closing the common limit. Moreover, for $A$ sufficiently large (or whenever a surviving optimal path above $kappa_A$ exists), strict supermodularity of $rho.alt(x, y)$ combined with the envelope theorem implies $V'_("surv")(x) = rho.alt_x (x, g^+(x)) > rho.alt_x (x, g^-(x)) = V'_("ext")(x)$ at any coexistence point, forcing a single Skiba threshold $S_A^- = S_A^+$ (as verified by VFI at $beta = 0.90$).
]

== Numerical verification of the first-order condition and VFI frontiers

Figure 2 and Table 3 distinguish two complementary verification layers for the harmonic CES benchmark ($theta = 3\/2, d = 1, r = 1\/2, beta = 0.97, q = 0.92, eta = 0.70$) across $A in [0.75, 10^8]$: (i) evaluating the exact interior labor condition $L^*_A$ at the fixed rescaled benchmark $(k, c) = (0.002, 10^(-4))$, where $A dot L^*_A$ converges toward $0.133074$ while leisure cost and output gap vanish at rate $O(A^(-1))$; and (ii) *solving the cake-normalized Bellman equation directly (VFI)* via continuous interpolation over an $880$-point three-zone grid in $k = A^2 K$ ($360$ uniform nodes in $[0.00078, 0.00102]$ plus $25$-point local Skiba-crossing refinement, with dynamic modified-golden-rule steady-state bracketing scaling as $A^(2.5)$) to compute the actual survival thresholds $A^2 S_A^("fix") (1)$ and $A^2 S_A^("endo")$. Across the entire grid $A in [0.75, 10^8]$, VFI confirms $S_A^("fix") (1) < S_A^("endo")$ (consistent with Part 2's variational condition, as the productive surplus stays strictly positive in $Delta W_A^+ in [0.29, 8.70]$) and shows the frontier ratio $S_A^("endo") \/ S_A^("fix") (1)$ converging monotonically toward $1$ (from $1.01997$ at $A = 0.75$ down to $1.00125$ at $A = 100$, $1.00090$ at $A = 10^3$, and $1.00039$ at $A = 10^8$; doubling the grid to $1760$ points shifts this ratio by less than $2.3 times 10^(-5)$ at both $A = 100$ and $A = 10^8$). Moreover, because $beta theta = 1.455 > 1$, the joint approach of $A^2 S_A$ toward the physical floor $(delta\/c_K)^2 = 0.000800$ proceeds at an ultraslow logarithmic rate $O(1\/log log A)$, reaching $0.000848$ at $A = 10^3$ and $0.000835$ at $A = 10^8$. To corroborate Corollary 2\* directly where (2.3) fails, VFI at $beta = 0.90$ ($beta[q + theta delta] = 0.936 < 1 < beta theta = 1.35$, where $(D\/c_K)^2 = 0.004565$) confirms a single Skiba threshold descending steadily toward $(delta\/c_K)^2 = 0.000800$ while the ratio approaches $1$: $(A^2 S_A^("fix")(1), A^2 S_A^("endo"), "ratio")$ moves from $(0.002038, 0.002153, 1.05642)$ at $A = 1.5$ to $(0.001909, 0.001919, 1.00508)$ at $A = 100$ and $(0.001727, 0.001731, 1.00191)$ at $A = 10^8$.

#figure(
  image("fig2_scaling_en.svg", width: 100%),
  caption: [Asymptotic scaling and direct VFI frontier resolution of Footnote 1 ($theta = 3\/2, d = 1, r = 1\/2$). Panel (a) displays $kappa_A$, the Theorem 8 finite-$A$ certified band $0.0014025025 A^(-2)$, and actual VFI thresholds $S_A^("endo")$ and $S_A^("fix") (1)$ over $A in [0.75, 100]$ ($A^(-2)$ scaling); Panel (b) plots both exact FOC trajectories evaluated at fixed $(k, c) = (0.002, 10^(-4))$ ($A^(-1)$ and $A^(-2)$ decay) and the VFI-computed frontier gap $S_A^("endo")\/S_A^("fix") (1) - 1 -> 0$.],
)

#v(0.2em)
#figure(
  text(size: 7.7pt, table(
    columns: (0.55fr, 1.12fr, 0.78fr, 1.12fr, 0.75fr, 0.78fr, 0.88fr, 0.90fr, 0.92fr, 0.65fr),
    align: (center, center, center, center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [$A$], [$kappa_A$], [$A^2 kappa_A$], [$L^*_A$ \ $(k, c)$], [$A L^*_A$], [$F_A$ gap], [$A^2 S_A^("fix") (1)$ \ (VFI)], [$A^2 S_A^("endo")$ \ (VFI)], [$S_A^("endo") \/ S_A^("fix") (1)$ \ (VFI)], [$Delta W_A^+$],
    table.hline(stroke: 0.6pt),
    [$0.75$], [$1.428 times 10^(-3)$], [$0.000803$], [$1.583 times 10^(-1)$], [$0.11874$], [$3.276\%$], [$0.000875$], [$0.000893$], [*$1.01997$*], [$8.70$],
    [$1.50$], [$3.559 times 10^(-4)$], [$0.000801$], [$8.380 times 10^(-2)$], [$0.12571$], [$1.570\%$], [$0.000868$], [$0.000877$], [*$1.01089$*], [$5.24$],
    [$3.00$], [$8.891 times 10^(-5)$], [$0.000800$], [$4.311 times 10^(-2)$], [$0.12934$], [$0.768\%$], [$0.000864$], [$0.000869$], [*$1.00621$*], [$3.19$],
    [$10.0$], [$8.000 times 10^(-6)$], [$0.000800$], [$1.319 times 10^(-2)$], [$0.13194$], [$0.227\%$], [$0.000859$], [$0.000862$], [*$1.00279$*], [$1.46$],
    [$30.0$], [$8.889 times 10^(-7)$], [$0.000800$], [$4.423 times 10^(-3)$], [$0.13270$], [$0.075\%$], [$0.000856$], [$0.000857$], [*$1.00172$*], [$0.94$],
    [$100.0$], [$8.000 times 10^(-8)$], [$0.000800$], [$1.330 times 10^(-3)$], [$0.13296$], [$0.023\%$], [$0.000853$], [$0.000854$], [*$1.00125$*], [$0.66$],
    [$10^3$], [$8.000 times 10^(-10)$], [$0.000800$], [$1.331 times 10^(-4)$], [$0.13306$], [$0.002\%$], [$0.000848$], [$0.000848$], [*$1.00090$*], [$0.53$],
    [$10^8$], [$8.000 times 10^(-20)$], [$0.000800$], [$1.331 times 10^(-9)$], [$0.13307$], [$0.000\%$], [$0.000835$], [$0.000835$], [*$1.00039$*], [$0.29$],
    table.hline(stroke: 0.6pt),
    [$-> infinity$], [$-> 0$], [*$0.000800$*], [$-> 0$], [*$0.133074$*], [*$0\%$*], [*$0.000800$*], [*$0.000800$*], [*$1.00000$*], [$> 0$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Joint numerical verification of Theorem 3\* under the harmonic CES benchmark: columns 2–6 at the FOC point $(k, c) = (0.002, 10^(-4))$ and columns 7–10 via direct 880-point VFI computation of both survival frontiers and productive surplus ($c_K = 2 sqrt(2)$, $(delta\/c_K)^2 = 0.000800$).],
)

= Regulation, Taxation, and Public Infrastructure: The Institutional U-Curve

== Barro–CES microfoundation and Theorem 10

In Section 4.3 of Milei and Reidel (2026), the authors study a permanent loss of productive efficiency of the form $A_e = (1 - tau) A$ with $tau in (0, 1)$, proving in Proposition 2 that the sustainable interval $[kappa(A_e), K^+(A_e)]$ shrinks monotonically with $tau$ and collapses to the empty set when $tau > tau^* := 1 - A_("rep")\/A$. The authors explicitly note on page 10 that applying this experiment to taxes or regulation requires accounting for returned revenue and productive benefits.

To close this gap analytically without sacrificing one-sector tractability, we incorporate the classic institutional channel of Barro (1990) under a period-by-period balanced public budget. Suppose the government levies a total wedge $tau = tau_p + tau_u in (0, 1)$ on gross output $Y_t$, allocating $G_t = tau_p Y_t$ to productive public infrastructure, courts, and property-rights enforcement, while $tau_u Y_t$ represents unproductive public spending or pure regulatory compliance overhead. If productive public goods $G_t$ enter aggregate output with elasticity $gamma in (0, 1)$ alongside a private CES aggregator of degree $theta_0$:
$ Y_t = tilde(A)_0 G_t^gamma [w K_t^rho + (1 - w) L_t^rho]^(theta_0 / rho), quad G_t = tau_p Y_t, $
solving for $Y_t$ shows that net disposable private income $(1 - tau_p - tau_u) Y_t$ takes *the exact functional form (2.1) of Milei and Reidel (2026)*:
$ Y_t^("priv") = (1 - tau_p - tau_u) Y_t = A_e (tau_p, tau_u) [w K_t^rho + (1 - w) L_t^rho]^(theta / rho), $
where the effective scale exponent is $theta := theta_0 \/ (1 - gamma)$, the induced institutional elasticity is $alpha := gamma \/ (1 - gamma) > 0$, base capacity is $A_0 := tilde(A)_0^(1\/(1-gamma))$, and net effective productivity equals:
$ A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u) quad ("and without deadweight waste " tau_u = 0, quad A_e (tau) = A_0 tau^alpha (1 - tau)). $
Notably, this microfoundation also explains the emergence of aggregate increasing returns ($theta > 1$): even under constant private returns ($theta_0 = 1$), fiscal feedback from productive public infrastructure ($gamma in (0, 1\/2)$) endogenously generates $theta = 1\/(1 - gamma) in (1, 2)$. Moreover, substituting $alpha = gamma \/ (1 - gamma)$ gives the exact Barro (1990) optimal rule $tau^* = alpha \/ (1 + alpha) = gamma$. (In the numerical illustration of Table 4 we preserve $theta = 3\/2$ for direct comparability with the harmonic CES benchmark while setting $gamma = tau^* = 0.20$ and $alpha = 0.25$, which corresponds to $theta_0 = theta(1 - gamma) = 1.20$; conversely, $theta_0 = 1$ with $theta = 3\/2$ would correspond to $gamma = 1\/3, alpha = 1\/2$.)

Because $A_e (tau)$ enters solely as a multiplicative productivity scalar in (2.1), *every* structural theorem of Milei and Reidel (2026)—Proposition 1 and Theorems 1–3—transfers verbatim via composition with the unimodal curve $A_e (tau)$ for a *fiscal planner* internalizing $G_t = tau_p Y_t$.

#thm_box([Theorem 10 (Institutional U-curve of certified bounds, symmetry, and $S(tau)$ limit)])[
  Consider an economy with effective productivity $A_e (tau) = A_0 tau^alpha (1 - tau)$, where $alpha = gamma\/(1 - gamma) > 0$ and the remaining six primitives satisfy the patience condition (2.3). Define the unique optimal Barro institutional burden:
  $ tau^* = alpha / (1 + alpha) = gamma in (0, 1), quad A_(max) := A_e (tau^*) = A_0 alpha^alpha / (1 + alpha)^(1 + alpha). $
  1. *Twin physical extinction thresholds (Anarchy vs. Hyper-regulation):* Letting $Lambda_a := sup_(K > 0) F_1 (K, 1)\/K = delta\/A_("rep")$, if $A_(max) > A_("rep")$, there exist exactly two critical burdens $0 < tau_(min) < tau^* < tau_(max) < 1$, unique roots of $tau^alpha (1 - tau) = A_("rep") \/ A_0$, such that:
     - For $tau in (0, tau_(min))$ (*anarchy / state-deficit trap*) and $tau in (tau_(max), 1)$ (*confiscatory / over-regulation trap*), the physically sustainable set is empty ($cal(M)(tau) = emptyset$) and every feasible history contracts geometrically to extinction: $K_t <= [q + A_e (tau) Lambda_a]^t K_0 -> 0$.
     - For $tau in (tau_(min), tau_(max))$, the sustainable interval $[kappa(tau), K^+(tau)]$ is nonempty, attains maximum width at $tau = tau^*$, and $kappa(tau)$ traces an exact differentiable U-curve minimized uniquely at $tau^*$ ($partial log kappa(tau)\/partial tau < 0$ for $tau < tau^*$ and $> 0$ for $tau > tau^*$).
  2. *Economic extinction band and distinction between asymptotic envelope $overline(S)_("asy")(tau)$, certified bound $overline(S)_("cert")(tau)$, and true frontier $S(tau)$:* Suppose $A_(max) > A_* = A_("SN")$ (the endogenous saddle-node threshold above which survival optima exist), and let $(tau_1, tau_2) subset (tau_(min), tau_(max))$ be the open viability interval where $A_e (tau) > A_*$. On the sub-bands $(tau_(min), tau_1]$ and $[tau_2, tau_(max))$ where $A_("rep") < A_e (tau) <= A_*$, *economic extinction* holds: $cal(M)(tau) != emptyset$, yet no survival threshold $S(tau)$ exists and every optimal path extinguishes. On $(tau_1, tau_2)$, a unique continuous frontier $S(tau) > kappa(tau)$ exists; as Milei and Reidel (2026, pp. 10 and 20) emphasize, $S_A = Theta(A^(-1\/(theta-1)))$ gives order bounds but does not establish differentiability, monotonicity, or finite-$A$ validity of the asymptotic constant at low $A$. Separating the three levels rigorously:
     - *(a) Asymptotic envelope $overline(S)_("asy")(tau)$ vs. Theorem 8 finite-$A$ certified bound $overline(S)_("cert")(tau)$:* Any scaled power envelope $overline(S)(tau) := overline(c)_+ [A_e (tau)]^(-1\/(theta - 1))$ traces a smooth, strictly convex U-curve on $(tau_1, tau_2)$ minimized uniquely at $tau^* = gamma = alpha\/(1+alpha)$ with exact closed-form log-derivative:
       $ partial / (partial tau) log overline(S)(tau) = - 1 / (theta - 1) [ alpha / tau - 1 / (1 - tau) ] = (tau - tau^*) / ((theta - 1)(1 - tau^*) tau (1 - tau)). $
       Crucially, Theorem 3's asymptotic envelope $overline(S)_("asy")(tau) := (D\/c_K)^(1\/(theta-1)) [A_e (tau)]^(-1\/(theta-1))$ (tabulated in our Table 4) is an *asymptotic* benchmark that empirically bounds true VFI $S(tau)$ for $A_e (tau) >= A_("cross")$ ($0.110038$ in the harmonic calibration), *but is violated by $S(tau)$ when $A_* < A_e (tau) < A_("cross")$* near $tau_1$ and $tau_2$. By contrast, Theorem 8's explicit finite-$A$ certified upper bound $overline(S)_("cert")(tau) := 0.0014025025 thin [A_e (tau)]^(-2) = (0.03745)^2 [A_e (tau)]^(-2)$ is mathematically certified only on the high-productivity subinterval where $A_e (tau) >= 0.749$ ($tau in [0.117245, 0.304799]$ in Table 4).
     - *(b) Level-set symmetry of the true frontier $S(tau)$ at every finite $A_0$:* Because $S(tau) = S_(A_e (tau))$ depends on $tau$ solely through the unimodal scalar $A_e (tau)$, every burden $tau_- in (tau_1, tau^*)$ has a unique conjugate $tau_+ in (tau^*, tau_2)$ with $A_e (tau_-) = A_e (tau_+)$ and identical true frontier ($S(tau_-) = S(tau_+)$), while the U-shaped localization band $kappa(tau) < S(tau) < 1.75 kappa(tau)$ holds wherever Theorem 8 applies ($A_e (tau) >= 0.749$).
     - *(c) Exact asymptotic U-curve of $S(tau)$ ($A_0 -> infinity$):* By Theorem 3\* ($lim_(A -> infinity) A^(1\/(theta-1)) S_A = s_infinity^* := (delta\/c_K)^(1\/(theta-1))$), the rescaled true frontier converges uniformly on compact subsets of $(0, 1)$ to the exact differentiable profile:
       $ lim_(A_0 -> infinity) A_0^(1/(theta-1)) S(tau) = s_infinity^* [tau^alpha (1 - tau)]^(-1/(theta-1)), $
       whose unique global minimum occurs at the optimal Barro rate $tau^* = alpha\/(1 + alpha) = gamma$.
]

#proof_block[
  The function $g(tau) = tau^alpha (1 - tau)$ is strictly log-concave on $(0, 1)$, with logarithmic derivative $g'(tau)\/g(tau) = alpha\/tau - 1\/(1 - tau) = (tau^* - tau)\/[(1 - tau^*) tau (1 - tau)]$. Hence $g(tau)$ strictly increases on $(0, tau^*)$, attains its unique global maximum at $tau^* = alpha\/(1+alpha) = gamma$, and strictly decreases on $(tau^*, 1)$, vanishing at both endpoints. If $A_(max) = A_0 g(tau^*) > A_("rep")$, the intermediate value theorem yields two unique roots $tau_(min) in (0, tau^*)$ and $tau_(max) in (tau^*, 1)$ of $A_e (tau) = A_("rep")$, and similarly $(tau_1, tau_2)$ for $A_e (tau) = A_* = A_("SN")$. Applying Proposition 1 of Milei and Reidel at $A = A_e (tau)$ gives part 1, and implicit differentiation in Eq. (4.2) of the original paper yields:
  $ (partial log kappa(tau)) / (partial tau) = - 1 / (theta s(kappa(tau)) - 1) (partial log A_e (tau)) / (partial tau) = (tau - tau^*) / ([theta s(kappa(tau)) - 1](1 - tau^*) tau (1 - tau)), $
  which is strictly negative on $(tau_(min), tau^*)$ and strictly positive on $(tau^*, tau_(max))$ since $theta s(kappa) - 1 > 0$. For part 2(a), differentiating $log overline(S)(tau) = log overline(c)_+ - (theta - 1)^(-1) log A_e (tau)$ yields the exact log-derivative identity and strict log-convexity (second derivative $> 0$), while Theorem 8 transfers finite-$A$ certification exclusively wherever $A_e (tau) >= 0.749$ (and continuous VFI reveals the finite-$A$ crossing below $A_("cross")$ between $A_*$ and $0.749$). For 2(b), strict unimodality of $A_e (tau)$ yields two unique preimages for every level $A in (A_*, A_(max))$. For 2(c), substituting $A = A_0 tau^alpha (1 - tau)$ into the limit $A^(1\/(theta-1)) S_A -> (delta\/c_K)^(1\/(theta-1))$ proved in Theorem 3\* establishes uniform convergence on any compact $[underline(tau), overline(tau)] subset (0, 1)$ to the exact asymptotic U-curve.
]

_Remark (Fiscal planner vs. decentralized $G_t$ externality)._ Substituting $G_t = tau_p Y_t$ into $Y_t$ prior to solving the dynamic program characterizes a *fiscal planner* who internalizes $G_t$'s social scale elasticity $theta = theta_0 \/ (1 - gamma)$. If instead decentralized firms and households treat aggregate public infrastructure $G_t$ as an external spillover (matching the constant-private-returns case $theta_0 = 1$), private after-tax marginal products retain an extra $(1 - gamma) = 1\/(1 + alpha)$ wedge relative to the planner's reduced form: Barro's rule $tau^* = gamma$ still maximizes private incentives, yet the decentralized survival frontier lies strictly above $S_(A_e (tau))$ (analogous to the $1\/theta$ wedge in Proposition 2\*).

== Productive vs. unproductive burden decomposition and quantitative synthesis

Decomposing the total burden into productive spending ($tau_p$) and unproductive compliance or bureaucratic overhead ($tau_u$) via $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$ yields two complementary policy laws unifying Milei and Reidel's original Proposition 2 with our institutional U-curve:

1. *Monotonicity in unproductive waste $tau_u$:* For any fixed level of institutional provision $tau_p$, $partial A_e \/ partial tau_u = -A_0 tau_p^alpha < 0$ contracts the sustainable interval ($partial kappa \/ partial tau_u > 0$ and $partial overline(S)_("asy") \/ partial tau_u > 0$ *everywhere*, $partial overline(S)_("cert") \/ partial tau_u > 0$ on $A_e >= 0.749$, and $partial S \/ partial tau_u > 0$ in the $A_0 -> infinity$ limit), recovering Proposition 2 of Milei and Reidel (2026) along $tau_u$.
2. *U-curve and crowding-out on productive provision $tau_p$:* For fixed $tau_u in lr([0, 1))$, the productive tax maximizing $A_e (tau_p, tau_u)$ and minimizing $kappa(tau_p, tau_u)$, $overline(S)_("asy")(tau_p, tau_u)$, and $overline(S)_("cert")(tau_p, tau_u)$ is $tau_p^* (tau_u) = frac(alpha, 1 + alpha) (1 - tau_u) = gamma(1 - tau_u)$, where peak productivity scales as $A_e^* (tau_u) prop (1 - tau_u)^(1 + alpha)$ and the minimal envelope scales as $overline(S)^* (tau_u) = overline(c)_+ A_e^* (tau_u)^(-1\/(theta - 1)) prop (1 - tau_u)^(-(1+alpha)\/(theta-1))$. Thus, cutting $tau_u$ and rolling back excessive regulation ($tau_p > tau_p^*$) sharply lowers survival barriers, whereas on the left branch ($tau_p < tau_p^*$) basic property rights and infrastructure remain indispensable to escape the anarchy trap.

In the harmonic CES benchmark ($A_0 = 1.45, alpha = 0.25, gamma = 0.20$), physical viability requires $A_e > A_("rep") = 0.073485$, yielding physical extinction roots $tau_(min) = 6.60 times 10^(-6)$ and $tau_(max) = 0.948649$. However, the endogenous saddle-node threshold is $A_* = A_("SN") = 0.0995245$, so economic survival exists only on $(tau_1, tau_2) = (2.219660 times 10^(-5), 0.930108)$, while continuous VFI confirms both economic extinction ($S(tau)$ nonexistent) on $(tau_(min), tau_1]$ and $[tau_2, tau_(max))$ (e.g., `survives = False` at $tau = 2.0 times 10^(-5)$ with $A_e = 0.096965$ and at $tau = 0.94$ with $A_e = 0.085665$) and asymptotic-bound crossing at $A_("cross") = 0.110038$, i.e., $(tau_(c,1), tau_(c,2)) = (3.317089 times 10^(-5), 0.922567)$. Theorem 8's finite-$A$ certification ($A_e >= 0.749$) applies across $[0.117245, 0.304799]$, as displayed in Figure 3 and Table 4.

#figure(
  image("fig3_ucurve_en.svg", width: 100%),
  caption: [Institutional extension of Section 4.3 ($A_e (tau) = A_0 tau^alpha (1 - tau)$ with $A_0 = 1.45, alpha = 0.25, tau^* = gamma = 0.20, A_("rep") = 0.0735, A_* = A_("SN") = 0.0995$). Panel (a) contrasts net productivity with public infrastructure against the pure linear wedge $A(1-tau)$, marking physical extinction ($tau_(min) = 6.60 times 10^(-6)$, $tau_(max) = 0.9486$), economic extinction ($tau_1 = 2.22 times 10^(-5)$, $tau_2 = 0.9301$), and Theorem 8's threshold $A_e >= 0.749$; Panel (b) contrasts $kappa(tau)$, the dashed Theorem 3 asymptotic envelope $overline(S)_("asy")(tau) = (D\/c_K)^2 A_e (tau)^(-2)$, the solid VFI frontier $S(tau)$ (crossing above $overline(S)_("asy")$ below $A_("cross") = 0.110038$, at $tau_(c,1) = 3.317 times 10^(-5)$ and $tau_(c,2) = 0.9226$), and Theorem 8's finite-$A$ certified bound $0.0014025025 A_e (tau)^(-2)$ on $[0.117245, 0.304799]$.],
)

#v(0.2em)
#figure(
  text(size: 8.9pt, table(
    columns: (0.85fr, 0.85fr, 0.85fr, 1.0fr, 1.15fr, 2.2fr),
    align: (center, center, center, center, center, left),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [Burden $tau$], [$A_e (tau)$], [$A_e (tau) \/ A_("rep")$], [$kappa(tau)$], [$overline(S)_("asy")(tau)$], [Institutional regime],
    table.hline(stroke: 0.6pt),
    [$5.0 times 10^(-6)$], [$0.0686$], [$0.93$], [—], [—], [Global physical extinction ($cal(M) = emptyset$)],
    [$2.0 times 10^(-5)$], [$0.0970$], [$1.32$], [$0.119322$], [— ($0.163590^*$)], [*Economic extinction ($cal(M) != emptyset$, $S(tau)$ nonexistent; $A_e < A_*$)*],
    [$0.02$], [$0.5344$], [$7.27$], [$0.002825$], [$0.005386$], [Left branch (under-provision; $A_e >= A_("cross")$)],
    [$0.05$], [$0.6514$], [$8.86$], [$0.001896$], [$0.003625$], [Infrastructure expansion],
    [$0.10$], [$0.7339$], [$9.99$], [$0.001492$], [$0.002856$], [Near institutional optimum],
    [*$0.20$ ($tau^*$)*], [*$0.7757$*], [*$10.56$*], [*$0.001335$*], [*$0.002556$*], [*Unique optimum; Thm 8 certified ($overline(S)_("cert") = 0.002331$)*],
    [$0.40$], [$0.6919$], [$9.42$], [$0.001680$], [$0.003213$], [Right branch (excessive burden)],
    [$0.60$], [$0.5105$], [$6.95$], [$0.003099$], [$0.005903$], [Severe interval contraction],
    [$0.80$], [$0.2743$], [$3.73$], [$0.010990$], [$0.020448$], [Acute viability erosion],
    [$0.90$], [$0.1412$], [$1.92$], [$0.045887$], [$0.077114$], [Near collapse threshold],
    [$0.94$], [$0.0857$], [$1.17$], [$0.178378$], [— ($0.209599^*$)], [*Economic extinction ($cal(M) != emptyset$, $S(tau)$ nonexistent; $A_e < A_*$)*],
    [$0.95$], [$0.0716$], [$0.97$], [—], [—], [Global physical extinction ($cal(M) = emptyset$)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Quantitative classification of institutional regimes under Theorem 10 in the harmonic CES benchmark ($A_0 = 1.45, alpha = 0.25, gamma = 0.20, A_("rep") = 0.073485, A_* = A_("SN") = 0.0995245, tau_(min) = 6.60 times 10^(-6), tau_(max) = 0.948649$). Column 5 reports the Theorem 3 asymptotic envelope $overline(S)_("asy")(tau) = (D\/c_K)^2 A_e (tau)^(-2)$ (empirically valid above $A_("cross") = 0.110038$, i.e., $tau in [3.317 times 10^(-5), 0.922567]$); starred values at $tau = 2.0 times 10^(-5)$ and $0.94$ indicate the algebraic formula in the economic-extinction zone where $cal(M)(tau) != emptyset$ yet $S(tau)$ does not exist. Theorem 8's finite-$A$ bound $overline(S)_("cert")(tau) = 0.0014025025 A_e (tau)^(-2)$ holds on $tau in [0.117245, 0.304799]$ ($A_e >= 0.749$).],
)

= Structural Extensions: Firm Decentralization, Unbounded Growth, and Stochastic Barriers

Whereas policy debates around minimum viable scale center on firm scale, antitrust fragmentation, sustained "hockey-stick" growth, and macroeconomic crises, the baseline mathematical model of Milei and Reidel (2026) assumes a deterministic central planner bounded by a stationary ceiling $K_p^+$. We show below how to embed all three dimensions into their architecture—highlighting both exact isomorphisms where they hold and persistent marginal wedges or ceiling breaks where they do not.

== Decentralization, market power, and the cost of firm fragmentation

With increasing returns $theta in (1, 2)$, Euler's theorem gives $K F_(A,K) + L F_(A,L) = theta F_A (K, L) > F_A (K, L)$, so perfectly competitive price-taking firms without externalities would suffer operating losses $(1 - theta) Y_t < 0$. Two canonical decentralizations support technology (2.1): (i) *monopolistic competition or symmetric oligopoly* (Dixit and Stiglitz, 1977) with markup $mu >= theta > 1$, where factors earn $R_t^K = (1\/mu) F_(A,K)$ and $w_t = (1\/mu) F_(A,L)$ while the remaining fraction $(1 - theta\/mu) Y_t >= 0$ covers fixed operating costs or profits; or (ii) *aggregate scale externalities* (Romer, 1986), where individual firms face constant private returns while aggregate scale lifts TFP.

#thm_box("Proposition 2* (Firm-scale decentralization, marginal wedge, and fragmentation)")[
  Under CES technology (2.1) with $theta in (1, 2)$ and $r = theta - 1 > 0$:
  1. *Regulatory or antitrust fragmentation theorem:* Splitting aggregate inputs $(K_t, L_t)$ across $N_f >= 1$ isolated symmetric firms ($K_(i,t) = K_t \/ N_f$, $L_(i,t) = L_t \/ N_f$) contracts aggregate output exactly as:
  $ Y_t^((N_f)) = sum_(i=1)^(N_f) F_A (K_t / N_f, L_t / N_f) = N_f dot N_f^(-theta) F_A (K_t, L_t) = F_(A \/ N_f^r) (K_t, L_t). $
  Thus, fragmenting firm scale into $N_f$ units is *mathematically isomorphic* to depressing TFP to $A_("ef") (N_f) = A \/ N_f^(theta - 1)$, scaling up Minimum Viable Scale by a factor $N_f$ asymptotically ($S_A (N_f) = Theta(N_f dot S_A)$), triggering *economic extinction* ($cal(M)(N_f) != emptyset$ with no survival threshold) once $N_f > N_(f,"SN") := (A \/ A_*)^(1\/(theta - 1))$ ($56.79$ firms at $A = 0.75, theta = 1.5$), and causing *global physical extinction* ($cal(M)(N_f) = emptyset$) whenever $N_f >= N_(f,"rep") := (A \/ A_("rep"))^(1\/(theta - 1))$ ($104.17$ firms).
  2. *Exact factor accounting and persistent decentralized underinvestment wedge:* Under monopolistic competition with markup $mu >= theta > 1$ and factor prices $R_t^K = (1\/mu) F_(A,K)$, $w_t = (1\/mu) F_(A,L)$, Euler's theorem implies that aggregate factor income received by households equals:
  $ R_t^K K_t + w_t L_t = theta / mu F_A (K_t, L_t) = F_(A_("mkt")) (K_t, L_t), quad A_("mkt") := theta / mu A <= A. $
  However, price-taking households optimize against the linear budget $C_t + K_(t+1) <= (q + R_t^K) K_t + w_t L_t + Pi_t$, facing private marginal returns $R_t^K = (1\/theta) F_(A_("mkt"),K)$ and $w_t = (1\/theta) F_(A_("mkt"),L)$ rather than the social marginal products of $F_(A_("mkt"))$.
  - *(Fixed-overhead / zero-net-profit closure, $Pi_t = 0$):* Even when fixed operating costs absorb $(1 - theta\/mu) Y_t$ so household income matches $F_(A_("mkt"))(K_t, L_t)$, *no Bellman isomorphism holds with Milei and Reidel's planner at $A_("mkt")$*: a persistent $1\/theta < 1$ marginal wedge distorts the private Euler equation $1\/C_t = beta(q + R_(t+1)^K)\/C_(t+1)$ and labor FOC $(1 - eta)\/(1 - L_t) = (eta\/C_t) w_t$. Consequently, a decentralized underinvestment trap $[S_A, S^("eq")(mu))$ with $S^("eq")(mu) > S_(A_("mkt")) >= S_A$ opens *already at $mu = theta$*, where $K_("lo")(mu)$ denotes the lower unstable steady state on the stable manifold converging to $K_("hi")(mu)$ (so every monotonic trajectory toward $K_("hi")(mu)$ requires $K_0 >= K_("lo")(mu)$, fixing $S^("eq")(mu) >= K_("lo")(mu)$; at $mu = theta = 1.5$, $A_("mkt") = A$ and overhead vanishes with $K_("lo") = 0.003039 > S_A = 0.001587$), matching the same $1\/theta$ wedge present under Romer (1986) CRS spillovers.
  - *(Lump-sum profit rebate closure, $Pi_t = (1 - theta\/mu) Y_t$):* When pure profits are rebated lump-sum to households ($partial Pi_t \/ partial K_t = 0$), the aggregate resource constraint preserves $F_A (K_t, L_t)$ and the algebraic Euler and labor FOCs retain the marginal factor wedge $1\/mu <= 1\/theta < 1$. For $mu > theta$, positive rebates $Pi_t > 0$ raise $C_t$ relative to fixed-overhead absorption, lowering equilibrium labor $L_t$ via the leisure wealth effect and depressing $R_(t+1)^K$, which further expands the decentralized trap ($K_("lo")^("rebate") > K_("lo")^("overhead") > S_(A_("mkt"))$, e.g., $0.004670 > 0.004490 > 0.002302$ at $mu = 1.8$).
]

#proof_block[
  Degree-$theta = 1 + r$ homogeneity of $F_A (K, L) = A [w K^rho + (1 - w) L^rho]^(theta\/rho)$ implies $F_A (K\/N_f, L\/N_f) = N_f^(-theta) F_A (K, L)$. Summing across $N_f$ firms yields $Y_t^((N_f)) = N_f^(1-theta) F_A (K, L) = F_(A N_f^(-r)) (K, L)$. Applying Proposition 1, Theorem 1, and Theorem 3 of Milei and Reidel at $tilde(A) = A N_f^(-r)$ establishes physical extinction iff $A N_f^(-r) <= A_("rep")$ ($N_f >= 104.17$ at $A = 0.75$), economic extinction iff $A N_f^(-r) <= A_* = A_("SN") = 0.0995245$ ($N_f >= 56.79$), and threshold scaling $S_(tilde(A)) = Theta(tilde(A)^(-1\/r)) = N_f dot Theta(A^(-1\/r))$. Next, Euler's identity $K F_(A,K) + L F_(A,L) = theta F_A (K, L)$ implies total factor payments equal $(theta\/mu) F_A (K_t, L_t) = F_(A_("mkt")) (K_t, L_t)$ with $A_("mkt") = (theta\/mu) A$. Because individual price-taking households solve against $(q + R_t^K) K_t + w_t L_t + Pi_t$ with $R_t^K = (1\/mu) F_(A,K) = (1\/theta) F_(A_("mkt"),K)$ and $w_t = (1\/mu) F_(A,L) = (1\/theta) F_(A_("mkt"),L)$, the $1\/theta < 1$ wedge persists at every $mu >= theta > 1$, so decentralized steady-state/saddle-point dynamics do not coincide with the planner Bellman operator at $A_("mkt")$ ($1\/mu <= 1\/theta < 1$ relative to $F_A$). Evaluating the exact decentralized steady-state system in the harmonic CES benchmark yields $K_("lo") = 0.003039 > S_A = 0.001587$ already at $mu = theta = 1.5$, $(K_("lo"), K_("hi")) = (0.004490, 1.558817)$ vs. $(0.004670, 1.390019)$ at $mu = 1.8$, and $(0.005644, 1.423495)$ vs. $(0.006055, 1.171530)$ at $mu = 2.0$ (all strictly above planner VFI $S(A_("mkt"))$).
]

== Eliminating the stationary ceiling $K_p^+$ and "hockey-stick" growth

In Milei and Reidel's baseline model, $L_t <= 1$ and $rho < 0$ impose an output asymptote $F_A (K, 1) < A (1 - w)^(theta\/rho)$, creating a stationary ceiling $K_p^+ < infinity$. Introducing labor-augmenting technical progress at rate $g > 0$ eliminates $K_p^+$ and yields perpetual exponential growth while leaving every verified constant intact in efficiency units (whereas switching to an endogenous learning-by-doing $A K$ regime on $H$ fundamentally alters the continuation value on $H$, as detailed in Footnote 2).

#thm_box("Proposition 3* (Balanced-growth isomorphism and unbounded exponential takeoff)")[
  Suppose labor-augmenting technical progress evolves as $E_t = (1 + g)^t$ ($g > 0$) with aggregate production homogeneous of degree $1$ in $(K_t, E_t)$:
  $ Y_t = (1 + g)^t F_A ( K_t / (1 + g)^t, L_t ) = A (1 + g)^((1 - theta) t) [w K_t^rho + (1 - w) ((1 + g)^t L_t)^rho]^(theta / rho). $
  In efficiency units $hat(K)_t = K_t \/ (1 + g)^t$ and $tilde(C)_t = C_t \/ (1 + g)^(t+1)$, the resource constraint reduces exactly to:
  $ tilde(C)_t + hat(K)_(t+1) <= tilde(q) hat(K)_t + F_(tilde(A)) (hat(K)_t, L_t), quad tilde(q) := q / (1 + g), quad tilde(A) := A / (1 + g), $
  while period utility differs from $u(tilde(C)_t, L_t)$ only by an additive policy-independent constant $eta [(t + 1) log(1 + g)]$. Consequently:
  1. The dynamic problem in $(hat(K)_t, tilde(C)_t, L_t)$ is *100% identical* to Milei and Reidel's economy with parameters $(tilde(A), beta, tilde(q), eta, theta, rho, w)$, possessing a unique relative threshold $hat(S)_p > hat(kappa)_p$.
  2. For $K_0 < hat(S)_p$, the economy enters the liquidation trap ($hat(K)_t -> 0$). For $K_0 > hat(S)_p$, $hat(K)_t$ enters the productive band $hat(H) = lr([hat(h), hat(K)_p^+])$ in finite time (within $tau_H <= 23$ periods from $M$ whenever $(tilde(A), beta, tilde(q), eta)$ lies in box 7.3), implying unbounded exponential growth in real levels forever:
  $ K_t = (1 + g)^t hat(K)_t >= (1 + g)^t hat(h) -> infinity quad (t -> infinity). $
]

#proof_block[
  Dividing $C_t + K_(t+1) <= q K_t + (1 + g)^t F_A (K_t \/ (1 + g)^t, L_t)$ by $(1 + g)^(t+1)$ immediately yields $tilde(C)_t + hat(K)_(t+1) <= tilde(q) hat(K)_t + F_(tilde(A)) (hat(K)_t, L_t)$. Because $sum_(t=0)^infinity beta^t eta (t + 1) log(1 + g) < infinity$ is independent of $(hat(K)_(t+1), L_t)$, optimal paths of $hat(K)_t$ coincide pointwise with the stationary economy at $(tilde(A), tilde(q))$.#footnote[If instead one replaces exogenous $E_t$ with endogenous knowledge spillovers (Romer, 1986) where effective labor is $Gamma_t L_t$ ($Gamma_t = 1$ on $K_t < h$ and $Gamma_t = K_t \/ h$ on $H = lr([h, infinity))$), the stationary Section 3 geometry and constants do *not* remain unaltered: substituting $Gamma_t L_t = (K_t \/ h) L_t$ directly into the $theta = 3\/2$ CES aggregator produces superlinear $K_t^(3\/2)$ growth and infinite value ($V = +infinity$ since $beta theta = 1.455 > 1$), whereas dropping $theta$ abruptly to $1$ on $H$ induces a $+51.2\%$ upward output jump at $(h, 1) = (0.28, 1)$ ($0.217034 -> 0.328125$). Restoring continuity across $K = h$ requires the piecewise $A K$ technology $Y_t = (K_t \/ h) F_A (h, L_t)$ on $H$; even then, optimizing constant $(s, L)$ at $h = 0.28$ gives $V_("AK")(0.28) >= +240.7598 >> Psi^sharp (0.28) = -27.870334$, invalidating the stationary continuation ceiling $Psi^sharp$ on $H$ and requiring a re-derived non-stationary ceiling and re-calibrated exit bounds.]
]

== Macroeconomic uncertainty and Stochastic Bellman Barriers (Doob's Theorem)

A major methodological advantage of First Passage Bellman Barriers (Section 6 of Milei and Reidel, 2026) over deterministic monotonicity proofs (Dechert and Nishimura, 1983) is that regional barrier inequalities extend naturally to stochastic environments via martingale theory and *Doob's Optional Stopping Theorem* (Doob, 1953). However, plugging the risk-free deterministic horizon $T^* = 23$ into an ex-post survival expression $(1 - p)^23$ implicitly assumes myopic optimizers acting with $beta = 0.97$ ($p = 0$), ignoring how forward-looking agents who anticipate annual crisis risk $p > 0$ alter their investment policy $K'^((p)) (K)$, labor supply $L^((p)) (K)$, and effective impatience.

To separate pure analytical results, computer-assisted certificates, and quantitative VFI evidence cleanly, we structure this extension across three layers: (1) a general stopped-supermartingale result (*Lemma 2*); (2) continuous `log-PWL` computational certificates for endogenous deadlines $T^*(p)$ under ruin risk and the coupled $2 times 2$ Markov barrier system $(B_G, B_B)$ across $32$ parameter sub-boxes (*Proposition 4\**); and (3) an 880-point continuous golden-section stochastic VFI experiment (Table 5) uncovering the behavioral policy dichotomy between ruin risk and recoverable recessions.

#thm_box("Lemma 2 (Stochastic FPBB Supermartingale Certificate and Doob's Optional Stopping)")[
  Let $(omega_t)_(t>=0)$ be a Markovian macroeconomic shock process on $(Omega, cal(F), bb(P))$ affecting primitives each period, under the integrability condition $sup_(t <= T) bb(E)[ |V(K_(t and tau), omega_(t and tau))| ] < infinity$ for every finite horizon $T >= 1$. Let $B : lr([b, infinity)) times Omega -> bb(R)$ be a measurable function bounded on $[b, h)$ satisfying the one-step Bellman inequality for every staying action in $M = lr([b, h))$ and every upward-exit action into $H = lr([h, infinity))$:
  $ B(K, omega) >= rho.alt(K, omega, a) + beta bb(E) [ B(K', omega') | K, omega, a ] quad (K in M, K' >= b). $
  Consider any policy that avoids exits below $b$ (i.e., $K_tau >= b$ almost surely at the stopping time $tau = inf{t >= 0 : K_t in.not M}$, where $[b, infinity)$ lies in the domain of $B$) and satisfies $bb(E)[sum_(j=0)^((t and tau) - 1) beta^j |rho.alt_j| ] < infinity$. Then the stopped process $Z_(t and tau) := beta^(t and tau) B(K_(t and tau), omega_(t and tau)) + sum_(j=0)^((t and tau) - 1) beta^j rho.alt_j$ is an integrable *supermartingale* with respect to the natural filtration $cal(F)_t$. By Doob's Optional Stopping Theorem, for every horizon $T >= 1$:
  $ bb(E)_(x_0, omega_0) [J(pi)] <= B(x_0, omega_0) + bb(E)_(x_0, omega_0) [ beta^(T and tau) ( V(K_(T and tau), omega_(T and tau)) - B(K_(T and tau), omega_(T and tau)) ) ]. $
]

#proof_block[
  On ${tau > t}$, the extended Bellman inequality for $K in M$ and $K' >= b$, the exclusion $K_tau >= b$ a.s., and integrability give $bb(E)[Z_((t+1) and tau) - Z_(t and tau) | cal(F)_t] = beta^t bb(1)_(tau > t) { rho.alt(K_t, omega_t, a_t) + beta bb(E)[B(K_(t+1), omega_(t+1)) | cal(F)_t] - B(K_t, omega_t) } <= 0$, so $(Z_(t and tau))$ is an integrable stopped supermartingale and Doob's Optional Stopping Theorem at $T and tau$ yields the value bound immediately.
]

#thm_box("Proposition 4* (Computational Certificates for Endogenous Deadlines T*(p) and Coupled Markov Barriers)")[
  Applying Lemma 2 over parameter box (7.3) using continuously certified `log-PWL` super-barriers on $(0, infinity)$:
  1. *Endogenous Doob deadline $T^*(p)$ under anticipated ruin/expropriation hazard ($tilde(beta)_p := beta(1 - p)$):* Suppose at each date $t$ (anticipated ex ante by optimizers), normal parameter box (7.3) holds with probability $1 - p$, while an absorbing catastrophic crash with present continuation value upon ruin $U_0 in bb(R)$ (delivering $(1 - beta) U_0$ per period forever) occurs with probability $p in (0, 1)$. Subtracting the exact invariant crash series $frac(beta p U_0, 1 - tilde(beta)_p)$ reduces both dynamic optimization and Doob's stopped supermartingale identically to effective patience $tilde(beta)_p = beta(1 - p)$. Defining the stochastic affine barrier extended to $[b, infinity)$ as $B_1^((p)) (x) := B_*^((p)) - frac(eta q (h - x)_+, C_(max))$ with $B_*^((p)) = frac(hat(R) - Delta_2 (p), 1 - tilde(beta)_p)$, explicit $25$-step worst-case rational witnesses $W_X^((p))$ (evaluated at $tilde(beta)_(p,+)$ since all stage payoffs are negative), and a box-uniform *continuously certified log-PWL global super-barrier* $Psi^((p))$ on all $(0, infinity)$ (since the parametric $a_p K - b_p K^(-1\/2) + c_p$ form develops a lower-tail singularity above $p_("sing") := 1 - sqrt(q_+) \/ beta_+ = 1.1217\%$ and degrades already at $0.5\%, 1.0\%$):
  - Across box (7.3), both staying margins ($>= 0.093$ at $p = 2.0\%$) and continuous adverse-exit margins—including continuous `< b` non-exit slope checks and 50-interval covers on $M$ ($>= +0.839$) and $H_1$ ($>= +0.409$)—remain strictly positive for all $p in lr([0, 2.00%])$, hitting the one-step certification breakdown limit at *$p_("cert") = 2.0434\%$* (well beyond the local patience breakdown $p_("pat") = 0.8723\%$, or $0.8573\%$ corner, because marginal gross returns on $M$ reach $1.631$–$1.667$ at $L = 0.68$ and up to $1.832$ at $A_+$, versus $1.0398$ at $kappa_A$);
  - The Doob-certified deadline *$T^*(p)$ increases strictly and endogenously with $p$* ($T^*(0) = 22$, $T^*(0.5\%) = 25$, $T^*(1.0\%) = 30$, $T^*(1.5\%) = 40$, $T^*(2.0\%) = 84$), showing that the anticipation-valid Doob certified lower bound $bb(P)_p ("Survival to " H) >= (1 - p)^(T^*(p))$ falls to *$0.1832$* at $p = 2.0\%$, vs. the myopic $p = 0$ bound $(1 - 0.02)^23 = 0.6283$ (both are worst-case lower bounds below realized survival along the 4-period entry witness path).
  2. *Coupled 2-state Markov barrier system $(B_G, B_B)$ for recoverable recessions:* Under a two-state Markov process $Omega = {G, B\}$ between normal TFP ($A_G in [0.749, 0.751]$) and a recoverable severe recession ($A_B in [0.349, 0.351]$, where $kappa(A_B) = 0.0066 < b$), with transition matrix $P = mat(1 - p, p; p_("rec"), 1 - p_("rec"))$ ($p_("rec") = 1\/3$), the extended state-dependent affine pair $B_omega (x) = B_(*, omega) - m_omega (h - x)_+$ ($m_omega = eta_- q_- \/ C_(max, omega)$) on $lr([b, infinity)) times {G, B}$ solves the closed $2 times 2$ linear system:
  $ (I - beta_- P) mat(B_(*, G); B_(*, B)) = mat(hat(R)_G; hat(R)_B) - mat(Delta_G (p, p_("rec")); Delta_B (p, p_("rec"))), quad Delta_omega := (h - b) min lr((eta_- / C_(max, omega), beta_- (P bold(m))_omega)). $
  Pairing $(B_G, B_B)$ with exact stationary on-grid feasible Markov witnesses $(W_G, W_B)$ and matched-$beta$ continuously certified log-PWL super-barriers $(Psi_G, Psi_B)$ across all $32$ ($4 times 2 times 2 times 2$) parameter sub-boxes yields strictly positive staying margins, continuous `< b` non-exit checks, and continuous adverse-exit margins ($>= +1.15$ in $M_G$, $>= +0.053$ in $M_B$ with continuous cover $>= +0.032$, $>= +0.55$ in $H_G$, and 32-box $>= +0.013$ in $H_B$) at every tested grid point $p in {0\%, 0.5\%, 1.0\%, 1.5\%, 2.0\%, 5.0\%, 8.0\%, 12.0\%}$, ruling out almost-sure stagnation traps in $M$ ($bb(P)(tau = infinity) = 0$) and giving escape horizons $T^*_G (p) in {21, dots, 33}$ and $T^*_B (p) in {45, dots, 88}$ (with staying-root extrapolation reaching $p_("cert")^("Markov") = 15.45\%$ in state $B$).
]

#proof_block[
  In part 1, along every path staying in $M$ up to $T and tau$, expected cumulative ruin payments prior to exit plus continuation $tilde(beta)_p^(T and tau) (beta p U_0)\/(1 - tilde(beta)_p)$ sum identically to $frac(beta p U_0, 1 - tilde(beta)_p)$, matching the ruin stream of witness $W_X^((p))$ so $U_0$ cancels identically. Because $rho.alt(K, s)$ is independent of $tilde(beta)_p$, $partial(W_X^((p)) - E^+)\/partial K$ coincides verbatim with Proposition 1\*\*, preserving state-by-state monotonicity whenever boundary checks at $b = 0.10$ and $h = 0.28$ remain positive. However, for $a_p K - b_p K^(-1\/2) + c_p$, near $x -> 0^+$ the ratio $(q_+ x + F_(A_+)(x, 1))\/x -> q_+$ makes the Bellman discrepancy scale as $b_p (tilde(beta)_(p,+) \/ sqrt(q_+) - 1) x^(-1\/2)$, blowing up to $+infinity$ above $p_("sing") = 1 - sqrt(q_+)\/beta_+ = 1.1217\%$. Replacing the parametric family with a continuous log-PWL super-barrier $Psi^((p))$ certified on all $(0, infinity)$ via exact 3D centered-form and monotone branch-and-bound on $[10^(-8), 90]$, analytical contraction tail on $(0, 10^(-8)]$, and 3-regime analytical upper tail on $[90, infinity)$ at both $tilde(beta)_(p,-)$ and $tilde(beta)_(p,+)$, together with the `< b` slope test $tilde(beta)_(p,-) min_((0, b]) (Psi^((p)))' > eta_+ \/ c_("opt")(0.10)$ (ensuring the downward-exit supremum on $(0, b]$ occurs at $K' = b$) and a 50-interval continuous cover on $M = [0.10, 0.28)$, certifies every $p in [0, 2.00\%]$ uniformly over box (7.3).

  In part 2, note first that the standard parametric $a x - b x^(-0.5)$ shape cannot fall near $V_B (0.10) approx -40.5$ ($Psi_("std", B)(0.10) > -36.0$, violating adverse-exit calibration on $M_B$). Using coupled log-PWL super-barriers $(Psi_G, Psi_B)$ instead, for $(x, y) in M times M$ and $omega in {G, B}$, minimizing the affine function $eta y\/C_(max, omega) + beta_- (P bold(m))_omega (h - y)$ on $y in [b, h]$ occurs at $y in {b, h}$, validating $rho.alt_omega (x, y) + beta bb(E)[B(y, omega') | omega] <= B(x, omega)$ whenever $(I - beta_- P) bold(B)_* = hat(bold(R)) - bold(Delta)$; for exit transitions $y >= h$, $B(y, omega') = B_(*, omega')$ and $y$ enters as $(y - b)$ with $y >= h$, preserving the exact one-step Bellman inequality. Since $rho(beta_- P) = beta_- < 1$, explicit inversion is positive. Matching $beta in {beta_-, beta_+}$ across $(B_omega, W_omega, Psi_omega)$ over all $32$ ($4 times 2 times 2 times 2$) sub-boxes of $(A_G, A_B, q, eta)$ using exact stationary on-grid Markov witnesses $(W_G, W_B)$ on a fine superset grid (zero interpolation error), verifying $beta_- min_((0, b]) (d \/ (d y)) bb(E)[Psi(y, omega') | omega] > eta_+ \/ c_("opt", omega)(0.10)$ to exclude `< b` exits, and checking a continuous cover across $M = [0.10, 0.28)$ proves all margins positive across $p in {0\%, 0.5\%, 1.0\%, 1.5\%, 2.0\%, 5.0\%, 8.0\%, 12.0\%}$. From $x_0 = 0.10$, three maximal-investment steps yield $K_1 = 0.150233 < K_2 = 0.238496 < 0.28 < K_3 = 0.398940$ (so $tau >= 3$, $y_("max") = 0.474952$, and $bb(E)[beta^tau] <= beta_+^3$), giving $bb(P)(tau <= T) >= [W_omega - B_omega - beta_+^T max(Psi - B_*)]\/[beta_+^3 max(Psi(y_("max")) - B_*) - beta_+^T max(Psi - B_*)] > 0$ (specifically $0.120$ down to $0.057$ at $T = T^*_G + 4$).
]

*Numerical experiment: Anticipatory optimal policy dichotomy (Continuous stochastic VFI):* Solving both stochastic models via Howard-accelerated 880-point continuous golden-section stochastic VFI (matching Ruin and Markov policies identically at $p = 0\%$), Table 5 and Figure 4 reveal a sharp behavioral policy dichotomy: irreversible ruin risk ($tilde(beta)_p$) depresses investment $K'^((p)) (0.10)$ and labor supply $L^((p)) (0.10)$ and nearly triples the survival threshold $S^("ruin")(p)$ ($0.001588 -> 0.004589$ at $p = 8\%$; note that $S^("ruin")(p)$ remains well-defined and unique via Theorem 1 at $A = 0.75$ past $p_("pat") = 0.8723\%$ because (2.3) governs only local patience at $kappa_A$ as $A -> infinity$, whereas peak gross returns $q + F_(A,K)(K, 1) = 1.8307 >> 1\/tilde(beta)_(0.08) = 1.1206$ and $tilde(beta)_p theta > 1$ persists up to $p approx 31.3\%$), whereas recoverable macroeconomic crises ($A_G <-> A_B$) trigger a *precautionary "sprint to safety"* in which both $K'_G (0.10)$ and $L_G (0.10)$ *increase* with $p$ (and intensify under slower recovery $p_("rec") = 0.20$ vs. $0.50$) to reach $H$ faster, while $S_G (p)$ rises mildly ($0.001588 -> 0.001774$), $S_B^("kink")(p)$ rises from $0.00166$ to $0.00187$, and the recession zero-net-investment boundary $K_B^*(p)$ falls from $0.01086$ to $0.00991$.

#v(0.2em)
#figure(
  text(size: 7.1pt, table(
    columns: (0.48fr, 0.52fr, 0.96fr, 1.32fr, 1.48fr, 1.98fr),
    align: (center, center, center, center, center, center),
    inset: (x: 2.5pt, y: 3.3pt),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [Hazard $p$], [Doob \ $T^*(p)$], [$bb(P)_("Doob")(p)$ vs. \ $(1 - p)^23$], [Markov $2 times 2$ \ $B_G (0.10)$/$T^*_G$ ; $B_B (0.10)$/$T^*_B$], [Ruin VFI ($tilde(beta)_p$) \ $S^("ruin")(p)$ ; $K'^((p))$ ; $L^((p))$], [Markov VFI ($G, B$) \ $S_G$ ; $S_B^("kink")$ ; $K_B^*$ ; $K'_G$ ; $L_G$],
    table.hline(stroke: 0.6pt),
    [$0.0\%$], [*$22$*], [*$1.0000$* / $1.0000$], [$-43.358$/$21$ ; $-44.302$/$45$], [$0.001588$ ; $0.13364$ ; $0.6626$], [$0.001588$ ; $0.00166$ ; $0.01086$ ; $0.13364$ ; $0.6626$],
    [$0.5\%$], [*$25$*], [*$0.8822$* / $0.8911$], [$-43.508$/$21$ ; $-44.439$/$46$], [$0.001670$ ; $0.13324$ ; $0.6579$], [$0.001603$ ; $0.00168$ ; $0.01062$ ; $0.13373$ ; $0.6638$],
    [$1.0\%$], [*$30$*], [*$0.7397$* / $0.7936$], [$-43.654$/$22$ ; $-44.573$/$47$], [$0.001769$ ; $0.13294$ ; $0.6545$], [$0.001608$ ; $0.00169$ ; $0.01062$ ; $0.13379$ ; $0.6645$],
    [$1.5\%$], [*$40$*], [*$0.5463$* / $0.7064$], [$-43.796$/$22$ ; $-44.703$/$48$], [$0.001884$ ; $0.13254$ ; $0.6502$], [$0.001622$ ; $0.00171$ ; $0.01062$ ; $0.13386$ ; $0.6654$],
    [$2.0\%$], [*$84$*], [*$0.1832$* / $0.6283$], [$-43.935$/$23$ ; $-44.829$/$49$], [$0.002013$ ; $0.13219$ ; $0.6464$], [$0.001636$ ; $0.00172$ ; $0.01062$ ; $0.13392$ ; $0.6660$],
    [$5.0\%$], [$> p_("cert")$], [— / $0.3074$], [$-44.695$/$25$ ; $-45.525$/$56$], [$0.003053$ ; $0.12990$ ; $0.6225$], [$0.001703$ ; $0.00179$ ; $0.01038$ ; $0.13435$ ; $0.6710$],
    [$8.0\%$], [$> p_("cert")$], [— / $0.1471$], [$-45.353$/$29$ ; $-46.127$/$66$], [*$0.004589$* ; *$0.12757$* ; *$0.6008$*], [*$0.001774$* ; *$0.00187$* ; *$0.00991$* ; *$0.13475$* ; *$0.6759$*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Joint stochastic verification of Lemma 2 and Proposition 4\* over box (7.3): endogenous Doob certificate via box-uniform continuous log-PWL $Psi^((p))$ ($p_("cert") = 2.0434\%$), matched-$beta$ 32-box coupled 2-state Markov system ($A_G = 0.75 <-> A_B = 0.35, p_("rec") = 1\/3$; extending identically to $p = 12\%$ with $T^*_G = 33, T^*_B = 88$ in Appendix A.3), and 880-point continuous golden-section VFI policy contrast ($K'$ and $L$ evaluated at $K = 0.10$) between ruin discouragement and precautionary sprint-to-safety. At $p = 8\%$, sensitivity to $p_("rec") in {0.20, 1\/3, 0.50}$ shifts $(S_G, S_B^("kink"), K_B^*, K'_G, L_G)$ from $(0.001836, 0.00192, 0.00969, 0.13511, 0.6803)$ at $p_("rec") = 0.20$ to $(0.001735, 0.00182, 0.01038, 0.13447, 0.6726)$ at $p_("rec") = 0.50$ (Appendix A.4).],
)

#figure(
  image("fig4_structural_en.svg", width: 100%),
  caption: [Structural extensions of the model. Panel (a) plots VFI trajectories from $K_0 = 0.06$ illustrating unbounded hockey-stick growth ($K_t = (1+g)^t hat(K)_t, g = 0.025$) vs. stationary convergence ($g = 0$) for $N_f = 1$, survival for $N_f = 2$ ($A_("ef") = 0.5303$, $S(0.5303) = 0.003223 < 0.06$), and collapse to extinction under severe regulatory fragmentation ($N_f = 60 > N_(f,"SN") = 56.79$, $A_("ef") = A\/N_f^(theta-1) = 0.0968 < A_*$); Panel (b) contrasts the anticipation-valid Doob certified lower bound $(1 - p)^(T^*(p))$ ($tilde(beta)_p = beta(1 - p)$, continuous log-PWL + $b_(max)$ witness giving $T^*(p) = (22, 25, 30, 40, 84)$, $bb(P)_("Doob")(2\%) = 18.3\%$, breakdown at $p_("cert") = 2.04\%$) against the myopic deterministic Theorem 9\* / MR-Table 4 bounds $(1 - p)^23$ and $(1 - p)^46$.],
)

= Conclusion

Milei and Reidel (2026) introduce a rigorous mathematical framework for extinction traps and certified optimal survival in nonconcave growth models with endogenous labor. We have shown that their analytical apparatus admits four targeted extensions and quantitative strengthenings that answer its open questions, tighten all FPBB certificate margins, and expand its economic applications:

1. *Full sharpening of the FPBB certificate (Section 3):* Without altering any primitive or assumption of Section 7.2, replacing the disjoint-pair bound (7.6) with our *one-step affine regional barrier* $B_1 (K)$ (Lemma 1 and Theorem 9\*) nearly triples the staying calibration margin ($> 7.4665$) and *cuts the certified productive entry deadline exactly in half* (from $46$ to *$23$ periods*, and within $33$ total periods from $K_0 = 0.05$ via Proposition 1\*, further tightened to $tau_(.1) <= 9$ and $tau_H <= 21$–$22$ under our sharpened $M_0$ witness and continuously certified $Psi^((0))$ in Corollary 1\*, while exact restricted-$M$ DP and continuous VFI explain the slack down to $tau_H^("DP") = 9$ and $tau_H^("VFI") = 4$). Furthermore, accounting for the sign of $c''_M > 0$ on $[0.10, 0.17)$ and downward nonsmooth kinks, the analytical interval certificate of Proposition 1\*\* excludes interior minima ($Delta''_M <= -2.5107, Delta''_(H_1) <= -0.1889$) and collapses the twelve finite subintervals of MR-Table 5 into two boundary evaluations, raising the adverse-exit margin on $M$ to $> 0.0947$ and lifting the global FPBB certificate margin from $0.0423$ ($0.04$) to *$> 0.0571$* ($+35\%$).
2. *Asymptotic frontier convergence, variational criterion, and labor isomorphism (Section 4):* Rescaled analysis at $K = A^(-1\/r) k$ together with the exact isomorphism $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$ (Theorem 3\*) resolves Footnote 1 asymptotically ($A -> infinity$): we prove under the patience condition that both rescaled frontiers converge to the common physical limit $(delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), state a precise variational criterion over optimal/confined extinct paths $cal(O)_(-)^("fix")$ with uniform $chi_p^("fix") = Omega(1) > 0$ for $S_A^("fix") (1) < S_A$, show via Corollary 2\* that frontier equivalence extends directly to the weaker regime $beta theta > 1$, and corroborate convergence via continuous VFI through $A = 10^8$ ($S_A^("endo") \/ S_A^("fix") (1) = 1.00039$).
3. *Institutional U-curve and fiscal–regulatory decomposition (Section 5):* Microfounding Section 4.3 with balanced-budget productive public spending ($G_t = tau_p Y_t$) and unproductive compliance overhead ($tau_u$) yields Theorem 10, establishing Barro's rule $tau^* = gamma = alpha\/(1+alpha)$, cleanly separating the physical extinction traps ($tau_(min), tau_(max)$), the economic extinction zones ($A_("rep") < A_e <= A_* = A_("SN") = 0.0995245$), the Theorem 3 asymptotic envelope $overline(S)_("asy")(tau)$ (violated below $A_("cross") = 0.110038$), and Theorem 8's finite-$A$ certified upper bound $overline(S)_("cert")(tau)$ ($A_e >= 0.749$, $[0.117245, 0.304799]$), alongside finite-$A_0$ level-set symmetry and the exact asymptotic $S(tau)$ profile as $A_0 -> infinity$.
4. *Decentralization, unbounded growth, and stochastic barriers (Section 6):* Finally, our structural extensions formalize monopolistic decentralization with consistent Euler factor accounting $(theta\/mu) Y_t$—revealing a persistent $1\/mu <= 1\/theta < 1$ marginal wedge that opens a decentralized trap already at $mu = theta$ and showing that fragmenting firms into $N_f$ units collapses TFP as $A\/N_f^(theta-1)$ (causing economic extinction at $N_(f,"SN") = 56.79$ vs. physical extinction at $N_(f,"rep") = 104.17$)—eliminate the stationary ceiling $K_p^+$ via efficiency-unit scaling (while noting Footnote 2's continuous $A K$ ceiling break), and close the stochastic extension cleanly across Lemma 2 (Doob's Optional Stopping Theorem), Proposition 4\* (continuous `log-PWL` super-barriers with endogenous deadlines $T^*(p)$ up to $84$ at $p = 2\%$, $p_("cert") = 2.0434\%$, and 32-box coupled Markov barriers $(B_G, B_B)$ certified across $p in {0\%, dots, 12\%}$), and 880-point continuous golden-section stochastic VFI across $(S^("ruin")(p), S_G (p), S_B^("kink")(p), K_B^*(p))$ and $p_("rec")$ sensitivity.

#heading(numbering: none)[References]

#[
#set text(size: 9.8pt)
#set par(first-line-indent: 0pt, hanging-indent: 1.5em, leading: 0.54em)
#set list(spacing: 0.34em)
- Acemoglu, D., S. Johnson, and J. A. Robinson (2005): "Institutions as a Fundamental Cause of Long-Run Growth," in P. Aghion and S. N. Durlauf (eds.), _Handbook of Economic Growth_, vol. 1A, ch. 6, pp. 385–472. Amsterdam: Elsevier.
- Akao, K., T. Kamihigashi, and K. Nishimura (2011): "Monotonicity and Continuity of the Critical Capital Stock in the Dechert–Nishimura Model," _Journal of Mathematical Economics_, 47(6), 677–682.
- Akao, K., H. Ishii, T. Kamihigashi, and K. Nishimura (2022): "Existence of an Optimal Path in a Continuous-Time Nonconcave Ramsey Model," _Pure and Applied Functional Analysis_, 7(6), 1939–1952.
- Arrow, K. J., H. B. Chenery, B. S. Minhas, and R. M. Solow (1961): "Capital-Labor Substitution and Economic Efficiency," _The Review of Economics and Statistics_, 43(3), 225–250.
- Azariadis, C., and A. Drazen (1990): "Threshold Externalities in Economic Development," _The Quarterly Journal of Economics_, 105(2), 501–526.
- Barro, R. J. (1990): "Government Spending in a Simple Model of Endogenous Growth," _Journal of Political Economy_, 98(5, Part 2), S103–S125.
- Bellman, R. (1957): _Dynamic Programming_. Princeton, NJ: Princeton University Press.
- Benhabib, J., and R. E. A. Farmer (1994): "Indeterminacy and Increasing Returns," _Journal of Economic Theory_, 63(1), 19–41.
- Bertsekas, D. P. (1972): "Infinite-Time Reachability of State-Space Regions by Using Feedback Control," _IEEE Transactions on Automatic Control_, 17(5), 604–613.
- Dechert, W. D., and K. Nishimura (1983): "A Complete Characterization of Optimal Growth Paths in an Aggregated Model with a Non-Concave Production Function," _Journal of Economic Theory_, 31(2), 332–354.
- de Hek, P. A. (1998): "An Aggregative Model of Capital Accumulation with Leisure-Dependent Utility," _Journal of Economic Dynamics and Control_, 23(2), 255–276.
- Dixit, A. K., and J. E. Stiglitz (1977): "Monopolistic Competition and Optimum Product Diversity," _American Economic Review_, 67(3), 297–308.
- Doob, J. L. (1953): _Stochastic Processes_. New York: John Wiley & Sons.
- Futagami, K., Y. Morita, and A. Shibata (1993): "Dynamic Analysis of an Endogenous Growth Model with Public Capital," _The Scandinavian Journal of Economics_, 95(4), 607–625.
- Gaitsgory, V., A. Parkinson, and I. Shvartsman (2019): "Linear Programming Based Optimality Conditions and Approximate Solution of a Deterministic Infinite Horizon Discounted Optimal Control Problem in Discrete Time," _Discrete and Continuous Dynamical Systems, Series B_, 24(4), 1743–1767.
- Galor, O., and J. Zeira (1993): "Income Distribution and Macroeconomics," _The Review of Economic Studies_, 60(1), 35–52.
- Garicano, L., C. Lelarge, and J. Van Reenen (2016): "Firm Size Distortions and the Productivity Distribution: Evidence from France," _American Economic Review_, 106(11), 3439–3479.
- Geiselhart, R., R. H. Gielen, M. Lazar, and F. R. Wirth (2014): "An Alternative Converse Lyapunov Theorem for Discrete-Time Systems," _Systems & Control Letters_, 70, 49–59.
- Grüne, L., M. A. Müller, C. M. Kellett, and S. R. Weller (2021): "Strict Dissipativity for Discrete Time Discounted Optimal Control Problems," _Mathematical Control and Related Fields_, 11(4), 771–796.
- Haugh, M. B., and L. Kogan (2004): "Pricing American Options: A Duality Approach," _Operations Research_, 52(2), 258–270.
- Hsieh, C.-T., and P. J. Klenow (2009): "Misallocation and Manufacturing TFP in China and India," _The Quarterly Journal of Economics_, 124(4), 1403–1448.
- Kamihigashi, T., and S. Roy (2007): "A Nonsmooth, Nonconvex Model of Optimal Growth," _Journal of Economic Theory_, 132(1), 435–460.
- Klump, R., P. McAdam, and A. Willman (2007): "Factor Substitution and Factor-Augmenting Technical Progress in the United States: A Normalized Supply-Side System Approach," _The Review of Economics and Statistics_, 89(1), 183–192.
- Kraay, A., and D. McKenzie (2014): "Do Poverty Traps Exist? Assessing the Evidence," _Journal of Economic Perspectives_, 28(3), 127–148.
- Majumdar, M., and T. Mitra (1982): "Intertemporal Allocation with a Non-Convex Technology: The Aggregative Framework," _Journal of Economic Theory_, 27(1), 101–136.
- Milei, J., and D. Reidel (2026): _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, Working Paper, October 2026 (baseline edition for theorem numbering, constants, and tables; subsequently updated as _Extinction and Escape under Increasing Returns_, November 2026).
- Milgrom, P., and I. Segal (2002): "Envelope Theorems for Arbitrary Choice Sets," _Econometrica_, 70(2), 583–601.
- Mitra, T., and D. Ray (1984): "Dynamic Optimization on a Non-Convex Feasible Set: Some General Results for Non-Smooth Technologies," _Journal of Economics_ (_Zeitschrift für Nationalökonomie_), 44(2), 151–175.
- Noroozi, N., R. Geiselhart, L. Grüne, and F. R. Wirth (2020): "Control of Discrete-Time Nonlinear Systems via Finite-Step Control Lyapunov Functions," _Systems & Control Letters_, 138, 104631.
- Restuccia, D., and R. Rogerson (2008): "Policy Distortions and Aggregate Productivity with Heterogeneous Establishments," _Review of Economic Dynamics_, 11(4), 707–720.
- Romer, P. M. (1986): "Increasing Returns and Long-Run Growth," _Journal of Political Economy_, 94(5), 1002–1037.
- Skiba, A. K. (1978): "Optimal Growth with a Convex–Concave Production Function," _Econometrica_, 46(3), 527–539.
- Stokey, N. L., and R. E. Lucas, Jr., with E. C. Prescott (1989): _Recursive Methods in Economic Dynamics_. Cambridge, MA: Harvard University Press.
- Trebbi, F., M. B. Zhang, and M. Simkovic (2026): "The Cost of Regulatory Compliance in the United States," _The Review of Financial Studies_, 39(9), 2901–2962.
- Wagener, F. (2020): "Geometrical Methods for Analyzing the Optimal Management of Tipping Point Dynamics," _Natural Resource Modeling_, 33(3), e12258.
]

#pagebreak(weak: true)
#set heading(numbering: "A.1")
#counter(heading).update(0)
#set figure(numbering: n => "A." + str(n))
#counter(figure.where(kind: table)).update(0)

= Technical Appendix: Explicit Witnesses and Numerical Reproducibility Certificates

This Technical Appendix collects our collision-free symbol disambiguation table and the complete quantitative certificates generated by `verify_results.py` (evaluated via analytical interval enclosures in IEEE-754 double precision against certified margins $>= 2.9 times 10^(-3)$) across Sections 3–6.

== Notation Disambiguation Table

Table A.1 maps each formerly overloaded symbol to its collision-free notation while preserving all canonical Milei and Reidel (2026) primitives (`M, cal(M), S_A, S(tau), S_p, r = theta - 1, H`).

#figure(
  text(size: 8.6pt, table(
    columns: (0.95fr, 1.85fr, 1.5fr, 2.3fr),
    align: (center, left, center, left),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Former symbol*], [*Preserved role*], [*Disambiguated symbol*], [*Role & primary location*],
    table.hline(stroke: 0.6pt),
    [$M$], [Staging band $M = lr([0.10, 0.28))$ \ & sustainable set $cal(M)$], [*$N_f$*], [Symmetric firm count ($Y_t^((N_f)), A_("ef")(N_f)$, $N_(f,"SN") = 56.79$ vs. $N_(f,"rep") = 104.17$; Sec. 6.1, Fig. 4)],
    [$S$], [MVS frontier $S_A, S(tau), overline(S)_("asy")(tau)$], [*$cal(S)(K)$*], [Prop. 1\*\* virtual majorant resource ($cal(S)'(K), cal(S)''(K)$; Sec. 3.3)],
    [$S_p$], [MR baseline vector threshold $S_p, hat(S)_p, kappa_p$], [*$S^("ruin")(p)$*, *$K'^((p)), L^((p))$*], [Prop. 4\* & VFI ruin-hazard frontier & policies (paired with $S_G (p), S_B^("kink")(p), K_B^*(p)$; Sec. 6.3, Table 5)],
    [$r$], [Homogeneity excess $r = theta - 1$], [*$rho.alt(...)$* \ *$R_t^K$* \ *$p_("rec")$*], [1) Reduced 1-step return ($rho.alt(K, s), rho.alt_j, rho.alt_omega$; Secs. 3, 6.3) \ 2) Capital rental rate ($R_t^K$; Sec. 6.1) \ 3) Markov recovery prob. ($p_("rec") = 1\/3$; Sec. 6.3)],
    [$H$], [Target band $H = lr([0.28, infinity))$ ($H_1, H_2$)], [*$Lambda_a$* \ *$Gamma_t$*], [1) CES upper factor $sup F_1 (K, 1)\/K = delta\/A_("rep")$ (Thm 10) \ 2) Endogenous spillover $Gamma_t L_t$ (Sec. 6.2, Fn. 2)],
    [Table 4 / Table 5], [This paper's Tables 1–5], [*MR-Table 4* \ *MR-Table 5*], [Tables 4 and 5 of Milei and Reidel (2026) (Secs. 1–3, Fig. 1, Fig. 4)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Collision-free notation disambiguation across the manuscript.],
)

== Section 3 Explicit Witnesses and Interval Bounds

1. *Anchor band $M_0 = lr([0.05, 0.10))$ and U1 continuous unification:*
   - *Baseline witness (Proposition 1\*):* Constants $C_(max,0) = 0.100233$, $Delta_(0,"exact") = 0.311503 > 0.3115$, $hat(R)_(0,"exact") = -1.827072 -> B_0^* = -71.048986 <= -71.046512$. Progression $K_0 -> 0.065 -> 0.0845 -> 0.100$ at $L = 0.75$ yields worst-case $(A_-, q_-, eta_+)$ consumptions $(0.002495, 0.006286, 0.022068)$ and utilities $(-4.611772, -3.964892, -3.085659)$, giving $W_(M_0)(K_0) >= W_(M_0)(0.05) = -43.844826 > -43.845$ (step 1 max consumption as $L -> 1$ is $0.003009$, $max_L u = -4.597860 < -4.59$). At $T_0 = 10$, $J(10; 0.05) = -43.899678 < -43.845$.
   - *U1 sharpened witness and continuous $Psi^((0))$ (Corollary 1\*):* Progression $K_0 -> 0.0595 -> 0.0755 -> 0.100$ at $L = (0.45, 0.50, 0.60)$ yields utilities $(-3.681867, -3.888538, -3.828711)$, giving $W_(M_0)(0.05) = -43.540132$ (under MR-Table 4 tail) and $-43.500107$ (under 25-step stationary $W_M^((0))(0.10; beta_+) = -35.536014$). Continuous B&B certification of $Psi^((0))(x) = 0.45 x - 5.0 x^(-1\/2) + c_0$ on $(0, infinity)$ yields $c_0 (beta_+) = -18.855281$ (giving $Psi^((0))(0.28; beta_+) = -28.178393$; $d(beta_+) in [-0.564473, -0.564273]$, upper tail margin $>= 1.0433$) and box-uniform $c_(0,"unif") = -18.713835$ ($Psi_("unif")^((0))(0.10) = -34.480223$, $Psi_("unif")^((0))(0.28) = -28.036947$). Then $tau_(.1) <= 9$ via state-to-state comparison with $B^(0)(0.05) = -71.367682$ ($J(9; 0.05) = -43.543050$, min gap $+0.0029$ on $M_0$), $tau_H <= 22$ under independent box endpoints using $B_* (beta_-) = -43.0465116$ and $B_1 (0.10; beta_-) = -43.355594$ ($T = 21$ gap $-0.114831$, $T = 22$ gap $+0.122408$), and $tau_H <= 21$ under matched $beta$ consistently recomputing $B_* (beta)$ and $B_1 (0.10; beta)$ (e.g., $B_* (0.9701) = -43.339148$, $B_1 (0.10; 0.9701) = -43.648230$; gaps $+0.070042$, $+0.083959$, $+0.097882$).
   - *Restricted-$M$ slack decomposition on $M = lr([0.10, 0.28))$ (`verify_restricted_M_vfi`):* Under MR-Table 4 / $Psi^sharp$ bounds, exact restricted DP $J_T^(*, Psi^sharp) - W_M$ equals $+0.028144$ ($T = 8$) and $-0.556742$ ($T = 9$); the optimal fixed-point regional barrier $B_("opt") in [-56.794979, -52.457990]$ yields $-0.103800$ ($T = 8$) and $+0.472857$ ($T = 9$) evaluated at the uniform / worst-case initial state $x_0 = 0.28^-$ ($inf_M (W_M - B_("opt")) = 19.1824$ vs. $21.2151$ at $0.10$). At the box center ($V(0.10) = -35.597030$), unrestricted VFI enters $H$ from all $K_0 in M$ in $<= 4$ steps, and true restricted DP $J_T^(*, "VFI") - V$ drops to $-0.173124$ ($T = 4$) and $-0.752234$ ($T = 5$).
2. *Proposition 1\*\* analytical subinterval bounds and U2 variational values:*
   - *Region $M = lr([0.10, 0.28))$ ($l_M = 0.68, s_M = 0.135, a = 0.10, l_0 = 0.44$):* On the $4$ equal subintervals (`[0.100, 0.145, 0.190, 0.235, 0.280]`), $Q_M <= [-0.06341, -0.05880, -0.05061, -0.04375]$ and $Delta'_M >= [3.0288, 0.3955, 0.1252, 0.0723]$. On $8$ equal subintervals (using $eta_+$ for $c''_M > 0$ on $[0.10, 0.17)$), $Delta''_M <= [-421.1331, -107.5343, -42.3434, -21.2734, dots, -2.5107]$ ($max = -2.5107 < 0$); $Delta'_M (0.28^-) = +0.502666$; $u^*(K) in [0.5662, 0.6808] < 1 => L^* >= 0.3192$; margin at $K = 0.10$ is $0.094717$ ($Psi^sharp$) and $0.062495$ ($Psi$).
   - *Region $H_1 = lr([0.28, 0.80))$ ($l_H = 0.72, s_H = 0.375, a = 0.28, l_0 = 0.57$):* On the $6$ subintervals (`[0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80]`), $Q_(H_1) <= [-0.18976, -0.16941, -0.15171, -0.13844, -0.13124, -0.13540]$ and $Delta'_(H_1) >= [1.4675, 0.3243, 0.1022, 0.0348, 0.0095, 0.0119]$. On $10$ equal subintervals, $Delta''_(H_1) <= [-40.4320, -12.4955, -5.3078, -2.6661, dots, -0.1889]$ ($max = -0.1889 < 0$); $Delta'_(H_1)(0.80^-) = +0.100489$; $u^*(K) in [0.4301, 0.5427] < 1 => L^* >= 0.4573$. Downward kinks occur at $k_W = 0.406819$ ($W': 3.954006 -> 3.952877$) and $k_E = 0.573570$ ($(-E^+)': -1.652310 -> -1.652744$). Margin at $K = 0.28$ is $0.056121$ ($l_0 = 0.60, Psi^sharp$), $0.057148$ ($l_0 = 0.57, Psi^sharp$), and $0.024926$ ($l_0 = 0.57, Psi$).
   - *U2 variational alignment:* $L^*(0.28) = 0.569743$, $L^*(0.10) = 0.437261$, and $L_("tan")(0.10; 0.44) in [0.433462, 0.433840]$.

== Lemma 2 and Proposition 4\* Stochastic Certificates and 25-Step Witnesses

*Construction of the `log-PWL` grid and analytical tails:* The continuous `log-PWL` envelope is defined on $645$ knots over $[10^(-8), 90.0]$ via linear interpolation in $log K$ ($642$ unique knots on $[10^(-8), 60.0]$ across $11$ log-spaced subgrids—concentrating $220$ knots in the Skiba zone $[0.0012, 0.0030]$ and including exact boundary knots $0.10, 0.28$—extended by tail knots $\{68.0, 78.0, 90.0\}$). On the lower tail $lr((0, 10^(-8)])$, it takes the exact log-linear form $Psi(x) = Psi(10^(-8)) + s_("tail") log(x \/ 10^(-8))$ with $s_("tail") = eta_- \/ (1 - b_v)$ (under the analytical contraction $q_+ + F_(A_+)(10^(-8), 1)\/10^(-8) < 1$); because $log(x \/ 10^(-8)) <= 0$ requires $eta_- - (1 - b) s_("tail") >= 0$, here $b_v$ takes the lower endpoint ($tilde(beta)_(p,-)$ or $beta_-$). On the upper tail $[90.0, infinity)$, it takes $Psi(x) = Psi(60.0) + D_("hi") log(x \/ 60.0)$ with $D_("hi") >= eta_+ \/ (1 - b_v)$; because $log(x \/ 60.0) > 0$ requires $eta_+ - (1 - b) D_("hi") <= 0$, here $b_v$ takes the upper endpoint ($tilde(beta)_(p,+)$ or $beta_+$), analytically verified across the three successor regimes $y in (0, 1]$, $y in [1, 60.0]$, and $y > 60.0$ using $Y(90.0, 1) < 90.0$.

Tables A.2 and A.3 reproduce the complete log-PWL super-barrier certificates, 25-step rational witnesses, and 32-box Markov exit margins underlying Lemma 2 and Proposition 4\*.

#figure(
  text(size: 8.2pt, table(
    columns: (0.65fr, 1.45fr, 0.9fr, 1.0fr, 1.0fr, 1.05fr, 1.05fr, 1.0fr),
    align: (center, center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [$p$], [Parametric $(a_p, b_p, c_p)$], [PWL $c_("pwl")$], [$Psi^((p))(0.10)$], [$Psi^((p))(0.28)$], [$W_M^((p))(0.10)$], [$W_H^((p))(0.28)$], [Exit margins \ ($M$ cont. / $H$)],
    table.hline(stroke: 0.6pt),
    [$0.00\%$], [$(0.45, 5.0, -18.7138)$], [$0.05025$], [$-35.1934$], [$-28.2088$], [$-35.536014$], [$-28.529814$], [$+0.913$ / $+0.409$],
    [$0.50\%$], [blowup ($x -> 0^+$)], [$0.06592$], [$-32.0566$], [$-25.2133$], [$-32.361297$], [$-25.497581$], [$+0.890$ / $+0.413$],
    [$1.00\%$], [blowup ($x -> 0^+$)], [$0.03059$], [$-29.6649$], [$-22.9590$], [$-29.898125$], [$-23.171248$], [$+0.901$ / $+0.453$],
    [$1.50\%$], [blowup ($x -> 0^+$)], [$0.02625$], [$-27.7135$], [$-21.1402$], [$-27.915233$], [$-21.322296$], [$+0.876$ / $+0.453$],
    [$2.00\%$], [blowup ($x -> 0^+$)], [$0.03063$], [$-26.0891$], [$-19.6444$], [$-26.273549$], [$-19.809973$], [$+0.839$ / $+0.441$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Proposition 4\*(1) ruin-hazard (`5A`) continuous log-PWL super-barrier certificates on $(0, infinity)$ (upper-tail slack $-0.030$ at $x = 90$) and 25-step stationary witnesses (evaluated at worst-case $tilde(beta)_(p,+)$). At $p = 0.00\%$, the first 5 witness steps from $0.1000$ are $(0.1000, 0.6662 -> 0.1338), (0.1338, 0.6854 -> 0.1815), (0.1815, 0.7109 -> 0.2497), (0.2497, 0.7301 -> 0.3434), (0.3434, 0.7556 -> 0.4727) dots -> 2.9036$ with $rho.alt in [-3.3968, -0.6205]$; at $p = 2.00\%$, $(0.1000, 0.6471 -> 0.1320), (0.1320, 0.6662 -> 0.1765), (0.1765, 0.6982 -> 0.2395), (0.2395, 0.7173 -> 0.3249), (0.3249, 0.7429 -> 0.4440) dots -> 2.5619$ with $rho.alt in [-3.3015, -0.6333]$.],
)

#figure(
  text(size: 8.1pt, table(
    columns: (0.55fr, 1.15fr, 1.25fr, 1.0fr, 0.85fr, 1.25fr, 1.25fr, 0.85fr),
    align: (center, center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [$p$], [Shifts $(c_G, c_B)$ \ at $beta_-$], [Witnesses \ $(W_G, W_B)$], [Stay margins \ $(G, B)$], [$T^* = (T^*_G, T^*_B)$], [Exit $M$ \ ($G \/ B$ [cont.])], [Exit $H$ \ ($G \/ B_("32bx")$)], [$bb(P)(tau <= T^*_G + 4)$],
    table.hline(stroke: 0.6pt),
    [$0.0\%$], [$(0.0396, 0.0389)$], [$(-35.3952, -40.4501)$], [$(7.963, 3.852)$], [$(21, 45)$], [$+1.152 \/ +0.053$ [$>= +0.032$]], [$+0.553 \/ +0.013$], [$>= 0.120$],
    [$0.5\%$], [$(0.0350, 0.0347)$], [$(-35.7208, -40.7379)$], [$(7.787, 3.701)$], [$(21, 46)$], [$+1.168 \/ +0.059$ [$>= +0.037$]], [$+0.563 \/ +0.019$], [$>= 0.109$],
    [$1.0\%$], [$(0.0322, 0.0322)$], [$(-36.0392, -41.0197)$], [$(7.615, 3.553)$], [$(22, 47)$], [$+1.182 \/ +0.062$ [$>= +0.040$]], [$+0.571 \/ +0.021$], [$>= 0.117$],
    [$1.5\%$], [$(0.0357, 0.0354)$], [$(-36.3512, -41.2963)$], [$(7.445, 3.406)$], [$(22, 48)$], [$+1.190 \/ +0.059$ [$>= +0.038$]], [$+0.573 \/ +0.023$], [$>= 0.105$],
    [$2.0\%$], [$(0.0332, 0.0331)$], [$(-36.6568, -41.5657)$], [$(7.278, 3.264)$], [$(23, 49)$], [$+1.203 \/ +0.061$ [$>= +0.040$]], [$+0.578 \/ +0.025$], [$>= 0.097$],
    [$5.0\%$], [$(0.0358, 0.0356)$], [$(-38.3626, -43.0710)$], [$(6.333, 2.454)$], [$(25, 56)$], [$+1.264 \/ +0.063$ [$>= +0.043$]], [$+0.609 \/ +0.021$], [$>= 0.082$],
    [$8.0\%$], [$(0.0336, 0.0337)$], [$(-39.8733, -44.4031)$], [$(5.480, 1.724)$], [$(29, 66)$], [$+1.334 \/ +0.073$ [$>= +0.053$]], [$+0.648 \/ +0.022$], [$>= 0.072$],
    [$12.0\%$], [$(0.0373, 0.0372)$], [$(-41.6563, -45.9694)$], [$(4.447, 0.844)$], [$(33, 88)$], [$+1.413 \/ +0.080$ [$>= +0.060$]], [$+0.689 \/ +0.022$], [$>= 0.057$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Proposition 4\*(2) coupled 2-state Markov (`5B`) matched-$beta$ certificates over $p in {0.0\%, dots, 12.0\%}$ (exact on-grid stationary witnesses on `ks_wit`, all $32$ ($4 times 2 times 2 times 2$) sub-boxes B&B-certified at both $beta_-$ and $beta_+$, and continuous $< b$ and $[0.10, 0.28)$ exit covers). Note $p_("cert")^("Markov") = 15.45\%$ is a $B$-state staying-root extrapolation only beyond the pointwise exit-certified grid ${0\%, dots, 12\%}$.],
)

== U-Curve, VFI Frontiers, and Decentralized Equilibria

1. *U-curve critical regimes and thresholds (Theorem 10):* $A_("rep") = 0.073485$, $(tau_(min), tau_(max)) = (6.60 times 10^(-6), 0.948649)$; saddle-node economic threshold $A_* = A_("SN") = 0.0995245$, $(tau_1, tau_2) = (2.219660 times 10^(-5), 0.930108)$; asymptotic-bound crossing $A_("cross") = 0.110038$, $(tau_(c,1), tau_(c,2)) = (3.317089 times 10^(-5), 0.922567)$; Theorem 8 finite-$A$ certified domain ($A_e >= 0.749$) $[0.117245, 0.304799]$. Direct VFI verifies economic extinction (`survives = False`) at $tau = 2.0 times 10^(-5)$ ($A_e = 0.096965$) and $tau = 0.94$ ($A_e = 0.085665$). Barro optimum: $tau^* = gamma = 0.20$; fragmentation counts: $N_(f,"SN") = 56.79$ vs. $N_(f,"rep") = 104.17$; continuous $A K$ regime at $h = 0.28$: $V_("AK")(0.28) = +240.7598 >> Psi^sharp (0.28) = -27.870334$.
2. *Decentralized steady states vs. planner VFI (Proposition 2\*) and U4/U5 sensitivities:*
   - $mu = 1.5$ (overhead, $A_("mkt") = 0.7500$): $S(A_("mkt")) = 0.001587 < K_("lo") = 0.003039$ ($L = 0.1423$), $K_("hi") = 1.808955$ ($L = 0.6787$).
   - $mu = 1.8$ ($A_("mkt") = 0.6250, S(A_("mkt")) = 0.002302$): overhead gives $K_("lo") = 0.004490$ ($L = 0.1689$), $K_("hi") = 1.558817$ ($L = 0.6755$); lump-sum rebate gives $K_("lo") = 0.004670$ ($L = 0.1346$), $K_("hi") = 1.390019$ ($L = 0.6226$).
   - $mu = 2.0$ ($A_("mkt") = 0.5625, S(A_("mkt")) = 0.002856$): overhead gives $K_("lo") = 0.005644$ ($L = 0.1862$), $K_("hi") = 1.423495$ ($L = 0.6734$); lump-sum rebate gives $K_("lo") = 0.006055$ ($L = 0.1349$), $K_("hi") = 1.171530$ ($L = 0.5872$).
   - *U4 hazard landmarks:* $p_("pat") = 0.8723\%$ ($0.8573\%$ corner), $q + F_(A,K)(kappa, 1) = 1.0398$ vs. $q + F_(A,K)(M) in [1.631, 1.667]$ at $L = 0.68$ (reaching $1.832$ at $A_+, L = 1$), $p_("sing") = 1.1217\%$, and $p_("cert") = 2.0434\%$.
   - *U5 recovery probability $p_("rec")$ sensitivity at $p = 8.0\%$ (continuous golden-section Markov VFI):* $p_("rec") = 0.2000 -> S_G = 0.001836, S_B^("kink") = 0.00192, K_B^* = 0.00969, K'_G (0.10) = 0.13511, L_G = 0.6803$; $p_("rec") = 1\/3 -> 0.001774, 0.00187, 0.00991, 0.13475, 0.6759$; $p_("rec") = 0.5000 -> 0.001735, 0.00182, 0.01038, 0.13447, 0.6726$.
