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
  We develop four analytical extensions and quantitative strengthenings for the nonconcave optimal growth model with increasing returns to scale, gross complementarity, and endogenous labor of Milei and Reidel (2026, _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_). *First*, in the First Passage Bellman Barrier (FPBB) certificate of Section 7.2, we identify an unexploited algebraic slack in their two-period block construction: comparing any staying transition $(x, y) in M times M$ against the reference pair $(h, b)$ at identical labor retains both the initial capital difference $q(h - x)$ and the terminal saving difference $(y - b)$ on _every single edge_. Using a state-dependent one-step affine barrier $B_1 (x)$, we lower the barrier ceiling by nearly five welfare units ($-43.0465$ vs. $-38.1442$), *nearly triple the staying calibration margin* (from $2.564$ to $7.4665$ uniformly and $7.7756$ at $b = 0.10$), and *cut the certified productive entry deadline in half* from $46$ to *$23$ periods* ($24$ uniformly). We further extend the certificate to the preceding anchor band $M_0 = lr([0.05, 0.10))$ with an explicit bound $tau_(.1) <= 10$ periods, and prove analytically via a Wronskian ratio decomposition and interval arithmetic that the $12$ finite origin subintervals in Table 5 collapse to two boundary checks with no interior minima, raising the adverse-exit margin on $M$ from $0.0436$ to $> 0.0947$ and the global FPBB certificate margin from $0.0423$ ($0.04$) to *$> 0.0571$* ($+35\%$). *Second*, we resolve Footnote 1 of the original paper by proving the finite-$A$ isomorphism $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, formulating a sharp variational condition for $S_A^("fix") (1) < S_A$, and proving under the patience condition that as $A -> infinity$ both endogenous- and fixed-labor rescaled frontiers converge to $s_infinity^* = (delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), supported by direct value function iteration (VFI). *Third*, we microfound Section 4.3 with productive public spending in the spirit of Barro (1990) and unproductive compliance costs $(tau_p, tau_u)$, separating the exact differentiable U-curve of the certified upper bound $overline(S)(tau)$ and physical floor $kappa(tau)$, level-set symmetry of $S(tau)$ at finite $A_0$, and its asymptotic limit as $A_0 -> infinity$. *Fourth*, we formalize firm decentralization with consistent Euler factor accounting $(theta\/mu) Y_t$, unbounded balanced growth in efficiency units, and Stochastic Bellman Barriers via Doob's Optional Stopping Theorem (*Theorem 11\**), deriving the endogenous risk-adjusted deadline $T^*(p)$ (vs. the myopic deterministic $23$-period bound), an explicit coupled Markov system $(B_G, B_B)$, and forward-looking 880-point Stochastic VFI policy responses.
  #v(0.65em)
  *Keywords.* minimum viable scale; First Passage Bellman Barriers; entry time bounds; endogenous labor; institutional U-curve. \
  *JEL codes.* C61, D24, D61, H21, O41.
]

#v(0.7em)

= Introduction

In _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, Milei and Reidel (2026) develop a unified theory of optimal economic survival when aggregate production exhibits increasing returns to scale ($1 < theta < 2$), gross complementarity between capital and labor ($rho = -d < 0$), and endogenous labor supply with logarithmic consumption–leisure preferences ($L in [0, 1]$). Their core classification result shows that under a patience condition ($beta[q + theta delta] > 1$) and sufficiently high productivity ($A > A_*$), a unique Minimum Viable Scale $S_p$ separates optimal extinction from productive survival strictly above the physical maintenance boundary $kappa_p$ (*Theorem 1*). In the intermediate band $(kappa_p, S_p)$, sustaining capital forever with positive consumption and leisure is physically feasible, yet every optimal path depletes capital toward zero because preservation does not repay current consumption and leisure costs. At $S_p$, extinct and productive optima coexist with identical total welfare, producing a strict upward kink in the value function (*Theorem 2*). Moreover, because postponed-liquidation paths approximate optimal initial welfare arbitrarily closely (*Proposition 3*), the authors introduce *First Passage Bellman Barriers* (FPBB) to certify finite entry into a target productive region $H$ and permanence thereafter without solving for the exact value function $V_p (K)$.

While Milei and Reidel (2026) provide a rigorous foundation and a computer-assisted rational verification in Section 7 and Appendix F, close examination of their proofs and explicitly stated open questions uncovers four analytical gaps that can be closed precisely without altering any primitive or assumption of their model:

1. *Joint sharpening of the staying barrier, initial crossing bound, and interval certification of adverse exits (Section 3):* In Theorem 9 of Milei and Reidel (2026), on parameter box (7.3) with staging region $M = lr([0.10, 0.28))$ and target region $H = lr([0.28, infinity))$, no constant regional barrier can satisfy calibration because choosing $b = 0.10$ from near $h = 0.28$ yields higher period reward than optimal lifetime welfare at $b$. To bypass this obstruction, the authors construct a two-period ($N = 2$) block barrier giving $B(K) <= -38.144176$, staying margin $> 2.564$, entry deadline $tau_H <= 46$, and global margin $0.04$ (governed by a minimum of $0.0423$ across Table 5). We prove in *Lemma 1* and *Theorem 9\** that Equation (7.6) discards roughly half of per-edge resource dissipation on every transition $(x, y) in M times M$: a *one-step* affine barrier $B_1 (x)$ retains both terms simultaneously, lowers the barrier ceiling to $-43.046512$, raises the staying margin to *$> 7.4665$* ($> 7.7755$ at $b = 0.10$), and halves the certified entry deadline to *$tau_H <= 23$ periods* ($24$ uniformly). We also close the unbounded initial delay of Figure 6 on $M_0 = lr([0.05, 0.10))$ with *$tau_(.1) <= 10$ periods* (*Proposition 1\**) and establish via an analytical interval certificate on the Wronskian and second derivative (*Proposition 1\*\**) that no interior minima exist on $M$ and $H_1$, collapsing the $12$ finite subintervals of Table 5 into two boundary evaluations and lifting the global FPBB certificate margin from $0.0423$ ($0.04$) to *$> 0.0571$* ($+35\%$).
2. *Asymptotic convergence, variational ordering, and finite-productivity isomorphism between endogenous and fixed labor (Section 4):* In Footnote 1 (p. 2), Milei and Reidel (2026) note that comparing the endogenous-labor frontier $S_A$ with the frontier $S_A^("fix") (overline(L))$ of an otherwise identical fixed-labor economy remains open. *Theorem 3\** proves the exact finite-$A$ scaling isomorphism $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, states the precise variational condition under which $S_A^("fix") (1) < S_A$, and proves under the patience condition (2.3) (which implies $beta theta > 1$) that both $A^(1\/r) S_A$ and $A^(1\/r) S_A^("fix") (overline(L))$ converge to the common physical limit $(delta\/c_K)^(1\/r)$, settling $S_A \/ S_A^("fix") (overline(L)) -> 1$ as $A -> infinity$, corroborated numerically by continuous-state VFI.
3. *Institutional microfoundation and fiscal–regulatory U-curve (Section 5):* In Section 4.3, Milei and Reidel (2026) represent efficiency distortions via an exogenous wedge $A_e = (1 - tau) A$, explicitly cautioning that applying this experiment to taxes or regulation requires accounting for returned revenue and productive benefits. Coupling their CES technology with balanced-budget productive public infrastructure and property-rights enforcement in the spirit of Barro (1990) alongside unproductive compliance waste ($tau = tau_p + tau_u$), *Theorem 10* establishes twin physical extinction traps ($tau < tau_(min)$ and $tau > tau_(max)$), proves exact differentiable U-curves for the physical floor $kappa(tau)$ and certified upper bound $overline(S)(tau)$ minimized uniquely at $tau^* = alpha\/(1+alpha)$, characterizes level-set symmetry of the true frontier $S(tau)$ at finite $A_0$ and its exact asymptotic U-profile as $A_0 -> infinity$, and preserves strict monotonicity in unproductive bureaucracy $tau_u$.
4. *Decentralization, unbounded growth, and Stochastic Bellman Barriers (Section 6):* Finally, we extend the deterministic planner framework with stationary ceiling $K_p^+$ along three axes: (i) decentralization under monopolistic competition (Dixit and Stiglitz, 1977) with consistent Euler factor accounting $(theta\/mu) Y_t$ and scale externalities (Romer, 1986), proving that fragmenting firms into $M$ isolated units reduces aggregate TFP to $A\/M^(theta-1)$ (*Proposition 2\**); (ii) labor-augmenting technical progress ($g > 0$), eliminating $K_p^+$ to generate unbounded "hockey-stick" exponential growth while preserving every FPBB certificate in efficiency units (*Proposition 3\**); and (iii) a complete probabilistic FPBB formulation via Doob's Optional Stopping Theorem (*Theorem 11\**), replacing fixed deterministic $23$-period bounds with endogenous risk-adjusted Doob deadlines $T^*(p)$, coupled 2-state Markov barrier systems $(B_G, B_B)$, and stochastic VFI showing how forward-looking investment, labor supply, and survival thresholds respond differently to irreversible ruin hazard versus recoverable recessions.

The remainder of the paper is organized as follows. Section 2 positions our contributions within the related literature. Section 3 develops the one-step affine barrier, the anchor crossing bound, and the Table 5 reduction. Section 4 resolves Footnote 1 and reports exact numerical verification of asymptotic scaling. Section 5 derives the institutional U-curve and the $(tau_p, tau_u)$ decomposition. Section 6 presents structural extensions on firm scale, unbounded growth, and stochastic barriers. Section 7 concludes.

= Related Literature and Theoretical Positioning

Our contributions sit at the intersection of four strands of economic theory and verified optimal control, closing concrete analytical gaps relative to prior work and Milei and Reidel (2026).

== Non-Concave Optimal Growth, Skiba Thresholds, and Poverty Traps

Since the foundational contributions of Skiba (1978), Majumdar and Mitra (1982), and Dechert and Nishimura (1983), non-concave optimal growth theory has shown that increasing returns or convex–concave technologies generate critical indifference thresholds dividing optimal trajectories toward extinction or prosperity. Subsequent work by Mitra and Ray (1984), Kamihigashi and Roy (2007), and Akao, Kamihigashi, and Nishimura (2011) generalized global monotonicity and existence results to non-smooth and non-convex settings in discrete time, later extended to continuous-time Ramsey models by Akao, Ishii, Kamihigashi, and Nishimura (2022). In development macroeconomics, Azariadis and Drazen (1990) and Galor and Zeira (1993) linked threshold externalities and indivisible investments to persistent poverty traps, while Wagener (2020) analyzed tipping-point geometry through indifference manifolds and envelope conditions. Yet as Kraay and McKenzie (2014) emphasize in assessing empirical evidence on poverty traps, classical threshold models typically assume inelastic labor and prove only qualitative asymptotic convergence without bounding finite transition durations. Our *Theorem 9\** and *Proposition 1\** supply explicit finite-time capture deadlines ($tau_(.1) <= 10$ and $tau_H <= 23$ periods) for an endogenous-labor economy.

== Endogenous Labor Supply and Factor Complementarity under Increasing Returns

