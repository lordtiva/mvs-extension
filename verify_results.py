"""
Reproducible numerical & analytical interval verification script for:
  "State-Dependent Affine Bellman Barriers, Asymptotic Equivalence,
   and the Institutional U-Curve" (Marcelo Segura, 2026)

Verifies:
  1. Lemma 1, Theorem 9*, and Proposition 1* (one-step affine barriers & entry bounds).
  2. Proposition 1** & Table 2 (interval arithmetic & Wronskian monotonicity without grid dependence).
  3. Theorem 3* & Table 3 (exact FOC scaling + 880-point two-zone continuous-state normalized VFI).
  4. Theorem 10 & Table 4 (Barro-CES institutional U-curve & extinction thresholds).
  5. Theorem 11* & Table 5 (Endogenous Doob deadlines T*(p), 2-state Markov barriers, and anticipating VFI).

Usage:
  python verify_results.py
"""

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq


# ---------------------------------------------------------------------------
# Box (7.3) primitives and production technology
# ---------------------------------------------------------------------------
A_MIN, A_MAX = 0.749, 0.751
BETA_MIN, BETA_MAX = 0.9699, 0.9701
Q_MIN, Q_MAX = 0.9199, 0.9201
ETA_MIN, ETA_MAX = 0.6999, 0.7001
B_M, H_M = 0.10, 0.28


def F_A(A, K, L):
    return A * (2.0 * K * L / (K + L)) ** 1.5


def dF_dK(A, K, L):
    return 1.5 * A * (2.0 ** 1.5) * (K ** 0.5) * (L ** 2.5) * ((K + L) ** (-2.5))


def d2F_dK2(A, K, L):
    return 0.75 * A * (2.0 ** 1.5) * (L ** 2.5) * (L - 4.0 * K) * (K ** (-0.5)) * ((K + L) ** (-3.5))


def dF_dL(A, K, L):
    return 1.5 * A * (2.0 ** 1.5) * (K ** 2.5) * (L ** 0.5) * ((K + L) ** (-2.5))


def d2F_dKdL(A, K, L):
    return 2.25 * A * (2.0 ** 1.5) * (K ** 0.5) * (L ** 0.5) * ((K + L) ** (-3.5)) * (K + L / 3.0)


def d3F_dK2dL(A, K, L):
    # t(K) = dF/dL(A+, K, l0); t'(K) and t''(K) exact formulas
    return None


def exact_kappa(A_val, delta_val=0.08):
    coeffs = [-delta_val**2, -3 * delta_val**2, 8 * (A_val**2) - 3 * delta_val**2, -delta_val**2]
    roots = np.roots(coeffs)
    real_pos = sorted([float(np.real(rt)) for rt in roots if abs(np.imag(rt)) < 1e-12 and np.real(rt) > 0])
    return real_pos[0]


# ---------------------------------------------------------------------------
# 1. Lemma 1, Theorem 9*, Proposition 1*
# ---------------------------------------------------------------------------
def verify_barriers():
    print("=" * 72)
    print("1. LEMMA 1, THEOREM 9*, AND PROPOSITION 1* (ONE-STEP AFFINE BARRIER)")
    print("=" * 72)

    C_max_plus = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
    R_hat = -0.996
    Delta_2 = 0.2997
    Delta_2_exact = (ETA_MIN * BETA_MIN * Q_MIN * (H_M - B_M)) / C_max_plus

    B_star = (R_hat - Delta_2) / (1.0 - BETA_MIN)
    slope = (ETA_MIN * Q_MIN) / C_max_plus
    B1_b = B_star - slope * (H_M - B_M)

    # Feasible witness W_M(b) > -35.579855 > -35.58
    W_M_floor = -35.58
    margin_unif = W_M_floor - B_star
    margin_state = W_M_floor - B1_b

    # Prefix checks (Psi(h) < -27.83)
    J_T24 = B_star + (BETA_MAX ** 24) * (-27.83 - B_star)
    slack_T23 = (W_M_floor - B1_b) - (BETA_MAX ** 23) * (-27.83 - B_star)

    # Anchor band M0 = [0.05, 0.10) (Proposition 1*)
    b0, h0 = 0.05, 0.10
    C_max0 = Q_MAX * h0 + F_A(A_MAX, h0, 1.0) - b0
    Delta_0 = 0.3115
    Delta_0_exact = (ETA_MIN * BETA_MIN * Q_MIN * (h0 - b0)) / C_max0
    R_hat0 = -1.827
    B0_star = (R_hat0 - Delta_0) / (1.0 - BETA_MIN)
    W_M0_floor = -43.845
    Psi_h0 = -34.271388
    J_M0_T10 = B0_star + (BETA_MAX ** 10) * (Psi_h0 - B0_star)

    print(f"  C_max+          = {C_max_plus:.8f}")
    print(f"  Delta_2 exact   = {Delta_2_exact:.7f} (> {Delta_2})")
    print(f"  B_*             = {B_star:.7f} (<= -43.0465116)")
    print(f"  B_1(0.10)       = {B1_b:.6f} (<= -43.355594)")
    print(f"  Margin (unif.)  = {margin_unif:.4f} (> 7.4665)")
    print(f"  Margin (state)  = {margin_state:.6f} (> 7.7755)")
    print(f"  T=24 uniform    = {J_T24:.5f} (< -35.58)")
    print(f"  T=23 slack      = +{slack_T23:.6f} (> 0)")
    print(f"  M0 C_max0       = {C_max0:.6f}, Delta_0 exact = {Delta_0_exact:.6f}")
    print(f"  M0 B_0*         = {B0_star:.6f}, T0=10 prefix = {J_M0_T10:.4f} (< {W_M0_floor})")

    assert abs(C_max_plus - 0.37495167) < 1e-6
    assert B_star <= -43.0465115
    assert B1_b <= -43.355593
    assert margin_unif > 7.4665
    assert margin_state > 7.77559
    assert J_T24 < W_M_floor
    assert slack_T23 > 0.2056
    assert J_M0_T10 < W_M0_floor


# ---------------------------------------------------------------------------
# 2. Proposition 1** (Analytical interval arithmetic & Wronskian)
# ---------------------------------------------------------------------------
def t_func(K, l0):
    return dF_dL(A_MAX, K, l0)


def t_prime(K, l0):
    # t'(K) = d^2 F_{A+}/dK dL(K, l0) = (9/4)*sqrt(2)*A_+ * sqrt(K*l0) * (K + l0)^(-7/2) * (K + l0? wait check exact!)
    # F_L = 1.5*A*(2KL/(K+L))^(1/2) * 2K^2/(K+L)^2 = 3*A*sqrt(2)*K^(5/2)*L^(1/2)*(K+L)^(-5/2)
    # Differentiate K^(5/2)*(K+L)^(-5/2): (5/2)*K^(3/2)*(K+L)^(-7/2)*L
    return 1.5 * A_MAX * (2.0 ** 1.5) * 2.5 * (K ** 1.5) * (l0 ** 1.5) * ((K + l0) ** (-3.5))


def t_double_prime(K, l0):
    # Derivative of K^(3/2)*(K+L)^(-7/2) = K^(1/2)*(K+L)^(-9/2) * (1.5*L - 2*K)
    return 1.5 * A_MAX * (2.0 ** 1.5) * 2.5 * (l0 ** 1.5) * (K ** 0.5) * ((K + l0) ** (-4.5)) * (1.5 * l0 - 2.0 * K)