The constant elasticity of substitution (CES) aggregate introduced by Arrow, Chenery, Minhas, and Solow (1961) plays a decisive role when capital and labor are gross complements ($rho < 0$), a regime empirically supported for aggregate production by Klump, McAdam, and Willman (2007). When CES production interacts with endogenous leisure choice, de Hek (1998) proved that consumption–leisure preferences can induce multiple steady states and poverty traps even under convex technology, while Benhabib and Farmer (1994) demonstrated indeterminacy under increasing returns. In Milei and Reidel (2026), combining $1 < theta < 2$, $rho = -d < 0$, and logarithmic leisure utility left the comparison between endogenous-labor and fixed-labor thresholds open (Footnote 1). *Theorem 3\** resolves this comparison analytically via an exact finite-$A$ isomorphism and a singular-scaling proof showing that optimal labor vanishes slower than capital ($K_t\/L_t -> 0$), causing the leisure cost to disappear algebraically as $A -> infinity$.

== Bellman Barriers, Duality, and Stochastic First-Passage Certificates

The FPBB methodology of Milei and Reidel (2026) bridges classical dynamic programming (Bellman, 1957; Stokey, Lucas, and Prescott, 1989) and nonsmooth envelope theorems (Milgrom and Segal, 2002) with finite-time reachability (Bertsekas, 1972), storage functions in dissipative systems (Willems, 1972; Grüne, Müller, Kellett, and Weller, 2021), finite-step Lyapunov iterates (Geiselhart, Gielen, Lazar, and Wirth, 2014; Noroozi, Geiselhart, Grüne, and Wirth, 2020), and American option duality and linear programming optimality (Haugh and Kogan, 2004; Gaitsgory, Parkinson, and Shvartsman, 2019). However, the analytical application in Section 7.2 of Milei and Reidel (2026) relies on $N = 2$ block comparisons with a constant reference—discarding half of per-edge resource dissipation—and discretizes $M union H$ into twelve subintervals in Table 5 to verify adverse-exit bounds. Replacing constant blocks with our one-step affine barrier and proving state-by-state monotonicity (*Proposition 1\*\**) halves the entry deadline and widens the global certificate margin by $35\%$. Moreover, *Theorem 11\** completes the stochastic FPBB program via supermartingales and Doob's Optional Stopping Theorem (Doob, 1953), delivering both anticipation-adjusted analytical certificates ($T^*(p)$ and coupled Markov barriers) and full stochastic VFI policy characterization.

== Productive Public Goods, Regulatory Distortions, and Market Structure

Section 4.3 of Milei and Reidel (2026) draws on the misallocation and compliance-cost literature—where Restuccia and Rogerson (2008), Hsieh and Klenow (2009), Garicano, Lelarge, and Van Reenen (2016), and Trebbi, Zhang, and Simkovic (2026) document how size-dependent regulations and compliance burdens depress aggregate TFP. As Milei and Reidel explicitly note (p. 10), modeling wedges solely as $A_e = (1 - tau) A$ omits the productive returns of public infrastructure and property-rights enforcement (Barro, 1990; Futagami, Morita, and Shibata, 1993; Acemoglu, Johnson, and Robinson, 2005). *Theorem 10* unifies both mechanisms in $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$, preserving unconditional monotonicity in unproductive waste $tau_u$ while deriving the institutional U-curve in productive taxation $tau_p$. Section 6 further shows how increasing returns are decentralized without losses via monopolistic competition (Dixit and Stiglitz, 1977) or aggregate spillovers (Romer, 1986), proving that regulatory firm fragmentation maps directly into a TFP loss $A\/M^(theta-1)$.

= One-Step Affine Bellman Barriers, Entry Deadlines, and Global Certificate Sharpening

== Parameter box and unexploited slack in two-period blocks

Following Section 7 of Milei and Reidel (2026), consider the harmonic CES technology $(theta, rho, w) = (3\/2, -1, 1\/2)$ with production and period utility:
$ F_A (K, L) = A ( (2 K L) / (K + L) )^(3/2), quad u(C, L) = eta log C + (1 - eta) log(1 - L), quad C + K' <= q K + F_A (K, L), $
over parameter box (7.3) of the original paper:
$ A in [0.749, 0.751], quad beta in [0.9699, 0.9701], quad q in [0.9199, 0.9201], quad eta in [0.6999, 0.7001]. $
For staging region $M = lr([b, h)) = lr([0.10, 0.28))$ and target region $H = lr([h, infinity)) = lr([0.28, infinity))$, let $r(K, s) = max_(0 <= L < 1) {eta log(q K + F_A (K, L) - s) + (1 - eta) log(1 - L)}$ be the reduced one-period return. The rationally verified constants in Equation (7.5) and page 59 of Milei and Reidel (2026) are:
$ hat(R) = -0.996 > r(h, b), quad Delta_2 = 0.2997 < (eta_- beta_- q_- (h - b)) / (q_+ h + F_(A_+) (h, 1) - b) = 0.2997787, $
with maximal feasible consumption $C_(max) = q h + F_A (h, 1) - b <= C_(max)^+ = 0.37495167$, staging witness floor $W_M (K) >= W_M (b) > -35.579855 > -35.58$, and unrestricted continuation ceiling $Psi^sharp (K) = Psi(K) - 10\/301 >= V(K)$ satisfying $Psi(h) < -27.83$ (and more precisely $Psi(0.28) = -27.837112$, $Psi^sharp (0.28) = -27.870334$).

On page 22 of Milei and Reidel (2026), for two staying transitions $x -> y -> z$ in $M$, the authors bound each edge separately:
$ r(x, y) <= r(h, b) - (eta (y - b)) / C_(max), quad r(y, z) <= r(h, b) - (eta q (h - y)) / C_(max), $
summing both to obtain $[hat(R) - r(x, y)] + beta [hat(R) - r(y, z)] >= Delta_2$ and defining the two-period barrier $B_0 = hat(R)\/(1 - beta) - Delta_2\/(1 - beta^2) <= -38.144176$.

Observe, however, what happens on *any single transition* $(x, y) in M times M$. Let $L in lr([0, 1))$ be the labor level attaining $r(x, y)$, with consumption $c_0 = q x + F_A (x, L) - y > 0$. Evaluating utility at $(h, b)$ with the exact *same* labor $L$ yields consumption $c_1 = q h + F_A (h, L) - b <= C_(max)$. The exact consumption difference between $(h, b)$ and $(x, y)$ at identical labor is:
$ c_1 - c_0 = q(h - x) + [F_A (h, L) - F_A (x, L)] + (y - b). $
Since $x < h$ and $F_A (dot, L)$ is nondecreasing in capital for all $L in [0, 1]$, $F_A (h, L) - F_A (x, L) >= 0$. Therefore, *both* terms $q(h - x) > 0$ and $(y - b) >= 0$ are present simultaneously on every individual edge $(x, y) in M times M$. By discarding $q(h - x)$ on the first edge and $(z - b)$ on the second, the $N = 2$ disjoint block construction forfeits roughly half of the accumulated dissipation along staying trajectories.

== One-step affine barrier and halved entry deadline

The following lemma formalizes the single-edge loss bound and constructs an explicit affine regional barrier satisfying the Bellman inequality in one step across all of $M$.

#thm_box("Lemma 1 (Unified single-edge loss bound and affine regional barrier on M)")[
  Under parameter box (7.3), every staying transition $(x, y) in M times M = lr([b, h)) times lr([b, h))$ satisfies:
  $ r(x, y) <= r(h, b) - eta / C_(max) [q(h - x) + (y - b)] <= hat(R) - eta / C_(max) [q(h - x) + (y - b)]. $
  Consequently, the state-dependent affine function on $M = lr([b, h))$ defined by:
  $ B_1 (x) = B_* - (eta q (h - x)) / C_(max), quad B_* = (hat(R) - Delta_2) / (1 - beta), $
  is a bounded regional Bellman barrier on $M$, i.e., $B_1 (x) >= r(x, y) + beta B_1 (y)$ for all $x, y in M$. Moreover, uniformly on (7.3):
  $ B_1 (x) <= B_* <= -43.0465116, quad B_1 (b) <= -43.355594, $
  and the calibration margin against the feasible witness $W_M (x)$ satisfies $W_M (x) - B_1 (x) >= W_M (b) - B_1 (b) > 7.7755$ (and uniformly $W_M (x) - B_* > 7.4665$).
]

#proof_block[
  For any $(x, y) in M times M$, let $L in lr([0, 1))$ attain $r(x, y)$ with consumption $c_0 = q x + F_A (x, L) - y > 0$, and put $c_1 = q h + F_A (h, L) - b <= C_(max)$. Since $(h, b, L)$ is feasible at $(h, b)$ and the leisure term $(1 - eta) log(1 - L)$ cancels, concavity of the logarithm ($log(c_1\/c_0) >= (c_1 - c_0)\/c_1$) and monotonicity $F_A (h, L) >= F_A (x, L)$ give:
  $ r(h, b) - r(x, y) >= eta log(c_1 / c_0) >= eta (c_1 - c_0) / c_1 >= eta / C_(max) [q(h - x) + (y - b)]. $
  Substituting $r(h, b) <= hat(R)$ yields the first inequality. Evaluating $r(x, y) + beta B_1 (y)$ for any $x, y in M$:
  $ r(x, y) + beta B_1 (y) &<= hat(R) - (eta q (h - x)) / C_(max) - (eta (y - b)) / C_(max) + beta B_* - (eta beta q (h - y)) / C_(max) \
  &= hat(R) + beta B_* - (eta q (h - x)) / C_(max) - eta / C_(max) [(y - b) + beta q (h - y)]. $
  Because $y in lr([b, h))$ and $beta q < 1$, we have $(y - b) + beta q (h - y) = (1 - beta q)(y - b) + beta q (h - b) >= beta q (h - b)$, bounding the last bracket below by $(eta beta q (h - b))\/C_(max) > Delta_2$. Since $hat(R) - Delta_2 + beta B_* = B_*$ by definition of $B_*$, we conclude $r(x, y) + beta B_1 (y) <= B_* - (eta q (h - x))\/C_(max) = B_1 (x)$ for all $x, y in M$. On box (7.3), $hat(R) - Delta_2 = -1.2957 < 0$ and $beta >= 0.9699$, yielding $B_* <= -1.2957 \/ 0.0301 = -43.04651162...$ and $(eta q)\/C_(max) >= (0.6999 times 0.9199)\/0.37495167 = 1.717123$, so $B_1 (b) <= -43.355594$. Finally, since the first-step witness consumption $c_M (x) = q x + F_A (x, 0.68) - 0.135$ satisfies $0 < c_M (x) < C_(max)$ and $F_(A,K) (x, 0.68) > 0$, we have $W'_M (x) = eta[q + F_(A,K) (x, 0.68)]\/c_M (x) > (eta q)\/C_(max) = B'_1 (x)$ on $M$. Hence $W_M (x) - B_1 (x)$ is strictly increasing on $lr([b, h))$ and attains its infimum at $x = b$, giving $inf_(x in M)[W_M (x) - B_1 (x)] = W_M (b) - B_1 (b) > -35.58 - (-43.355594) = 7.775594$.
]

With Lemma 1 established, we prove our sharpened version of Theorem 9 in Milei and Reidel (2026), cutting the certified entry deadline from $46$ to $23$ periods ($24$ under uniform endpoint bounds).