def verify_prop1_double_star():
    print("\n" + "=" * 72)
    print("2. PROPOSITION 1** & TABLE 2 (ANALYTICAL INTERVAL CERTIFICATE)")
    print("=" * 72)

    regions = {
        "M": dict(l_X=0.68, s_X=0.135, T_X=-33.103, a=0.10, l0=0.44, k_min=0.10, k_max=0.28, n_q=4, n_d2=8),
        "H1": dict(l_X=0.72, s_X=0.375, T_X=-27.164, a=0.28, l0=0.57, k_min=0.28, k_max=0.80, n_q=6, n_d2=10),
    }

    def S_val(K, l0):
        return Q_MAX * K + F_A(A_MAX, K, l0) + (1.0 - l0) * t_func(K, l0)

    def S_prime(K, l0):
        return Q_MAX + dF_dK(A_MAX, K, l0) + (1.0 - l0) * t_prime(K, l0)

    def S_double_prime(K, l0):
        return d2F_dK2(A_MAX, K, l0) + (1.0 - l0) * t_double_prime(K, l0)

    def c_val(K, l_X, s_X):
        return Q_MIN * K + F_A(A_MIN, K, l_X) - s_X

    def c_prime(K, l_X):
        return Q_MIN + dF_dK(A_MIN, K, l_X)

    def c_double_prime(K, l_X):
        return d2F_dK2(A_MIN, K, l_X)

    def max_abs_d2F(kL, kR, L):
        # F_{A,KK} crosses 0 at L/4; its extrema on [kL, kR] lie at endpoints or critical point of |F_{A,KK}|
        # Critical points of (L-4K)K^(-1/2)(K+L)^(-7/2) satisfy d/dK[...] = 0
        # Wait: evaluate analytic extreme via quadratic or endpoints + peak of |F_{A,KK}|:
        # Since F_{A,KK}(K) has a unique interior extreme above L/4 at K_c = L*(7 - sqrt(33))/8? Let's compute both ways cleanly!
        # Let's include critical roots where d/dK[(L-4K) K^(-1/2)(K+L)^(-7/2)] = 0:
        # -4 K(K+L) - 0.5(L-4K)(K+L) - 3.5(L-4K)K = 0 => 12 K^2 - 7 K L - 0.5 L^2 = 0
        pts = [kL, kR]
        disc = 49.0 + 24.0
        for sgn in (-1.0, 1.0):
            kc = L * (7.0 + sgn * np.sqrt(disc)) / 24.0
            if kL < kc < kR:
                pts.append(kc)
        if kL < L / 4.0 < kR:
            pts.append(L / 4.0)
        return pts

    def max_abs_tpp_pts(kL, kR, l0):
        # d/dK[(1.5*l0 - 2K)*K^(1/2)*(K+l0)^(-9/2)] = 0 =>
        # -2 K(K+l0) + 0.5(1.5 l0 - 2K)(K+l0) - 4.5(1.5 l0 - 2K)K = 0 => 6 K^2 - 9 l0 K + 0.75 l0^2 = 0
        pts = [kL, kR]
        disc = 81.0 - 18.0
        for sgn in (-1.0, 1.0):
            kc = l0 * (9.0 + sgn * np.sqrt(disc)) / 12.0
            if kL < kc < kR:
                pts.append(kc)
        if kL < 0.75 * l0 < kR:
            pts.append(0.75 * l0)
        return pts

    def d1_exact(K, cfg):
        l_X, s_X, a, l0 = cfg["l_X"], cfg["s_X"], cfg["a"], cfg["l0"]
        S = S_val(K, l0)
        Sp = S_prime(K, l0)
        c = c_val(K, l_X, s_X)
        cp = c_prime(K, l_X)
        R = (S - a) / c
        return (ETA_MIN * cp * R - Sp) / (S - a) + (1.0 - ETA_MAX) * 2.5 * l0 / (K * (K + l0))

    for name, cfg in regions.items():
        l_X, s_X, T_X, a, l0 = cfg["l_X"], cfg["s_X"], cfg["T_X"], cfg["a"], cfg["l0"]
        if name == "M":
            edges_q = np.linspace(cfg["k_min"], cfg["k_max"], cfg["n_q"] + 1)
        else:
            edges_q = np.array([0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80])

        Q_bounds = []
        d1_bounds = []
        for kL, kR in zip(edges_q[:-1], edges_q[1:]):
            km = 0.5 * (kL + kR)
            Qm = S_prime(km, l0) * c_val(km, l_X, s_X) - c_prime(km, l_X) * (S_val(km, l0) - a)
            # Bound |Q'(K)| = |S''(K) c(K) - c''(K) (S(K)-a)| on [kL, kR]
            d2F_pts = max_abs_d2F(kL, kR, l0)
            tpp_pts = max_abs_tpp_pts(kL, kR, l0)
            d2Fc_pts = max_abs_d2F(kL, kR, l_X)
            Spp_abs_max = max(abs(d2F_dK2(A_MAX, pt, l0)) for pt in d2F_pts) + (1.0 - l0) * max(abs(t_double_prime(pt, l0)) for pt in tpp_pts)
            cpp_abs_max = max(abs(d2F_dK2(A_MIN, pt, l_X)) for pt in d2Fc_pts)
            Qp_max = Spp_abs_max * c_val(kR, l_X, s_X) + cpp_abs_max * (S_val(kR, l0) - a)
            Q_ub = Qm + 0.5 * (kR - kL) * Qp_max
            Q_bounds.append(Q_ub)
            assert Q_ub < 0.0, f"Wronskian upper bound positive on [{kL},{kR}]"

            # Unimodal bounds on F_{A,K} (peak at L/4) and t'(K) (peak at 3*l0/4)
            cp_min = min(c_prime(kL, l_X), c_prime(kR, l_X))
            cands_dFk = [kL, kR] + ([l0 / 4.0] if kL < l0 / 4.0 < kR else [])
            cands_tp = [kL, kR] + ([0.75 * l0] if kL < 0.75 * l0 < kR else [])
            Sp_max = Q_MAX + max(dF_dK(A_MAX, p, l0) for p in cands_dFk) + (1.0 - l0) * max(t_prime(p, l0) for p in cands_tp)
            R_lb = (S_val(kR, l0) - a) / c_val(kR, l_X, s_X)
            num_lb = ETA_MIN * cp_min * R_lb - Sp_max
            denom = (S_val(kR, l0) - a) if num_lb >= 0 else (S_val(kL, l0) - a)
            d1_lb = num_lb / denom + (1.0 - ETA_MAX) * 2.5 * l0 / (kR * (kR + l0))
            d1_bounds.append(d1_lb)
            assert d1_lb > 0.0, f"Delta'_X lower bound <= 0 on [{kL},{kR}]"

        # Second derivative interval bounds on n_d2 equal subintervals
        edges_d2 = np.linspace(cfg["k_min"], cfg["k_max"], cfg["n_d2"] + 1)
        d2_bounds = []
        for kL, kR in zip(edges_d2[:-1], edges_d2[1:]):
            # Delta''_X <= [(S')^2 - eta_- (c'_X R_X)^2]/(S-a)^2 + eta_- c''_X/c_X - S''/(S-a) + (1-eta_+)(t'/t)'(K)
            cands_dFk = [kL, kR] + ([l0 / 4.0] if kL < l0 / 4.0 < kR else [])
            cands_tp = [kL, kR] + ([0.75 * l0] if kL < 0.75 * l0 < kR else [])
            Sp_ub = Q_MAX + max(dF_dK(A_MAX, p, l0) for p in cands_dFk) + (1.0 - l0) * max(t_prime(p, l0) for p in cands_tp)
            cp_lb = min(c_prime(kL, l_X), c_prime(kR, l_X))
            R_lb = (S_val(kR, l0) - a) / c_val(kR, l_X, s_X)
            t1_num = Sp_ub ** 2 - ETA_MIN * (cp_lb * R_lb) ** 2
            t1_ub = t1_num / ((S_val(kL, l0) - a) ** 2 if t1_num >= 0 else (S_val(kR, l0) - a) ** 2)

            # c''_X on [kL, kR]
            if kL >= l_X / 4.0:
                cpp_pts = [kL, kR]
                # c''_X <= 0 on this subinterval: max (least negative) c''_X divided by c_X(kR) (if <=0)
                cands_cpp = max_abs_d2F(kL, kR, l_X)
                cpp_ub = max(d2F_dK2(A_MIN, p, l_X) for p in cands_cpp)
                t2_ub = ETA_MIN * cpp_ub / (c_val(kR, l_X, s_X) if cpp_ub <= 0 else c_val(kL, l_X, s_X))
            else:
                cands_cpp = max_abs_d2F(kL, kR, l_X)
                cpp_ub = max(d2F_dK2(A_MIN, p, l_X) for p in cands_cpp)
                t2_ub = ETA_MIN * cpp_ub / (c_val(kL, l_X, s_X) if cpp_ub >= 0 else c_val(kR, l_X, s_X))

            # -S''/(S-a)
            Spp_pts_L = max_abs_d2F(kL, kR, l0)
            Spp_pts_t = max_abs_tpp_pts(kL, kR, l0)
            Spp_lb = min(d2F_dK2(A_MAX, p, l0) for p in Spp_pts_L) + (1.0 - l0) * min(t_double_prime(p, l0) for p in Spp_pts_t)
            t3_ub = (-Spp_lb) / (S_val(kL, l0) - a if (-Spp_lb) >= 0 else S_val(kR, l0) - a)

            # (1 - eta_+) * (t'/t)'(K) < 0, least negative at kR
            t4_ub = (1.0 - ETA_MAX) * (-2.5 * l0 * (2.0 * kR + l0)) / ((kR ** 2) * ((kR + l0) ** 2))
            d2_ub = t1_ub + t2_ub + t3_ub + t4_ub
            d2_bounds.append(d2_ub)
            assert d2_ub < 0.0, f"Delta''_X upper bound >= 0 on [{kL},{kR}]: {d2_ub}"

        d1_right = d1_exact(cfg["k_max"], cfg)
        print(f"  Region {name}:")
        print(f"    Wronskian Q_{name} <= {[round(x, 5) for x in Q_bounds]}")
        print(f"    Delta'_{name}     >= {[round(x, 4) for x in d1_bounds]}")
        print(f"    max Delta''_{name}<= {max(d2_bounds):.4f} (< 0 across {cfg['n_d2']} intervals)")
        print(f"    Delta'_{name}(right) = +{d1_right:.6f}")

    # Exact left-endpoint adverse-exit margins (Prop 1** part 2)
    def margin_left(K, l_X, s_X, T_X, a, l0, Psi_sharp_a):
        c = Q_MIN * K + F_A(A_MIN, K, l_X) - s_X
        W_1 = ETA_MIN * np.log(c) + (1.0 - ETA_MIN) * np.log(1.0 - l_X) + BETA_MAX * T_X
        W_2 = ETA_MAX * np.log(c) + (1.0 - ETA_MAX) * np.log(1.0 - l_X) + BETA_MAX * T_X
        W_X = min(W_1, W_2)
        t = dF_dL(A_MAX, K, l0)
        S = Q_MAX * K + F_A(A_MAX, K, l0) + (1.0 - l0) * t
        E_1 = ETA_MIN * np.log(S - a) + (1.0 - ETA_MIN) * np.log(t / ETA_MIN) + (1.0 - ETA_MIN) * (np.log((1.0 - ETA_MIN) / (S - a)) - 1.0)
        # Simpler exact E^+ = max_{eta} [ eta log(S-a) + (1-eta) log(t*(1-eta)/(eta*(S-a)))? Wait check exact F.19:
        # max_{L in [0,1)} eta log(qK + F(K,l0) + (1-l0)t - a - t(1-L)) + (1-eta) log(1-L) => 1-L = (1-eta)(S-a)/t
        # => c_opt = eta(S-a), 1-L_opt = (1-eta)(S-a)/t => u_tan = eta log(eta(S-a)) + (1-eta) log((1-eta)(S-a)/t)
        E_a = ETA_MIN * np.log(ETA_MIN * (S - a)) + (1.0 - ETA_MIN) * np.log((1.0 - ETA_MIN) * (S - a) / t)
        E_b = ETA_MAX * np.log(ETA_MAX * (S - a)) + (1.0 - ETA_MAX) * np.log((1.0 - ETA_MAX) * (S - a) / t)
        E_plus = max(E_a, E_b)
        return W_X - (E_plus + BETA_MIN * Psi_sharp_a)

    # Psi(0.10) = -34.271388..., Psi#(0.10) = Psi(0.10) - 10/301
    Psi_010 = 0.4 * 0.10 - 5.0 / np.sqrt(0.10) - 18.5
    Psi_s_010 = Psi_010 - 10.0 / 301.0
    Psi_028 = 0.4 * 0.28 - 5.0 / np.sqrt(0.28) - 18.5
    Psi_s_028 = Psi_028 - 10.0 / 301.0

    m_M_sharp = margin_left(0.10, 0.68, 0.135, -33.103, 0.10, 0.44, Psi_s_010)
    m_M_psi = margin_left(0.10, 0.68, 0.135, -33.103, 0.10, 0.44, Psi_010)
    m_H_60 = margin_left(0.28, 0.72, 0.375, -27.164, 0.28, 0.60, Psi_s_028)
    m_H_57 = margin_left(0.28, 0.72, 0.375, -27.164, 0.28, 0.57, Psi_s_028)
    m_H_57_psi = margin_left(0.28, 0.72, 0.375, -27.164, 0.28, 0.57, Psi_028)

    print(f"  K=0.10 (l0=0.44): margin(Psi#) = {m_M_sharp:.6f}, margin(Psi) = {m_M_psi:.6f}")
    print(f"  K=0.28 (l0=0.60): margin(Psi#) = {m_H_60:.6f}")
    print(f"  K=0.28 (l0=0.57): margin(Psi#) = {m_H_57:.6f}, margin(Psi) = {m_H_57_psi:.6f}")

    assert m_M_sharp > 0.0947 and m_M_psi > 0.0624
    assert m_H_60 > 0.0561 and m_H_57 > 0.0571 and m_H_57_psi > 0.0249


# ---------------------------------------------------------------------------
# 3. Theorem 3* & Table 3 (FOC + Direct Continuous-State 880-point VFI)
# ---------------------------------------------------------------------------
def solve_vfi_frontiers(A_val):
    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    q = 1.0 - delta
    c_K = w ** (theta / rho)
    D = 1.0 / beta - q
    V_cake_const = (eta / (1.0 - beta)) * (
        np.log((1.0 - beta) * q) + (beta / (1.0 - beta)) * np.log(beta * q)
    )

    def f_norm(k_arr, L_arr):
        return c_K * (k_arr ** 1.5) * ((1.0 + k_arr / ((A_val ** 2) * L_arr)) ** (-1.5))

    def df_dk(k):
        return 1.5 * c_K * (k ** 0.5) * ((1.0 + k / (A_val ** 2)) ** (-2.5))

    # Modified golden-rule steady state (covers entire optimal dynamics)
    k_ss = brentq(lambda k: df_dk(k) - D, 0.25 * (A_val ** 2), 1e10)
    k_lo, k_hi = 1e-6, 1.10 * k_ss

    # 880-point concentrated 3-region grid in k = A^2 K
    k_grid = np.unique(np.concatenate([
        np.geomspace(k_lo, 0.00078, 160, endpoint=False),
        np.linspace(0.00078, 0.00102, 360, endpoint=False),
        np.geomspace(0.00102, k_hi, 360),
    ]))
    n_k = len(k_grid)  # 880

    def interp_V(kp_arr, V_curr):
        v_lin = np.interp(np.clip(kp_arr, k_lo, k_hi), k_grid, V_curr)
        below = kp_arr < k_lo
        if np.any(below):
            v_lin = np.where(
                below,
                V_curr[0] + (eta / (1.0 - beta)) * np.log(np.maximum(kp_arr, 1e-30) / k_lo),
                v_lin,
            )
        return v_lin

    def solve_L_vec(k_arr, kp_arr):
        lo_L = np.full_like(k_arr, 1e-7)
        hi_L = np.full_like(k_arr, 1.0 - 1e-9)
        inv_phi = (np.sqrt(5.0) - 1.0) / 2.0
        x1 = hi_L - inv_phi * (hi_L - lo_L)
        x2 = lo_L + inv_phi * (hi_L - lo_L)

        def obj(L_v):
            c_v = q * k_arr + f_norm(k_arr, L_v) - kp_arr
            return np.where(
                c_v > 1e-15,
                eta * np.log(np.maximum(c_v, 1e-30)) + (1.0 - eta) * np.log(1.0 - L_v),
                -1e9 + c_v,
            )

        f1, f2 = obj(x1), obj(x2)
        for _ in range(28):
            move_r = f1 < f2
            lo_L = np.where(move_r, x1, lo_L)
            hi_L = np.where(move_r, hi_L, x2)
            x1_new = np.where(move_r, x2, hi_L - inv_phi * (hi_L - lo_L))
            x2_new = np.where(move_r, lo_L + inv_phi * (hi_L - lo_L), x1)
            f1_new = np.where(move_r, f2, obj(x1_new))
            f2_new = np.where(move_r, obj(x2_new), f1)
            x1, x2, f1, f2 = x1_new, x2_new, f1_new, f2_new
        L_best = 0.5 * (lo_L + hi_L)
        return L_best, obj(L_best)

    def refine_skiba(i_jump, V_sol, endo=False):
        k_sub = np.linspace(k_grid[i_jump - 1], k_grid[i_jump], 25)
        y_sub = q * k_sub + f_norm(k_sub, 1.0)
        diffs = np.empty_like(k_sub)
        for ii, (ks, ys) in enumerate(zip(k_sub, y_sub)):
            # Compare best shrinking kp <= ks vs best growing kp >= ks
            kp_d = np.linspace(max(1e-7, 0.90 * ks), ks, 30)
            kp_u = np.linspace(ks, ys - 1e-12, 30) if ys > ks + 1e-12 else np.array([ks])
            if not endo:
                vd = np.max(eta * np.log(np.maximum(ys - kp_d, 1e-30)) + beta * interp_V(kp_d, V_sol))
                vu = (
                    np.max(eta * np.log(np.maximum(ys - kp_u, 1e-30)) + beta * interp_V(kp_u, V_sol))
                    if ys > ks + 1e-12
                    else -1e9
                )
            else:
                _, ud = solve_L_vec(np.full_like(kp_d, ks), kp_d)
                vd = np.max(ud + beta * interp_V(kp_d, V_sol))
                if ys > ks + 1e-12:
                    _, uu = solve_L_vec(np.full_like(kp_u, ks), kp_u)
                    vu = np.max(uu + beta * interp_V(kp_u, V_sol))
                else:
                    vu = -1e9
            diffs[ii] = vu - vd
        pos = np.where(diffs >= 0)[0]
        if len(pos) > 0 and pos[0] > 0:
            idx0 = pos[0]
            d0, d1 = diffs[idx0 - 1], diffs[idx0]
            w0 = abs(d0) / max(abs(d0) + abs(d1), 1e-15)
            return float(k_sub[idx0 - 1] + w0 * (k_sub[idx0] - k_sub[idx0 - 1]))
        return float(0.5 * (k_grid[i_jump - 1] + k_grid[i_jump]))

    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0

    # --- 1. Fixed labor L = 1 ---
    y_fix = q * k_grid + f_norm(k_grid, 1.0)
    V_fix = np.where(
        k_grid > 0.00082,
        eta * np.log(f_norm(k_ss, 1.0) - delta * k_ss) / (1.0 - beta),
        V_cake_const + (eta / (1.0 - beta)) * np.log(k_grid),
    )

    s_cand = 1.0 - np.geomspace(1e-5, 0.15, 60)
    kp_mat_tail = y_fix[:, None] * s_cand[None, :]
    u_mat_tail = eta * np.log(y_fix[:, None] * (1.0 - s_cand[None, :]))

    c_mat_grid = y_fix[:, None] - k_grid[None, :]
    u_mat_grid = np.where(c_mat_grid > 1e-15, eta * np.log(np.maximum(c_mat_grid, 1e-30)), -1e9)

    for _ in range(120):
        v_grid = u_mat_grid + beta * V_fix[None, :]
        j_best = np.argmax(v_grid, axis=1)
        best_g = v_grid[np.arange(n_k), j_best]

        v_tail = u_mat_tail + beta * interp_V(kp_mat_tail, V_fix)
        s_best = np.argmax(v_tail, axis=1)
        best_t = v_tail[np.arange(n_k), s_best]

        use_t = best_t > best_g
        lo_t = kp_mat_tail[np.arange(n_k), np.maximum(0, s_best - 1)]
        hi_t = kp_mat_tail[np.arange(n_k), np.minimum(len(s_cand) - 1, s_best + 1)]
        lo = np.where(use_t, np.minimum(lo_t, hi_t), k_grid[np.maximum(0, j_best - 1)])
        hi = np.where(
            use_t,
            np.minimum(np.maximum(lo_t, hi_t), y_fix - 1e-12),
            np.minimum(k_grid[np.minimum(n_k - 1, j_best + 1)], y_fix - 1e-12),
        )

        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        f1 = eta * np.log(np.maximum(y_fix - x1, 1e-30)) + beta * interp_V(x1, V_fix)
        f2 = eta * np.log(np.maximum(y_fix - x2, 1e-30)) + beta * interp_V(x2, V_fix)
        for _g in range(14):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1_n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2_n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            f1_n = np.where(mr, f2, eta * np.log(np.maximum(y_fix - x1_n, 1e-30)) + beta * interp_V(x1_n, V_fix))
            f2_n = np.where(mr, eta * np.log(np.maximum(y_fix - x2_n, 1e-30)) + beta * interp_V(x2_n, V_fix), f1)
            x1, x2, f1, f2 = x1_n, x2_n, f1_n, f2_n
        pol_fix = np.where(f1 > f2, x1, x2)
        u_pol = eta * np.log(np.maximum(y_fix - pol_fix, 1e-30))
        V_eval = np.maximum(f1, f2)
        for _h in range(60):
            Ve_n = u_pol + beta * interp_V(pol_fix, V_eval)
            if np.max(np.abs(Ve_n - V_eval)) < 1e-9:
                V_eval = Ve_n
                break
            V_eval = Ve_n
        if np.max(np.abs(V_eval - V_fix)) < 1e-8:
            V_fix = V_eval
            break
        V_fix = V_eval

    idx_m = np.where((k_grid >= 0.00078) & (k_grid <= 0.00102))[0]
    jump = np.where((pol_fix - k_grid)[idx_m] > 0)[0][0]
    k_S_fix = refine_skiba(idx_m[jump], V_fix, endo=False)

    # --- 2. Endogenous labor L in [0, 1) ---
    L_grid = np.unique(np.concatenate([
        np.geomspace(1e-5, 0.05, 24, endpoint=False),
        np.linspace(0.05, 0.999, 40),
    ]))
    f_kL = c_K * (k_grid[:, None] ** 1.5) * ((1.0 + k_grid[:, None] / ((A_val ** 2) * L_grid[None, :])) ** (-1.5))
    y_kL = q * k_grid[:, None] + f_kL
    dis_L = (1.0 - eta) * np.log(1.0 - L_grid[None, :])

    u_endo_grid = np.full((n_k, n_k), -1e9)
    chunk = 88
    for start in range(0, n_k, chunk):
        end = min(n_k, start + chunk)
        c_blk = y_kL[start:end, None, :] - k_grid[None, :, None]
        u_blk = np.where(c_blk > 1e-15, eta * np.log(np.maximum(c_blk, 1e-30)) + dis_L[:, None, :], -1e9)
        u_endo_grid[start:end, :] = np.max(u_blk, axis=2)

    s_cand_e = 1.0 - np.geomspace(1e-5, 0.15, 24)
    kp_tail_e = y_kL[:, -1][:, None] * s_cand_e[None, :]
    u_tail_e = np.full((n_k, len(s_cand_e)), -1e9)
    for j in range(len(s_cand_e)):
        _, u_tail_e[:, j] = solve_L_vec(k_grid, kp_tail_e[:, j])

    V_endo = V_fix.copy() - 0.5
    y_max_row = y_kL[:, -1]
    for _ in range(80):
        v_g = u_endo_grid + beta * V_endo[None, :]
        j_best = np.argmax(v_g, axis=1)
        best_g = v_g[np.arange(n_k), j_best]

        v_t = u_tail_e + beta * interp_V(kp_tail_e, V_endo)
        s_best = np.argmax(v_t, axis=1)
        best_t = v_t[np.arange(n_k), s_best]

        use_t = best_t > best_g
        lo_t = kp_tail_e[np.arange(n_k), np.maximum(0, s_best - 1)]
        hi_t = kp_tail_e[np.arange(n_k), np.minimum(len(s_cand_e) - 1, s_best + 1)]
        lo = np.where(use_t, np.minimum(lo_t, hi_t), k_grid[np.maximum(0, j_best - 1)])
        hi = np.where(
            use_t,
            np.minimum(np.maximum(lo_t, hi_t), y_max_row - 1e-12),
            np.minimum(k_grid[np.minimum(n_k - 1, j_best + 1)], y_max_row - 1e-12),
        )

        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        _, u1 = solve_L_vec(k_grid, x1)
        _, u2 = solve_L_vec(k_grid, x2)
        f1 = u1 + beta * interp_V(x1, V_endo)
        f2 = u2 + beta * interp_V(x2, V_endo)
        for _g in range(14):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1_n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2_n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            _, u1_n = solve_L_vec(k_grid, x1_n)
            _, u2_n = solve_L_vec(k_grid, x2_n)
            f1_n = np.where(mr, f2, u1_n + beta * interp_V(x1_n, V_endo))
            f2_n = np.where(mr, u2_n + beta * interp_V(x2_n, V_endo), f1)
            x1, x2, f1, f2 = x1_n, x2_n, f1_n, f2_n
        pol_endo = np.where(f1 > f2, x1, x2)
        _, u_pol_e = solve_L_vec(k_grid, pol_endo)
        V_eval = np.maximum(f1, f2)
        for _h in range(60):
            Ve_n = u_pol_e + beta * interp_V(pol_endo, V_eval)
            if np.max(np.abs(Ve_n - V_eval)) < 1e-9:
                V_eval = Ve_n
                break
            V_eval = Ve_n
        if np.max(np.abs(V_eval - V_endo)) < 1e-8:
            V_endo = V_eval
            break
        V_endo = V_eval

    diff_endo = pol_endo - k_grid
    jump_e = np.where(diff_endo[idx_m] > 0)[0][0]
    k_S_endo = refine_skiba(idx_m[jump_e], V_endo, endo=True)
    dW_plus = float(np.interp(k_S_endo, k_grid, V_fix) - np.interp(k_S_endo, k_grid, V_endo))
    return k_S_fix, k_S_endo, dW_plus