#thm_box("Theorem 9* (Sharpened CES first passage certificate and halved entry deadline)")[
  Under parameter box (7.3), set $M = lr([0.10, 0.28))$ and $H = lr([0.28, infinity))$.
  1. The affine regional barrier $B_1 (K)$ of Lemma 1 and the feasible witnesses of Table 4 in Milei and Reidel (2026) form a strict First Passage Bellman Barrier (FPBB) certificate with uniform staying margin $> 7.466$ ($7.775$ state-by-state) and adverse-exit margin $> 0.0423$ under the original partition (sharpened to $> 0.0571$ in Proposition 1\*\*).
  2. Every optimal history starting in $M$ enters the productive target $H = lr([0.28, infinity))$ by date *$tau_H <= 23$* (or $tau_H <= 24$ using only uniform bounds independent of $K_0$) and remains in $H$ forever. If $K_0 in [0.10, 0.105]$, its first entry date satisfies:
  $ 3 <= tau_H <= 23. $
]

#proof_block[
  Adverse-departure comparisons from $M$ and $H$ into actions below $b$ and $h$ depend only on $W_M, W_H$ and the ceiling $Psi^sharp$, preserving the Table 5 uniform margin $> 0.0423$ (which Proposition 1\*\* improves to $> 0.0571$). By Theorem 5 (global FPBB selection), no optimizer from $M union H$ ever takes an adverse exit or remains forever in $M$.

  To bound the entry deadline $tau_H$, consider any feasible path staying in $M$ for $T >= 1$ consecutive transitions $x_0 -> x_1 -> dots.c -> x_T$ with $x_t in M$ for $0 <= t <= T$, followed by any feasible continuation from $x_T$. Iterating $r(x_t, x_(t+1)) <= B_1 (x_t) - beta B_1 (x_(t+1))$ for $t = 0, dots, T - 1$ and bounding continuation at $x_T$ via $V(x_T) <= Psi^sharp (x_T) <= Psi(x_T)$ gives:
  $ J_(x_0) (pi) <= B_1 (x_0) + beta^T [Psi^sharp (x_T) - B_1 (x_T)]. $
  On $x in lr([0.10, 0.28))$, the derivative of $Psi^sharp (x) = 0.4 x - 5 x^(-1\/2) - 18.5 - 10\/301$ satisfies $(Psi^sharp)'(x) = 0.4 + 2.5 x^(-3\/2) >= 17.272 > 2 > (eta q)\/C_(max) = B'_1 (x)$, so $Psi^sharp (x_T) - B_1 (x_T)$ is strictly increasing on $lr([b, h))$ and bounded above by $Psi^sharp (h) - B_* < -27.83 - B_*$.
  *Uniform bound ($T = 24$):* Using $B_1 (x_0) <= B_* <= -43.0465116$ and $Psi(h) < -27.83$ from page 59 of Milei and Reidel (2026), at $T = 24$:
  $ J_(x_0) (pi) <= -43.0465116 + (0.9701)^24 (-27.83 - (-43.0465116)) = -35.70251 < -35.58 <= W_M (x_0). $
  *State-matched bound ($T = 23$):* Since $W_M (x_0) - B_1 (x_0)$ is strictly increasing on $lr([b, h))$ by Lemma 1, for all $x_0, x_T in M$:
  $ W_M (x_0) - J_(x_0) (pi) >= [W_M (b) - B_1 (b)] - beta_+^T [Psi(h) - B_*]. $
  At $T = 23$ (exactly half the $46$-period bound of the original paper), we obtain:
  $ W_M (x_0) - J_(x_0) (pi) >= 7.775594 - (0.9701)^23 (15.2165116) = 7.775594 - 7.569980 = +0.205614 > 0. $
  (Using the exact verified values $hat(R) = -0.996799$, $Delta_2 = 0.299778$, and $Psi^sharp (0.28) = -27.870334$ from pages 57–59 of Milei and Reidel, the gap is positive even at $T = 22$ with $+0.0073$). Thus no optimal path can remain in $M$ for $23$ periods, certifying $tau_H <= 23$. The lower bound $tau_H >= 3$ on $[0.10, 0.105]$ follows directly from $Phi(0.105) < 0.16$ and $Phi(0.16) < 0.26 < 0.28$.
]

#figure(
  image("fig1_barrier_en.svg", width: 100%),
  caption: [Comparison between the two-period block barrier of Milei and Reidel (2026) and our one-step affine barrier $B_1 (K)$ on $M = lr([0.10, 0.28))$. Panel (a) shows the calibration gain of nearly $5$ welfare units; Panel (b) illustrates the halving of the certified entry deadline from $tau_H <= 46$ to $tau_H <= 23$–$24$ periods.],
)

== Explicit crossing deadline on the anchor band $M_0 = lr([0.05, 0.10))$

In Figure 6 (p. 21) of Milei and Reidel (2026), crossing from $K_0 > S_A$ to $0.10$ is guaranteed only in finite time ($tau_(.1) < infinity$) with no quantitative bound. Although no uniform deadline can reach $K_0 -> S_A^+$ due to hyperbolic slowdown near the coexistence frontier $S_A$, our one-step affine barrier extends directly to the anchor interval $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, where Theorem 8 already excludes downward exits ($G(K) > K$).

#thm_box([Proposition 1\* (Explicit crossing bound on the preceding anchor band $M_0 = lr([0.05, 0.10))$)])[
  Under parameter box (7.3), set $M_0 = lr([0.05, 0.10))$. Every optimal history with $K_0 in M_0$ crosses $0.10$ within *$tau_(.1) <= 10$ periods* and enters the productive target $H = lr([0.28, infinity))$ within $tau_H <= 33$ total periods.
]

#proof_block[
  On $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, direct maximization over $L in lr([0, 1))$ gives $r(0.10, 0.05) <= -1.827072 < hat(R)_0 := -1.827$, maximum consumption $C_(max,0) <= q_+(0.10) + F_(A_+) (0.10, 1) - 0.05 = 0.100233$, and per-step loss bound $Delta^(0) := 0.3115 < (eta_- beta_- q_- (0.05))\/C_(max,0) = 0.311503$. Applying Lemma 1 to $M_0$ yields $B^(0) (x) = B_*^(0) - (eta q (h_0 - x))\/C_(max,0)$ with $B_*^(0) = (hat(R)_0 - Delta^(0))\/(1 - beta) <= -2.1385 \/ 0.0301 = -71.046512$.

  As a feasible witness from $K_0 in M_0$, we prepend to $W_M (0.10) > -35.58$ the first three steps of the geometric expansion on page 46 of Milei and Reidel ($0.05 -> 0.065 -> 0.0845 -> 0.100$) at constant labor $L = 0.75$. Evaluated at worst-case box endpoints $A_-, q_-$ and $eta_(plus.minus)$, the stage payoffs exceed $(-3.791, -3.504, -3.197)$, guaranteeing a witness floor $W_(M_0) (K_0) >= W_(M_0) (0.05) > -43.845$. Since $Psi(0.10) < -34.271388$ at $h_0 = 0.10$, after $T_0 = 10$ steps in $M_0$:
  $ B_*^(0) + (0.9701)^10 [Psi(0.10) - B_*^(0)] = -71.046512 + (0.9701)^10 (36.775124) = -43.8980 < -43.845 < W_(M_0) (K_0). $
  Since monotone successor order (F.1) rules out downward exits below $0.05$ from $M_0$, every optimal history from $M_0$ enters $lr([0.10, infinity))$ within $tau_(.1) <= 10$ periods, and by Theorem 9\* reaches $H$ within $10 + 23 = 33$ periods.
]

#v(0.3em)
#figure(
  text(size: 9.2pt, table(
    columns: (2.3fr, 1.5fr, 1.45fr, 1.45fr),
    align: (left, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Certified metric on box (7.3)*], [*Milei & Reidel (2026)*], [*This paper (Barrier $B_1$)*], [*Improvement*],
    table.hline(stroke: 0.6pt),
    [Regional reference on $M = lr([0.10, 0.28))$], [Constant ($N = 2$)], [Affine in $K$ ($N = 1$)], [Retains $q(h-x)$ and $(y-b)$],
    [Barrier upper bound $B(K)$ on $M$], [$-38.144176$], [$-43.046512$ \ (to $-43.3556$)], [$-4.90$ to $-5.21$ units],
    [Staying calibration margin ($W_M - B$)], [$> 2.564$], [$> 7.466$ \ ($> 7.775$ at $b$)], [$times 2.91$ \ (to $times 3.03$)],
    [Certified entry deadline from $M$ to $H$ ($tau_H$)], [$<= 46$ periods], [*$<= 23$ periods* \ ($24$ unif.)], [*$50\%$ reduction*],
    [Entry window from $K_0 in [0.10, 0.105]$], [$3 <= tau_H <= 46$], [*$3 <= tau_H <= 23$*], [Upper bound halved],
    [Crossing deadline from $lr([0.05, 0.10))$ to $0.10$], [Finite \ (unbounded)], [*$<= 10$ periods*], [Closes unbounded gap],
    [Total deadline from $K_0 = 0.05$ to $H = lr([0.28, infinity))$], [Finite \ (unbounded)], [*$<= 33$ periods*], [$13$ periods below $46$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Quantitative synthesis of analytical improvements over Section 7.2 and Theorem 9 of Milei and Reidel (2026) under identical parameters (7.3).],
)

== State-by-state monotonicity of adverse exits and Table 5 reduction

Because $B_1 (K)$ raises the staying calibration margin to $> 7.4665$ ($> 7.7755$ at $b = 0.10$) and the staying prefix margin at $T = 23$ to $+0.2056$, staying transitions on $M$ cease to bind. In Table 5 of Milei and Reidel (2026, p. 23 and Appendix F.3), adverse-departure comparisons across $M = [0.10, 0.28)$ and $H_1 = [0.28, 0.80)$ partition those domains into $12$ finite subintervals $[k_-, k_+]$, evaluating $underline(W)_X (k_-)$ at the left endpoint against $E^+ (k_+, a; l_0) + beta_- Psi^sharp (a)$ at the right endpoint to obtain a global margin of $0.0423$ (reported as $.04$).

We now prove that interval discretization is unnecessary: evaluated at the *same* state $K$, the witness advantage over the tangent upper bound is strictly increasing in $K$ across all of $M$ and $H_1$, collapsing the $12$ finite rows of Table 5 to just two boundary checks at $K = 0.10$ and $K = 0.28$ and expanding the global certificate margin by $35\%$.

#thm_box([Proposition 1\*\* (Analytical interval certification of monotonicity and Table 5 collapse)])[
  Under box (7.3), take the Table 4 witnesses of Milei and Reidel (2026) given by $(l_M, s_M, underline(T)_M, a, l_0) = (0.68, 0.135, -33.103, 0.10, 0.44)$ on $M = lr([0.10, 0.28))$ and $(l_H, s_H, underline(T)_H, a, l_0) = (0.72, 0.375, -27.164, 0.28, 0.57)$ on $H_1 = lr([0.28, 0.80))$. The pointwise witness advantage over the adverse-exit envelope (F.19)–(F.20),
  $ Delta_X (K) := underline(W)_X (K) - [E^+ (K, a; l_0) + beta_- Psi^sharp (a)], $
  is strictly increasing across both intervals with no interior minima. Specifically:
  1. An analytical interval certificate on the ratio $R_X (K) = (S(K) - a)\/c_X (K)$ across $4$ subintervals of $M$ and $6$ of $H_1$ guarantees uniformly $Delta'_M (K) >= +0.0722 > 0$ on $M$ and $Delta'_(H_1) (K) >= +0.0094 > 0$ on $H_1$; furthermore, second-derivative interval enclosures verify $Delta''_M (K) <= -0.8564 < 0$ (on $8$ subintervals) and $Delta''_(H_1) (K) <= -0.0439 < 0$ (on $10$ subintervals), placing the minimum of $Delta'_X$ uniquely at the right endpoint:
     $ min_(K in M) Delta'_M (K) = Delta'_M (0.28) = +0.502666, quad min_(K in H_1) Delta'_(H_1) (K) = Delta'_(H_1) (0.80) = +0.100489. $
  2. Consequently, $inf Delta_X$ is attained at the left boundary of each domain, collapsing the $12$ finite subintervals of Table 5 in Milei and Reidel (2026) into two boundary evaluations at $K = 0.10$ and $K = 0.28$:
     - On $M = lr([0.10, 0.28))$, the certified adverse-exit margin rises from $> 0.0436$ to *$> 0.0947$* ($+117\%$).
     - On $H_1 = lr([0.28, 0.80))$, the certified margin rises from $> 0.0423$ to $> 0.0561$ ($l_0 = 0.60$) and *$> 0.0571$* ($l_0 = 0.57$), lifting the global FPBB certificate margin across $M union H$ from $0.0423$ ($.04$) to *$> 0.0571$* ($+35\%$).
]