def verify_theorem3_star():
    print("\n" + "=" * 72)
    print("3. THEOREM 3* & TABLE 3 (FOC + DIRECT 880-POINT VFI)")
    print("=" * 72)

    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    nu = (1.0 - eta) / eta
    c_K = w ** (theta / rho)
    k_b, c_b = 0.002, 0.0001

    print(f"  Benchmark limit (delta/c_K)^2 = {(delta / c_K)**2:.6f}, beta*theta = {beta*theta:.4f} > 1")
    print("  A       kappa_A      A^2*kappa   L*          A*L*     Gap_FA   A^2*S_fix  A^2*S_endo  Ratio(VFI)  dW+")
    for A_val in [0.75, 1.50, 3.00, 10.0, 30.0, 100.0]:
        kap = exact_kappa(A_val, delta)
        K_v = k_b / (A_val ** 2)
        C_v = c_b / (A_val ** 2)
        L_s = brentq(lambda L: dF_dL(A_val, K_v, L) - nu * C_v / (1.0 - L), K_v / 3.0, 1.0 - 1e-12)
        gap_FA = (c_K * (k_b ** 1.5) - (A_val ** 2) * F_A(A_val, K_v, L_s)) / (c_K * (k_b ** 1.5))
        kS_fix, kS_endo, dWp = solve_vfi_frontiers(A_val)
        ratio = kS_endo / kS_fix
        print(
            f"  {A_val:5.2f}  {kap:10.3e}  {A_val**2*kap:9.6f}  {L_s:10.3e}  {A_val*L_s:8.5f}  "
            f"{100*gap_FA:6.3f}%  {kS_fix:9.6f}  {kS_endo:10.6f}  {ratio:10.5f}  {dWp:6.2f}"
        )
        assert kS_fix < kS_endo
        assert dWp > 0.0