#proof_block[
  Following Appendix F.3 (Equations F.19–F.20 of Milei and Reidel), for each region $X in {M, H_1}$ with witness labor $l_X$, successor $s_X$, tail floor $underline(T)_X$, exit threshold $a$, and tangent labor $l_0 >= K\/2$, minimum witness consumption is $c_X (K) = q_- K + F_(A_-) (K, l_X) - s_X > 0$, tangent slope is $t(K) = partial_L F_(A_+) (K, l_0)$, and virtual resources equal $S(K) = q_+ K + F_(A_+) (K, l_0) + (1 - l_0) t(K)$. At $(K, a, l_0) = (0.28, 0.28, 0.57)$, $l_0 = 0.57 >= 0.80\/2$ holds throughout $H_1$ and $beta_- psi'(0.28) = 16.7535 > 4.6539 = 1\/(S(0.28) - 0.28)$, so the envelope over $[0.05, a]$ attains its maximum at $s = a$ (the $s = 0$ branch is lower by over $5.37$ on $M$ and $11.77$ on $H_1$).

  *Exact decomposition of $Delta'_X (K)$ and exclusion of interior minima:* The tangent slope obeys the exact logarithmic identities:
  $ (t'(K)) / (t(K)) = (5 l_0) / (2 K (K + l_0)) > 0, quad ((t'\/t)')(K) = - (5 l_0 (2 K + l_0)) / (2 K^2 (K + l_0)^2) < 0. $
  Differentiating each branch of $underline(W)_X$ and $E^+ (K, a; l_0)$ and setting $R_X (K) := (S(K) - a)\/c_X (K) > 1$ yields the exact lower bound (valid at smooth points and for both one-sided derivatives at kink points of $min\/max$):
  $ Delta'_X (K) >= (eta_- c'_X (K) R_X (K) - S'(K)) / (S(K) - a) + (1 - eta_+) (5 l_0) / (2 K (K + l_0)). $
  To certify $R'_X (K) < 0$, write $R'_X (K) = Q_X (K)\/c_X (K)^2$ with Wronskian $Q_X (K) := S'(K) c_X (K) - c'_X (K)(S(K) - a)$, whose derivative cancels $S' c'$ identically: $Q'_X (K) = S''(K) c_X (K) - c''_X (K)(S(K) - a)$. Since $partial_K F_(A,K)(K, L) prop (L - 4K) K^(-1\/2)(K + L)^(-7\/2)$ and $t''(K) prop (3 l_0\/2 - 2K) K^(1\/2)(K + l_0)^(-9\/2)$, both $F_(A,K)$ (unique peak at $L\/4$) and $t'$ (unique peak at $3 l_0\/4$) have no interior minima, while $|Q'_X|$ is bounded on each subinterval $[k_L, k_R]$ by endpoint envelopes of $|F_(A, K K)|$ and $|t''|$. The midpoint Lipschitz bound $Q_X (K) <= Q_X (k_m) + (k_R - k_L)|Q'_X|_([k_L, k_R])\/2$ gives:
  - across the $4$ equal subintervals of $M$ (`[0.100, 0.145, 0.190, 0.235, 0.280]`): $Q_M (K) <= -0.06165, -0.05640, -0.04694, -0.03960 < 0$;
  - across the $6$ subintervals of $H_1$ (`[0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80]`): $Q_(H_1) (K) <= -0.18135, -0.15687, -0.13910, -0.12646, -0.12009, -0.12746 < 0$.
  Thus $R_X (K)$ strictly decreases throughout $M$ and $H_1$, satisfying $R_X (K) >= R_X (k_R)$ on every $[k_L, k_R]$. Bounding $c'_X (K) >= min{c'_X (k_L), c'_X (k_R)}$, $S'(K) <= S'_([k_L, k_R], max)$ via unimodality of $F_(A,K)$ and $t'$, and $S(K) - a$ by its appropriate monotone endpoint yields exact analytical interval lower bounds:
  - on $M$ ($4$ subintervals): $Delta'_M (K) >= +3.0287, +0.3955, +0.1252, +0.0722 > 0$;
  - on $H_1$ ($6$ subintervals): $Delta'_(H_1) (K) >= +1.4674, +0.3242, +0.1022, +0.0348, +0.0094, +0.0119 > 0$.
  This eliminates any grid dependence and rules out interior minima of $Delta_X (K)$. Moreover, factoring $Delta''_X (K) <= [(S')^2 - eta_- (c'_X R_X)^2]\/(S-a)^2 + eta_- c''_X\/c_X - S''\/(S-a) + (1 - eta_+)(t'\/t)'(K)$ (using $c''_X <= 0$ whenever $k_L >= l_X\/4$), the same endpoint arithmetic on $8$ equal subintervals of $M$ and $10$ of $H_1$ certifies $Delta''_M (K) <= -0.8564 < 0$ and $Delta''_(H_1) (K) <= -0.0439 < 0$. Strict concavity forces $Delta'_X$ to attain its minimum at the right boundary ($Delta'_M (0.28) = +0.502666$, $Delta'_(H_1) (0.80) = +0.100489$), and $Delta_X$ to attain its infimum at the left boundary:
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
    [$M = lr([0.10, 0.28))$], [Original Table 5 ($4$ intervals)], [$> 0.0114$], [$> 0.0436$],
    [$M = lr([0.10, 0.28))$], [*Prop. 1\*\* at $K = 0.10$* \ *($l_0 = 0.44$)*], [*$> 0.0624$*], [*$> 0.0947$*],
    [$H_1 = lr([0.28, 0.80))$], [Original Table 5 ($8$ intervals)], [$> 0.01008$], [$> 0.0423$],
    [$H_1 = lr([0.28, 0.80))$], [*Prop. 1\*\* at $K = 0.28$* \ *($l_0 = 0.57$)*], [*$> 0.0249$*], [*$> 0.0571$*],
    [$H_2 = lr([0.80, infinity))$], [Global bound Eq. (F.21)], [$> 2.2662$], [$> 2.2984$],
    table.hline(stroke: 0.6pt),
    [*Global FPBB margin*], [*Minimum over $M union H$*], [*$> 0.0249$* \ (vs. $0.01008$)], [*$> 0.0571$* \ (vs. $0.0423$)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Collapse of the $12$ finite subintervals in Table 5 of Milei and Reidel (2026) via the state-by-state monotonicity of Proposition 1\*\*.],
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
  Relative to endogenous labor, full-capacity fixed labor ($overline(L) = 1$ with no leisure cost) strictly dominates in welfare ($V_A^("fix") (K; 1) > V_A (K)$ for all $K > 0$). At $S_A$, let $Delta W_A^+ := J_A^("fix") (pi^+ |_(L=1)) - V_A (S_A) > 0$ be the surplus gained by setting $L equiv 1$ along a productive optimal trajectory $pi^+$ from $S_A$, and let $Delta W_A^- := sup_(pi^- in cal(O)_(-)^("fix")) [J_A^("fix") (pi^-) - V_A (S_A)]$ be the maximum excess of any extinct fixed-labor trajectory from $S_A$. Then $Delta W_A^- = O(A^(-d\/[r(1+d)]))$, and the strict ordering $S_A^("fix") (1) < S_A$ holds at every $A$ satisfying $Delta W_A^+ > Delta W_A^-$.
]