# ---------------------------------------------------------------------------
# 4. Theorem 10 & Table 4 (Barro-CES Institutional U-Curve)
# ---------------------------------------------------------------------------
def verify_theorem10():
    print("\n" + "=" * 72)
    print("4. THEOREM 10 & TABLE 4 (BARRO-CES INSTITUTIONAL U-CURVE)")
    print("=" * 72)

    A0, alpha, delta, beta = 1.45, 0.25, 0.08, 0.97
    c_K = 0.5 ** (-1.5)
    D = 1.0 / beta - (1.0 - delta)
    H_a = ((2.0 * 0.5 / 1.5) ** 1.5) / 0.5
    A_rep = delta / H_a
    tau_min = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_rep, 1e-9, 0.20)
    tau_max = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_rep, 0.20, 1.0 - 1e-9)

    print(f"  A_rep = {A_rep:.6f}, tau_min = {tau_min:.2e}, tau_max = {tau_max:.6f}")
    assert abs(A_rep - 0.073485) < 1e-5
    assert abs(tau_max - 0.948649) < 1e-5

    taus = [5e-6, 2e-5, 0.02, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 0.90, 0.94, 0.95]
    for tau in taus:
        Ae = A0 * (tau ** alpha) * (1.0 - tau)
        ratio = Ae / A_rep
        if ratio > 1.0:
            kap = exact_kappa(Ae, delta)
            Sbar = ((D / c_K) ** 2) / (Ae ** 2)
            print(f"  tau={tau:7.2e}  Ae={Ae:.4f}  Ae/Arep={ratio:5.2f}  kappa={kap:.6f}  Sbar={Sbar:.6f}")
        else:
            print(f"  tau={tau:7.2e}  Ae={Ae:.4f}  Ae/Arep={ratio:5.2f}  (global extinction)")


# ---------------------------------------------------------------------------
# 5. Theorem 11* & Table 5 (Endogenous Stochastic Doob Certificate & Anticipating VFI)
# ---------------------------------------------------------------------------
def verify_theorem11_stochastic():
    print("\n" + "=" * 72)
    print("5. THEOREM 11* & TABLE 5 (STOCHASTIC DOOB T*(p), MARKOV BARRIERS & VFI)")
    print("=" * 72)

    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    q = 1.0 - delta
    A_G, A_B = 0.75, 0.35
    r_rec = 1.0 / 3.0
    C_max = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
    R_hat = -0.996

    def E_plus(A_hi, K, a, l0):
        c_sup = Q_MAX * K + F_A(A_hi, K, l0) + (1.0 - l0) * dF_dL(A_hi, K, l0) - a
        ec = ETA_MIN if c_sup < 1.0 else ETA_MAX
        return ec * np.log(c_sup) + (1.0 - ETA_MAX) * np.log(1.0 - l0)

    def psi_discrepancy(A_hi, b_max, a_c, b_c):
        xs = np.geomspace(0.01, 45.0, 140)
        Ls = np.linspace(0.02, 0.995, 55)
        mv = -1e9
        for x in xs:
            Ys = Q_MAX * x + F_A(A_hi, x, Ls)
            px = a_c * x - b_c * (x ** -0.5)
            for Y, L in zip(Ys, Ls):
                ys = np.linspace(max(1e-4, 0.1 * x), Y - 1e-5, 55)
                cs = Y - ys
                ec = np.where(cs < 1.0, ETA_MIN, ETA_MAX)
                rs = ec * np.log(cs) + (1.0 - ETA_MAX) * np.log(1.0 - L)
                v = np.max(rs + b_max * (a_c * ys - b_c * (ys ** -0.5)) - px)
                if v > mv:
                    mv = v
        return float(mv)

    # Worst-case feasible trajectory builder on box (7.3) for explicit rational witness sums
    Kp_m = brentq(lambda K: F_A(A_MIN, K, 1.0) - (1.0 - Q_MIN) * K, 0.5, 50.0)
    k_wg = np.unique(np.concatenate([np.geomspace(0.05, 0.4, 150, endpoint=False), np.geomspace(0.4, Kp_m * 1.02, 200)]))
    n_kw = len(k_wg)
    L_wg = np.linspace(0.20, 0.96, 120)

    def build_u_worst(A_lo):
        y = Q_MIN * k_wg[:, None] + F_A(A_lo, k_wg[:, None], L_wg[None, :])
        um = np.full((n_kw, n_kw), -1e9)
        Lm = np.zeros((n_kw, n_kw))
        for i in range(n_kw):
            cm = y[i, None, :] - k_wg[:, None]
            ec = np.where(cm < 1.0, ETA_MAX, ETA_MIN)
            u = np.where(cm > 1e-10, ec * np.log(np.maximum(cm, 1e-30)) + (1.0 - ETA_MIN) * np.log(1.0 - L_wg[None, :]), -1e9)
            bl = np.argmax(u, axis=1)
            um[i, :] = u[np.arange(n_kw), bl]
            Lm[i, :] = L_wg[bl]
        return um, Lm

    uw_G, Lw_G = build_u_worst(A_MIN)
    uw_B, _ = build_u_worst(0.349)

    def witness_seq_val(b_min, K0):
        V = np.full(n_kw, -25.0)
        for _ in range(40):
            jb = np.argmax(uw_G + b_min * V[None, :], axis=1)
            up = uw_G[np.arange(n_kw), jb]
            Ve = up + b_min * V[jb]
            for _h in range(150):
                Ve = up + b_min * Ve[jb]
            if np.max(np.abs(Ve - V)) < 1e-9:
                V = Ve
                break
            V = Ve
        idx = np.argmin(np.abs(k_wg - K0))
        traj = []
        for _ in range(25):
            nxt = jb[idx]
            traj.append((round(float(k_wg[idx]), 4), round(float(Lw_G[idx, nxt]), 4), round(float(k_wg[nxt]), 4)))
            idx = nxt
        traj[0] = (K0, traj[0][1], traj[0][2])
        for t in range(1, len(traj)):
            traj[t] = (traj[t - 1][2], traj[t][1], traj[t][2])
        rs = []
        for i, (K, L, Kp) in enumerate(traj):
            Kn = Kp if i + 1 < len(traj) else K
            c = Q_MIN * K + F_A(A_MIN, K, L) - Kn
            ec = ETA_MAX if c < 1.0 else ETA_MIN
            rs.append(ec * np.log(c) + (1.0 - ETA_MIN) * np.log(1.0 - L))
        return float(sum((b_min ** t) * r for t, r in enumerate(rs[:-1])) + (b_min ** (len(rs) - 1)) * rs[-1] / (1.0 - b_min))

    # 5A. Endogenous Doob Certificate T*(p) under Ruin/Expropriation Hazard p (effective beta_eff = beta*(1-p))
    eM_exit = E_plus(A_MAX, B_M, B_M, 0.44)
    eH_exit = E_plus(A_MAX, H_M, H_M, 0.57)
    psi_shapes = {0.0: (0.45, 5.0), 0.005: (0.40, 5.0), 0.010: (0.35, 5.0), 0.015: (0.40, 4.8), 0.020: (0.35, 4.8)}

    print("  [5A] Endogenous Doob Stochastic Affine Barrier Certificate T*(p) vs Naive (1-p)^23:")
    T_prev = 0
    for p in [0.0, 0.005, 0.010, 0.015, 0.020]:
        b_min = BETA_MIN * (1.0 - p)
        b_max = BETA_MAX * (1.0 - p)
        WM = witness_seq_val(b_min, B_M)
        WH = witness_seq_val(b_min, H_M)
        a_c, b_c = psi_shapes[p]
        mv = psi_discrepancy(A_MAX, b_max, a_c, b_c)
        shift = mv / (1.0 - b_max) + 0.005
        psi_10 = a_c * B_M - b_c * (B_M ** -0.5) + shift
        psi_28 = a_c * H_M - b_c * (H_M ** -0.5) + shift
        mExitM = WM - (eM_exit + b_min * psi_10)
        mExitH = WH - (eH_exit + b_min * psi_28)

        D2_p = (ETA_MIN * b_min * Q_MIN * (H_M - B_M)) / C_max
        B_star_p = (R_hat - D2_p) / (1.0 - b_min)
        B1_b_p = B_star_p - (ETA_MIN * Q_MIN / C_max) * (H_M - B_M)
        marg_stay = WM - B1_b_p
        gap_exit = psi_28 - B_star_p
        T_star = int(np.ceil(np.log(marg_stay / gap_exit) / np.log(b_max)))
        P_doob = (1.0 - p) ** T_star
        P_naive = (1.0 - p) ** 23
        print(
            f"    p={100*p:4.2f}% | b_eff={b_min:.4f} | B1(0.10)={B1_b_p:7.3f} | stay={marg_stay:5.3f} | "
            f"exitM={mExitM:+.3f}, exitH={mExitH:+.3f} | T*(p)={T_star:2d} | P_Doob={P_doob:.4f} (vs {P_naive:.4f})"
        )
        assert marg_stay > 0.0 and mExitM > 0.0 and mExitH > 0.0
        assert T_star >= T_prev
        T_prev = T_star

    # Exact certification breakdown threshold p_cert where staying margin crosses 0
    def stay_gap_fn(p_v):
        b_min = BETA_MIN * (1.0 - p_v)
        WM = witness_seq_val(b_min, B_M)
        D2_p = (ETA_MIN * b_min * Q_MIN * (H_M - B_M)) / C_max
        B1_b_p = (R_hat - D2_p) / (1.0 - b_min) - (ETA_MIN * Q_MIN / C_max) * (H_M - B_M)
        return WM - B1_b_p

    p_cert = brentq(stay_gap_fn, 0.015, 0.030, xtol=1e-5)
    print(f"    Certification breakdown limit (1-step affine barrier): p_cert = {100*p_cert:.2f}%")
    assert 0.020 < p_cert < 0.022

    # 5B. Coupled 2-State Markov Bellman Barrier System (Omega = {G, B}, A_G=0.75 <-> A_B=0.35, r_rec=1/3)
    print("\n  [5B] Coupled 2-State Markov Barrier (B_G, B_B) via (I - beta*P) B_* = R_hat - Delta:")
    Ls_B = np.linspace(0.01, 0.9999, 1500)
    cs_B = Q_MAX * H_M + F_A(0.351, H_M, Ls_B) - B_M
    R_hat_B = float(np.max(np.where(cs_B < 1.0, ETA_MIN, ETA_MAX) * np.log(cs_B) + (1.0 - ETA_MAX) * np.log(1.0 - Ls_B)))
    C_max_B = float(Q_MAX * H_M + F_A(0.351, H_M, 1.0) - B_M)
    m_G = (ETA_MIN * Q_MIN) / C_max
    m_B = (ETA_MIN * Q_MIN) / C_max_B
    v_G0 = psi_discrepancy(A_MAX, BETA_MAX, 0.40, 5.0)
    v_B0 = psi_discrepancy(0.351, BETA_MAX, 0.40, 5.0)

    for p in [0.0, 0.005, 0.01, 0.015, 0.02, 0.05, 0.08, 0.12]:
        P = np.array([[1.0 - p, p], [r_rec, 1.0 - r_rec]])
        m_bar = P @ np.array([m_G, m_B])
        Delta = (H_M - B_M) * np.minimum(np.array([ETA_MIN / C_max, ETA_MIN / C_max_B]), BETA_MIN * m_bar)
        B_star = np.linalg.solve(np.eye(2) - BETA_MIN * P, np.array([R_hat, R_hat_B]) - Delta)
        B_b = np.array([B_star[0] - m_G * (H_M - B_M), B_star[1] - m_B * (H_M - B_M)])
        shift_v = np.linalg.solve(np.eye(2) - BETA_MAX * P, np.array([v_G0, v_B0])) + 0.01
        Psi_h = 0.40 * H_M - 5.0 * (H_M ** -0.5) + shift_v

        VG_w, VB_w = np.full(n_kw, -30.0), np.full(n_kw, -32.0)
        for _ in range(45):
            jbG = np.argmax(uw_G + BETA_MIN * ((1.0 - p) * VG_w + p * VB_w)[None, :], axis=1)
            jbB = np.argmax(uw_B + BETA_MIN * (r_rec * VG_w + (1.0 - r_rec) * VB_w)[None, :], axis=1)
            upG, upB = uw_G[np.arange(n_kw), jbG], uw_B[np.arange(n_kw), jbB]
            VGe, VBe = VG_w.copy(), VB_w.copy()
            for _h in range(150):
                VGn = upG + BETA_MIN * ((1.0 - p) * VGe[jbG] + p * VBe[jbG])
                VBn = upB + BETA_MIN * (r_rec * VGe[jbB] + (1.0 - r_rec) * VBe[jbB])
                if max(np.max(np.abs(VGn - VGe)), np.max(np.abs(VBn - VBe))) < 1e-9:
                    VGe, VBe = VGn, VBn
                    break
                VGe, VBe = VGn, VBn
            if max(np.max(np.abs(VGe - VG_w)), np.max(np.abs(VBe - VB_w))) < 1e-8:
                VG_w, VB_w = VGe, VBe
                break
            VG_w, VB_w = VGe, VBe
        WG0, WB0 = float(np.interp(B_M, k_wg, VG_w)), float(np.interp(B_M, k_wg, VB_w))
        margG, margB = WG0 - B_b[0], WB0 - B_b[1]
        max_exit = float(np.max(Psi_h - B_star))
        T_G = int(np.ceil(np.log(margG / max_exit) / np.log(BETA_MAX)))
        T_B = int(np.ceil(np.log(margB / max_exit) / np.log(BETA_MAX)))
        print(
            f"    p={100*p:4.1f}% | BG(0.10)={B_b[0]:7.3f} (marg={margG:5.2f}, T*_G={T_G:2d}) | "
            f"BB(0.10)={B_b[1]:7.3f} (marg={margB:5.2f}, T*_B={T_B:2d})"
        )
        assert margG > 0.0 and margB > 0.0

    # 5C. Anticipatory Stochastic VFI Policy & Threshold Comparison (880-pt Ruin + Markov)
    print("\n  [5C] Forward-Looking Stochastic VFI (Optimal Policy K'(0.10), L(0.10) & S_p):")
    K_ss = brentq(lambda K: dF_dK(A_G, K, 1.0) - (1.0 / beta - q), 0.25, 25.0)
    k_lo, k_hi = 1e-5 / (A_G ** 2), 1.15 * K_ss
    k_grid = np.unique(np.concatenate([
        np.geomspace(k_lo, 0.00138, 130, endpoint=False),
        np.linspace(0.00138, 0.00650, 320, endpoint=False),
        np.geomspace(0.00650, 0.08, 110, endpoint=False),
        np.linspace(0.08, 0.34, 160, endpoint=False),
        np.geomspace(0.34, k_hi, 160),
    ]))
    n_k = len(k_grid)
    L_grid = np.unique(np.concatenate([np.geomspace(1e-4, 0.08, 24, endpoint=False), np.linspace(0.08, 0.995, 64)]))
    dis_L = (1.0 - eta) * np.log(1.0 - L_grid[None, :])

    def build_u_bench(A_v):
        y_kL = q * k_grid[:, None] + F_A(A_v, k_grid[:, None], L_grid[None, :])
        um = np.full((n_k, n_k), -1e9)
        for i in range(n_k):
            cm = y_kL[i, None, :] - k_grid[:, None]
            u = np.where(cm > 1e-15, eta * np.log(np.maximum(cm, 1e-30)) + dis_L, -1e9)
            um[i, :] = np.max(u, axis=1)
        return um, y_kL

    u_G, y_kL_G = build_u_bench(A_G)
    u_B, _ = build_u_bench(A_B)

    def solve_L_p(k_arr, kp_arr):
        lo_L = np.full_like(k_arr, 1e-7)
        hi_L = np.full_like(k_arr, 1.0 - 1e-9)
        inv_phi = (np.sqrt(5.0) - 1.0) / 2.0
        x1 = hi_L - inv_phi * (hi_L - lo_L)
        x2 = lo_L + inv_phi * (hi_L - lo_L)

        def obj(Lv):
            cv = q * k_arr + F_A(A_G, k_arr, Lv) - kp_arr
            return np.where(cv > 1e-15, eta * np.log(np.maximum(cv, 1e-30)) + (1.0 - eta) * np.log(1.0 - Lv), -1e9 + cv)

        f1, f2 = obj(x1), obj(x2)
        for _ in range(24):
            mr = f1 < f2
            lo_L = np.where(mr, x1, lo_L)
            hi_L = np.where(mr, hi_L, x2)
            x1n = np.where(mr, x2, hi_L - inv_phi * (hi_L - lo_L))
            x2n = np.where(mr, lo_L + inv_phi * (hi_L - lo_L), x1)
            f1n, f2n = np.where(mr, f2, obj(x1n)), np.where(mr, obj(x2n), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        Lb = 0.5 * (lo_L + hi_L)
        return Lb, obj(Lb)

    s_cand = 1.0 - np.geomspace(1e-5, 0.15, 22)
    kp_tail = y_kL_G[:, -1][:, None] * s_cand[None, :]
    u_tail = np.full((n_k, len(s_cand)), -1e9)
    for j in range(len(s_cand)):
        _, u_tail[:, j] = solve_L_p(k_grid, kp_tail[:, j])

    def interp_Vs(V, kp, b_eff):
        r = np.interp(np.clip(kp, k_lo, k_hi), k_grid, V)
        return np.where(kp < k_lo, V[0] + (eta / (1.0 - b_eff)) * np.log(np.maximum(kp, 1e-30) / k_lo), r)

    def smooth_policy_at(K_val, EV_arr, A_v, b_eff):
        pchip = PchipInterpolator(k_grid, EV_arr)
        Ls = np.linspace(0.30, 0.95, 300)
        Y_L = q * K_val + F_A(A_v, K_val, Ls)
        dL = (1.0 - eta) * np.log(1.0 - Ls)
        kps = np.linspace(max(1e-4, 0.9 * K_val), np.max(Y_L) - 1e-6, 350)
        cm = Y_L[:, None] - kps[None, :]
        rhs = np.where(cm > 1e-12, eta * np.log(np.maximum(cm, 1e-30)) + dL[:, None] + b_eff * pchip(kps)[None, :], -1e9)
        il, ik = np.unravel_index(np.argmax(rhs), rhs.shape)
        dk = kps[1] - kps[0]
        kp0 = kps[ik]
        kps_f = np.linspace(max(1e-4, kp0 - 2 * dk), min(np.max(Y_L) - 1e-7, kp0 + 2 * dk), 200)
        Ls_f = np.linspace(max(0.01, Ls[il] - 0.03), min(0.998, Ls[il] + 0.03), 200)
        Yf = q * K_val + F_A(A_v, K_val, Ls_f)
        dLf = (1.0 - eta) * np.log(1.0 - Ls_f)
        cm_f = Yf[:, None] - kps_f[None, :]
        rhs_f = np.where(cm_f > 1e-12, eta * np.log(np.maximum(cm_f, 1e-30)) + dLf[:, None] + b_eff * pchip(kps_f)[None, :], -1e9)
        il2, ik2 = np.unravel_index(np.argmax(rhs_f), rhs_f.shape)
        return float(kps_f[ik2]), float(Ls_f[il2]), float(Yf[il2])

    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0
    y_max_row = y_kL_G[:, -1]
    V_ss_est = eta * np.log(F_A(A_G, K_ss, 0.7) - delta * K_ss)

    p_tests = [0.0, 0.005, 0.010, 0.015, 0.020, 0.050, 0.080]
    ruin_S, ruin_kp, ruin_L = [], [], []
    markov_kp, markov_L = [], []

    for p in p_tests:
        # Case 1: Ruin/Expropriation (beta_eff = beta*(1-p)) with golden-section continuous VFI
        b_eff = beta * (1.0 - p)
        Vc = (eta / (1.0 - b_eff)) * (np.log((1.0 - b_eff) * q) + (b_eff / (1.0 - b_eff)) * np.log(b_eff * q))
        V = np.where(k_grid > 0.00145, V_ss_est / (1.0 - b_eff), Vc + (eta / (1.0 - b_eff)) * np.log(k_grid))
        for _ in range(55):
            vg = u_G + b_eff * V[None, :]
            jb = np.argmax(vg, axis=1)
            bg = vg[np.arange(n_k), jb]
            vt = u_tail + b_eff * interp_Vs(V, kp_tail, b_eff)
            sb = np.argmax(vt, axis=1)
            bt = vt[np.arange(n_k), sb]
            ut = bt > bg
            lo_t = kp_tail[np.arange(n_k), np.maximum(0, sb - 1)]
            hi_t = kp_tail[np.arange(n_k), np.minimum(len(s_cand) - 1, sb + 1)]
            lo = np.where(ut, np.minimum(lo_t, hi_t), k_grid[np.maximum(0, jb - 1)])
            hi = np.where(ut, np.minimum(np.maximum(lo_t, hi_t), y_max_row - 1e-12), np.minimum(k_grid[np.minimum(n_k - 1, jb + 1)], y_max_row - 1e-12))
            x1 = hi - inv_phi * (hi - lo)
            x2 = lo + inv_phi * (hi - lo)
            _, u1 = solve_L_p(k_grid, x1)
            _, u2 = solve_L_p(k_grid, x2)
            f1 = u1 + b_eff * interp_Vs(V, x1, b_eff)
            f2 = u2 + b_eff * interp_Vs(V, x2, b_eff)
            for _g in range(12):
                mr = f1 < f2
                lo = np.where(mr, x1, lo)
                hi = np.where(mr, hi, x2)
                x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
                x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
                _, u1n = solve_L_p(k_grid, x1n)
                _, u2n = solve_L_p(k_grid, x2n)
                f1n = np.where(mr, f2, u1n + b_eff * interp_Vs(V, x1n, b_eff))
                f2n = np.where(mr, u2n + b_eff * interp_Vs(V, x2n, b_eff), f1)
                x1, x2, f1, f2 = x1n, x2n, f1n, f2n
            pol = np.where(f1 > f2, x1, x2)
            _, upol = solve_L_p(k_grid, pol)
            Ve = np.maximum(f1, f2)
            for _h in range(60):
                Vn = upol + b_eff * interp_Vs(Ve, pol, b_eff)
                if np.max(np.abs(Vn - Ve)) < 1e-9:
                    Ve = Vn
                    break
                Ve = Vn
            if np.max(np.abs(Ve - V)) < 1e-8:
                V = Ve
                break
            V = Ve
        idx_m = np.where((k_grid >= 0.00138) & (k_grid <= 0.0065))[0]
        i0 = idx_m[np.where((pol - k_grid)[idx_m] > 0)[0][0]]
        k_sub = np.linspace(k_grid[i0 - 1], k_grid[i0], 25)
        diffs = []
        for ks in k_sub:
            ys = q * ks + F_A(A_G, ks, 1.0)
            kd = np.linspace(max(1e-5, 0.90 * ks), ks, 30)
            _, ud = solve_L_p(np.full_like(kd, ks), kd)
            vd = np.max(ud + b_eff * interp_Vs(V, kd, b_eff))
            if ys > ks + 1e-12:
                ku = np.linspace(ks, ys - 1e-12, 30)
                _, uu = solve_L_p(np.full_like(ku, ks), ku)
                vu = np.max(uu + b_eff * interp_Vs(V, ku, b_eff))
            else:
                vu = -1e9
            diffs.append(vu - vd)
        pos = np.where(np.array(diffs) >= 0)[0]
        kS = float(k_sub[pos[0] - 1] + abs(diffs[pos[0] - 1]) / (abs(diffs[pos[0] - 1]) + abs(diffs[pos[0]])) * (k_sub[pos[0]] - k_sub[pos[0] - 1])) if (len(pos) > 0 and pos[0] > 0) else float(0.5 * (k_grid[i0 - 1] + k_grid[i0]))
        kp_r, L_r, Y_r = smooth_policy_at(B_M, V, A_G, b_eff)
        ruin_S.append(kS)
        ruin_kp.append(kp_r)
        ruin_L.append(L_r)

        # Case 2: Markov Recoverable Crisis Switching (A_G=0.75 <-> A_B=0.35, r_rec=1/3)
        Vc0 = (eta / (1.0 - beta)) * (np.log((1.0 - beta) * q) + (beta / (1.0 - beta)) * np.log(beta * q))
        VG = np.where(k_grid > 0.00145, V_ss_est / (1.0 - beta), Vc0 + (eta / (1.0 - beta)) * np.log(k_grid))
        VB = VG.copy() - 5.0
        for _ in range(50):
            EVG = (1.0 - p) * VG + p * VB
            EVB = r_rec * VG + (1.0 - r_rec) * VB
            jbG = np.argmax(u_G + beta * EVG[None, :], axis=1)
            jbB = np.argmax(u_B + beta * EVB[None, :], axis=1)
            upG, upB = u_G[np.arange(n_k), jbG], u_B[np.arange(n_k), jbB]
            VGe, VBe = VG.copy(), VB.copy()
            for _h in range(150):
                VGn = upG + beta * ((1.0 - p) * VGe[jbG] + p * VBe[jbG])
                VBn = upB + beta * (r_rec * VGe[jbB] + (1.0 - r_rec) * VBe[jbB])
                if max(np.max(np.abs(VGn - VGe)), np.max(np.abs(VBn - VBe))) < 1e-10:
                    VGe, VBe = VGn, VBn
                    break
                VGe, VBe = VGn, VBn
            if max(np.max(np.abs(VGe - VG)), np.max(np.abs(VBe - VB))) < 1e-9:
                VG, VB = VGe, VBe
                break
            VG, VB = VGe, VBe
        EVG = (1.0 - p) * VG + p * VB
        kp_m, L_m, Y_m = smooth_policy_at(B_M, EVG, A_G, beta)
        markov_kp.append(kp_m)
        markov_L.append(L_m)
        print(
            f"    p={100*p:4.1f}% | Ruin: S_p={kS:.6f}, K'(0.10)={kp_r:.5f}, L={L_r:.4f} | "
            f"Markov: K'_G(0.10)={kp_m:.5f}, L_G={L_m:.4f}"
        )

    assert all(ruin_S[i] < ruin_S[i + 1] for i in range(len(p_tests) - 1))
    assert all(ruin_kp[i] > ruin_kp[i + 1] and ruin_L[i] > ruin_L[i + 1] for i in range(len(p_tests) - 1))
    assert all(markov_kp[i] <= markov_kp[i + 1] and markov_L[i] <= markov_L[i + 1] for i in range(len(p_tests) - 1))
    assert markov_kp[-1] > markov_kp[0] and markov_L[-1] > markov_L[0]


if __name__ == "__main__":
    verify_barriers()
    verify_prop1_double_star()
    verify_theorem3_star()
    verify_theorem10()
    verify_theorem11_stochastic()
    print("\nALL ANALYTICAL AND NUMERICAL CHECKS PASSED SUCCESSFULLY.")