#proof_block[
  *Part 1 (Operator scaling and frontier convergence).* Set $K = A^(-1\/r) k$ and $C = A^(-1\/r) c$. Using $1 - theta\/r = -1\/r$ and $rho = -d < 0$:
  $ f_A (k, L) := A^(1/r) F_A (A^(-1\/r) k, L) = c_K k^theta [1 + c_w (k / (A^(1\/r) L))^d]^(-theta/d), quad c_w = (1 - w) / w. $
  With fixed labor $L equiv overline(L) in lr((0, 1])$, $(A^(1\/r) overline(L))^(-d) = O(A^(-d\/r)) -> 0$ and $f_A (k, overline(L)) -> c_K k^theta$. With endogenous labor, multiplying the interior first-order condition $F_(A,L)(K, L) = nu C\/(1 - L)$ ($nu = (1 - eta)\/eta$) by $A^(1\/r)$ yields:
  $ theta c_K c_w k^(theta + d) A^(-d/r) L^(-1 - d) [1 + c_w (A^(1/r) L / k)^(-d)]^(-1 - theta/d) = nu c / (1 - L), $
  requiring $L = [theta c_K c_w k^(theta + d)\/(nu c)]^(1\/(1+d)) A^(-d\/[r(1+d)])(1 + o(1)) -> 0$ and $K\/L = Theta(A^(-1\/[r(1+d)])) -> 0$, so $f_A (k, L) = c_K k^theta [1 + O(A^(-d\/[r(1+d)]))]$, $(1 - eta)log(1 - L) = -O(A^(-d\/[r(1+d)]))$ and the normalized Bellman operator converges on compacts to the fixed-labor limit.

  To prove convergence of the frontiers themselves, observe that for $q in (0, 1)$ and $theta > 1$, $theta - (q + theta delta) = q(theta - 1) > 0$. Hence patience condition (2.3), $beta[q + theta delta] > 1$, necessarily implies $beta theta > 1$. Fix any rescaled stock $k_0 > (delta\/c_K)^(1\/r)$ and set $K_0 = A^(-1\/r) k_0$. Construct a feasible expansion at constant labor $L_0 in (0, 1)$ (e.g. $L_0 = 3\/4$, valid in both endogenous labor and fixed labor with $overline(L) = 1$, and analogously for $overline(L) in (0, 1)$ via the finite-$A$ isomorphism):
  - Choose $epsilon_1 in (0, 1)$ with $c_K (1 - epsilon_1) k_0^r > delta$ and a small fixed macroscopic threshold $K_("esc") > 0$ (independent of $A$) such that $[1 + c_w (K_("esc")\/L_0)^d]^(-theta\/d) >= 1 - epsilon_1\/2$, ensuring $f_A (k, L_0) >= c_K (1 - epsilon_1\/2) k^theta$ whenever $K_t <= K_("esc")$.
  - *Phase I (bottleneck escape):* Consuming half of net surplus above $k_t$ reaches in $T_1 (k_0) < infinity$ periods (independent of $A$) a fixed level $k_1$ where $c_K (1 - epsilon_1\/2) k_1^(theta - tilde(theta)) >= 2$, having fixed $tilde(theta) in (beta^(-1), theta)$ (possible since $beta theta > 1$).
  - *Phase II (superexponential climb):* Saving half of total resources ($C_t = K_(t+1) = [q K_t + F_A (K_t, L_0)]\/2$) yields $k_(t+1) >= k_t^(tilde(theta))$ while $k_t <= A^(1\/r) K_("esc")$, hitting $K_(T_1 + J) >= K_("esc")$ within $J(A) <= (log log A)\/(log tilde(theta)) + O(1)$ steps.
  - *Phase III (macroscopic plateau):* For $t >= T_1 + J$, holding $K_("esc")$ yields consumption $A f_1 (K_("esc"), L_0) - delta K_("esc") = Omega(A)$, delivering discounted payoff at least $beta^(T_1 + J) (eta\/(1 - beta)) log A - O(1)$.

  By contrast, Lemma 9's resource bound on $(0, K_0]$ (with growth factor $G_A (K_0) = q + F_A (K_0, 1)\/K_0 -> q + c_K k_0^r = O(1)$) bounds every history confined to $(0, K_0]$—including any extinct optimum from $K_0$—from above by $-(eta\/[r(1 - beta)]) log A + O(1)$. Subtracting both bounds and using $beta^(J(A)) >= c_0 (log A)^(-|log beta|\/log tilde(theta))$, the net surplus of the feasible expansion scales at least as $c_1 (log A)^(1 - |log beta|\/log tilde(theta)) - O(1) -> +infinity$ because $beta tilde(theta) > 1 => 1 - |log beta|\/log tilde(theta) > 0$. By Theorem 1, no optimum can become extinct from $K_0 = A^(-1\/r) k_0$ for large $A$, so $limsup_(A -> infinity) A^(1\/r) S_A <= (delta\/c_K)^(1\/r)$ (and identically for $S_A^("fix") (overline(L))$). Combined with the lower physical bound (4.5) in Theorem 3 and (2.4) for $kappa_A^("fix") (overline(L))$, both frontiers converge to $(delta\/c_K)^(1\/r)$ and their ratio tends to $1$.

  *Part 2 (Finite-$A$ isomorphism and variational criterion).* Degree-$theta = 1 + r$ homogeneity implies $F_A (overline(L) tilde(K), overline(L)) = overline(L) F_(A overline(L)^r) (tilde(K), 1)$ and $eta log(overline(L) tilde(C)_t) = eta log tilde(C)_t + eta log overline(L)$, establishing the exact isomorphism. By Theorem 1, at $K_0 = S_A$ a productive optimum $pi^+$ and an extinct optimum attain $V_A (S_A)$. Setting $L equiv 1$ (without leisure disutility) along $pi^+$ is feasible under fixed labor and yields $V_A^("fix") (S_A; 1) >= J_A^("fix") (pi^+ |_(L=1)) = V_A (S_A) + Delta W_A^+$. Conversely, suppose $S_A^("fix") (1) >= S_A$: then some strictly decreasing fixed-labor extinct optimum $pi^- = (C_t^("f"), K_(t+1)^("f"))_(t>=0)$ satisfies $K_t^("f") <= S_A <= c_+ A^(-1\/r)$ for all $t >= 0$. Pairing $(K_t^("f"))$ with endogenous labor $tilde(L)_t = c_0 A^(-d\/[r(1+d)])$ and consumption $tilde(C)_t = C_t^("f") - [F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)]$, Proposition 4 for fixed labor ($C_t^("f") >= chi_p^("fix") K_t^("f")$) bounds the relative output shortfall at every date $t >= 0$ by:
  $ (F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)) / C_t^("f") <= C_1 A (K_t^("f"))^r (K_t^("f") / tilde(L)_t)^d = O(A^(- d / (r(1+d)))), $
  matching the order of the leisure cost $(1 - eta)|log(1 - tilde(L)_t)| = O(tilde(L)_t)$. Discounting and summing gives $V_A (S_A) >= J_A^("endo") (pi^- |_(tilde(L))) >= J_A^("fix") (pi^-) - C_2 A^(-d\/[r(1+d)])$, hence $Delta W_A^- = O(A^(-d\/[r(1+d)]))$. Whenever $Delta W_A^+ > Delta W_A^-$, $J_A^("fix") (pi^+ |_(L=1)) > sup_(cal(O)_(-)^("fix")) J_A^("fix") (pi^-)$, ruling out optimal extinction at $S_A$ and forcing $S_A^("fix") (1) < S_A$.
]

== Numerical verification of the first-order condition and VFI frontiers

Figure 2 and Table 3 distinguish two complementary verification layers for the harmonic CES benchmark ($theta = 3\/2, d = 1, r = 1\/2, beta = 0.97, q = 0.92, eta = 0.70$) across $A in [0.75, 100]$: (i) evaluating the exact interior labor condition $L^*_A$ at the rescaled reference point $(k, c) = (0.002, 0.0001)$, where $A dot L^*_A$ converges toward $0.133074$ while leisure cost and output gap vanish at rate $O(A^(-1))$; and (ii) *solving the cake-normalized Bellman equation directly (VFI)* via continuous interpolation over an $880$-point two-zone grid in $k = A^2 K$ to compute the actual survival thresholds $A^2 S_A^("fix") (1)$ and $A^2 S_A^("endo")$. Across the entire grid $A in [0.75, 100]$, VFI confirms $S_A^("fix") (1) < S_A^("endo")$ (consistent with Part 2's variational condition, as the productive surplus stays in $Delta W_A^+ in [3.20, 9.73]$) and shows the frontier ratio $S_A^("endo") \/ S_A^("fix") (1)$ converging monotonically toward $1$ (from $1.02078$ at $A = 0.75$ down to $1.00198$ at $A = 100$). Moreover, because $beta theta = 1.455 > 1$, the joint approach of $A^2 S_A$ toward the physical floor $(delta\/c_K)^2 = 0.000800$ proceeds at an ultraslow logarithmic rate $O(1\/log log A)$, reaching $0.000847$ at $A = 10^3$ and $0.000834$ at $A = 10^8$.

#figure(
  image("fig2_scaling_en.svg", width: 100%),
  caption: [Asymptotic scaling and direct VFI frontier resolution of Footnote 1 ($theta = 3\/2, d = 1, r = 1\/2$). Panel (a) displays the localization band between $kappa_A$ and the upper bounds on $S_A$ ($A^(-2)$ scaling); Panel (b) plots both exact FOC trajectories at $(k, c) = (0.002, 0.0001)$ ($A^(-1)$ and $A^(-2)$ decay) and the VFI-computed frontier gap $S_A^("endo")\/S_A^("fix") (1) - 1 -> 0$.],
)

#v(0.2em)
#figure(
  text(size: 8.2pt, table(
    columns: (0.55fr, 1.15fr, 0.85fr, 1.15fr, 0.8fr, 0.85fr, 0.95fr, 0.95fr, 1.0fr),
    align: (center, center, center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [$A$], [$kappa_A$], [$A^2 kappa_A$], [$L^*_A$ \ $(k, c)$], [$A L^*_A$], [$F_A$ gap], [$A^2 S_A^("fix") (1)$ \ (VFI)], [$A^2 S_A^("endo")$ \ (VFI)], [$S_A^("endo") \/ S_A^("fix") (1)$ \ (VFI)],
    table.hline(stroke: 0.6pt),
    [$0.75$], [$1.428 times 10^(-3)$], [$0.000803$], [$1.583 times 10^(-1)$], [$0.11874$], [$3.276\%$], [$0.000875$], [$0.000893$], [*$1.02078$*],
    [$1.50$], [$3.559 times 10^(-4)$], [$0.000801$], [$8.381 times 10^(-2)$], [$0.12571$], [$1.570\%$], [$0.000867$], [$0.000877$], [*$1.01183$*],
    [$3.00$], [$8.891 times 10^(-5)$], [$0.000800$], [$4.311 times 10^(-2)$], [$0.12934$], [$0.768\%$], [$0.000863$], [$0.000869$], [*$1.00717$*],
    [$10.0$], [$8.000 times 10^(-6)$], [$0.000800$], [$1.319 times 10^(-2)$], [$0.13194$], [$0.227\%$], [$0.000858$], [$0.000861$], [*$1.00371$*],
    [$30.0$], [$8.889 times 10^(-7)$], [$0.000800$], [$4.423 times 10^(-3)$], [$0.13270$], [$0.075\%$], [$0.000855$], [$0.000857$], [*$1.00255$*],
    [$100.0$], [$8.000 times 10^(-8)$], [$0.000800$], [$1.330 times 10^(-3)$], [$0.13296$], [$0.023\%$], [$0.000852$], [$0.000853$], [*$1.00198$*],
    table.hline(stroke: 0.6pt),
    [$-> infinity$], [$-> 0$], [*$0.000800$*], [$-> 0$], [*$0.133074$*], [*$0\%$*], [*$0.000800$*], [*$0.000800$*], [*$1.00000$*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Joint numerical verification of Theorem 3\* under the harmonic CES benchmark: columns 2–6 at the FOC point $(k, c) = (0.002, 0.0001)$ and columns 7–9 via direct VFI computation of both survival frontiers ($c_K = 2 sqrt(2)$, $(delta\/c_K)^2 = 0.000800$).],
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
Notably, this microfoundation also explains the emergence of aggregate increasing returns ($theta > 1$): even under constant private returns ($theta_0 = 1$), fiscal feedback from productive public infrastructure ($gamma in (0, 1\/2)$) endogenously generates $theta = 1\/(1 - gamma) in (1, 2)$.

Because $A_e (tau)$ enters solely as a multiplicative productivity scalar in (2.1), *every* structural theorem of Milei and Reidel (2026)—Proposition 1 and Theorems 1–3—transfers verbatim via composition with the unimodal curve $A_e (tau)$.

#thm_box([Theorem 10 (Institutional U-curve of certified bounds, symmetry, and $S(tau)$ limit)])[
  Consider an economy with effective productivity $A_e (tau) = A_0 tau^alpha (1 - tau)$, where $alpha > 0$ and the remaining six primitives satisfy the patience condition (2.3). Define the unique optimal institutional burden:
  $ tau^* = alpha / (1 + alpha) in (0, 1), quad A_(max) := A_e (tau^*) = A_0 alpha^alpha / (1 + alpha)^(1 + alpha). $
  1. *Twin physical extinction thresholds (Anarchy vs. Hyper-regulation):* If $A_(max) > A_("rep")$, there exist exactly two critical burdens $0 < tau_(min) < tau^* < tau_(max) < 1$, unique roots of $tau^alpha (1 - tau) = A_("rep") \/ A_0$, such that:
     - For $tau in (0, tau_(min))$ (*anarchy / state-deficit trap*) and $tau in (tau_(max), 1)$ (*confiscatory / over-regulation trap*), the physically sustainable set is empty ($cal(M)(tau) = emptyset$) and every feasible history contracts geometrically to extinction: $K_t <= [q + A_e (tau) H_a]^t K_0 -> 0$.
     - For $tau in (tau_(min), tau_(max))$, the sustainable interval $[kappa(tau), K^+(tau)]$ is nonempty, attains maximum width at $tau = tau^*$, and $kappa(tau)$ traces an exact differentiable U-curve minimized uniquely at $tau^*$ ($partial log kappa(tau)\/partial tau < 0$ for $tau < tau^*$ and $> 0$ for $tau > tau^*$).
  2. *Distinction between the certified envelope $overline(S)(tau)$ and the true frontier $S(tau)$:* If $A_(max) > A_*$, let $(tau_1, tau_2) subset (tau_(min), tau_(max))$ be the open interval where $A_e (tau) > A_*$, on which a unique continuous frontier $S(tau) > kappa(tau)$ exists. As Milei and Reidel (2026, pp. 10 and 20) emphasize, $S_A = Theta(A^(-1\/(theta-1)))$ gives order bounds but does not by itself establish differentiability or monotonicity of $S(tau)$ at finite $A_0$. Separating the three levels rigorously:
     - *(a) Exact U-curve of the certified upper bound $overline(S)(tau)$:* Any scaled upper envelope $overline(S)(tau) := overline(c)_+ [A_e (tau)]^(-1\/(theta - 1))$ (such as the Theorem 3 benchmark bound with $overline(c)_+ = (D\/c_K)^(1\/(theta-1))$ tabulated in Table 4, or Theorem 8's explicit bound with $overline(c)_+ = (.0014025025)^(1\/2)$ wherever $A_e (tau) >= 0.749$) traces a smooth, strictly convex U-curve on $(tau_1, tau_2)$ minimized uniquely at $tau^* = alpha\/(1+alpha)$ with exact closed-form log-derivative:
       $ partial / (partial tau) log overline(S)(tau) = - 1 / (theta - 1) [ alpha / tau - 1 / (1 - tau) ] = (tau - tau^*) / ((theta - 1)(1 - tau^*) tau (1 - tau)). $
     - *(b) Level-set symmetry of the true frontier $S(tau)$ at every finite $A_0$:* Because $S(tau) = S_(A_e (tau))$ depends on $tau$ solely through the unimodal scalar $A_e (tau)$, every burden $tau_- in (tau_1, tau^*)$ has a unique conjugate $tau_+ in (tau^*, tau_2)$ with $A_e (tau_-) = A_e (tau_+)$ and identical true frontier ($S(tau_-) = S(tau_+)$), while the U-shaped localization band $kappa(tau) < S(tau) < 1.798 kappa(tau)$ holds wherever Theorem 8 applies.
     - *(c) Exact asymptotic U-curve of $S(tau)$ ($A_0 -> infinity$):* By Theorem 3\* ($lim_(A -> infinity) A^(1\/(theta-1)) S_A = s_infinity^* := (delta\/c_K)^(1\/(theta-1))$), the rescaled true frontier converges uniformly on compact subsets of $(0, 1)$ to the exact differentiable profile:
       $ lim_(A_0 -> infinity) A_0^(1/(theta-1)) S(tau) = s_infinity^* [tau^alpha (1 - tau)]^(-1/(theta-1)), $
       whose unique global minimum occurs at the optimal Barro rate $tau^* = alpha\/(1 + alpha)$.
]

#proof_block[
  The function $g(tau) = tau^alpha (1 - tau)$ is strictly log-concave on $(0, 1)$, with logarithmic derivative $g'(tau)\/g(tau) = alpha\/tau - 1\/(1 - tau) = (tau^* - tau)\/[(1 - tau^*) tau (1 - tau)]$. Hence $g(tau)$ strictly increases on $(0, tau^*)$, attains its unique global maximum at $tau^* = alpha\/(1+alpha)$, and strictly decreases on $(tau^*, 1)$, vanishing at both endpoints. If $A_(max) = A_0 g(tau^*) > A_("rep")$, the intermediate value theorem yields two unique roots $tau_(min) in (0, tau^*)$ and $tau_(max) in (tau^*, 1)$ of $A_e (tau) = A_("rep")$. Applying Proposition 1 of Milei and Reidel at $A = A_e (tau)$ gives part 1, and implicit differentiation in Eq. (4.2) of the original paper yields:
  $ (partial log kappa(tau)) / (partial tau) = - 1 / (theta s(kappa(tau)) - 1) (partial log A_e (tau)) / (partial tau) = (tau - tau^*) / ([theta s(kappa(tau)) - 1](1 - tau^*) tau (1 - tau)), $
  which is strictly negative on $(tau_(min), tau^*)$ and strictly positive on $(tau^*, tau_(max))$ since $theta s(kappa) - 1 > 0$. For part 2(a), differentiating $log overline(S)(tau) = log overline(c)_+ - (theta - 1)^(-1) log A_e (tau)$ yields the exact log-derivative identity and strict log-convexity (second derivative $> 0$). For 2(b), strict unimodality of $A_e (tau)$ yields two unique preimages for every level $A in (A_*, A_(max))$ and transfers Theorem 8 wherever $A_e (tau) >= 0.749$. For 2(c), substituting $A = A_0 tau^alpha (1 - tau)$ into the limit $A^(1\/(theta-1)) S_A -> (delta\/c_K)^(1\/(theta-1))$ proved in Theorem 3\* establishes uniform convergence on any compact $[underline(tau), overline(tau)] subset (0, 1)$ to the exact asymptotic U-curve.
]

== Productive vs. unproductive burden decomposition and quantitative synthesis

Decomposing the total burden into productive spending ($tau_p$) and unproductive compliance or bureaucratic overhead ($tau_u$) via $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$ yields two complementary policy laws unifying Milei and Reidel's original Proposition 2 with our institutional U-curve:

1. *Monotonicity in unproductive waste $tau_u$:* For any fixed level of institutional provision $tau_p$, $partial A_e \/ partial tau_u = -A_0 tau_p^alpha < 0$ contracts the sustainable interval ($partial kappa \/ partial tau_u > 0$ and $partial overline(S) \/ partial tau_u > 0$ *everywhere*, and $partial S \/ partial tau_u > 0$ in the $A_0 -> infinity$ limit), recovering Proposition 2 of Milei and Reidel (2026) along $tau_u$.
2. *U-curve and crowding-out on productive provision $tau_p$:* For fixed $tau_u in lr([0, 1))$, the productive tax maximizing $A_e (tau_p, tau_u)$ and minimizing both $kappa(tau_p, tau_u)$ and $overline(S)(tau_p, tau_u)$ is $tau_p^* (tau_u) = frac(alpha, 1 + alpha) (1 - tau_u)$, where peak productivity scales as $A_e^* (tau_u) prop (1 - tau_u)^(1 + alpha)$ and the minimal certified envelope scales as $overline(S)^* (tau_u) = overline(c)_+ A_e^* (tau_u)^(-1\/(theta - 1)) prop (1 - tau_u)^(-(1+alpha)\/(theta-1))$. Thus, cutting $tau_u$ and rolling back excessive regulation ($tau_p > tau_p^*$) sharply lowers survival barriers, whereas on the left branch ($tau_p < tau_p^*$) basic property rights and infrastructure remain indispensable to escape the anarchy trap.

#figure(
  image("fig3_ucurve_en.svg", width: 100%),
  caption: [Institutional extension of Section 4.3 ($A_e (tau) = A_0 tau^alpha (1 - tau)$ with $A_0 = 1.45, alpha = 0.25, tau^* = 0.20, A_("rep") = 0.0735$). Panel (a) contrasts net productivity with public infrastructure against the pure linear wedge $A(1-tau)$ and marks both extinction roots ($tau_(min) = 6.60 times 10^(-6)$ and $tau_(max) = 0.9486$); Panel (b) depicts the exact resulting U-curve for $kappa(tau)$ and the certified upper bound $overline(S)(tau) = (D\/c_K)^2 A_e (tau)^(-2)$.],
)

#v(0.2em)
#figure(
  table(
    columns: (0.9fr, 1.0fr, 1.0fr, 1.15fr, 1.2fr, 1.7fr),
    align: (center, center, center, center, center, left),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [Burden $tau$], [$A_e (tau)$], [$A_e (tau) \/ A_("rep")$], [$kappa(tau)$], [Bound $overline(S)(tau)$], [Institutional regime],
    table.hline(stroke: 0.6pt),
    [$5.0 times 10^(-6)$], [$0.0685$], [$0.93$], [—], [—], [Extinction (anarchy trap)],
    [$2.0 times 10^(-5)$], [$0.0970$], [$1.32$], [$0.119322$], [$0.163590$], [Anarchy margin ($tau > tau_(min)$)],
    [$0.02$], [$0.5344$], [$7.27$], [$0.002825$], [$0.005386$], [Left branch (under-provision)],
    [$0.05$], [$0.6514$], [$8.86$], [$0.001896$], [$0.003625$], [Infrastructure expansion],
    [$0.10$], [$0.7339$], [$9.99$], [$0.001492$], [$0.002856$], [Near institutional optimum],
    [*$0.20$ ($tau^*$)*], [*$0.7757$*], [*$10.56$*], [*$0.001335$*], [*$0.002556$*], [*Unique optimal burden (min $overline(S), kappa$)*],
    [$0.40$], [$0.6919$], [$9.42$], [$0.001680$], [$0.003213$], [Right branch (excessive burden)],
    [$0.60$], [$0.5105$], [$6.95$], [$0.003099$], [$0.005903$], [Severe interval contraction],
    [$0.80$], [$0.2743$], [$3.73$], [$0.010990$], [$0.020448$], [Acute viability erosion],
    [$0.90$], [$0.1412$], [$1.92$], [$0.045887$], [$0.077114$], [Near collapse threshold],
    [$0.94$], [$0.0857$], [$1.17$], [$0.178378$], [$0.209599$], [Over-regulation edge ($tau < tau_(max)$)],
    [$0.95$], [$0.0716$], [$0.97$], [—], [—], [Extinction (hyper-regulation)],
    table.hline(stroke: 1.1pt),
  ),
  caption: [Quantitative classification of institutional regimes under Theorem 10 in the harmonic CES benchmark ($A_0 = 1.45, alpha = 0.25, A_("rep") = 0.073485, tau_(min) = 6.60 times 10^(-6), tau_(max) = 0.948649$). Column 5 reports the scaled envelope $overline(S)(tau) = (D\/c_K)^2 A_e (tau)^(-2)$ (further tightened by Theorem 8's explicit bound $0.0014025025 A_e (tau)^(-2) = 0.002331$ at $tau^*$ where $A_e >= 0.749$).],
)

= Structural Extensions: Firm Decentralization, Unbounded Growth, and Stochastic Barriers

Whereas policy debates around minimum viable scale center on firm scale, antitrust fragmentation, sustained "hockey-stick" growth, and macroeconomic crises, the baseline mathematical model of Milei and Reidel (2026) assumes a deterministic central planner bounded by a stationary ceiling $K_p^+$. We show below how to embed all three dimensions into their exact mathematical architecture without sacrificing their theorems or certificates.

== Decentralization, market power, and the cost of firm fragmentation

With increasing returns $theta in (1, 2)$, Euler's theorem gives $K F_(A,K) + L F_(A,L) = theta F_A (K, L) > F_A (K, L)$, so perfectly competitive price-taking firms without externalities would suffer operating losses $(1 - theta) Y_t < 0$. Two canonical decentralizations support technology (2.1): (i) *monopolistic competition or symmetric oligopoly* (Dixit and Stiglitz, 1977) with markup $mu >= theta > 1$, where factors earn $r_t = (1\/mu) F_(A,K)$ and $w_t = (1\/mu) F_(A,L)$ while the remaining fraction $(1 - theta\/mu) Y_t >= 0$ covers fixed operating costs; or (ii) *aggregate scale externalities* (Romer, 1986), where individual firms face constant private returns while aggregate scale lifts TFP.

#thm_box("Proposition 2* (Firm-scale decentralization, factor accounting, and fragmentation)")[
  Under CES technology (2.1) with $theta in (1, 2)$ and $r = theta - 1 > 0$:
  1. *Regulatory or antitrust fragmentation theorem:* Splitting aggregate inputs $(K_t, L_t)$ across $M >= 1$ isolated symmetric firms ($K_(i,t) = K_t \/ M$, $L_(i,t) = L_t \/ M$) contracts aggregate output exactly as:
  $ Y_t^((M)) = sum_(i=1)^M F_A (K_t / M, L_t / M) = M dot M^(-theta) F_A (K_t, L_t) = F_(A \/ M^r) (K_t, L_t). $
  Thus, fragmenting firm scale into $M$ units is *mathematically isomorphic* to depressing TFP to $A_("ef") (M) = A \/ M^(theta - 1)$, scaling up Minimum Viable Scale by a factor $M$ asymptotically ($S_A (M) = Theta(M dot S_A)$) and triggering global extinction ($cal(M)(M) = emptyset$) whenever $M >= (A \/ A_("rep"))^(1\/(theta - 1))$.
  2. *Exact factor accounting and decentralized underinvestment trap:* Under monopolistic competition with markup $mu >= theta > 1$ and factor prices $r_t = (1\/mu) F_(A,K)$, $w_t = (1\/mu) F_(A,L)$, Euler's theorem implies that aggregate factor income received by households equals:
  $ r_t K_t + w_t L_t = theta / mu F_A (K_t, L_t) = F_(A_("mkt")) (K_t, L_t), quad A_("mkt") := theta / mu A <= A. $
  - *(Fixed-overhead / zero-net-profit closure):* When the residual output share $(1 - theta\/mu) Y_t >= 0$ covers fixed operating and entry costs (so net profits are zero), the representative household's accumulation problem is strictly isomorphic to Milei and Reidel's Bellman operator at effective productivity $A_("mkt") = (theta\/mu) A$, inducing whenever $mu > theta$ the decentralized coordination trap $lr([S_A, S_((theta\/mu) A)))$.
  - *(Lump-sum profit rebate closure):* If pure residual profits $(1 - theta\/mu) Y_t$ are rebated lump-sum to households, aggregate resources retain $F_A (K_t, L_t)$, yet households' private Euler and intratemporal labor optimality conditions face marginal factor returns scaled down by $1\/mu < 1\/theta$, still depressing saving and raising the decentralized survival threshold above $S_A$.
]

#proof_block[
  Degree-$theta = 1 + r$ homogeneity of $F_A (K, L) = A [w K^rho + (1 - w) L^rho]^(theta\/rho)$ implies $F_A (K\/M, L\/M) = M^(-theta) F_A (K, L)$. Summing across $M$ firms yields $Y_t^((M)) = M^(1-theta) F_A (K, L) = F_(A M^(-r)) (K, L)$. Applying Proposition 1 and Theorem 3 of Milei and Reidel at $tilde(A) = A M^(-r)$ establishes extinction iff $A M^(-r) <= A_("rep")$ and threshold scaling $S_(tilde(A)) = Theta(tilde(A)^(-1\/r)) = M dot Theta(A^(-1\/r))$. Next, Euler's identity $K F_(A,K) + L F_(A,L) = theta F_A (K, L)$ implies total factor payments equal $(theta\/mu) F_A (K_t, L_t) = F_((theta\/mu)A) (K_t, L_t)$. When fixed overhead absorbs $(1 - theta\/mu) Y_t$, the household budget set matches the planner's problem at $A_("mkt") = (theta\/mu) A < A$ for all $mu > theta$, generating the trap $S_((theta\/mu) A) > S_A$; under lump-sum rebate $Pi_t = (1 - theta\/mu) Y_t$, the $1\/mu$ wedge on private marginal factor returns $r_t, w_t$ distorts private accumulation below the social optimum.
]

== Eliminating the stationary ceiling $K_p^+$ and "hockey-stick" growth

In Milei and Reidel's baseline model, $L_t <= 1$ and $rho < 0$ impose an output asymptote $F_A (K, 1) < A (1 - w)^(theta\/rho)$, creating a stationary ceiling $K_p^+ < infinity$. Introducing labor-augmenting technical progress at rate $g > 0$ (or learning-by-doing inside $H$) eliminates $K_p^+$ and yields perpetual exponential growth while leaving every verified constant of the original paper intact.

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
  Dividing $C_t + K_(t+1) <= q K_t + (1 + g)^t F_A (K_t \/ (1 + g)^t, L_t)$ by $(1 + g)^(t+1)$ immediately yields $tilde(C)_t + hat(K)_(t+1) <= tilde(q) hat(K)_t + F_(tilde(A)) (hat(K)_t, L_t)$. Because $sum_(t=0)^infinity beta^t eta (t + 1) log(1 + g) < infinity$ is independent of $(hat(K)_(t+1), L_t)$, optimal paths of $hat(K)_t$ coincide pointwise with the stationary economy at $(tilde(A), tilde(q))$.#footnote[Equivalently, under endogenous knowledge spillovers where effective labor is $H_t L_t$ with $H_t = 1$ on $K_t < h$ and $H_t = K_t \/ h$ once $K_t >= h$ (Romer, 1986), the entire extinction and staging geometry on $M = lr([b, h))$ remains unchanged while entry into $H$ triggers an $A K$ regime of perpetual endogenous growth.]
]

== Macroeconomic uncertainty and Stochastic Bellman Barriers (Doob's Theorem)

A major methodological advantage of First Passage Bellman Barriers (Section 6 of Milei and Reidel, 2026) over deterministic monotonicity proofs (Dechert and Nishimura, 1983) is that regional barrier inequalities extend naturally to stochastic environments via martingale theory and *Doob's Optional Stopping Theorem* (Doob, 1953). However, plugging the risk-free deterministic horizon $T^* = 23$ into an ex-post survival expression $(1 - p)^23$ implicitly assumes myopic optimizers acting with $beta = 0.97$ ($p = 0$), ignoring how forward-looking agents who anticipate annual crisis risk $p > 0$ alter their investment policy $K'_p (K)$, labor supply $L_p (K)$, and effective impatience.

Theorem 11\* resolves this stochastic extension completely across four verified layers: (1) the abstract Doob supermartingale certificate; (2) the endogenous risk-adjusted horizon $T^*(p)$ and breakdown limit $p_("cert")$ under anticipated irreversible ruin/expropriation risk; (3) an explicit closed $2 times 2$ Markov barrier system $(B_G, B_B)$ for recoverable recessions; and (4) full 880-point stochastic VFI uncovering a sharp behavioral policy dichotomy.

#thm_box("Theorem 11* (Stochastic Bellman Barriers, endogenous Doob deadlines T*(p), and anticipating policies)")[
  Let $(omega_t)_(t>=0)$ be a Markovian macroeconomic shock process on $(Omega, cal(F), bb(P))$ affecting primitives each period, under the integrability condition $sup_(t <= T) bb(E)[ |V(K_(t and tau), omega_(t and tau))| ] < infinity$ for every finite horizon $T >= 1$.
  1. *Supermartingale Certificate (Stochastic FPBB):* If a measurable bounded function $B : M times Omega -> bb(R)$ on $M = lr([b, h))$ satisfies, for every staying action in $M$:
  $ B(K, omega) >= r(K, omega, a) + beta bb(E) [ B(K', omega') | K, omega, a ], $
  and every finite-welfare staying history in $M$ satisfies $bb(E)[sum_(j=0)^(t-1) beta^j |r_j| ] < infinity$, then along any policy remaining in $M$ up to stopping time $tau = inf{t >= 0 : K_t in.not M}$, the process $Z_t := beta^t B(K_t, omega_t) + sum_(j=0)^(t-1) beta^j r_j$ is a *supermartingale* with respect to the natural filtration $cal(F)_t$. By Doob's Optional Stopping Theorem, for every horizon $T >= 1$:
  $ bb(E)_(x_0, omega_0) [J(pi)] <= B(x_0, omega_0) + bb(E)_(x_0, omega_0) [ beta^(T and tau) ( V(K_(T and tau), omega_(T and tau)) - B(K_(T and tau), omega_(T and tau)) ) ]. $
  2. *Endogenous Doob deadline $T^*(p)$ under anticipated ruin/expropriation hazard ($tilde(beta)_p := beta(1 - p)$):* Suppose at each date $t$ (anticipated ex ante by optimizers), normal parameter box (7.3) holds with probability $1 - p$, while an absorbing catastrophic crash yields a common ruin continuation $U_0 in bb(R)$ forever with probability $p in (0, 1)$. Subtracting the exact invariant crash series $frac(beta p U_0, 1 - tilde(beta)_p)$ reduces both dynamic optimization and Doob's supermartingale identically to effective patience $tilde(beta)_p = beta(1 - p)$. Defining the stochastic affine barrier $B_1^((p)) (x) := B_*^((p)) - frac(eta q (h - x), C_(max))$ with $B_*^((p)) = frac(hat(R) - Delta_2 (p), 1 - tilde(beta)_p)$, explicit $25$-step rational witnesses $W_X^((p))$, and the analytical global super-barrier $Psi^((p)) (K) = a_p K - b_p K^(-1\/2) + c_p$:
  - Across box (7.3), both staying margins and adverse-exit margins ($M$ and $H_1$, inheriting state-by-state monotonicity in $K$ directly from Proposition 1\*\*) remain strictly positive for all $p in lr([0, 2.00%])$, hitting the one-step certification breakdown limit at *$p_("cert") approx 2.07\%$*;
  - The Doob-certified deadline *$T^*(p)$ increases strictly and endogenously with $p$* ($T^*(0) = 21$, $T^*(0.5\%) = 24$, $T^*(1.0\%) = 29$, $T^*(1.5\%) = 38$, $T^*(2.0\%) = 74$), showing that genuine certified survival probability $bb(P)_p ("Survival to " H) >= (1 - p)^(T^*(p))$ falls to *$0.2242$* at $p = 2.0\%$, vs. $0.6283$ from naively inserting deterministic $T^* = 23$ into $(1 - 0.02)^23$.
  3. *Coupled 2-state Markov barrier system $(B_G, B_B)$ for recoverable recessions:* Under a two-state Markov process $Omega = {G, B\}$ between normal TFP ($A_G in [0.749, 0.751]$) and a recoverable severe recession ($A_B in [0.349, 0.351]$, where $kappa(A_B) = 0.0066 < b$), with transition matrix $P = mat(1 - p, p; r_("rec"), 1 - r_("rec"))$ ($r_("rec") = 1\/3$), the state-dependent affine pair $B_omega (x) = B_(*, omega) - m_omega (h - x)$ ($m_omega = eta_- q_- \/ C_(max, omega)$) solves the closed $2 times 2$ linear system:
  $ (I - beta_- P) mat(B_(*, G); B_(*, B)) = mat(hat(R)_G; hat(R)_B) - mat(Delta_G (p, r_("rec")); Delta_B (p, r_("rec"))), quad Delta_omega := (h - b) min lr((eta_- / C_(max, omega), beta_- (P bold(m))_omega)), $
  maintaining strictly positive margins against Markov feasible witnesses $(W_G, W_B)$ for all $p in lr([0, 12%])$, ruling out almost-sure stagnation traps in $M$ ($bb(P)(tau = infinity) = 0$) and yielding explicit escape bounds at horizons $T^*_omega (p)$.
  4. *Forward-looking optimal policy dichotomy (Stochastic VFI):* When agents internalize annual hazard $p > 0$, irreversible ruin risk ($tilde(beta)_p$) depresses investment $K'_p (0.10)$ and labor supply $L_p (0.10)$ and nearly triples the survival threshold $S_p$ ($0.001588 -> 0.004589$ at $p = 8\%$), whereas recoverable macroeconomic crises ($A_G <-> A_B$) trigger a *precautionary "sprint to safety"* in which both $K'_G (0.10)$ and $L_G (0.10)$ *increase* with $p$ to reach $H$ faster.
]

#proof_block[
  In part 1, the one-step conditional expectation inequality and integrability give $bb(E)[Z_(t+1) - Z_t | cal(F)_t] = beta^t { r(K_t, omega_t, a_t) + beta bb(E)[B(K_(t+1), omega_(t+1)) | cal(F)_t] - B(K_t, omega_t) } <= 0$ on ${tau > t}$, so $(Z_(t and tau))$ is an integrable supermartingale and Doob's Optional Stopping Theorem at $T and tau$ yields the value bound. In part 2, along every path staying in $M$ up to $T and tau$, expected cumulative ruin payments prior to exit plus continuation $tilde(beta)_p^(T and tau) (beta p U_0)\/(1 - tilde(beta)_p)$ sum identically to $frac(beta p U_0, 1 - tilde(beta)_p)$, matching the ruin stream of witness $W_X^((p))$ so $U_0$ cancels identically. Because $r(K, s)$ is independent of $tilde(beta)_p$, $partial(W_X^((p)) - E^+)\/partial K$ coincides verbatim with Proposition 1\*\*, preserving state-by-state monotonicity whenever boundary checks at $b = 0.10$ and $h = 0.28$ remain positive (verified over $p in [0, 2.00\%]$ with global super-solution $Psi^((p))$ over $[0.0014, 45.0]$ plus contraction tails on $(0, 0.0014]$ and $(45, infinity)$). In part 3, for $(x, y) in M times M$ and $omega in {G, B\}$, minimizing the affine function $eta y\/C_(max, omega) + beta_- (P bold(m))_omega (h - y)$ on $y in [b, h]$ occurs at $y in {b, h}$, validating $r_omega (x, y) + beta bb(E)[B(y, omega') | omega] <= B(x, omega)$ identically when $(I - beta_- P) bold(B)_* = hat(bold(R)) - bold(Delta)$; since $rho(beta_- P) = beta_- < 1$, explicit inversion is positive and Doob at $T and tau$ rules out $bb(P)(tau > T^*_omega) = 1$ (and gives $bb(P)(tau <= T) >= [W_omega - B_omega - beta_+^T max(Psi - B_*)]\/[beta_-^3 max(Psi(y_(max)) - B_*) - beta_+^T max(Psi - B_*)] > 0$ from $x_0 = 0.10$). Part 4 follows from Howard-accelerated 880-point continuous stochastic VFI.
]

#v(0.2em)
#figure(
  text(size: 7.7pt, table(
    columns: (0.68fr, 0.72fr, 1.25fr, 1.22fr, 1.92fr, 1.28fr),
    align: (center, center, center, center, center, center),
    inset: (x: 3pt, y: 3.5pt),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [Hazard $p$], [Doob \ $T^*(p)$], [$bb(P)_("Doob") (p)$ vs. \ $(1 - p)^23$], [Markov $2 times 2$ \ $B_G (0.10)$ / $T^*_G$], [Ruin VFI ($tilde(beta)_p$) \ $S_p$ ; $K'(0.10)$ ; $L$], [Markov VFI ($G$) \ $K'_G (0.10)$ ; $L_G$],
    table.hline(stroke: 0.6pt),
    [$0.0\%$], [*$21$*], [*$1.000$* / $1.000$], [$-43.358$ / $21$], [$0.001588$ ; $0.13364$ ; $0.6626$], [$0.13369$ ; $0.6632$],
    [$0.5\%$], [*$24$*], [*$0.887$* / $0.891$], [$-43.508$ / $22$], [$0.001670$ ; $0.13324$ ; $0.6579$], [$0.13380$ ; $0.6645$],
    [$1.0\%$], [*$29$*], [*$0.747$* / $0.794$], [$-43.654$ / $22$], [$0.001769$ ; $0.13294$ ; $0.6545$], [$0.13385$ ; $0.6651$],
    [$1.5\%$], [*$38$*], [*$0.563$* / $0.706$], [$-43.796$ / $23$], [$0.001884$ ; $0.13254$ ; $0.6502$], [$0.13389$ ; $0.6657$],
    [$2.0\%$], [*$74$*], [*$0.224$* / $0.628$], [$-43.935$ / $24$], [$0.002013$ ; $0.13219$ ; $0.6464$], [$0.13392$ ; $0.6660$],
    [$5.0\%$], [$> p_("cert")$], [— / $0.307$], [$-44.695$ / $29$], [$0.003053$ ; $0.12990$ ; $0.6225$], [$0.13432$ ; $0.6707$],
    [$8.0\%$], [$> p_("cert")$], [— / $0.147$], [$-45.353$ / $34$], [*$0.004589$* ; *$0.12757$* ; *$0.6008$*], [*$0.13474$* ; *$0.6759$*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Joint stochastic verification of Theorem 11\* over box (7.3): endogenous Doob certificate under crisis anticipation ($p_("cert") = 2.07\%$), coupled 2-state Markov system ($A_G = 0.75 <-> A_B = 0.35, r_("rec") = 1\/3$), and 880-point VFI policy contrast between ruin discouragement and precautionary sprint-to-safety.],
)

#figure(
  image("fig4_structural_en.svg", width: 100%),
  caption: [Structural extensions of the model. Panel (a) illustrates unbounded hockey-stick growth ($K_t = (1+g)^t hat(K)_t$) for consolidated firms ($M = 1$) vs. collapse under regulatory fragmentation ($M = 2$, $A_("ef") = A\/M^(theta-1)$); Panel (b) contrasts the genuine anticipation-adjusted Doob survival probability $(1 - p)^(T^*(p))$ ($tilde(beta)_p = beta(1 - p)$, breakdown at $p_("cert") approx 2.07\%$) against the naive deterministic bounds $(1 - p)^23$ and $(1 - p)^46$.],
)

= Conclusion

Milei and Reidel (2026) introduce a rigorous mathematical framework for extinction traps and certified optimal survival in nonconcave growth models with endogenous labor. We have shown that their analytical apparatus admits four targeted extensions and quantitative strengthenings that answer its open questions, tighten all FPBB certificate margins, and expand its economic applications:

1. *Full sharpening of the FPBB certificate (Section 3):* Without altering any primitive or assumption of Section 7.2, replacing the disjoint-pair bound (7.6) with our *one-step affine regional barrier* $B_1 (K)$ (Lemma 1 and Theorem 9\*) nearly triples the staying calibration margin ($> 7.4665$) and *cuts the certified productive entry deadline exactly in half* (from $46$ to *$23$ periods*, and within $33$ total periods from $K_0 = 0.05$ via Proposition 1\*). Furthermore, the analytical interval certificate of Proposition 1\*\* excludes interior minima and collapses the twelve finite subintervals of Table 5 into two boundary evaluations, raising the adverse-exit margin on $M$ to $> 0.0947$ and lifting the global FPBB certificate margin from $0.0423$ ($0.04$) to *$> 0.0571$* ($+35\%$).
2. *Asymptotic frontier convergence, variational criterion, and labor isomorphism (Section 4):* Rescaled analysis at $K = A^(-1\/r) k$ together with the exact isomorphism $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$ (Theorem 3\*) resolves Footnote 1: we prove under the patience condition that both rescaled frontiers converge to the common physical limit $(delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), state a precise variational criterion for $S_A^("fix") (1) < S_A$, and corroborate this frontier convergence directly via VFI.
3. *Institutional U-curve and fiscal–regulatory decomposition (Section 5):* Microfounding Section 4.3 with balanced-budget productive public spending ($G_t = tau_p Y_t$) and unproductive compliance overhead ($tau_u$) yields Theorem 10, cleanly separating the exact differentiable U-curve of the physical floor $kappa(tau)$ and certified upper bound $overline(S)(tau)$ at $tau^* = alpha\/(1+alpha)$, finite-$A_0$ level-set symmetry of $S(tau)$, and the exact asymptotic $S(tau)$ profile as $A_0 -> infinity$, while preserving monotonicity against unproductive waste $tau_u$.
4. *Decentralization, unbounded growth, and stochastic barriers (Section 6):* Finally, our structural extensions formalize monopolistic decentralization with consistent Euler factor accounting $(theta\/mu) Y_t$ and spillover decentralization (proving a TFP collapse $A\/M^(theta-1)$ under firm fragmentation), eliminate the stationary ceiling $K_p^+$ via efficiency-unit scaling to yield perpetual hockey-stick growth, and close Theorem 11\* stochastically via Doob's Optional Stopping Theorem with endogenous deadlines $T^*(p)$ (vs. the myopic $23$-period bound), coupled Markov barriers $(B_G, B_B)$, and 880-point forward-looking stochastic VFI.

= References

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
- Milei, J., and D. Reidel (2026): _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, Working Paper, October 2026.
- Milgrom, P., and I. Segal (2002): "Envelope Theorems for Arbitrary Choice Sets," _Econometrica_, 70(2), 583–601.
- Mitra, T., and D. Ray (1984): "Dynamic Optimization on a Non-Convex Feasible Set: Some General Results for Non-Smooth Technologies," _Journal of Economics_ (_Zeitschrift für Nationalökonomie_), 44(2), 151–175.
- Noroozi, N., R. Geiselhart, L. Grüne, and F. R. Wirth (2020): "Control of Discrete-Time Nonlinear Systems via Finite-Step Control Lyapunov Functions," _Systems & Control Letters_, 138, 104631.
- Restuccia, D., and R. Rogerson (2008): "Policy Distortions and Aggregate Productivity with Heterogeneous Establishments," _Review of Economic Dynamics_, 11(4), 707–720.
- Romer, P. M. (1986): "Increasing Returns and Long-Run Growth," _Journal of Political Economy_, 94(5), 1002–1037.
- Skiba, A. K. (1978): "Optimal Growth with a Convex–Concave Production Function," _Econometrica_, 46(3), 527–539.
- Stokey, N. L., and R. E. Lucas, Jr., with E. C. Prescott (1989): _Recursive Methods in Economic Dynamics_. Cambridge, MA: Harvard University Press.
- Trebbi, F., M. B. Zhang, and M. Simkovic (2026): "The Cost of Regulatory Compliance in the United States," _The Review of Financial Studies_, 39(9), 2901–2962.
- Wagener, F. (2020): "Geometrical Methods for Analyzing the Optimal Management of Tipping Point Dynamics," _Natural Resource Modeling_, 33(3), e12258.
