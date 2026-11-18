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
from scipy.optimize import brentq, minimize


# ---------------------------------------------------------------------------
# Box (7.3) primitives, production technology, and shared barrier helpers
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


def exact_kappa(A_val, delta_val=0.08):
    coeffs = [-delta_val**2, -3 * delta_val**2, 8 * (A_val**2) - 3 * delta_val**2, -delta_val**2]
    roots = np.roots(coeffs)
    real_pos = sorted([float(np.real(rt)) for rt in roots if abs(np.imag(rt)) < 1e-12 and np.real(rt) > 0])
    return real_pos[0]


def box_worst_u(c, L):
    """Minimum period utility over eta in [ETA_MIN, ETA_MAX] at fixed (c, L)."""
    u1 = ETA_MIN * np.log(c) + (1.0 - ETA_MIN) * np.log(1.0 - L)
    u2 = ETA_MAX * np.log(c) + (1.0 - ETA_MAX) * np.log(1.0 - L)
    return np.minimum(u1, u2)


def E_plus_exact(A_hi, q_hi, K, a, l0):
    """Exact tangent adverse-exit envelope max_{eta in box} E^+(K, a; l0)."""
    t = dF_dL(A_hi, K, l0)
    S = q_hi * K + F_A(A_hi, K, l0) + (1.0 - l0) * t
    c_sup = S - a
    vals = []
    for eta in (ETA_MIN, ETA_MAX):
        om_L = min(1.0, (1.0 - eta) * c_sup / t)
        c_opt = c_sup - t * om_L
        vals.append(eta * np.log(c_opt) + (1.0 - eta) * np.log(om_L))
    return max(vals)


def certify_psi_centered(A_hi, b_max, a_c, b_c, x_lo=8e-5, x_hi=45.0, tol=2e-4, buffer=0.0005):
    """Continuously certify Psi(x) = a_c*x - b_c*x^(-1/2) + c_shift on all (0, infinity).

    Combines:
      1) Analytical contraction tail on (0, x_lo]: Y(x_lo, 1)/x_lo < b_max^2 ensures
         1 - b_max*(y/x)^(-1/2) < 0 so discrepancy -> -inf as x -> 0.
      2) Exact 3D centered-form + monotone interval B&B over [x_lo, x_hi] x [0, 1) x (0, Y).
      3) Analytical upper tail on [x_hi, inf): verifies strict negativity of d/dx
         of the upper-bound majorant on [x_hi, inf) and checks value at x_hi.
    Returns (c_shift, d_ub, d_lb, tail_margin).
    """
    def f(k):
        return a_c * k - b_c * (k ** -0.5)

    def fp(k):
        return a_c + 0.5 * b_c * (k ** -1.5)

    # 1. Tight continuous lower bound via grid + Nelder-Mead
    xg = np.geomspace(x_lo, x_hi, 120)
    Lg = np.linspace(0.05, 0.995, 50)
    sg = np.linspace(0.10, 0.995, 50)
    Yg = Q_MAX * xg[:, None] + F_A(A_hi, xg[:, None], Lg[None, :])
    cg = Yg[:, :, None] * (1.0 - sg[None, None, :])
    yg = Yg[:, :, None] * sg[None, None, :]
    ecg = np.where(cg < 1.0, ETA_MIN, ETA_MAX)
    val = ecg * np.log(cg) + (1.0 - ETA_MAX) * np.log(1.0 - Lg[None, :, None]) + b_max * f(yg) - f(xg[:, None, None])
    i0, j0, k0 = np.unravel_index(np.argmax(val), val.shape)

    def neg_pt(z):
        x, L, s = z
        if not (x_lo <= x <= x_hi and 1e-6 <= L <= 1.0 - 1e-9 and 1e-6 <= s <= 1.0 - 1e-9):
            return 1e9
        Y = Q_MAX * x + F_A(A_hi, x, L)
        c, y = (1.0 - s) * Y, s * Y
        ec = ETA_MIN if c < 1.0 else ETA_MAX
        return -(ec * np.log(c) + (1.0 - ETA_MAX) * np.log(1.0 - L) + b_max * f(y) - f(x))

    res = minimize(neg_pt, [xg[i0], Lg[j0], sg[k0]], method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-10})
    best_lb = max(float(np.max(val)), -float(res.fun))
    target = best_lb + tol

    # 2. Exact 3D centered-form + monotone interval B&B on [x_lo, x_hi]
    xs = np.geomspace(x_lo, x_hi, 60)
    Ls = np.concatenate([[0.0, 0.05, 0.2, 0.4, 0.6], np.linspace(0.7, 0.99, 15, endpoint=False), [0.99, 0.998, 1.0]])
    ss = np.concatenate([[0.0, 0.2, 0.4, 0.6], np.linspace(0.7, 0.99, 15, endpoint=False), [0.99, 0.998, 1.0]])
    gxL, gLL, gsL = np.meshgrid(xs[:-1], Ls[:-1], ss[:-1], indexing="ij")
    gxR, gLR, gsR = np.meshgrid(xs[1:], Ls[1:], ss[1:], indexing="ij")
    bxL, bxR, bLL, bLR, bsL, bsR = gxL.ravel(), gxR.ravel(), gLL.ravel(), gLR.ravel(), gsL.ravel(), gsR.ravel()

    d_ub = None
    for _ in range(60):
        Y_min = Q_MAX * bxL + F_A(A_hi, bxL, bLL)
        Y_max = Q_MAX * bxR + F_A(A_hi, bxR, bLR)
        c_max = np.maximum((1.0 - bsL) * Y_max, 1e-300)
        ec_max = np.where(c_max < 1.0, ETA_MIN, ETA_MAX)
        ub_mono = (
            np.where(bsL >= 1.0, -1e9, ec_max * np.log(c_max))
            + (1.0 - ETA_MAX) * np.log(np.maximum(1.0 - bLL, 1e-300))
            + np.where(bsR <= 0.0, -1e9, b_max * f(np.maximum(bsR * Y_max, 1e-300)))
            - f(bxL)
        )
        xm = 0.5 * (bxL + bxR)
        Lm = 0.5 * (bLL + bLR)
        sm = 0.5 * (bsL + bsR)
        hx = 0.5 * (bxR - bxL)
        hL = 0.5 * (bLR - bLL)
        hs = 0.5 * (bsR - bsL)
        Ym = Q_MAX * xm + F_A(A_hi, xm, Lm)
        cm = (1.0 - sm) * Ym
        c_min = np.maximum((1.0 - bsR) * Y_min, 1e-300)
        valid_c = (bLR < 1.0) & (bsL > 0.0) & (bsR < 1.0) & (c_min > 1e-12)
        ub_cent = np.full_like(ub_mono, 1e9)
        if np.any(valid_c):
            xLv, xRv, LLv, LRv, sLv, sRv = (
                bxL[valid_c], bxR[valid_c], bLL[valid_c], bLR[valid_c], bsL[valid_c], bsR[valid_c]
            )
            xmv, Lmv, smv = xm[valid_c], Lm[valid_c], sm[valid_c]
            hxv, hLv, hsv = hx[valid_c], hL[valid_c], hs[valid_c]
            Y_min_v, Y_max_v, Ymv = Y_min[valid_c], Y_max[valid_c], Ym[valid_c]
            y_min_v, y_max_v = sLv * Y_min_v, sRv * Y_max_v
            px_hi = np.clip(LRv / 4.0, xLv, xRv)
            Yx_lo = Q_MAX + np.minimum(dF_dK(A_hi, xLv, LLv), dF_dK(A_hi, xRv, LLv))
            Yx_hi = Q_MAX + np.maximum(
                np.maximum(dF_dK(A_hi, xLv, LRv), dF_dK(A_hi, xRv, LRv)), dF_dK(A_hi, px_hi, LRv)
            )
            pL_hi = np.clip(xRv / 4.0, LLv, LRv)
            YL_lo = np.minimum(dF_dL(A_hi, xLv, LLv), dF_dL(A_hi, xLv, LRv))
            YL_hi = np.maximum(
                np.maximum(dF_dL(A_hi, xRv, LLv), dF_dL(A_hi, xRv, LRv)), dF_dL(A_hi, xRv, pL_hi)
            )
            fp_y_lo, fp_y_hi = fp(y_max_v), fp(y_min_v)
            fp_x_lo, fp_x_hi = fp(xRv), fp(xLv)
            cross_c1 = (c_min[valid_c] < 1.0) & (c_max[valid_c] >= 1.0)
            best_eta_ub = np.full(np.sum(valid_c), -1e9)
            for ec in (ETA_MIN, ETA_MAX):
                mask_ec = (c_min[valid_c] < 1.0) if ec == ETA_MIN else (c_max[valid_c] >= 1.0)
                ec_lo = np.where(cross_c1, ETA_MIN, ec)
                ec_hi = np.where(cross_c1, ETA_MAX, ec)
                hm = ec * np.log(cm[valid_c]) + (1.0 - ETA_MAX) * np.log(1.0 - Lmv) + b_max * f(smv * Ymv) - f(xmv)
                A_lo = ec_lo / Y_max_v + b_max * sLv * fp_y_lo
                A_hi_b = ec_hi / Y_min_v + b_max * sRv * fp_y_hi
                hx_lo = A_lo * Yx_lo - fp_x_hi
                hx_hi = A_hi_b * Yx_hi - fp_x_lo
                hL_lo = A_lo * YL_lo - (1.0 - ETA_MAX) / (1.0 - LRv)
                hL_hi = A_hi_b * YL_hi - (1.0 - ETA_MAX) / (1.0 - LLv)
                hs_lo = -ec_hi / (1.0 - sRv) + b_max * Y_min_v * fp_y_lo
                hs_hi = -ec_lo / (1.0 - sLv) + b_max * Y_max_v * fp_y_hi
                ub_ec = (
                    hm
                    + np.maximum(np.abs(hx_lo), np.abs(hx_hi)) * hxv
                    + np.maximum(np.abs(hL_lo), np.abs(hL_hi)) * hLv
                    + np.maximum(np.abs(hs_lo), np.abs(hs_hi)) * hsv
                )
                best_eta_ub = np.where(mask_ec, np.maximum(best_eta_ub, ub_ec), best_eta_ub)
            ub_cent[valid_c] = best_eta_ub
        ub = np.minimum(ub_mono, ub_cent)
        keep = ub > target
        n_keep = int(np.sum(keep))
        if n_keep == 0:
            d_ub = target
            break
        bxL, bxR, bLL, bLR, bsL, bsR = bxL[keep], bxR[keep], bLL[keep], bLR[keep], bsL[keep], bsR[keep]
        xm, Lm, sm = xm[keep], Lm[keep], sm[keep]
        Ym_k = Q_MAX * xm + F_A(A_hi, xm, Lm)
        cm_k = (1.0 - sm) * Ym_k
        ecm_k = np.where(cm_k < 1.0, ETA_MIN, ETA_MAX)
        lb_k = np.where(
            (Lm < 1.0) & (sm > 0.0) & (sm < 1.0),
            ecm_k * np.log(np.maximum(cm_k, 1e-300))
            + (1.0 - ETA_MAX) * np.log(np.maximum(1.0 - Lm, 1e-300))
            + b_max * f(np.maximum(sm * Ym_k, 1e-300))
            - f(xm),
            -1e9,
        )
        if np.max(lb_k) > best_lb:
            best_lb = float(np.max(lb_k))
            target = best_lb + tol
        if n_keep <= 1500:
            nxL = np.concatenate([bxL, xm, bxL, xm, bxL, xm, bxL, xm])
            nxR = np.concatenate([xm, bxR, xm, bxR, xm, bxR, xm, bxR])
            nLL = np.concatenate([bLL, bLL, Lm, Lm, bLL, bLL, Lm, Lm])
            nLR = np.concatenate([Lm, Lm, bLR, bLR, Lm, Lm, bLR, bLR])
            nsL = np.concatenate([bsL, bsL, bsL, bsL, sm, sm, sm, sm])
            nsR = np.concatenate([sm, sm, sm, sm, bsR, bsR, bsR, bsR])
            bxL, bxR, bLL, bLR, bsL, bsR = nxL, nxR, nLL, nLR, nsL, nsR
        else:
            dx = (bxR - bxL) / np.maximum(bxL, 1e-4)
            dL = (bLR - bLL) / np.maximum(1.0 - bLR, 1e-4)
            ds = (bsR - bsL) / np.maximum(1.0 - bsR, 1e-4)
            m1 = (dx >= dL) & (dx >= ds)
            m2 = (~m1) & (dL >= ds)
            m3 = (~m1) & (~m2)
            axL, axR, aLL, aLR, asL, asR = bxL.copy(), bxR.copy(), bLL.copy(), bLR.copy(), bsL.copy(), bsR.copy()
            bxLc, bxRc, bLLc, bLRc, bsLc, bsRc = bxL.copy(), bxR.copy(), bLL.copy(), bLR.copy(), bsL.copy(), bsR.copy()
            axR[m1] = xm[m1]; bxLc[m1] = xm[m1]
            aLR[m2] = Lm[m2]; bLLc[m2] = Lm[m2]
            asR[m3] = sm[m3]; bsLc[m3] = sm[m3]
            bxL = np.concatenate([axL, bxLc]); bxR = np.concatenate([axR, bxRc])
            bLL = np.concatenate([aLL, bLLc]); bLR = np.concatenate([aLR, bLRc])
            bsL = np.concatenate([asL, bsLc]); bsR = np.concatenate([asR, bsRc])
    assert d_ub is not None, "certify_psi_centered B&B did not converge within 60 iterations"
    c_shift = (d_ub + buffer) / (1.0 - b_max)

    # 3. Analytical lower tail (0, x_lo] and upper tail [x_hi, inf) checks
    Y_lo_ratio = (Q_MAX * x_lo + F_A(A_hi, x_lo, 1.0)) / x_lo
    assert Y_lo_ratio < b_max ** 2, f"Lower tail ratio {Y_lo_ratio:.6f} >= b_max^2 {b_max**2:.6f}"
    # On [x_hi, inf), Y(x,L) <= Y_top(x) := Q_MAX*x + F_inf where F_inf = A_hi * 2^1.5.
    # For fixed Y >= Y_top(x_hi), ec*log(c) + b_max*a_c*(Y - c) is maximized over c in (0, Y) at a constant c*:
    #   on c in [1, Y): c_1 = max(ETA_MAX/(b_max*a_c), 1.0); on c in (0, 1]: c_2 = min(ETA_MIN/(b_max*a_c), 1.0).
    F_inf = A_hi * (2.0 ** 1.5)
    Y_top = Q_MAX * x_hi + F_inf
    u_max = ETA_MAX / (b_max * a_c)
    u_min = ETA_MIN / (b_max * a_c)
    assert Y_top > max(u_max, 1.0), f"Upper tail Y_top={Y_top:.4f} <= u_max={u_max:.4f}"
    c_hi = max(u_max, 1.0)
    c_lo = min(u_min, 1.0)
    phi_c_hi = max(
        ETA_MAX * np.log(c_hi) - b_max * a_c * c_hi,
        ETA_MIN * np.log(c_lo) - b_max * a_c * c_lo,
    )
    # Using s*Y_top <= Y_top => -b_c*(s*Y_top)^(-0.5) <= -b_c*Y_top^(-0.5), global upper-tail derivative wrt x satisfies:
    d_tail_dx_ub = (
        -a_c * (1.0 - b_max * Q_MAX)
        + 0.5 * b_c * max(0.0, b_max / (Q_MAX ** 0.5) - 1.0) * (x_hi ** -1.5)
    )
    assert d_tail_dx_ub < 0.0, f"Upper tail derivative bound not negative on [x_hi, inf): {d_tail_dx_ub}"
    top_val = (
        phi_c_hi
        + b_max * (a_c * Y_top - b_c * (Y_top ** -0.5))
        - (a_c * x_hi - b_c * (x_hi ** -0.5))
        - (1.0 - b_max) * c_shift
    )
    assert top_val < 0.0, f"Upper tail value at x_hi positive: {top_val}"
    return float(c_shift), float(d_ub), float(best_lb), float(-top_val)


def build_25step_witness_builder():
    """Precompute worst-case box transition tables for explicit 25-step witnesses."""
    Kp_m = brentq(lambda K: F_A(A_MIN, K, 1.0) - (1.0 - Q_MIN) * K, 0.5, 50.0)
    k_wg = np.unique(np.concatenate([np.geomspace(0.05, 0.4, 150, endpoint=False), np.geomspace(0.4, Kp_m * 1.02, 200)]))
    n_kw = len(k_wg)
    L_wg = np.linspace(0.20, 0.96, 120)

    def build_u_worst(A_lo, eta_mode="outer"):
        y = Q_MIN * k_wg[:, None] + F_A(A_lo, k_wg[:, None], L_wg[None, :])
        um = np.full((n_kw, n_kw), -1e9)
        Lm = np.zeros((n_kw, n_kw))
        for i in range(n_kw):
            cm = y[i, None, :] - k_wg[:, None]
            if eta_mode == "outer":
                ec = np.where(cm < 1.0, ETA_MAX, ETA_MIN)
                u = np.where(cm > 1e-10, ec * np.log(np.maximum(cm, 1e-30)) + (1.0 - ETA_MIN) * np.log(1.0 - L_wg[None, :]), -1e9)
            else:
                u = np.where(cm > 1e-10, box_worst_u(np.maximum(cm, 1e-30), L_wg[None, :]), -1e9)
            bl = np.argmax(u, axis=1)
            um[i, :] = u[np.arange(n_kw), bl]
            Lm[i, :] = L_wg[bl]
        return um, Lm

    uw_G, Lw_G = build_u_worst(A_MIN, "outer")

    def eval_witness(b_eval, K0, b_solve=None, eta_mode="outer"):
        """Find 25-step trajectory using b_solve (default b_eval) and evaluate at b_eval."""
        if b_solve is None:
            b_solve = b_eval
        V = np.full(n_kw, -25.0)
        for _ in range(40):
            jb = np.argmax(uw_G + b_solve * V[None, :], axis=1)
            up = uw_G[np.arange(n_kw), jb]
            Ve = up + b_solve * V[jb]
            for _h in range(150):
                Ve = up + b_solve * Ve[jb]
            if np.max(np.abs(Ve - V)) < 1e-9:
                V = Ve
                break
            V = Ve
        idx = int(np.argmin(np.abs(k_wg - K0)))
        traj = []
        for _ in range(25):
            nxt = int(jb[idx])
            traj.append((round(float(k_wg[idx]), 4), round(float(Lw_G[idx, nxt]), 4), round(float(k_wg[nxt]), 4)))
            idx = nxt
        traj[0] = (K0, traj[0][1], traj[0][2])
        for t in range(1, len(traj)):
            traj[t] = (traj[t - 1][2], traj[t][1], traj[t][2])
        rs = []
        for i, (K, L, Kp) in enumerate(traj):
            Kn = Kp if i + 1 < len(traj) else K
            c = Q_MIN * K + F_A(A_MIN, K, L) - Kn
            if eta_mode == "outer":
                ec = ETA_MAX if c < 1.0 else ETA_MIN
                rs.append(float(ec * np.log(c) + (1.0 - ETA_MIN) * np.log(1.0 - L)))
            else:
                rs.append(float(box_worst_u(c, L)))
        val = float(sum((b_eval ** t) * r for t, r in enumerate(rs[:-1])) + (b_eval ** (len(rs) - 1)) * rs[-1] / (1.0 - b_eval))
        assert all(r < 0.0 for r in rs), "Expected all stage payoffs negative for b_max worst-case monotonicity"
        return val, traj, rs

    return k_wg, n_kw, build_u_worst, eval_witness


# ---------------------------------------------------------------------------
# 1. Lemma 1, Theorem 9*, Proposition 1* & Upgrade U1
# ---------------------------------------------------------------------------
def verify_barriers():
    print("=" * 72)
    print("1. LEMMA 1, THEOREM 9*, PROPOSITION 1* & U1 (ONE-STEP AFFINE BARRIERS)")
    print("=" * 72)

    C_max_plus = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
    R_hat = -0.996
    Delta_2 = 0.2997
    Delta_2_exact = (ETA_MIN * BETA_MIN * Q_MIN * (H_M - B_M)) / C_max_plus

    B_star = (R_hat - Delta_2) / (1.0 - BETA_MIN)
    slope = (ETA_MIN * Q_MIN) / C_max_plus
    B1_b = B_star - slope * (H_M - B_M)

    # Exact Table 4 witness floor W_M(0.10) from (l_M, s_M, T_M) = (0.68, 0.135, -33.103)
    c_M_10 = Q_MIN * B_M + F_A(A_MIN, B_M, 0.68) - 0.135
    W_M_10_exact = float(box_worst_u(c_M_10, 0.68) + BETA_MAX * (-33.103))
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
    # Exact r(0.10, 0.05) max over L
    Ls_chk = np.linspace(0.01, 0.999, 5000)
    cs_chk = Q_MAX * h0 + F_A(A_MAX, h0, Ls_chk) - b0
    R_hat0_exact = float(np.max(np.maximum(
        ETA_MIN * np.log(cs_chk) + (1.0 - ETA_MIN) * np.log(1.0 - Ls_chk),
        ETA_MAX * np.log(cs_chk) + (1.0 - ETA_MAX) * np.log(1.0 - Ls_chk),
    )))
    B0_star = (R_hat0 - Delta_0) / (1.0 - BETA_MIN)
    B0_star_exact = (R_hat0_exact - Delta_0_exact) / (1.0 - BETA_MIN)

    # Corrected original 3-step witness (0.05 -> 0.065 -> 0.0845 -> 0.100, L=0.75) at (A_-, q_-, eta_pm)
    orig_steps = [(0.05, 0.065, 0.75), (0.065, 0.0845, 0.75), (0.0845, 0.100, 0.75)]
    orig_cs = [Q_MIN * k + F_A(A_MIN, k, L) - kp for k, kp, L in orig_steps]
    orig_us = [float(box_worst_u(c, L)) for c, (_, _, L) in zip(orig_cs, orig_steps)]
    W_M0_orig = sum((BETA_MAX ** t) * u for t, u in enumerate(orig_us)) + (BETA_MAX ** 3) * W_M_10_exact

    # Verify Step 1 max feasible consumption (L -> 1) and max_L u(eta_+) < -4.59
    c1_max_L1 = Q_MIN * 0.05 + F_A(A_MIN, 0.05, 1.0) - 0.065
    u1_max_L = max(float(box_worst_u(Q_MIN * 0.05 + F_A(A_MIN, 0.05, L) - 0.065, L)) for L in np.linspace(0.50, 0.90, 2000))

    Psi_h0 = -34.271388
    J_M0_T10 = B0_star + (BETA_MAX ** 10) * (Psi_h0 - B0_star)

    # Upgrade U1: Sharpened M0 witness (0.05 -> 0.0595 -> 0.0755 -> 0.100), L=(0.45, 0.50, 0.60)
    u1_steps = [(0.05, 0.0595, 0.45), (0.0595, 0.0755, 0.50), (0.0755, 0.100, 0.60)]
    u1_cs = [Q_MIN * k + F_A(A_MIN, k, L) - kp for k, kp, L in u1_steps]
    u1_us = [float(box_worst_u(c, L)) for c, (_, _, L) in zip(u1_cs, u1_steps)]
    W_M0_u1_old = sum((BETA_MAX ** t) * u for t, u in enumerate(u1_us)) + (BETA_MAX ** 3) * W_M_10_exact

    # Full K0 in [0.05, 0.10) coverage via temporary liquidation K0 -> 0.0595 -> 0.0755 -> 0.100
    k0_grid = np.linspace(0.05, 0.09999, 200)
    W_M0_k0_grid = np.array([
        float(box_worst_u(Q_MIN * K0 + F_A(A_MIN, K0, 0.45) - 0.0595, 0.45))
        + BETA_MAX * u1_us[1]
        + (BETA_MAX ** 2) * u1_us[2]
        + (BETA_MAX ** 3) * W_M_10_exact
        for K0 in k0_grid
    ])

    # U1 Unification with 25-step W_M^(0) and continuously certified Psi^(0) (a=0.45, b=5.0)
    _, _, _, eval_witness = build_25step_witness_builder()
    W_M_25_bmax, _, _ = eval_witness(BETA_MAX, B_M, b_solve=BETA_MAX, eta_mode="outer")
    W_M_25_bmin, _, _ = eval_witness(BETA_MIN, B_M, b_solve=BETA_MIN, eta_mode="outer")
    W_M0_u1_25 = sum((BETA_MAX ** t) * u for t, u in enumerate(u1_us)) + (BETA_MAX ** 3) * W_M_25_bmax

    c0_bmax, d0_ub, d0_lb, tail0_marg = certify_psi_centered(A_MAX, BETA_MAX, 0.45, 5.0, tol=2e-4, buffer=0.0005)
    c0_bmin, d0_ub_min, _, tail0_marg_min = certify_psi_centered(A_MAX, BETA_MIN, 0.45, 5.0, tol=2e-4, buffer=0.0005)
    c0_unif = max(c0_bmax, c0_bmin)
    Psi0_10_unif = 0.45 * B_M - 5.0 * (B_M ** -0.5) + c0_unif
    Psi0_28_unif = 0.45 * H_M - 5.0 * (H_M ** -0.5) + c0_unif

    # Box-uniform independent endpoints (T=22, T0=9) vs matched-beta recomputing c0(b_m) at each beta (T=21)
    J_T21_indep = B1_b + (BETA_MAX ** 21) * (Psi0_28_unif - B_star)
    J_T22_indep = B1_b + (BETA_MAX ** 22) * (Psi0_28_unif - B_star)
    gaps_matched_T21 = {}
    for b_m in (BETA_MIN, 0.9700, BETA_MAX):
        D2_m = (ETA_MIN * b_m * Q_MIN * (H_M - B_M)) / C_max_plus
        Bs_m = (R_hat - D2_m) / (1.0 - b_m)
        B1b_m = Bs_m - slope * (H_M - B_M)
        WM_m, _, _ = eval_witness(b_m, B_M, b_solve=b_m, eta_mode="outer")
        c0_m, _, _, _ = certify_psi_centered(A_MAX, b_m, 0.45, 5.0, tol=2e-4, buffer=0.0005)
        Psi0_28_m = 0.45 * H_M - 5.0 * (H_M ** -0.5) + c0_m
        gaps_matched_T21[b_m] = WM_m - (B1b_m + (b_m ** 21) * (Psi0_28_m - Bs_m))
    slope0 = (ETA_MIN * Q_MIN) / C_max0
    B0_1_grid = B0_star - slope0 * (h0 - k0_grid)
    J_T0_9_grid = B0_1_grid + (BETA_MAX ** 9) * (Psi0_10_unif - B0_star)
    J_T0_9_b0 = float(J_T0_9_grid[0])
    min_gap_T0_9 = float(np.min(W_M0_k0_grid - J_T0_9_grid))

    print(f"  C_max+          = {C_max_plus:.8f}")
    print(f"  Delta_2 exact   = {Delta_2_exact:.7f} (> {Delta_2})")
    print(f"  B_*             = {B_star:.7f} (<= -43.0465116)")
    print(f"  B_1(0.10)       = {B1_b:.6f} (<= -43.355594)")
    print(f"  W_M(0.10) exact = {W_M_10_exact:.8f} (> -35.58)")
    print(f"  Margin (unif.)  = {margin_unif:.4f} (> 7.4665), Margin (state) = {margin_state:.6f} (> 7.7755)")
    print(f"  T=24 uniform    = {J_T24:.5f} (< -35.58), T=23 slack = +{slack_T23:.6f} (> 0)")
    print(f"  M0 C_max0       = {C_max0:.6f}, Delta_0 exact = {Delta_0_exact:.6f}")
    print(f"  M0 B_0*         = {B0_star:.6f} (exact R_hat0={R_hat0_exact:.6f} -> B_0*={B0_star_exact:.6f} <= -71.046512)")
    print(f"  M0 orig path u  = {[round(x, 6) for x in orig_us]} -> W_M0(0.05)={W_M0_orig:.6f} (> -43.845)")
    print(f"    (Step 1 max c(L->1) = {c1_max_L1:.6f}, max_L u = {u1_max_L:.6f} < -4.59; T0=10 prefix = {J_M0_T10:.6f})")
    print(f"  U1 sharpened u  = {[round(x, 6) for x in u1_us]}")
    print(f"    W_M0(0.05; old tail)   = {W_M0_u1_old:.6f} (all K0 in [0.05, 0.10) temp. liq. >= {W_M0_k0_grid[0]:.6f})")
    print(f"    W_M0(0.05; 25-st tail) = {W_M0_u1_25:.6f} (using W_M^(0)(0.10; beta_+) = {W_M_25_bmax:.6f})")
    print(f"  U1 Psi^(0) cert : c0(b+)={c0_bmax:.6f}, c0_unif(box)={c0_unif:.6f} (B&B d(b+) in [{d0_lb:.6f}, {d0_ub:.6f}], tail={min(tail0_marg, tail0_marg_min):.4f})")
    print(f"    Psi^(0)_unif(0.10) = {Psi0_10_unif:.6f}, Psi^(0)_unif(0.28) = {Psi0_28_unif:.6f}")
    print(f"    tau_.1 <= 9 (box-unif B^(0)): J(9;0.05) = {J_T0_9_b0:.6f} < {W_M0_u1_old:.6f} (min gap on M0 = +{min_gap_T0_9:.4f})")
    print(f"    tau_H param (indep box): T=21 gap = {W_M_25_bmax - J_T21_indep:+.6f} (fails), T=22 gap = {W_M_25_bmax - J_T22_indep:+.6f} (passes)")
    print(f"    tau_H param (matched beta, Psi^(0)(b_m)): T=21 gaps = " + ", ".join(f"{b:.4f}:+{g:.6f}" for b, g in gaps_matched_T21.items()))

    assert abs(C_max_plus - 0.37495167) < 1e-6
    assert B_star <= -43.0465115 and B1_b <= -43.355593
    assert W_M_10_exact > -35.58 and abs(W_M_10_exact - (-35.579855)) < 1e-5
    assert margin_unif > 7.4665 and margin_state > 7.77559
    assert J_T24 < W_M_floor and slack_T23 > 0.2056
    assert abs(B0_star - (-71.046512)) < 1e-6 and B0_star_exact <= B0_star
    assert abs(orig_us[0] - (-4.611772)) < 2e-6 and abs(orig_us[1] - (-3.964892)) < 2e-6 and abs(orig_us[2] - (-3.085659)) < 2e-6
    assert W_M0_orig > -43.845 and abs(W_M0_orig - (-43.844826)) < 2e-5
    assert c1_max_L1 < 0.00301 and u1_max_L < -4.59
    assert J_M0_T10 < W_M0_orig
    assert abs(W_M0_u1_old - (-43.540132)) < 2e-5 and abs(W_M0_u1_25 - (-43.500107)) < 5e-5
    assert np.all(np.diff(W_M0_k0_grid) > 0.0) and W_M0_k0_grid[0] == W_M0_u1_old
    assert J_T0_9_b0 < W_M0_u1_old and J_T0_9_b0 < W_M0_u1_25 and min_gap_T0_9 > 0.0
    assert W_M_25_bmax - J_T21_indep < 0.0 and W_M_25_bmax - J_T22_indep > 0.0
    assert all(g > 0.06 for g in gaps_matched_T21.values())


# ---------------------------------------------------------------------------
# 2. Proposition 1** & Upgrade U2 (Analytical interval arithmetic & Wronskian)
# ---------------------------------------------------------------------------
def t_func(K, l0):
    return dF_dL(A_MAX, K, l0)


def t_prime(K, l0):
    return 1.5 * A_MAX * (2.0 ** 1.5) * 2.5 * (K ** 1.5) * (l0 ** 1.5) * ((K + l0) ** (-3.5))


def t_double_prime(K, l0):
    return 1.5 * A_MAX * (2.0 ** 1.5) * 2.5 * (l0 ** 1.5) * (K ** 0.5) * ((K + l0) ** (-4.5)) * (1.5 * l0 - 2.0 * K)


def verify_prop1_double_star():
    print("\n" + "=" * 72)
    print("2. PROPOSITION 1**, TABLE 2 & U2 (ANALYTICAL INTERVAL CERTIFICATE)")
    print("=" * 72)

    regions = {
        "M": dict(l_X=0.68, s_X=0.135, T_X=-33.103, a=0.10, l0=0.44, k_min=0.10, k_max=0.28, n_q=4, n_d2=8),
        "H1": dict(l_X=0.72, s_X=0.375, T_X=-27.164, a=0.28, l0=0.57, k_min=0.28, k_max=0.80, n_q=6, n_d2=10),
    }

    def S_val(K, l0):
        return Q_MAX * K + F_A(A_MAX, K, l0) + (1.0 - l0) * t_func(K, l0)

    def S_prime(K, l0):
        return Q_MAX + dF_dK(A_MAX, K, l0) + (1.0 - l0) * t_prime(K, l0)

    def c_val(K, l_X, s_X):
        return Q_MIN * K + F_A(A_MIN, K, l_X) - s_X

    def c_prime(K, l_X):
        return Q_MIN + dF_dK(A_MIN, K, l_X)

    def max_abs_d2F(kL, kR, L):
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
        l_X, s_X, _, a, l0 = cfg["l_X"], cfg["s_X"], cfg["T_X"], cfg["a"], cfg["l0"]
        assert l0 >= cfg["k_max"] / 2.0, f"Global tangency dominance l0 >= sup(X)/2 failed on {name}"
        if name == "M":
            edges_q = np.linspace(cfg["k_min"], cfg["k_max"], cfg["n_q"] + 1)
        else:
            edges_q = np.array([0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80])

        Q_bounds = []
        d1_bounds = []
        for kL, kR in zip(edges_q[:-1], edges_q[1:]):
            km = 0.5 * (kL + kR)
            Qm = S_prime(km, l0) * c_val(km, l_X, s_X) - c_prime(km, l_X) * (S_val(km, l0) - a)
            d2F_pts = max_abs_d2F(kL, kR, l0)
            tpp_pts = max_abs_tpp_pts(kL, kR, l0)
            d2Fc_pts = max_abs_d2F(kL, kR, l_X)
            Spp_abs_max = max(abs(d2F_dK2(A_MAX, pt, l0)) for pt in d2F_pts) + (1.0 - l0) * max(abs(t_double_prime(pt, l0)) for pt in tpp_pts)
            cpp_abs_max = max(abs(d2F_dK2(A_MIN, pt, l_X)) for pt in d2Fc_pts)
            Qp_max = Spp_abs_max * c_val(kR, l_X, s_X) + cpp_abs_max * (S_val(kR, l0) - a)
            Q_ub = Qm + 0.5 * (kR - kL) * Qp_max
            Q_bounds.append(Q_ub)
            assert Q_ub < 0.0, f"Wronskian upper bound positive on [{kL},{kR}]"

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
            cands_dFk = [kL, kR] + ([l0 / 4.0] if kL < l0 / 4.0 < kR else [])
            cands_tp = [kL, kR] + ([0.75 * l0] if kL < 0.75 * l0 < kR else [])
            Sp_ub = Q_MAX + max(dF_dK(A_MAX, p, l0) for p in cands_dFk) + (1.0 - l0) * max(t_prime(p, l0) for p in cands_tp)
            cp_lb = min(c_prime(kL, l_X), c_prime(kR, l_X))
            R_lb = (S_val(kR, l0) - a) / c_val(kR, l_X, s_X)
            t1_num = Sp_ub ** 2 - ETA_MIN * (cp_lb * R_lb) ** 2
            t1_ub = t1_num / ((S_val(kL, l0) - a) ** 2 if t1_num >= 0 else (S_val(kR, l0) - a) ** 2)

            # Fix c_M'' sign bug: when cpp_ub >= 0 (occurring on [0.10, l_M/4 = 0.17)), multiply by ETA_MAX!
            cands_cpp = max_abs_d2F(kL, kR, l_X)
            cpp_ub = max(d2F_dK2(A_MIN, p, l_X) for p in cands_cpp)
            if cpp_ub >= 0.0:
                t2_ub = ETA_MAX * cpp_ub / c_val(kL, l_X, s_X)
            else:
                t2_ub = ETA_MIN * cpp_ub / c_val(kR, l_X, s_X)

            Spp_pts_L = max_abs_d2F(kL, kR, l0)
            Spp_pts_t = max_abs_tpp_pts(kL, kR, l0)
            Spp_lb = min(d2F_dK2(A_MAX, p, l0) for p in Spp_pts_L) + (1.0 - l0) * min(t_double_prime(p, l0) for p in Spp_pts_t)
            t3_ub = (-Spp_lb) / (S_val(kL, l0) - a if (-Spp_lb) >= 0 else S_val(kR, l0) - a)
            t4_ub = (1.0 - ETA_MAX) * (-2.5 * l0 * (2.0 * kR + l0)) / ((kR ** 2) * ((kR + l0) ** 2))
            d2_ub = t1_ub + t2_ub + t3_ub + t4_ub
            d2_bounds.append(d2_ub)
            assert d2_ub < 0.0, f"Delta''_X upper bound >= 0 on [{kL},{kR}]: {d2_ub}"

        # Interior u*(K) = (1 - eta)(S(K) - a)/t(K) range on region
        Ks_dense = np.linspace(cfg["k_min"], cfg["k_max"], 1000)
        t_dense = t_func(Ks_dense, l0)
        S_dense = S_val(Ks_dense, l0)
        u_lo = float(np.min((1.0 - ETA_MAX) * (S_dense - a) / t_dense))
        u_hi = float(np.max((1.0 - ETA_MIN) * (S_dense - a) / t_dense))

        d1_right = d1_exact(cfg["k_max"], cfg)
        print(f"  Region {name}:")
        print(f"    Wronskian Q_{name} <= {[round(float(x), 5) for x in Q_bounds]}")
        print(f"    Delta'_{name}     >= {[round(float(x), 4) for x in d1_bounds]}")
        print(f"    Delta''_{name}    <= {[round(float(x), 4) for x in d2_bounds[:4]]} ... (max {max(d2_bounds):.4f} < 0)")
        print(f"    Delta'_{name}(right) = +{d1_right:.6f} | u*(K) in [{u_lo:.4f}, {u_hi:.4f}] < 1 => L* >= {1.0 - u_hi:.4f}")
        assert u_hi < 1.0
        if name == "M":
            assert abs(d2_bounds[0] - (-421.1331)) < 0.01
            assert abs(u_hi - 0.6808) < 0.001

    # U2 Variational Values & H1 Downward Kink Verification
    L_star_028 = brentq(
        lambda L: ETA_MIN * dF_dL(A_MAX, 0.28, L) / (Q_MAX * 0.28 + F_A(A_MAX, 0.28, L) - 0.28) - (1.0 - ETA_MIN) / (1.0 - L),
        0.1, 0.99,
    )
    L_star_010 = brentq(
        lambda L: ETA_MIN * dF_dL(A_MAX, 0.10, L) / (Q_MAX * 0.10 + F_A(A_MAX, 0.10, L) - 0.10) - (1.0 - ETA_MIN) / (1.0 - L),
        0.1, 0.99,
    )
    L_tan_010_em = 1.0 - (1.0 - ETA_MIN) * (S_val(0.10, 0.44) - 0.10) / t_func(0.10, 0.44)
    L_tan_010_ep = 1.0 - (1.0 - ETA_MAX) * (S_val(0.10, 0.44) - 0.10) / t_func(0.10, 0.44)

    # H1 kinks where c_H1(K) = 1 - l_H (0.28) and where E_a = E_b (t = 0.428571)
    k_kink_W = brentq(lambda K: c_val(K, 0.72, 0.375) - (1.0 - 0.72), 0.28, 0.80)
    def E_diff(K):
        S_a = S_val(K, 0.57) - 0.28
        t_k = t_func(K, 0.57)
        Ea = ETA_MIN * np.log(ETA_MIN * S_a) + (1.0 - ETA_MIN) * np.log((1.0 - ETA_MIN) * S_a / t_k)
        Eb = ETA_MAX * np.log(ETA_MAX * S_a) + (1.0 - ETA_MAX) * np.log((1.0 - ETA_MAX) * S_a / t_k)
        return Ea - Eb
    k_kink_E = brentq(E_diff, 0.28, 0.80)
    # Verify downward jumps in Delta'_H1 at both kinks
    W_p_left = ETA_MAX * c_prime(k_kink_W, 0.72) / c_val(k_kink_W, 0.72, 0.375)
    W_p_right = ETA_MIN * c_prime(k_kink_W, 0.72) / c_val(k_kink_W, 0.72, 0.375)
    S_a_E = S_val(k_kink_E, 0.57) - 0.28
    Sp_E = S_prime(k_kink_E, 0.57)
    tp_over_t_E = 2.5 * 0.57 / (k_kink_E * (k_kink_E + 0.57))
    mE_p_left = -(Sp_E / S_a_E - (1.0 - ETA_MIN) * tp_over_t_E)
    mE_p_right = -(Sp_E / S_a_E - (1.0 - ETA_MAX) * tp_over_t_E)

    print(f"  U2 Variational: L*(0.28)={L_star_028:.6f}, L*(0.10)={L_star_010:.6f}, L_tan(0.10;0.44) in [{L_tan_010_em:.6f}, {L_tan_010_ep:.6f}]")
    print(f"  H1 Downward Kinks: k_W={k_kink_W:.6f} (W': {W_p_left:.6f} -> {W_p_right:.6f}), k_E={k_kink_E:.6f} ((-E+)': {mE_p_left:.6f} -> {mE_p_right:.6f})")
    assert abs(L_star_028 - 0.569743) < 1e-4 and abs(L_star_010 - 0.437261) < 1e-4
    assert abs(L_tan_010_ep - 0.433840) < 1e-4
    assert abs(k_kink_W - 0.406819) < 1e-5 and W_p_right < W_p_left
    assert abs(k_kink_E - 0.573570) < 1e-5 and mE_p_right < mE_p_left

    # Exact left-endpoint adverse-exit margins (Prop 1** part 2)
    def margin_left(K, l_X, s_X, T_X, a, l0, Psi_sharp_a):
        c = Q_MIN * K + F_A(A_MIN, K, l_X) - s_X
        W_X = float(box_worst_u(c, l_X)) + BETA_MAX * T_X
        E_plus = E_plus_exact(A_MAX, Q_MAX, K, a, l0)
        return W_X - (E_plus + BETA_MIN * Psi_sharp_a)

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
def _golden_solve_L(k_arr, kp_arr, f_norm, q, eta):
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

    # Modified golden-rule steady state with dynamic upper bracket scaling as A^2.5
    lo_ss = 0.25 * (A_val ** 2)
    hi_ss = max(1e10, 10.0 * np.sqrt(1.5 * c_K / D) * (A_val ** 2.5))
    while df_dk(hi_ss) >= D:
        hi_ss *= 10.0
    k_ss = brentq(lambda k: df_dk(k) - D, lo_ss, hi_ss)
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
        return _golden_solve_L(k_arr, kp_arr, f_norm, q, eta)

    def refine_skiba(i_jump, V_sol, endo=False):
        k_sub = np.linspace(k_grid[i_jump - 1], k_grid[i_jump], 25)
        y_sub = q * k_sub + f_norm(k_sub, 1.0)
        diffs = np.empty_like(k_sub)
        for ii, (ks, ys) in enumerate(zip(k_sub, y_sub)):
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


def solve_endo_threshold_vfi(A_val):
    """General continuous golden-section VFI in physical K to find S_A (or nan under economic extinction)."""
    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    q = 1.0 - delta
    V_cake_const = (eta / (1.0 - beta)) * (np.log((1.0 - beta) * q) + (beta / (1.0 - beta)) * np.log(beta * q))
    K_hi = max(2.5, 2.0 * (A_val ** 2) * 3.0)
    Ks = np.unique(np.concatenate([
        np.geomspace(1e-4, 0.05, 60, endpoint=False),
        np.linspace(0.05, 0.35, 300, endpoint=False),
        np.geomspace(0.35, K_hi, 100),
    ]))
    nk = len(Ks)
    Ls = np.unique(np.concatenate([np.geomspace(1e-4, 0.08, 20, endpoint=False), np.linspace(0.08, 0.999, 50)]))
    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0

    def f_K(K, L):
        return F_A(A_val, K, L)

    y_kL = q * Ks[:, None] + f_K(Ks[:, None], Ls[None, :])
    dis_L = (1.0 - eta) * np.log(1.0 - Ls[None, :])
    u_g = np.full((nk, nk), -1e9)
    for i in range(nk):
        cb = y_kL[i, None, :] - Ks[:, None]
        u_g[i, :] = np.max(np.where(cb > 1e-15, eta * np.log(np.maximum(cb, 1e-30)) + dis_L, -1e9), axis=1)

    def interp_V(Kp, V):
        v = np.interp(np.clip(Kp, Ks[0], Ks[-1]), Ks, V)
        return np.where(Kp < Ks[0], V[0] + (eta / (1.0 - beta)) * np.log(np.maximum(Kp, 1e-30) / Ks[0]), v)

    sc = 1.0 - np.geomspace(1e-5, 0.15, 20)
    kpt = y_kL[:, -1][:, None] * sc[None, :]
    ut = np.full((nk, len(sc)), -1e9)
    for j in range(len(sc)):
        _, ut[:, j] = _golden_solve_L(Ks, kpt[:, j], f_K, q, eta)
    V = V_cake_const + (eta / (1.0 - beta)) * np.log(Ks)
    ym = y_kL[:, -1]
    for _ in range(110):
        vg = u_g + beta * V[None, :]
        jb = np.argmax(vg, axis=1)
        bg = vg[np.arange(nk), jb]
        vt = ut + beta * interp_V(kpt, V)
        sb = np.argmax(vt, axis=1)
        bt = vt[np.arange(nk), sb]
        use = bt > bg
        lot = kpt[np.arange(nk), np.maximum(0, sb - 1)]
        hit = kpt[np.arange(nk), np.minimum(len(sc) - 1, sb + 1)]
        lo = np.where(use, np.minimum(lot, hit), Ks[np.maximum(0, jb - 1)])
        hi = np.where(use, np.minimum(np.maximum(lot, hit), ym - 1e-12), np.minimum(Ks[np.minimum(nk - 1, jb + 1)], ym - 1e-12))
        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        _, u1 = _golden_solve_L(Ks, x1, f_K, q, eta)
        _, u2 = _golden_solve_L(Ks, x2, f_K, q, eta)
        f1 = u1 + beta * interp_V(x1, V)
        f2 = u2 + beta * interp_V(x2, V)
        for _g in range(14):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            _, u1n = _golden_solve_L(Ks, x1n, f_K, q, eta)
            _, u2n = _golden_solve_L(Ks, x2n, f_K, q, eta)
            f1n = np.where(mr, f2, u1n + beta * interp_V(x1n, V))
            f2n = np.where(mr, u2n + beta * interp_V(x2n, V), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        pol = np.where(f1 > f2, x1, x2)
        _, up = _golden_solve_L(Ks, pol, f_K, q, eta)
        Ve = np.maximum(f1, f2)
        for _h in range(90):
            Vn = up + beta * interp_V(pol, Ve)
            if np.max(np.abs(Vn - Ve)) < 1e-10:
                Ve = Vn
                break
            Ve = Vn
        if np.max(np.abs(Ve - V)) < 1e-9:
            V = Ve
            break
        V = Ve
    pos = np.where((pol - Ks) > 1e-8)[0]
    if len(pos) == 0:
        return False, np.nan
    i0 = int(pos[0])
    return True, float(0.5 * (Ks[i0 - 1] + Ks[i0]))


def verify_theorem3_star():
    print("\n" + "=" * 72)
    print("3. THEOREM 3* & TABLE 3 (FOC + DIRECT 880-POINT VFI UP TO A=1e8)")
    print("=" * 72)

    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    nu = (1.0 - eta) / eta
    c_K = w ** (theta / rho)
    k_b, c_b = 0.002, 0.0001

    print(f"  Benchmark limit (delta/c_K)^2 = {(delta / c_K)**2:.6f}, beta*theta = {beta*theta:.4f} > 1")
    print("  A         kappa_A      A^2*kappa   L*          A*L*     Gap_FA   A^2*S_fix  A^2*S_endo  Ratio(VFI)  dW+")
    prev_ratio = 2.0
    for A_val in [0.75, 1.50, 3.00, 10.0, 30.0, 100.0, 1000.0, 1e8]:
        kap = exact_kappa(A_val, delta)
        K_v = k_b / (A_val ** 2)
        C_v = c_b / (A_val ** 2)
        L_s = brentq(lambda L: dF_dL(A_val, K_v, L) - nu * C_v / (1.0 - L), K_v / 3.0, 1.0 - 1e-12)
        gap_FA = (c_K * (k_b ** 1.5) - (A_val ** 2) * F_A(A_val, K_v, L_s)) / (c_K * (k_b ** 1.5))
        kS_fix, kS_endo, dWp = solve_vfi_frontiers(A_val)
        ratio = kS_endo / kS_fix
        A_lbl = f"{A_val:8.2f}" if A_val <= 1000.0 else f"{A_val:8.1e}"
        print(
            f"  {A_lbl}  {kap:10.3e}  {A_val**2*kap:9.6f}  {L_s:10.3e}  {A_val*L_s:8.5f}  "
            f"{100*gap_FA:6.3f}%  {kS_fix:9.6f}  {kS_endo:10.6f}  {ratio:10.5f}  {dWp:6.2f}"
        )
        assert kS_fix < kS_endo
        assert dWp > 0.0
        if A_val <= 1000.0:
            assert ratio < prev_ratio
        prev_ratio = ratio
    assert kS_fix < 0.000836 and kS_endo < 0.000837 and abs(ratio - 1.0) < 0.002


# ---------------------------------------------------------------------------
# 4. Theorem 10, Table 4, U3 & Structural Extensions (Prop. 2*, Footnote 2)
# ---------------------------------------------------------------------------
def verify_theorem10():
    print("\n" + "=" * 72)
    print("4. THEOREM 10, TABLE 4, U3, PROP. 2* & FOOTNOTE 2")
    print("=" * 72)

    A0, alpha, delta, beta = 1.45, 0.25, 0.08, 0.97
    theta, eta, q = 1.5, 0.70, 1.0 - 0.08
    nu = (1.0 - eta) / eta
    c_K = 0.5 ** (-1.5)
    D = 1.0 / beta - q
    H_a = ((2.0 * 0.5 / 1.5) ** 1.5) / 0.5
    A_rep = delta / H_a
    tau_min = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_rep, 1e-9, 0.20)
    tau_max = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_rep, 0.20, 1.0 - 1e-9)

    # Exact endogenous MGR saddle-node A_* = A_SN and economic viability interval (tau_1, tau_2)
    def planner_ss_resid(u, A_v):
        L = (D / (1.5 * A_v * (2.0 ** 1.5) * (u ** 0.5) * ((1.0 + u) ** (-2.5)))) ** 2
        if L >= 1.0:
            return -1e3 - L
        K = u * L
        C = F_A(A_v, K, L) - delta * K
        if C <= 0.0:
            return -1e3
        return dF_dL(A_v, K, L) * (1.0 - L) - nu * C

    A_SN = brentq(lambda Av: max(planner_ss_resid(u, Av) for u in np.geomspace(0.05, 1.5, 800)), 0.095, 0.105, xtol=1e-9)
    tau_1 = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_SN, 1e-9, 0.20)
    tau_2 = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_SN, 0.20, 1.0 - 1e-9)

    # Theorem 8 finite-A certified domain (A_e >= 0.749)
    tau_t8_lo = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - 0.749, 1e-9, 0.20)
    tau_t8_hi = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - 0.749, 0.20, 1.0 - 1e-9)

    # Crossing threshold A_cross where asymptotic Sbar = (D/c_K)^2 / A^2 ceases to upper-bound true VFI S_endo
    A_cross = brentq(lambda Av: solve_endo_threshold_vfi(Av)[1] - ((D / c_K) ** 2) / (Av ** 2), 0.100, 0.120, xtol=2e-5)
    tau_cross_1 = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_cross, 1e-9, 0.20)
    tau_cross_2 = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_cross, 0.20, 1.0 - 1e-9)

    # True VFI checks at tau = 2.0e-5 and tau = 0.94 confirming economic extinction
    Ae_low = A0 * (2e-5 ** alpha) * (1.0 - 2e-5)
    Ae_high = A0 * (0.94 ** alpha) * (1.0 - 0.94)
    surv_low, S_low = solve_endo_threshold_vfi(Ae_low)
    surv_high, S_high = solve_endo_threshold_vfi(Ae_high)

    print(f"  A_rep = {A_rep:.6f}, tau_min = {tau_min:.2e}, tau_max = {tau_max:.6f}")
    print(f"  A_* = A_SN = {A_SN:.7f}, economic interval (tau_1, tau_2) = ({tau_1:.6e}, {tau_2:.6f})")
    print(f"  Asymptotic bound crossing: A_cross = {A_cross:.6f} -> (tau_c1, tau_c2) = ({tau_cross_1:.6e}, {tau_cross_2:.6f})")
    print(f"  Theorem 8 finite-A domain (Ae >= 0.749): [{tau_t8_lo:.6f}, {tau_t8_hi:.6f}]")
    print(f"  VFI economic extinction checks: tau=2e-5 (Ae={Ae_low:.6f}) survives={surv_low}; tau=0.94 (Ae={Ae_high:.6f}) survives={surv_high}")

    assert abs(A_rep - 0.073485) < 1e-5 and abs(tau_max - 0.948649) < 1e-5
    assert abs(A_SN - 0.0995245) < 1e-5
    assert abs(tau_1 - 2.2197e-5) < 1e-7 and abs(tau_2 - 0.930108) < 1e-5
    assert abs(tau_t8_lo - 0.117245) < 1e-5 and abs(tau_t8_hi - 0.304799) < 1e-5
    assert 0.105 < A_cross < 0.115
    assert (not surv_low) and (not surv_high)

    taus = [5e-6, 2e-5, 0.02, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 0.90, 0.94, 0.95]
    for tau in taus:
        Ae = A0 * (tau ** alpha) * (1.0 - tau)
        ratio = Ae / A_rep
        if ratio > 1.0:
            kap = exact_kappa(Ae, delta)
            Sbar = ((D / c_K) ** 2) / (Ae ** 2)
            econ_tag = " [ECONOMIC EXTINCTION: Ae < A_*]" if Ae < A_SN else (" [S_endo > Sbar]" if Ae < A_cross else "")
            print(f"  tau={tau:7.2e}  Ae={Ae:.4f}  Ae/Arep={ratio:5.2f}  kappa={kap:.6f}  Sbar_asy={Sbar:.6f}{econ_tag}")
        else:
            print(f"  tau={tau:7.2e}  Ae={Ae:.4f}  Ae/Arep={ratio:5.2f}  (global physical extinction)")
            if tau == 5e-6:
                assert round(Ae, 4) == 0.0686

    # U3: Barro rule tau* = gamma and Prop. 2*(1) fragmentation counts (M_SN vs M_rep)
    gamma_barro = alpha / (1.0 + alpha)
    tau_barro = alpha / (1.0 + alpha)
    M_rep = (0.75 / A_rep) ** (1.0 / (theta - 1.0))
    M_SN = (0.75 / A_SN) ** (1.0 / (theta - 1.0))
    print(f"  U3 Barro & Fragmentation: tau* = gamma = {tau_barro:.2f} (alpha={alpha}); M_SN = {M_SN:.2f} vs M_rep = {M_rep:.2f}")
    assert abs(tau_barro - gamma_barro) < 1e-12
    assert abs(M_rep - 104.17) < 0.05 and abs(M_SN - 56.79) < 0.05

    # Item 5: Proposition 2* decentralized equilibria (K_lo, K_hi) vs planner thresholds
    print("\n  [Item 5: Prop. 2* Decentralized Steady States (K_lo, K_hi) vs Planner VFI S(A_mkt)]")
    for mu in [1.5, 1.8, 2.0]:
        A_mkt = (theta / mu) * 0.75
        S_mkt = solve_vfi_frontiers(A_mkt)[1] / (A_mkt ** 2)
        for mode in ("overhead", "rebate"):
            if mu == 1.5 and mode == "rebate":
                continue

            def dec_resid_u(u):
                L = (D * mu / (1.5 * 0.75 * (2.0 ** 1.5) * (u ** 0.5) * ((1.0 + u) ** (-2.5)))) ** 2
                if L >= 1.0:
                    return -1e3 - L
                K = u * L
                coef = (theta / mu) if mode == "overhead" else 1.0
                C = coef * F_A(0.75, K, L) - delta * K
                if C <= 0.0:
                    return -1e3
                return (dF_dL(0.75, K, L) / mu) * (1.0 - L) - nu * C

            us_scan = np.geomspace(0.005, 10.0, 2000)
            vals_scan = np.array([dec_resid_u(u) for u in us_scan])
            roots = []
            for ii in range(len(us_scan) - 1):
                if abs(vals_scan[ii]) < 100.0 and abs(vals_scan[ii + 1]) < 100.0 and vals_scan[ii] * vals_scan[ii + 1] <= 0.0:
                    ur = brentq(dec_resid_u, us_scan[ii], us_scan[ii + 1])
                    Lr = (D * mu / (1.5 * 0.75 * (2.0 ** 1.5) * (ur ** 0.5) * ((1.0 + ur) ** (-2.5)))) ** 2
                    roots.append((ur * Lr, Lr))
            (K_lo, L_lo), (K_hi, L_hi) = roots[0], roots[-1]
            print(f"    mu={mu:.1f} ({mode:8s}): A_mkt={A_mkt:.4f}, S(A_mkt)={S_mkt:.6f} | K_lo={K_lo:.6f} (L={L_lo:.4f}), K_hi={K_hi:.6f} (L={L_hi:.4f})")
            assert K_lo > S_mkt

    # Item 6: Footnote 2 continuous AK regime check at h = 0.28
    def ak_val(s_L):
        s_ak, L_ak = s_L
        R_ak = q + F_A(0.75, 0.28, L_ak) / 0.28
        C0 = (1.0 - s_ak) * R_ak * 0.28
        if C0 <= 0 or L_ak <= 0 or L_ak >= 1 or s_ak <= 0 or s_ak >= 1:
            return 1e9
        g_log = np.log(s_ak * R_ak)
        V = (eta * np.log(C0) + (1.0 - eta) * np.log(1.0 - L_ak)) / (1.0 - beta) + (beta * eta * g_log) / ((1.0 - beta) ** 2)
        return -V

    res_ak = minimize(ak_val, [0.97, 0.92], method="Nelder-Mead", options={"xatol": 1e-8, "fatol": 1e-8})
    V_AK_028 = -float(res_ak.fun)
    Psi_sharp_028 = 0.4 * 0.28 - 5.0 / np.sqrt(0.28) - 18.5 - 10.0 / 301.0
    print(f"  [Item 6 Footnote 2] Continuous AK at h=0.28: V_AK(0.28) = +{V_AK_028:.4f} >> Psi#(0.28) = {Psi_sharp_028:.6f}")
    assert V_AK_028 > 240.0 and V_AK_028 > Psi_sharp_028


# ---------------------------------------------------------------------------
# 5. Theorem 11*, Table 5, U4, U5 & Technical Appendix Reproducibility
# ---------------------------------------------------------------------------
def _build_slope_tables(slopes_arr):
    m = len(slopes_arr)
    smin = np.full((m, m), np.inf)
    smax = np.full((m, m), -np.inf)
    for i in range(m):
        smin[i, i:] = np.minimum.accumulate(slopes_arr[i:])
        smax[i, i:] = np.maximum.accumulate(slopes_arr[i:])
    return smin, smax


def verify_theorem11_stochastic():
    print("\n" + "=" * 72)
    print("5. THEOREM 11*, TABLE 5, U4, U5 & TECHNICAL APPENDIX REPRODUCIBILITY")
    print("=" * 72)

    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    q = 1.0 - delta
    A_G, A_B = 0.75, 0.35
    AB_MIN, AB_MAX = 0.349, 0.351
    r_rec = 1.0 / 3.0
    C_max = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
    R_hat = -0.996

    k_wg, n_kw, build_u_worst, eval_witness = build_25step_witness_builder()
    uw_G, _ = build_u_worst(A_MIN, "outer")
    uw_B, _ = build_u_worst(AB_MIN, "outer")

    # Build continuous log-PWL super/sub-barrier machinery on [1e-8, 60.0] + analytical tails (0, 1e-8] & [90, inf)
    ks_m = np.unique(np.concatenate([
        np.geomspace(1e-8, 1e-5, 12, endpoint=False),
        np.geomspace(1e-5, 0.0012, 20, endpoint=False),
        np.geomspace(0.0012, 0.0030, 220, endpoint=False),
        np.geomspace(0.0030, 0.012, 65, endpoint=False),
        np.geomspace(0.012, 0.05, 50, endpoint=False),
        np.geomspace(0.05, 0.10, 45, endpoint=False),
        np.geomspace(0.10, 0.28, 50, endpoint=False),
        np.geomspace(0.28, 0.40, 25, endpoint=False),
        [B_M, H_M],
        np.geomspace(0.40, 2.0, 100, endpoint=False),
        np.geomspace(2.0, 60.0, 55),
    ]))
    lks_m = np.log(ks_m)
    nk_m = len(ks_m)
    Ls_m = np.unique(np.concatenate([[0.0], np.geomspace(1e-5, 0.08, 18, endpoint=False), np.linspace(0.08, 0.999, 52)]))
    s_cand_m = 1.0 - np.geomspace(1e-6, 0.15, 20)
    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0

    def precompute_state_pwl(A_v, q_v, is_upper, eL=ETA_MIN, eU=ETA_MAX):
        def get_u(Av, ka, La, kpa):
            cv = q_v * ka + F_A(Av, ka, La) - kpa
            lc = np.log(np.maximum(cv, 1e-30))
            ll = np.log(1.0 - La)
            ua = eL * lc + (1.0 - eL) * ll
            ub = eU * lc + (1.0 - eU) * ll
            uv = np.maximum(ua, ub) if is_upper else np.minimum(ua, ub)
            return np.where(cv > 1e-15, uv, -1e9 + cv)

        def solve_L(Av, ka, kpa):
            u0 = get_u(Av, ka, np.zeros_like(ka), kpa)
            lo = np.full_like(ka, 1e-7)
            hi = np.full_like(ka, 1.0 - 1e-9)
            x1 = hi - inv_phi * (hi - lo)
            x2 = lo + inv_phi * (hi - lo)
            f1, f2 = get_u(Av, ka, x1, kpa), get_u(Av, ka, x2, kpa)
            for _ in range(18):
                mr = f1 < f2
                lo = np.where(mr, x1, lo)
                hi = np.where(mr, hi, x2)
                x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
                x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
                f1n = np.where(mr, f2, get_u(Av, ka, x1n, kpa))
                f2n = np.where(mr, get_u(Av, ka, x2n, kpa), f1)
                x1, x2, f1, f2 = x1n, x2n, f1n, f2n
            Lb = 0.5 * (lo + hi)
            ub = get_u(Av, ka, Lb, kpa)
            return np.where(u0 > ub, 0.0, Lb), np.maximum(u0, ub)

        y = q_v * ks_m[:, None] + F_A(A_v, ks_m[:, None], Ls_m[None, :])
        um = np.full((nk_m, nk_m), -1e9)
        ll_m = np.log(1.0 - Ls_m[None, :])
        for i in range(nk_m):
            cm = y[i, None, :] - ks_m[:, None]
            lc_m = np.log(np.maximum(cm, 1e-30))
            ua = eL * lc_m + (1.0 - eL) * ll_m
            ub = eU * lc_m + (1.0 - eU) * ll_m
            uv = np.maximum(ua, ub) if is_upper else np.minimum(ua, ub)
            um[i, :] = np.max(np.where(cm > 1e-15, uv, -1e9), axis=1)
        ym = y[:, -1]
        kpt = ym[:, None] * s_cand_m[None, :]
        ut = np.zeros_like(kpt)
        for j in range(len(s_cand_m)):
            _, ut[:, j] = solve_L(A_v, ks_m, kpt[:, j])
        u0_mat = get_u(A_v, ks_m[:, None], 0.0, ks_m[None, :])
        return dict(A=A_v, qv=q_v, is_upper=is_upper, u=um, u0=u0_mat, ym=ym, kpt=kpt, ut=ut, solve_L=solve_L, get_u=get_u)

    def precompute_markov_pwl(AG_v, AB_v, q_v, is_upper, eL=ETA_MIN, eU=ETA_MAX):
        sG = precompute_state_pwl(AG_v, q_v, is_upper, eL, eU)
        sB = precompute_state_pwl(AB_v, q_v, is_upper, eL, eU)
        return dict(
            AG=AG_v, AB=AB_v, qv=q_v, is_upper=is_upper,
            uG=sG["u"], uG0=sG["u0"], ymG=sG["ym"], kptG=sG["kpt"], utG=sG["ut"],
            uB=sB["u"], uB0=sB["u0"], ymB=sB["ym"], kptB=sB["kpt"], utB=sB["ut"],
            solve_L=sG["solve_L"], get_u=sG["get_u"],
        )

    def solve_markov_pwl(pre, bv, p, init=None, return_ongrid_W=False, return_pol=False, tol_out=1e-8):
        ec0 = ETA_MIN if pre["is_upper"] else ETA_MAX
        s_lo_tail = ec0 / (1.0 - bv)
        d_hi_tail = (ETA_MAX if pre["is_upper"] else ETA_MIN) / (1.0 - bv)

        def interp(V, kp):
            lk = np.log(np.maximum(kp, 1e-30))
            r = np.interp(np.clip(lk, lks_m[0], lks_m[-1]), lks_m, V)
            r = np.where(kp < ks_m[0], V[0] + s_lo_tail * (lk - lks_m[0]), r)
            return np.where(kp > ks_m[-1], V[-1] + d_hi_tail * (lk - lks_m[-1]), r)

        if init is not None:
            VG, VB = init[0].copy(), init[1].copy()
        else:
            Vc = s_lo_tail * (np.log((1.0 - bv) * pre["qv"]) + (bv / (1.0 - bv)) * np.log(bv * pre["qv"]))
            VG = np.where(ks_m > 0.0016, -25.0, Vc + s_lo_tail * lks_m)
            VB = VG.copy() - 4.0
        solve_L = pre["solve_L"]
        get_u = pre["get_u"]
        for _ in range(40):
            EVG = (1.0 - p) * VG + p * VB
            EVB = r_rec * VG + (1.0 - r_rec) * VB
            pols, ups = [], []
            for uM, uM0, EV, Av, ym, kpt, ut in [
                (pre["uG"], pre["uG0"], EVG, pre["AG"], pre["ymG"], pre["kptG"], pre["utG"]),
                (pre["uB"], pre["uB0"], EVB, pre["AB"], pre["ymB"], pre["kptB"], pre["utB"]),
            ]:
                vg = uM + bv * EV[None, :]
                jb = np.argmax(vg, axis=1)
                bg = vg[np.arange(nk_m), jb]
                vt = ut + bv * interp(EV, kpt)
                sb = np.argmax(vt, axis=1)
                bt = vt[np.arange(nk_m), sb]
                uset = bt > bg
                lot = kpt[np.arange(nk_m), np.maximum(0, sb - 1)]
                hit = kpt[np.arange(nk_m), np.minimum(len(s_cand_m) - 1, sb + 1)]
                lo = np.where(uset, np.minimum(lot, hit), ks_m[np.maximum(0, jb - 1)])
                hi = np.where(uset, np.minimum(np.maximum(lot, hit), ym - 1e-12), np.minimum(ks_m[np.minimum(nk_m - 1, jb + 1)], ym - 1e-12))
                x1 = hi - inv_phi * (hi - lo)
                x2 = lo + inv_phi * (hi - lo)
                _, u1 = solve_L(Av, ks_m, x1)
                _, u2 = solve_L(Av, ks_m, x2)
                f1 = u1 + bv * interp(EV, x1)
                f2 = u2 + bv * interp(EV, x2)
                for _g in range(10):
                    mr = f1 < f2
                    lo = np.where(mr, x1, lo)
                    hi = np.where(mr, hi, x2)
                    x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
                    x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
                    _, u1n = solve_L(Av, ks_m, x1n)
                    _, u2n = solve_L(Av, ks_m, x2n)
                    f1n = np.where(mr, f2, u1n + bv * interp(EV, x1n))
                    f2n = np.where(mr, u2n + bv * interp(EV, x2n), f1)
                    x1, x2, f1, f2 = x1n, x2n, f1n, f2n
                pol_int = np.where(f1 > f2, x1, x2)
                _, up_int = solve_L(Av, ks_m, pol_int)
                val_int = up_int + bv * interp(EV, pol_int)
                # Dedicated concave L=0 corner search (prevents bimodal valley jump near k~30..40)
                jb0 = np.argmax(uM0 + bv * EV[None, :], axis=1)
                lo0 = ks_m[np.maximum(0, jb0 - 1)]
                hi0 = np.maximum(lo0, np.minimum(ks_m[np.minimum(nk_m - 1, jb0 + 1)], pre["qv"] * ks_m - 1e-12))
                z1 = hi0 - inv_phi * (hi0 - lo0)
                z2 = lo0 + inv_phi * (hi0 - lo0)
                g1 = get_u(Av, ks_m, 0.0, z1) + bv * interp(EV, z1)
                g2 = get_u(Av, ks_m, 0.0, z2) + bv * interp(EV, z2)
                for _g0 in range(10):
                    mr0 = g1 < g2
                    lo0 = np.where(mr0, z1, lo0)
                    hi0 = np.where(mr0, hi0, z2)
                    z1n = np.where(mr0, z2, hi0 - inv_phi * (hi0 - lo0))
                    z2n = np.where(mr0, lo0 + inv_phi * (hi0 - lo0), z1)
                    g1n = np.where(mr0, g2, get_u(Av, ks_m, 0.0, z1n) + bv * interp(EV, z1n))
                    g2n = np.where(mr0, get_u(Av, ks_m, 0.0, z2n) + bv * interp(EV, z2n), g1)
                    z1, z2, g1, g2 = z1n, z2n, g1n, g2n
                pol0 = np.where(g1 > g2, z1, z2)
                up0 = get_u(Av, ks_m, 0.0, pol0)
                use0 = (up0 + bv * interp(EV, pol0)) > val_int
                pols.append(np.where(use0, pol0, pol_int))
                ups.append(np.where(use0, up0, up_int))
            polG, polB = pols
            upG, upB = ups
            VGe, VBe = VG.copy(), VB.copy()
            for _h in range(180):
                EVGe = (1.0 - p) * VGe + p * VBe
                EVBe = r_rec * VGe + (1.0 - r_rec) * VBe
                VGn = upG + bv * interp(EVGe, polG)
                VBn = upB + bv * interp(EVBe, polB)
                if max(np.max(np.abs(VGn - VGe)), np.max(np.abs(VBn - VBe))) < 1e-9:
                    VGe, VBe = VGn, VBn
                    break
                VGe, VBe = VGn, VBn
            if max(np.max(np.abs(VGe - VG)), np.max(np.abs(VBe - VB))) < tol_out:
                VG, VB = VGe, VBe
                break
            VG, VB = VGe, VBe
        if return_pol:
            return VG, VB, polG, polB
        if not return_ongrid_W:
            return VG, VB
        # Exact feasible stationary on-grid policy evaluation (zero off-grid interpolation)
        EVG = (1.0 - p) * VG + p * VB
        EVB = r_rec * VG + (1.0 - r_rec) * VB
        jbG = np.argmax(pre["uG"] + bv * EVG[None, :], axis=1)
        jbB = np.argmax(pre["uB"] + bv * EVB[None, :], axis=1)
        u_onG = pre["uG"][np.arange(nk_m), jbG].copy()
        u_onB = pre["uB"][np.arange(nk_m), jbB].copy()
        assert np.all(u_onG[1:] > -1e8) and np.all(u_onB[1:] > -1e8)
        # Verify staging/anchor states [0.05, inf) stay >= ks_m[1] on-grid
        idx_05 = int(np.searchsorted(ks_m, 0.05))
        assert np.min(jbG[idx_05:]) >= 1 and np.min(jbB[idx_05:]) >= 1
        # Feasible geometric lower-tail fallback at row 0 (for completeness on unreached k=1e-8)
        u0_tail = float(box_worst_u((1.0 - bv) * pre["qv"] * ks_m[0], 0.0)) + bv * s_lo_tail * np.log(bv * pre["qv"])
        if u_onG[0] <= -1e8:
            jbG[0] = 0
            u_onG[0] = u0_tail
        if u_onB[0] <= -1e8:
            jbB[0] = 0
            u_onB[0] = u0_tail
        WG, WB = VG.copy(), VB.copy()
        for _ in range(1500):
            EVGw = (1.0 - p) * WG + p * WB
            EVBw = r_rec * WG + (1.0 - r_rec) * WB
            WGn = u_onG + bv * EVGw[jbG]
            WBn = u_onB + bv * EVBw[jbB]
            if max(np.max(np.abs(WGn - WG)), np.max(np.abs(WBn - WB))) < 1e-10:
                WG, WB = WGn, WBn
                break
            WG, WB = WGn, WBn
        return VG, VB, WG, WB

    def certify_logpwl_sens(Av, V_self, EV, bv, tol=1.5e-3, q_hi=Q_MAX, s_tail_arg=None, d_hi_arg=None, eL=ETA_MIN, eU=ETA_MAX):
        """Continuously certify log-PWL super-barrier on all (0, inf) via:
           (0, ks_m[0]]: exact contraction tail (needs s_tail <= eL/(1-bv), Y(x_lo, 1)/x_lo < 1),
           [ks_m[0], 90.0]: sensitivity-guided 3D interval B&B over log-PWL extended above 60 by D_hi,
           [90.0, inf): exact 3-regime analytical upper tail (needs D_hi >= eU/(1-bv)).
        """
        s_tail = eL / (1.0 - bv) if s_tail_arg is None else float(s_tail_arg)
        D_hi = eU / (1.0 - bv) if d_hi_arg is None else float(d_hi_arg)
        assert s_tail <= eL / (1.0 - bv) + 1e-12 and D_hi >= eU / (1.0 - bv) - 1e-12
        x_cut = float(ks_m[-1])
        tail_knots = np.array([68.0, 78.0, 90.0])
        ks_ext = np.concatenate([ks_m, tail_knots])
        lks_ext = np.log(ks_ext)
        nk_ext = len(ks_ext)
        V_self_ext = np.concatenate([V_self, V_self[-1] + D_hi * np.log(tail_knots / x_cut)])
        EV_ext = np.concatenate([EV, EV[-1] + D_hi * np.log(tail_knots / x_cut)])

        dlk = np.diff(lks_ext)
        s_self = np.diff(V_self_ext) / dlk
        s_EV = np.diff(EV_ext) / dlk
        assert np.all(s_self >= 0.0) and np.all(s_EV >= 0.0), "Monotonicity required for deriv_bounds"
        smin_self, smax_self = _build_slope_tables(s_self)
        smin_EV, smax_EV = _build_slope_tables(s_EV)

        def eval_V(V_arr, k_arr):
            lk = np.log(np.maximum(k_arr, 1e-30))
            r = np.interp(np.clip(lk, lks_ext[0], lks_ext[-1]), lks_ext, V_arr)
            r = np.where(k_arr < ks_ext[0], V_arr[0] + s_tail * (lk - lks_ext[0]), r)
            return np.where(k_arr > ks_ext[-1], V_arr[-1] + D_hi * (lk - lks_ext[-1]), r)

        def deriv_bounds(smin_tbl, smax_tbl, kL, kR):
            iL = np.clip(np.searchsorted(ks_ext, kL, side="right") - 1, 0, nk_ext - 2)
            iR = np.maximum(iL, np.clip(np.searchsorted(ks_ext, kR, side="left") - 1, 0, nk_ext - 2))
            lo_s, hi_s = smin_tbl[iL, iR], smax_tbl[iL, iR]
            below = kL < ks_ext[0]
            above = kR > ks_ext[-1]
            lo_s = np.where(above, np.minimum(lo_s, D_hi), lo_s)
            hi_s = np.where(above, np.maximum(hi_s, D_hi), hi_s)
            return (
                np.where(below, np.minimum(lo_s, s_tail), lo_s) / kR,
                np.where(below, np.maximum(hi_s, s_tail), hi_s) / kL,
            )

        # 1) Analytical lower tail (0, ks_m[0]] (since s_tail <= eL/(1-bv), coeff(log x) >= 0 -> max at x = ks_m[0])
        r_top = q_hi + F_A(Av, ks_m[0], 1.0) / ks_m[0]
        assert r_top < 1.0, f"Lower tail contraction failed: {r_top} >= 1.0"
        c_slo = eL + bv * s_tail
        s_lo_opt = (bv * s_tail) / c_slo
        tail_lo_val = float(
            eL * np.log((1.0 - s_lo_opt) * ks_m[0])
            + bv * s_tail * np.log(s_lo_opt)
            + c_slo * np.log(r_top)
            + bv * EV[0]
            - V_self[0]
        )

        # 2) Analytical upper tail [x_end=90.0, inf) across all y in (0, inf)
        x_end = float(ks_ext[-1])
        F_inf = Av * (2.0 ** 1.5)
        Y_end = q_hi * x_end + F_inf
        assert Y_end < x_end
        # y in (0, 1.0]: decreasing in x for all x >= x_end since eU < D_hi
        V1 = float(np.interp(np.log(1.0), lks_m, EV))
        tail_hi_lt1 = float(eU * np.log(Y_end) + bv * V1 - V_self_ext[-1])
        # y in [1.0, x_cut]: exact continuous concave slope lower bound sl_min = min_{[1, x_cut]} d(EV)/dy
        idx1 = max(0, int(np.searchsorted(ks_m, 1.0)) - 1)
        sl_min = float(np.min((np.diff(EV[idx1:]) / np.diff(lks_m[idx1:])) / ks_m[idx1 + 1:]))
        assert sl_min > 0.0 and np.all(EV[idx1:] <= EV[-1] - sl_min * (x_cut - ks_m[idx1:]) + 1e-12)
        c_star = eU / (bv * sl_min)
        x_cross = (x_cut + c_star - F_inf) / q_hi
        x_peak = D_hi * max(x_cut - F_inf, 1.0) / ((D_hi - eU) * q_hi)
        cand_x = [v for v in (x_end, x_cross, x_peak, 2.0 * x_end, 1e6) if v >= x_end]
        tail_hi_mid = -1e9
        for xv in cand_x:
            Ytv = q_hi * xv + F_inf
            c_op = max(c_star, Ytv - x_cut)
            val_m = eU * np.log(c_op) + bv * (EV[-1] + sl_min * (Ytv - c_op - x_cut)) - (V_self[-1] + D_hi * np.log(xv / x_cut))
            tail_hi_mid = max(tail_hi_mid, float(val_m))
        # y > x_cut: coeff(log x) = eU + bv*D_hi - D_hi <= 0 => bounded by x = x_end
        c_dhi = eU + bv * D_hi
        s_hi_opt = (bv * D_hi) / c_dhi
        tail_hi_log = float(
            eU * np.log(1.0 - s_hi_opt)
            + bv * D_hi * np.log(s_hi_opt)
            + c_dhi * np.log(Y_end / x_end)
            + eU * np.log(x_end)
            + (bv * D_hi - D_hi) * np.log(x_end / x_cut)
            + bv * EV[-1]
            - V_self[-1]
        )
        tail_hi_val = max(tail_hi_lt1, tail_hi_mid, tail_hi_log)
        assert tail_hi_val < 0.0, f"Upper tail [90, inf) not negative: lt1={tail_hi_lt1:.4f}, mid={tail_hi_mid:.4f}, log={tail_hi_log:.4f}"

        # 3) Tight lower bound on [ks_m[0], 90.0] (grid + knot-midpoint seeding)
        xg = np.geomspace(ks_m[0], x_end, 48)
        Lg = np.concatenate([[0.0], np.geomspace(1e-5, 0.999, 22)])
        sg = np.linspace(0.05, 0.998, 22)
        Y_g = q_hi * xg[:, None] + F_A(Av, xg[:, None], Lg[None, :])
        c_g = Y_g[:, :, None] * (1.0 - sg[None, None, :])
        y_g = Y_g[:, :, None] * sg[None, None, :]
        ec_g = np.where(c_g < 1.0, eL, eU)
        val_g = ec_g * np.log(c_g) + (1.0 - eU) * np.log(1.0 - Lg[None, :, None]) + bv * eval_V(EV_ext, y_g) - eval_V(V_self_ext, xg[:, None, None])
        xm_s = np.sqrt(ks_m[:-1] * ks_m[1:])[:, None, None]
        Lm_s = np.array([0.0, 0.37, 0.50, 0.62, 0.72, 0.85])[None, :, None]
        sm_s = np.array([0.82, 0.90, 0.955, 0.985, 0.9979])[None, None, :]
        Ym_s = q_hi * xm_s + F_A(Av, xm_s, Lm_s)
        cm_s = Ym_s * (1.0 - sm_s)
        ecm_s = np.where(cm_s < 1.0, eL, eU)
        val_ms = ecm_s * np.log(cm_s) + (1.0 - eU) * np.log(1.0 - Lm_s) + bv * eval_V(EV_ext, Ym_s * sm_s) - eval_V(V_self_ext, xm_s)
        best_lb = max(tail_lo_val, tail_hi_val, float(np.max(val_g)), float(np.max(val_ms)))
        target = best_lb + tol

        xs_b = np.concatenate([ks_m[::10], [x_cut, 68.0, 78.0, 90.0]])
        xs_b = np.unique(xs_b)
        Ls_b = np.concatenate([[0.0, 0.2, 0.5, 0.7], np.linspace(0.8, 0.99, 6, endpoint=False), [0.99, 0.999, 1.0]])
        ss_b = np.concatenate([[0.0, 0.3, 0.65], np.linspace(0.75, 0.99, 8, endpoint=False), [0.99, 0.996, 0.998, 0.999, 1.0]])
        gxL, gLL, gsL = np.meshgrid(xs_b[:-1], Ls_b[:-1], ss_b[:-1], indexing="ij")
        gxR, gLR, gsR = np.meshgrid(xs_b[1:], Ls_b[1:], ss_b[1:], indexing="ij")
        bxL, bxR, bLL, bLR, bsL, bsR = gxL.ravel(), gxR.ravel(), gLL.ravel(), gLR.ravel(), gsL.ravel(), gsR.ravel()

        for _ in range(60):
            Y_min = q_hi * bxL + F_A(Av, bxL, bLL)
            Y_max = q_hi * bxR + F_A(Av, bxR, bLR)
            c_max = np.maximum((1.0 - bsL) * Y_max, 1e-300)
            ec_max = np.where(c_max < 1.0, eL, eU)
            ub_mono = (
                np.where(bsL >= 1.0, -1e9, ec_max * np.log(c_max))
                + (1.0 - eU) * np.log(np.maximum(1.0 - bLL, 1e-300))
                + np.where(bsR <= 0.0, -1e9, bv * eval_V(EV_ext, bsR * Y_max))
                - eval_V(V_self_ext, bxL)
            )
            xm, Lm, sm = 0.5 * (bxL + bxR), 0.5 * (bLL + bLR), 0.5 * (bsL + bsR)
            hx, hL, hs = 0.5 * (bxR - bxL), 0.5 * (bLR - bLL), 0.5 * (bsR - bsL)
            Ym = q_hi * xm + F_A(Av, xm, Lm)
            cm = (1.0 - sm) * Ym
            c_min = np.maximum((1.0 - bsR) * Y_min, 1e-300)
            valid_c = (ub_mono > target) & (bLR < 1.0) & (bsL > 0.0) & (bsR < 1.0) & (c_min > 1e-12)
            ub_cent = np.full_like(ub_mono, 1e9)
            ex, eL_err, es = (bxR - bxL) / bxL, hL, hs
            if np.any(valid_c):
                xLv, xRv, LLv, LRv, sLv, sRv = bxL[valid_c], bxR[valid_c], bLL[valid_c], bLR[valid_c], bsL[valid_c], bsR[valid_c]
                xmv, Lmv, smv = xm[valid_c], Lm[valid_c], sm[valid_c]
                hxv, hLv, hsv = hx[valid_c], hL[valid_c], hs[valid_c]
                Y_min_v, Y_max_v, Ymv = Y_min[valid_c], Y_max[valid_c], Ym[valid_c]
                y_min_v, y_max_v = sLv * Y_min_v, sRv * Y_max_v
                px_hi = np.clip(LRv / 4.0, xLv, xRv)
                Yx_lo = q_hi + np.minimum(dF_dK(Av, xLv, LLv), dF_dK(Av, xRv, LLv))
                Yx_hi = q_hi + np.maximum(np.maximum(dF_dK(Av, xLv, LRv), dF_dK(Av, xRv, LRv)), dF_dK(Av, px_hi, LRv))
                pL_hi = np.clip(xRv / 4.0, LLv, LRv)
                YL_lo = np.minimum(dF_dL(Av, xLv, LLv), dF_dL(Av, xLv, LRv))
                YL_hi = np.maximum(np.maximum(dF_dL(Av, xRv, LLv), dF_dL(Av, xRv, LRv)), dF_dL(Av, xRv, pL_hi))
                fp_y_lo, fp_y_hi = deriv_bounds(smin_EV, smax_EV, y_min_v, y_max_v)
                fp_x_lo, fp_x_hi = deriv_bounds(smin_self, smax_self, xLv, xRv)
                cross_c1 = (c_min[valid_c] < 1.0) & (c_max[valid_c] >= 1.0)
                best_eta_ub = np.full(np.sum(valid_c), -1e9)
                err_x_v = np.zeros(np.sum(valid_c))
                err_L_v = np.zeros(np.sum(valid_c))
                err_s_v = np.zeros(np.sum(valid_c))
                for ec in (eL, eU):
                    mask_ec = (c_min[valid_c] < 1.0) if ec == eL else (c_max[valid_c] >= 1.0)
                    ec_lo = np.where(cross_c1, eL, ec)
                    ec_hi = np.where(cross_c1, eU, ec)
                    hm = ec * np.log(cm[valid_c]) + (1.0 - eU) * np.log(1.0 - Lmv) + bv * eval_V(EV_ext, smv * Ymv) - eval_V(V_self_ext, xmv)
                    A_lo = ec_lo / Y_max_v + bv * sLv * fp_y_lo
                    A_hi_b = ec_hi / Y_min_v + bv * sRv * fp_y_hi
                    sx = np.maximum(np.abs(A_lo * Yx_lo - fp_x_hi), np.abs(A_hi_b * Yx_hi - fp_x_lo)) * hxv
                    sL = np.maximum(np.abs(A_lo * YL_lo - (1.0 - eU) / (1.0 - LRv)), np.abs(A_hi_b * YL_hi - (1.0 - eU) / (1.0 - LLv))) * hLv
                    ss_e = np.maximum(np.abs(-ec_hi / (1.0 - sRv) + bv * Y_min_v * fp_y_lo), np.abs(-ec_lo / (1.0 - sLv) + bv * Y_max_v * fp_y_hi)) * hsv
                    ub_ec = hm + sx + sL + ss_e
                    best_eta_ub = np.where(mask_ec, np.maximum(best_eta_ub, ub_ec), best_eta_ub)
                    err_x_v = np.where(mask_ec, np.maximum(err_x_v, sx), err_x_v)
                    err_L_v = np.where(mask_ec, np.maximum(err_L_v, sL), err_L_v)
                    err_s_v = np.where(mask_ec, np.maximum(err_s_v, ss_e), err_s_v)
                ub_cent[valid_c] = best_eta_ub
                ex[valid_c], eL_err[valid_c], es[valid_c] = err_x_v, err_L_v, err_s_v
            ub = np.minimum(ub_mono, ub_cent)
            keep = ub > target
            n_keep = int(np.sum(keep))
            if n_keep == 0:
                return float(target), float(best_lb), float(max(tail_lo_val, tail_hi_val))
            bxL, bxR, bLL, bLR, bsL, bsR = bxL[keep], bxR[keep], bLL[keep], bLR[keep], bsL[keep], bsR[keep]
            xm, Lm, sm = xm[keep], Lm[keep], sm[keep]
            ex, eL_err, es = ex[keep], eL_err[keep], es[keep]
            Ym_k = q_hi * xm + F_A(Av, xm, Lm)
            cm_k = (1.0 - sm) * Ym_k
            ecm_k = np.where(cm_k < 1.0, eL, eU)
            lb_k = np.where(
                (Lm < 1.0) & (sm > 0.0) & (sm < 1.0),
                ecm_k * np.log(np.maximum(cm_k, 1e-300)) + (1.0 - eU) * np.log(np.maximum(1.0 - Lm, 1e-300)) + bv * eval_V(EV_ext, sm * Ym_k) - eval_V(V_self_ext, xm),
                -1e9,
            )
            if np.max(lb_k) > best_lb:
                best_lb = float(np.max(lb_k))
                target = best_lb + tol
            if n_keep <= 1000:
                nxL = np.concatenate([bxL, xm, bxL, xm, bxL, xm, bxL, xm])
                nxR = np.concatenate([xm, bxR, xm, bxR, xm, bxR, xm, bxR])
                nLL = np.concatenate([bLL, bLL, Lm, Lm, bLL, bLL, Lm, Lm])
                nLR = np.concatenate([Lm, Lm, bLR, bLR, Lm, Lm, bLR, bLR])
                nsL = np.concatenate([bsL, bsL, bsL, bsL, sm, sm, sm, sm])
                nsR = np.concatenate([sm, sm, sm, sm, bsR, bsR, bsR, bsR])
                bxL, bxR, bLL, bLR, bsL, bsR = nxL, nxR, nLL, nLR, nsL, nsR
            else:
                m1 = (ex >= eL_err) & (ex >= es)
                m2 = (~m1) & (eL_err >= es)
                m3 = (~m1) & (~m2)
                axL, axR, aLL, aLR, asL, asR = bxL.copy(), bxR.copy(), bLL.copy(), bLR.copy(), bsL.copy(), bsR.copy()
                bxLc, bxRc, bLLc, bLRc, bsLc, bsRc = bxL.copy(), bxR.copy(), bLL.copy(), bLR.copy(), bsL.copy(), bsR.copy()
                axR[m1] = xm[m1]; bxLc[m1] = xm[m1]
                aLR[m2] = Lm[m2]; bLLc[m2] = Lm[m2]
                asR[m3] = sm[m3]; bsLc[m3] = sm[m3]
                bxL = np.concatenate([axL, bxLc]); bxR = np.concatenate([axR, bxRc])
                bLL = np.concatenate([aLL, bLLc]); bLR = np.concatenate([aLR, bLRc])
                bsL = np.concatenate([asL, bsLc]); bsR = np.concatenate([asR, bsRc])
        raise AssertionError("certify_logpwl_sens B&B did not converge within 60 iterations")

    pre_up = precompute_markov_pwl(A_MAX, AB_MAX, Q_MAX, True)
    pre_lo = precompute_markov_pwl(A_MIN, AB_MIN, Q_MIN, False)

    # 5A. Endogenous Doob Certificate T*(p) under Ruin/Expropriation Hazard p (effective beta_eff = beta*(1-p))
    eM_exit = E_plus_exact(A_MAX, Q_MAX, B_M, B_M, 0.44)
    eH_exit = E_plus_exact(A_MAX, Q_MAX, H_M, H_M, 0.57)
    psi_shapes = {0.0: (0.45, 5.0), 0.005: (0.40, 5.0), 0.010: (0.35, 5.0), 0.015: (0.40, 4.8), 0.020: (0.35, 4.8)}
    # Note: -b_p*x^(-1/2) violates T Psi <= Psi on (0, 0.0014) for p > p_sing = 1.1217% (and degrades at 0.5%, 1.0%);
    # continuous log-PWL super-barrier covers ALL (0, inf) cleanly for every p in [0%, 2%].
    x_lo_5A = {0.0: 8e-5}
    p_sing = 1.0 - (Q_MAX ** 0.5) / BETA_MAX
    phi_loc = np.clip((np.log(0.060) - lks_m) / np.log(0.060 / 0.012), 0.0, 1.0)

    # U4: Patience breakdown p_pat vs finite-A certification limit p_cert
    p_pat_mid = 1.0 - 1.0 / (beta * (q + theta * delta))
    p_pat_box = 1.0 - 1.0 / (BETA_MIN * (Q_MAX + theta * (1.0 - Q_MAX)))
    kap_075 = exact_kappa(A_G, delta)
    qF_kap = q + dF_dK(A_G, kap_075, 1.0)
    qF_M = [q + dF_dK(A_G, K, 0.68) for K in (0.10, 0.20, 0.28)]
    print(f"  [U4] p_pat (mid) = {100*p_pat_mid:.4f}% (box {100*p_pat_box:.4f}%), q+F_K(kappa)={qF_kap:.4f} vs q+F_K(M) in [{min(qF_M):.3f}, {max(qF_M):.3f}]")
    print(f"       x^(-1/2) barrier lower-tail singularity limit: p_sing = 1 - sqrt(q+)/beta+ = {100*p_sing:.4f}%")
    assert abs(p_pat_mid - 0.008723) < 1e-5 and abs(p_pat_box - 0.008573) < 1e-5
    assert abs(p_sing - 0.011217) < 1e-5

    def min_c_E_plus(Av, qv, K, a, l0):
        t = dF_dL(Av, K, l0)
        c_sup = qv * K + F_A(Av, K, l0) + (1.0 - l0) * t - a
        return min(c_sup - t * min(1.0, (1.0 - eta_v) * c_sup / t) for eta_v in (ETA_MIN, ETA_MAX))

    def min_deriv_0_b(psi_arr, s_lo_val):
        idx_b = int(np.searchsorted(ks_m, B_M, side="left"))
        seg_d = (np.diff(psi_arr[:idx_b + 1]) / np.diff(lks_m[:idx_b + 1])) / ks_m[1:idx_b + 1]
        return float(min(s_lo_val / ks_m[0], np.min(seg_d)))

    print("\n  [5A] Endogenous Doob Stochastic Affine Barrier Certificate T*(p) (box-uniform Psi^(p) + continuous <b check):")
    T_prev = 0
    appendix_5A = []
    eta_max_c_M_5A = ETA_MAX / min_c_E_plus(A_MIN, Q_MIN, B_M, B_M, 0.44)
    for p in [0.0, 0.005, 0.010, 0.015, 0.020]:
        b_min = BETA_MIN * (1.0 - p)
        b_max = BETA_MAX * (1.0 - p)
        # All stage payoffs r_t < 0 => worst-case discounted witness uses b_max!
        WM, trajM, rsM = eval_witness(b_max, B_M, b_solve=b_max, eta_mode="outer")
        WH, _, _ = eval_witness(b_max, H_M, b_solve=b_max, eta_mode="outer")
        # 1) Box-uniform continuous parametric Psi^(0) at p = 0% (certified at BOTH BETA_MIN and BETA_MAX)
        if p in x_lo_5A:
            a_c, b_c = psi_shapes[p]
            c_par_hi, d_ub_par, d_lb_par, tail_m_par = certify_psi_centered(A_MAX, b_max, a_c, b_c, x_lo=x_lo_5A[p], tol=2e-4, buffer=0.0005)
            c_par_lo, _, _, _ = certify_psi_centered(A_MAX, b_min, a_c, b_c, x_lo=x_lo_5A[p], tol=2e-4, buffer=0.0005)
            c_p_par = max(c_par_hi, c_par_lo)
            psi28_par = a_c * H_M - b_c * (H_M ** -0.5) + c_p_par
        else:
            c_p_par = d_ub_par = d_lb_par = tail_m_par = psi28_par = None
        # 2) Box-uniform continuously certified log-PWL Psi^(p) on ALL (0, inf): solve at b_min, certify at BOTH b_min & b_max
        s_lo_u = ETA_MIN / (1.0 - b_min)
        d_hi_u = ETA_MAX / (1.0 - b_max)
        Vp_1, _ = solve_markov_pwl(pre_up, b_min, 0.0)
        Vp_1 = Vp_1 + (0.030 / (1.0 - b_min)) * phi_loc
        dp_ub_lo, _, tail_lo_u = certify_logpwl_sens(A_MAX, Vp_1, Vp_1, b_min, tol=4e-4, s_tail_arg=s_lo_u, d_hi_arg=d_hi_u)
        dp_ub_hi, _, tail_hi_u = certify_logpwl_sens(A_MAX, Vp_1, Vp_1, b_max, tol=4e-4, s_tail_arg=s_lo_u, d_hi_arg=d_hi_u)
        c_pwl = max((dp_ub_lo + 0.0002) / (1.0 - b_min), (dp_ub_hi + 0.0002) / (1.0 - b_max))
        tailp_val = max(tail_lo_u, tail_hi_u)
        psi_10 = float(np.interp(np.log(B_M), lks_m, Vp_1)) + c_pwl
        psi_28 = float(np.interp(np.log(H_M), lks_m, Vp_1)) + c_pwl

        # Verify continuous < b down-exit derivative condition + continuous mExitM over M=[0.10, 0.28)
        min_dPsi_5A = min_deriv_0_b(Vp_1, s_lo_u)
        assert b_min * min_dPsi_5A > eta_max_c_M_5A, f"5A <b slope failed: {b_min * min_dPsi_5A:.2f} <= {eta_max_c_M_5A:.2f}"
        _, L0_w, k1_w = trajM[0]
        tail_after_0 = WM - rsM[0]
        Ks_M_int = np.linspace(B_M, H_M, 51)
        mExitM_cont = min(
            float(box_worst_u(Q_MIN * Ks_M_int[j] + F_A(A_MIN, Ks_M_int[j], L0_w) - k1_w, L0_w))
            + tail_after_0
            - (E_plus_exact(A_MAX, Q_MAX, Ks_M_int[j + 1], B_M, 0.44) + b_min * psi_10)
            for j in range(50)
        )
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
        par_str = (
            f"param[T={int(np.ceil(np.log(marg_stay / (psi28_par - B_star_p)) / np.log(b_max)))}]"
            if psi28_par is not None else "param[N/A: tail-limited]"
        )
        print(
            f"    p={100*p:4.2f}% | b_eff=[{b_min:.4f},{b_max:.4f}] | B1(0.10)={B1_b_p:7.3f} | stay={marg_stay:5.3f} | "
            f"exitM={mExitM:+.3f}(cont {mExitM_cont:+.3f}), exitH={mExitH:+.3f} | T*(p)={T_star:2d} ({par_str}) | P_Doob={P_doob:.4f} (vs {P_naive:.4f})"
        )
        assert marg_stay > 0.0 and mExitM > 0.0 and mExitM_cont > 0.0 and mExitH > 0.0
        assert T_star >= T_prev
        T_prev = T_star
        appendix_5A.append((p, c_p_par, d_lb_par, d_ub_par, tail_m_par, c_pwl, psi_10, psi_28, tailp_val, WM, WH, trajM, rsM))

    # Exact certification breakdown threshold p_cert where staying margin crosses 0 (using b_max!)
    def stay_gap_fn(p_v):
        b_min = BETA_MIN * (1.0 - p_v)
        b_max = BETA_MAX * (1.0 - p_v)
        WM, _, _ = eval_witness(b_max, B_M, b_solve=b_max, eta_mode="outer")
        D2_p = (ETA_MIN * b_min * Q_MIN * (H_M - B_M)) / C_max
        B1_b_p = (R_hat - D2_p) / (1.0 - b_min) - (ETA_MIN * Q_MIN / C_max) * (H_M - B_M)
        return WM - B1_b_p

    p_cert = brentq(stay_gap_fn, 0.015, 0.025, xtol=1e-5)
    print(f"    Certification breakdown limit (1-step affine barrier, b_max witness): p_cert = {100*p_cert:.4f}%")
    assert abs(p_cert - 0.020434) < 0.0005

    # 5B. Coupled 2-State Markov Bellman Barrier System (Omega = {G, B}, A_G=0.75 <-> A_B=0.35, r_rec=1/3)
    print("\n  [5B] Coupled 2-State Markov Barrier (B_G, B_B) & Continuous Log-PWL Certificate:")
    # Verify tau >= 3 from x0 = 0.10 under (A_+, q_+) and y_max = q_+ h + F_{A_+}(h, 1)
    K1_up = Q_MAX * B_M + F_A(A_MAX, B_M, 1.0)
    K2_up = Q_MAX * K1_up + F_A(A_MAX, K1_up, 1.0)
    K3_up = Q_MAX * K2_up + F_A(A_MAX, K2_up, 1.0)
    y_max_exit = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0)
    print(f"    tau >= 3 check from x0=0.10: K1={K1_up:.6f} < K2={K2_up:.6f} < 0.28 < K3={K3_up:.6f}, y_max={y_max_exit:.6f}")
    assert K1_up < H_M and K2_up < H_M and K3_up >= H_M

    # Verify impossibility of standard (a_G, b_G, a_B, b_B) family for mExitMB >= 0 (at p=0%)
    xs_imp = np.geomspace(0.0014, 45.0, 50)
    Ls_imp = np.linspace(0.05, 0.995, 25)
    ss_imp = np.linspace(0.10, 0.995, 25)
    f_std = lambda k: 0.40 * k - 5.0 * (k ** -0.5)
    dG_std = max(
        float(np.max((np.where(c < 1, ETA_MIN, ETA_MAX) * np.log(c)) + (1 - ETA_MAX) * np.log(1 - Ls_imp[:, None]) + BETA_MAX * f_std(y) - f_std(x)))
        for x in xs_imp
        for Y in [Q_MAX * x + F_A(A_MAX, x, Ls_imp)]
        for c, y in [(Y[:, None] * (1 - ss_imp[None, :]), Y[:, None] * ss_imp[None, :])]
    )
    Psi_std_B10 = f_std(B_M) + dG_std / (1.0 - BETA_MAX)
    assert Psi_std_B10 > -36.0, "Standard a*x - b*x^-0.5 family cannot approach V_B(0.10) ~ -40.5"

    Ls_B = np.linspace(0.01, 0.9999, 1500)
    cs_B = Q_MAX * H_M + F_A(AB_MAX, H_M, Ls_B) - B_M
    R_hat_B = float(np.max(np.where(cs_B < 1.0, ETA_MIN, ETA_MAX) * np.log(cs_B) + (1.0 - ETA_MAX) * np.log(1.0 - Ls_B)))
    C_max_B = float(Q_MAX * H_M + F_A(AB_MAX, H_M, 1.0) - B_M)
    m_G = (ETA_MIN * Q_MIN) / C_max
    m_B = (ETA_MIN * Q_MIN) / C_max_B

    eMG_exit = E_plus_exact(A_MAX, Q_MAX, B_M, B_M, 0.44)
    eMB_exit = E_plus_exact(AB_MAX, Q_MAX, B_M, B_M, 0.478)
    eHG_exit = E_plus_exact(A_MAX, Q_MAX, H_M, H_M, 0.57)

    # Precompute cached single-state tables for 4x2x2x2 (=32 sub-boxes of (A_G, A_B, q, eta)) Box(7.3) cover of mExitHB
    aG_pts = np.linspace(A_MIN, A_MAX, 5)
    aB_pts = np.linspace(AB_MIN, AB_MAX, 3)
    q_pts = np.linspace(Q_MIN, Q_MAX, 3)
    e_pts = np.linspace(ETA_MIN, ETA_MAX, 3)
    cache_G = {(av, qv, ie, iu): precompute_state_pwl(av, qv, iu, e_pts[ie], e_pts[ie + 1]) for ie in range(2) for iu in (False, True) for qv in q_pts for av in aG_pts}
    cache_B = {(bv, qv, ie, iu): precompute_state_pwl(bv, qv, iu, e_pts[ie], e_pts[ie + 1]) for ie in range(2) for iu in (False, True) for qv in q_pts for bv in aB_pts}

    def pack_pre(ag, ab, qv, ie, iu):
        sG = cache_G[(ag, qv, ie, iu)]
        sB = cache_B[(ab, qv, ie, iu)]
        return dict(
            AG=ag, AB=ab, qv=qv, is_upper=iu,
            uG=sG["u"], uG0=sG["u0"], ymG=sG["ym"], kptG=sG["kpt"], utG=sG["ut"],
            uB=sB["u"], uB0=sB["u0"], ymB=sB["ym"], kptB=sB["kpt"], utB=sB["ut"],
            solve_L=sG["solve_L"], get_u=sG["get_u"],
        )

    # High-resolution finite-state feasible Markov policy witness grid (strict superset of ks_m)
    ks_wit = np.unique(np.concatenate([
        ks_m,
        np.geomspace(0.006, 0.05, 220, endpoint=False),
        np.geomspace(0.05, 0.28, 280, endpoint=False),
        np.geomspace(0.28, 1.5, 160, endpoint=False),
    ]))
    lks_wit = np.log(ks_wit)
    n_wit = len(ks_wit)
    idx_w05 = int(np.searchsorted(ks_wit, 0.05))
    iw_lo = int(np.searchsorted(ks_wit, B_M))
    iw_hi = int(np.searchsorted(ks_wit, H_M))
    assert ks_wit[iw_lo] == B_M and ks_wit[iw_hi] == H_M

    def solve_L_wit(Av, qv, eL, eU, ka, kpa):
        def uf(La):
            cv = qv * ka + F_A(Av, ka, La) - kpa
            lc = np.log(np.maximum(cv, 1e-30))
            ll = np.log(1.0 - La)
            return np.where(cv > 1e-15, np.minimum(eL * lc + (1.0 - eL) * ll, eU * lc + (1.0 - eU) * ll), -1e9 + cv)

        u0 = uf(np.zeros_like(ka))
        lo = np.full_like(ka, 1e-7)
        hi = np.full_like(ka, 1.0 - 1e-9)
        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        f1, f2 = uf(x1), uf(x2)
        for _ in range(18):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            f1n = np.where(mr, f2, uf(x1n))
            f2n = np.where(mr, uf(x2n), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        Lb = 0.5 * (lo + hi)
        ub = uf(Lb)
        return np.where(u0 > ub, 0.0, Lb), np.maximum(u0, ub)

    def eval_wit_chain(AG_v, AB_v, qv, eL, eU, bv, p, VG_ref, VB_ref, polG_ref, polB_ref, n_sw=6, half_w=5):
        WG = np.interp(lks_wit, lks_m, VG_ref)
        WB = np.interp(lks_wit, lks_m, VB_ref)
        pG_w = np.exp(np.interp(lks_wit, lks_m, np.log(np.maximum(polG_ref, 1e-30))))
        pB_w = np.exp(np.interp(lks_wit, lks_m, np.log(np.maximum(polB_ref, 1e-30))))
        jbG = np.clip(np.searchsorted(ks_wit, pG_w), 0, n_wit - 1)
        jbB = np.clip(np.searchsorted(ks_wit, pB_w), 0, n_wit - 1)
        offs = np.arange(-half_w, half_w + 1)[None, :]
        c0_t = (1.0 - bv) * qv * ks_wit[0]
        u0_t = min(ev * np.log(c0_t) for ev in (eL, eU)) + bv * (eU / (1.0 - bv)) * np.log(bv * qv)
        for _sw in range(n_sw):
            EVG = (1.0 - p) * WG + p * WB
            EVB = r_rec * WG + (1.0 - r_rec) * WB
            cG = np.clip(jbG[:, None] + offs, 0, n_wit - 1)
            cB = np.clip(jbB[:, None] + offs, 0, n_wit - 1)
            _, uGm = solve_L_wit(AG_v, qv, eL, eU, np.broadcast_to(ks_wit[:, None], cG.shape), ks_wit[cG])
            _, uBm = solve_L_wit(AB_v, qv, eL, eU, np.broadcast_to(ks_wit[:, None], cB.shape), ks_wit[cB])
            bG = np.argmax(uGm + bv * EVG[cG], axis=1)
            bB = np.argmax(uBm + bv * EVB[cB], axis=1)
            jbG = cG[np.arange(n_wit), bG]
            uG_on = uGm[np.arange(n_wit), bG]
            jbB = cB[np.arange(n_wit), bB]
            uB_on = uBm[np.arange(n_wit), bB]
            if uG_on[0] <= -1e8:
                jbG[0] = 0
                uG_on[0] = u0_t
            if uB_on[0] <= -1e8:
                jbB[0] = 0
                uB_on[0] = u0_t
            conv_w = False
            for _it in range(1500):
                EVGi = (1.0 - p) * WG + p * WB
                EVBi = r_rec * WG + (1.0 - r_rec) * WB
                WGn = uG_on + bv * EVGi[jbG]
                WBn = uB_on + bv * EVBi[jbB]
                if max(np.max(np.abs(WGn - WG)), np.max(np.abs(WBn - WB))) < 1e-11:
                    WG, WB = WGn, WBn
                    conv_w = True
                    break
                WG, WB = WGn, WBn
            assert conv_w
        assert np.min(jbG[idx_w05:]) >= 1 and np.min(jbB[idx_w05:]) >= 1
        assert np.all(uG_on[1:] > -1e8) and np.all(uB_on[1:] > -1e8)
        return WG, WB, jbG, jbB

    bump_5b = (0.030 / (1.0 - BETA_MAX)) * phi_loc
    idx_M_lo = int(np.searchsorted(ks_m, B_M))
    idx_M_hi = int(np.searchsorted(ks_m, H_M))
    assert ks_m[idx_M_lo] == B_M and ks_m[idx_M_hi] == H_M
    eta_max_c_MG = ETA_MAX / min_c_E_plus(A_MIN, Q_MIN, B_M, B_M, 0.44)
    eta_max_c_MB = ETA_MAX / min_c_E_plus(AB_MIN, Q_MIN, B_M, B_M, 0.478)
    print("    (Matched-beta across {BETA_MIN, BETA_MAX}, on-grid feasible witnesses, ALL 32 (4x2x2x2) sub-boxes B&B-certified, continuous M=[0.10,0.28) <b checks)")
    appendix_5B = []
    for p in [0.0, 0.005, 0.01, 0.015, 0.02, 0.05, 0.08, 0.12]:
        P = np.array([[1.0 - p, p], [r_rec, 1.0 - r_rec]])
        m_bar = P @ np.array([m_G, m_B])
        Delta = (H_M - B_M) * np.minimum(np.array([ETA_MIN / C_max, ETA_MIN / C_max_B]), BETA_MIN * m_bar)

        # Evaluate rigorously under matched-beta at BOTH endpoints bv in {BETA_MIN, BETA_MAX}
        worst_res = None
        for bv in (BETA_MIN, BETA_MAX):
            B_star = np.linalg.solve(np.eye(2) - bv * P, np.array([R_hat, R_hat_B]) - Delta)
            B_b = np.array([B_star[0] - m_G * (H_M - B_M), B_star[1] - m_B * (H_M - B_M)])
            s_lo_bv = ETA_MIN / (1.0 - bv)
            bump_bv = (0.030 / (1.0 - bv)) * phi_loc

            VGp, VBp = solve_markov_pwl(pre_up, bv, p)
            VGp = VGp + bump_bv
            VBp = VBp + bump_bv
            EVGp = (1.0 - p) * VGp + p * VBp
            EVBp = r_rec * VGp + (1.0 - r_rec) * VBp
            dG_ub, _, _ = certify_logpwl_sens(A_MAX, VGp, EVGp, bv, tol=2.5e-4)
            dB_ub, _, _ = certify_logpwl_sens(AB_MAX, VBp, EVBp, bv, tol=2.5e-4)
            cG, cB = np.linalg.solve(np.eye(2) - bv * P, np.array([dG_ub + 0.00003, dB_ub + 0.00003]))
            PsiG_arr = VGp + cG
            PsiB_arr = VBp + cB

            # Exact feasible stationary on-grid policy witnesses on ks_wit (zero off-grid interpolation)
            VGm, VBm, pGm, pBm = solve_markov_pwl(pre_lo, bv, p, return_pol=True)
            WG_on, WB_on, _, _ = eval_wit_chain(A_MIN, AB_MIN, Q_MIN, ETA_MIN, ETA_MAX, bv, p, VGm, VBm, pGm, pBm)
            assert np.all(np.diff(WG_on[iw_lo:iw_hi + 1]) >= 0.0) and np.all(np.diff(WB_on[iw_lo:iw_hi + 1]) >= 0.0)
            WG0 = float(np.min(WG_on[ks_wit >= B_M]))
            WB0 = float(np.min(WB_on[ks_wit >= B_M]))
            WGh = float(np.min(WG_on[ks_wit >= H_M]))
            WBh = float(np.min(WB_on[ks_wit >= H_M]))

            PsiGb = float(np.interp(np.log(B_M), lks_m, PsiG_arr))
            PsiBb = float(np.interp(np.log(B_M), lks_m, PsiB_arr))
            PsiGh = float(np.interp(np.log(H_M), lks_m, PsiG_arr))
            PsiBh = float(np.interp(np.log(H_M), lks_m, PsiB_arr))
            PsiG_ym = float(np.interp(np.log(y_max_exit), lks_m, PsiG_arr))
            PsiB_ym = float(np.interp(np.log(y_max_exit), lks_m, PsiB_arr))

            margG = WG0 - B_b[0]
            margB = WB0 - B_b[1]
            max_exit = max(PsiGh - B_star[0], PsiBh - B_star[1])
            T_G = int(np.ceil(np.log(margG / max_exit) / np.log(bv)))
            T_B = int(np.ceil(np.log(margB / max_exit) / np.log(bv)))

            EVGb_p = (1.0 - p) * PsiGb + p * PsiBb
            EVBb_p = r_rec * PsiGb + (1.0 - r_rec) * PsiBb
            EVGh_p = (1.0 - p) * PsiGh + p * PsiBh
            mExitMG = WG0 - (eMG_exit + bv * EVGb_p)
            mExitMB = WB0 - (eMB_exit + bv * EVBb_p)
            mExitHG = WGh - (eHG_exit + bv * EVGh_p)

            # Continuous < b down-exit derivative proof & knot-interval cover on ALL M=[0.10, 0.28)
            min_dEVG_b = min_deriv_0_b(EVGp, s_lo_bv)
            min_dEVB_b = min_deriv_0_b(EVBp, s_lo_bv)
            assert bv * min_dEVG_b > eta_max_c_MG, f"5B-G <b slope failed: {bv * min_dEVG_b:.2f} <= {eta_max_c_MG:.2f}"
            assert bv * min_dEVB_b > eta_max_c_MB, f"5B-B <b slope failed: {bv * min_dEVB_b:.2f} <= {eta_max_c_MB:.2f}"
            min_M_G = min(
                float(WG_on[ii]) - (E_plus_exact(A_MAX, Q_MAX, float(ks_wit[ii + 1]), B_M, 0.44) + bv * EVGb_p)
                for ii in range(iw_lo, iw_hi)
            )
            min_M_B = min(
                float(WB_on[ii]) - (E_plus_exact(AB_MAX, Q_MAX, float(ks_wit[ii + 1]), B_M, 0.478) + bv * EVBb_p)
                for ii in range(iw_lo, iw_hi)
            )

            # Certify ALL 32 sub-boxes of 4x2x2x2 cover via warm-started VFI + exact B&B on EVERY sub-box
            mExitHB_box = 1e9
            init_u = (VGp - bump_bv, VBp - bump_bv)
            for ie in range(2):
                eLs, eUs = e_pts[ie], e_pts[ie + 1]
                for iq in range(2):
                    qL, qU = q_pts[iq], q_pts[iq + 1]
                    for iG in range(4):
                        GL, GU = aG_pts[iG], aG_pts[iG + 1]
                        for iB in range(2):
                            BL, BU = aB_pts[iB], aB_pts[iB + 1]
                            _, WB_l, _, _ = eval_wit_chain(GL, BL, qL, eLs, eUs, bv, p, VGm, VBm, pGm, pBm)
                            VGu, VBu = solve_markov_pwl(pack_pre(GU, BU, qU, ie, True), bv, p, init=init_u, tol_out=1e-5)
                            VGu = VGu + bump_bv
                            VBu = VBu + bump_bv
                            dGs, _, _ = certify_logpwl_sens(GU, VGu, (1.0 - p) * VGu + p * VBu, bv, tol=2.5e-4, q_hi=qU, eL=eLs, eU=eUs)
                            dBs, _, _ = certify_logpwl_sens(BU, VBu, r_rec * VGu + (1.0 - r_rec) * VBu, bv, tol=2.5e-4, q_hi=qU, eL=eLs, eU=eUs)
                            cGs, cBs = np.linalg.solve(np.eye(2) - bv * P, np.array([dGs + 0.00003, dBs + 0.00003]))
                            wb_s = float(np.min(WB_l[ks_wit >= H_M]))
                            pg_s = float(np.interp(np.log(H_M), lks_m, VGu)) + cGs
                            pb_s = float(np.interp(np.log(H_M), lks_m, VBu)) + cBs
                            t_sb = dF_dL(BU, H_M, 0.603)
                            c_sb_sup = qU * H_M + F_A(BU, H_M, 0.603) + 0.397 * t_sb - H_M
                            e_sub = max(ev_s * np.log(c_sb_sup - t_sb * min(1.0, (1.0 - ev_s) * c_sb_sup / t_sb)) + (1.0 - ev_s) * np.log(min(1.0, (1.0 - ev_s) * c_sb_sup / t_sb)) for ev_s in (eLs, eUs))
                            mExitHB_box = min(mExitHB_box, wb_s - (e_sub + bv * (r_rec * pg_s + (1.0 - r_rec) * pb_s)))

            T_prob = T_G + 4
            max_ym_gap = max(PsiG_ym - B_star[0], PsiB_ym - B_star[1])
            P_tau_G = (margG - (bv ** T_prob) * max_exit) / ((bv ** 3) * max_ym_gap - (bv ** T_prob) * max_exit)

            assert margG > 0.0 and margB > 0.0
            assert min_M_G > 0.0 and min_M_B > 0.0 and mExitHG > 0.0 and mExitHB_box > 0.0
            assert 0.0 < P_tau_G <= 1.0
            if worst_res is None:
                worst_res = dict(
                    BG=B_b[0], BB=B_b[1], cG=cG, cB=cB, WG0=WG0, WB0=WB0,
                    margG=margG, margB=margB, T_G=T_G, T_B=T_B,
                    mExitMG=mExitMG, mExitMB=mExitMB, min_M_G=min_M_G, min_M_B=min_M_B,
                    mExitHG=mExitHG, mExitHB_box=mExitHB_box, T_prob=T_prob, P_tau_G=P_tau_G,
                )
            else:
                worst_res["margG"] = min(worst_res["margG"], margG)
                worst_res["margB"] = min(worst_res["margB"], margB)
                worst_res["T_G"] = max(worst_res["T_G"], T_G)
                worst_res["T_B"] = max(worst_res["T_B"], T_B)
                worst_res["mExitMG"] = min(worst_res["mExitMG"], mExitMG)
                worst_res["mExitMB"] = min(worst_res["mExitMB"], mExitMB)
                worst_res["min_M_G"] = min(worst_res["min_M_G"], min_M_G)
                worst_res["min_M_B"] = min(worst_res["min_M_B"], min_M_B)
                worst_res["mExitHG"] = min(worst_res["mExitHG"], mExitHG)
                worst_res["mExitHB_box"] = min(worst_res["mExitHB_box"], mExitHB_box)
                worst_res["P_tau_G"] = min(worst_res["P_tau_G"], P_tau_G)

        print(
            f"    p={100*p:4.1f}% | BG={worst_res['BG']:7.3f} (marg={worst_res['margG']:5.2f}, T*_G={worst_res['T_G']:2d}) | "
            f"BB={worst_res['BB']:7.3f} (marg={worst_res['margB']:5.2f}, T*_B={worst_res['T_B']:2d}) | "
            f"mExit(M:G/B={worst_res['mExitMG']:+.2f}/{worst_res['mExitMB']:+.3f} [cont>={worst_res['min_M_B']:+.3f}], "
            f"H:G/B_32bx={worst_res['mExitHG']:+.2f}/{worst_res['mExitHB_box']:+.3f}) | P(tau<={worst_res['T_prob']})>={worst_res['P_tau_G']:.3f}"
        )
        appendix_5B.append((
            p, worst_res["cG"], worst_res["cB"], worst_res["WG0"], worst_res["WB0"],
            worst_res["margG"], worst_res["margB"], worst_res["T_G"], worst_res["T_B"],
            worst_res["mExitMG"], worst_res["mExitMB"], worst_res["mExitHG"], worst_res["mExitHB_box"],
        ))

    # Markov staying breakdown p_cert^Markov (where margB crosses 0)
    def markov_stay_B_gap(p_v):
        P_v = np.array([[1.0 - p_v, p_v], [r_rec, 1.0 - r_rec]])
        mb = P_v @ np.array([m_G, m_B])
        Del = (H_M - B_M) * np.minimum(np.array([ETA_MIN / C_max, ETA_MIN / C_max_B]), BETA_MIN * mb)
        Bs = np.linalg.solve(np.eye(2) - BETA_MIN * P_v, np.array([R_hat, R_hat_B]) - Del)
        Bb = Bs[1] - m_B * (H_M - B_M)
        _, VBm_v = solve_markov_pwl(pre_lo, BETA_MAX, p_v)
        return float(np.interp(np.log(B_M), lks_m, VBm_v)) - Bb

    p_cert_markov = brentq(markov_stay_B_gap, 0.12, 0.18, xtol=1e-4)
    print(f"    Markov staying breakdown limit (B-state stay-root extrapolation only; exit certs verified pointwise on p in {{0%..12%}}): p_cert^Markov = {100*p_cert_markov:.2f}%")
    assert 0.14 < p_cert_markov < 0.17

    # 5C. Anticipatory Stochastic VFI Policy & Threshold Comparison (Continuous Golden-Section Ruin + Markov)
    print("\n  [5C] Forward-Looking Stochastic VFI (Continuous Golden-Section Ruin & Markov):")
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
    u_B, y_kL_B = build_u_bench(A_B)

    def solve_L_p(k_arr, kp_arr, A_v=A_G):
        return _golden_solve_L(k_arr, kp_arr, lambda k, L: F_A(A_v, k, L), q, eta)

    s_cand = 1.0 - np.geomspace(1e-5, 0.15, 22)
    kp_tail_G = y_kL_G[:, -1][:, None] * s_cand[None, :]
    kp_tail_B = y_kL_B[:, -1][:, None] * s_cand[None, :]
    u_tail_G = np.full((n_k, len(s_cand)), -1e9)
    u_tail_B = np.full((n_k, len(s_cand)), -1e9)
    for j in range(len(s_cand)):
        _, u_tail_G[:, j] = solve_L_p(k_grid, kp_tail_G[:, j], A_G)
        _, u_tail_B[:, j] = solve_L_p(k_grid, kp_tail_B[:, j], A_B)

    def interp_Vs(V, kp, b_eff):
        r = np.interp(np.clip(kp, k_lo, k_hi), k_grid, V)
        return np.where(kp < k_lo, V[0] + (eta / (1.0 - b_eff)) * np.log(np.maximum(kp, 1e-30) / k_lo), r)

    def refine_skiba_state(pol_arr, V_cont, A_v, b_eff):
        idx_m = np.where((k_grid >= 0.00138) & (k_grid <= 0.0065))[0]
        i0 = idx_m[np.where((pol_arr - k_grid)[idx_m] > 0)[0][0]]
        k_sub = np.linspace(k_grid[i0 - 1], k_grid[i0], 25)
        diffs = []
        for ks in k_sub:
            ys = q * ks + F_A(A_v, ks, 1.0)
            kd = np.linspace(max(1e-5, 0.90 * ks), ks, 30)
            _, ud = solve_L_p(np.full_like(kd, ks), kd, A_v)
            vd = np.max(ud + b_eff * interp_Vs(V_cont, kd, b_eff))
            if ys > ks + 1e-12:
                ku = np.linspace(ks, ys - 1e-12, 30)
                _, uu = solve_L_p(np.full_like(ku, ks), ku, A_v)
                vu = np.max(uu + b_eff * interp_Vs(V_cont, ku, b_eff))
            else:
                vu = -1e9
            diffs.append(vu - vd)
        pos = np.where(np.array(diffs) >= 0)[0]
        if len(pos) > 0 and pos[0] > 0:
            return float(k_sub[pos[0] - 1] + abs(diffs[pos[0] - 1]) / (abs(diffs[pos[0] - 1]) + abs(diffs[pos[0]])) * (k_sub[pos[0]] - k_sub[pos[0] - 1]))
        return float(0.5 * (k_grid[i0 - 1] + k_grid[i0]))

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

    V_ss_est = eta * np.log(F_A(A_G, K_ss, 0.7) - delta * K_ss)

    def solve_cont_markov_5C(p_val, r_rec_val):
        Vc0 = (eta / (1.0 - beta)) * (np.log((1.0 - beta) * q) + (beta / (1.0 - beta)) * np.log(beta * q))
        VG = np.where(k_grid > 0.00145, V_ss_est / (1.0 - beta), Vc0 + (eta / (1.0 - beta)) * np.log(k_grid))
        VB = VG.copy() - 5.0
        ym_G, ym_B = y_kL_G[:, -1], y_kL_B[:, -1]
        for _ in range(55):
            EVG = (1.0 - p_val) * VG + p_val * VB
            EVB = r_rec_val * VG + (1.0 - r_rec_val) * VB
            pols, ups = [], []
            for uM, EV, Av, ym, kpt, ut in [
                (u_G, EVG, A_G, ym_G, kp_tail_G, u_tail_G),
                (u_B, EVB, A_B, ym_B, kp_tail_B, u_tail_B),
            ]:
                vg = uM + beta * EV[None, :]
                jb = np.argmax(vg, axis=1)
                bg = vg[np.arange(n_k), jb]
                vt = ut + beta * interp_Vs(EV, kpt, beta)
                sb = np.argmax(vt, axis=1)
                bt = vt[np.arange(n_k), sb]
                uset = bt > bg
                lot = kpt[np.arange(n_k), np.maximum(0, sb - 1)]
                hit = kpt[np.arange(n_k), np.minimum(len(s_cand) - 1, sb + 1)]
                lo = np.where(uset, np.minimum(lot, hit), k_grid[np.maximum(0, jb - 1)])
                hi = np.where(uset, np.minimum(np.maximum(lot, hit), ym - 1e-12), np.minimum(k_grid[np.minimum(n_k - 1, jb + 1)], ym - 1e-12))
                x1 = hi - inv_phi * (hi - lo)
                x2 = lo + inv_phi * (hi - lo)
                _, u1 = solve_L_p(k_grid, x1, Av)
                _, u2 = solve_L_p(k_grid, x2, Av)
                f1 = u1 + beta * interp_Vs(EV, x1, beta)
                f2 = u2 + beta * interp_Vs(EV, x2, beta)
                for _g in range(12):
                    mr = f1 < f2
                    lo = np.where(mr, x1, lo)
                    hi = np.where(mr, hi, x2)
                    x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
                    x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
                    _, u1n = solve_L_p(k_grid, x1n, Av)
                    _, u2n = solve_L_p(k_grid, x2n, Av)
                    f1n = np.where(mr, f2, u1n + beta * interp_Vs(EV, x1n, beta))
                    f2n = np.where(mr, u2n + beta * interp_Vs(EV, x2n, beta), f1)
                    x1, x2, f1, f2 = x1n, x2n, f1n, f2n
                pol = np.where(f1 > f2, x1, x2)
                _, up = solve_L_p(k_grid, pol, Av)
                pols.append(pol)
                ups.append(up)
            polG, polB = pols
            upG, upB = ups
            VGe, VBe = VG.copy(), VB.copy()
            for _h in range(100):
                EVGe = (1.0 - p_val) * VGe + p_val * VBe
                EVBe = r_rec_val * VGe + (1.0 - r_rec_val) * VBe
                VGn = upG + beta * interp_Vs(EVGe, polG, beta)
                VBn = upB + beta * interp_Vs(EVBe, polB, beta)
                if max(np.max(np.abs(VGn - VGe)), np.max(np.abs(VBn - VBe))) < 1e-9:
                    VGe, VBe = VGn, VBn
                    break
                VGe, VBe = VGn, VBn
            if max(np.max(np.abs(VGe - VG)), np.max(np.abs(VBe - VB))) < 1e-8:
                VG, VB = VGe, VBe
                break
            VG, VB = VGe, VBe
        EVG = (1.0 - p_val) * VG + p_val * VB
        kp_m, L_m, _ = smooth_policy_at(B_M, EVG, A_G, beta)
        S_G = refine_skiba_state(polG, EVG, A_G, beta)
        # Skiba jump in B (max jump in polB/K) and zero-net-investment K_B*(p) (polB > K)
        idx_sk = np.where((k_grid >= 0.00138) & (k_grid <= 0.005))[0]
        j_kink = idx_sk[int(np.argmax(np.diff(polB[idx_sk] / k_grid[idx_sk])))]
        S_Bkink = float(0.5 * (k_grid[j_kink] + k_grid[j_kink + 1]))
        idx_kb = np.where((k_grid >= 0.005) & (k_grid <= 0.03))[0]
        j_kb = idx_kb[np.where((polB - k_grid)[idx_kb] > 0)[0][0]]
        KB_star = float(0.5 * (k_grid[j_kb - 1] + k_grid[j_kb]))
        return S_G, S_Bkink, KB_star, kp_m, L_m

    p_tests = [0.0, 0.005, 0.010, 0.015, 0.020, 0.050, 0.080]
    ruin_S, ruin_kp, ruin_L = [], [], []
    markov_SG, markov_SBk, markov_KBs, markov_kp, markov_L = [], [], [], [], []
    y_max_row = y_kL_G[:, -1]

    for p in p_tests:
        # Case 1: Ruin/Expropriation (beta_eff = beta*(1-p)) with continuous golden-section VFI
        b_eff = beta * (1.0 - p)
        Vc = (eta / (1.0 - b_eff)) * (np.log((1.0 - b_eff) * q) + (b_eff / (1.0 - b_eff)) * np.log(b_eff * q))
        V = np.where(k_grid > 0.00145, V_ss_est / (1.0 - b_eff), Vc + (eta / (1.0 - b_eff)) * np.log(k_grid))
        for _ in range(55):
            vg = u_G + b_eff * V[None, :]
            jb = np.argmax(vg, axis=1)
            bg = vg[np.arange(n_k), jb]
            vt = u_tail_G + b_eff * interp_Vs(V, kp_tail_G, b_eff)
            sb = np.argmax(vt, axis=1)
            bt = vt[np.arange(n_k), sb]
            ut = bt > bg
            lo_t = kp_tail_G[np.arange(n_k), np.maximum(0, sb - 1)]
            hi_t = kp_tail_G[np.arange(n_k), np.minimum(len(s_cand) - 1, sb + 1)]
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
        kS = refine_skiba_state(pol, V, A_G, b_eff)
        kp_r, L_r, _ = smooth_policy_at(B_M, V, A_G, b_eff)
        ruin_S.append(kS)
        ruin_kp.append(kp_r)
        ruin_L.append(L_r)

        # Case 2: Continuous golden-section Markov VFI (matching Ruin VFI at p=0.0%)
        S_G, S_Bkink, KB_star, kp_m, L_m = solve_cont_markov_5C(p, r_rec)
        markov_SG.append(S_G)
        markov_SBk.append(S_Bkink)
        markov_KBs.append(KB_star)
        markov_kp.append(kp_m)
        markov_L.append(L_m)
        print(
            f"    p={100*p:4.1f}% | Ruin: S_p={kS:.6f}, K'={kp_r:.5f}, L={L_r:.4f} | "
            f"Markov: S_G={S_G:.6f}, S_B_kink={S_Bkink:.5f}, K_B*={KB_star:.5f}, K'_G={kp_m:.5f}, L_G={L_m:.4f}"
        )

    assert abs(ruin_S[0] - markov_SG[0]) < 2e-6
    assert abs(ruin_kp[0] - markov_kp[0]) < 2e-5 and abs(ruin_L[0] - markov_L[0]) < 5e-4
    assert all(ruin_S[i] < ruin_S[i + 1] for i in range(len(p_tests) - 1))
    assert all(ruin_kp[i] > ruin_kp[i + 1] and ruin_L[i] > ruin_L[i + 1] for i in range(len(p_tests) - 1))
    assert all(markov_SG[i] <= markov_SG[i + 1] for i in range(len(p_tests) - 1))
    assert markov_SG[-1] > markov_SG[0] and markov_SBk[-1] > markov_SBk[0] and markov_KBs[-1] < markov_KBs[0]
    assert all(markov_kp[i] <= markov_kp[i + 1] and markov_L[i] <= markov_L[i + 1] for i in range(len(p_tests) - 1))
    assert markov_kp[-1] > markov_kp[0] and markov_L[-1] > markov_L[0]

    # U5: r_rec sensitivity at p = 8%
    print("\n  [U5] Recovery probability r_rec sensitivity at p=8.0%:")
    for r_val in (0.20, 1.0 / 3.0, 0.50):
        sg_r, sbk_r, kbs_r, kpm_r, lm_r = solve_cont_markov_5C(0.08, r_val)
        print(f"    r_rec={r_val:.4f}: S_G={sg_r:.6f}, S_B_kink={sbk_r:.5f}, K_B*={kbs_r:.5f}, K'_G(0.10)={kpm_r:.5f}, L_G={lm_r:.4f}")

    # Technical Appendix Reproducibility Summary
    print("\n  [APPENDIX] Technical Appendix Reproducibility Certificates:")
    print("    (A) Ruin Super-Barriers (Parametric x^(-1/2) for p<1.12%, Continuous Log-PWL for all p in [0%,2%]) & 25-step W_M^(p):")
    for p, c_p_par, d_lb_par, d_ub_par, tail_m_par, c_pwl, psi_10, psi_28, tailp_val, WM, WH, trajM, rsM in appendix_5A:
        if c_p_par is not None:
            a_c, b_c = psi_shapes[p]
            par_txt = f"par=({a_c:.2f},{b_c:.1f},{c_p_par:.4f}, tail+{tail_m_par:.3f})"
        else:
            par_txt = "par=(blowup x->0+)"
        print(
            f"      p={100*p:4.2f}% | {par_txt} | pwl(c={c_pwl:.5f}, Psi(0.10)={psi_10:.4f}, Psi(0.28)={psi_28:.4f}, tail={tailp_val:.3f}) | "
            f"W_M={WM:.6f}, W_H={WH:.6f}"
        )
        if p in (0.0, 0.02):
            steps_preview = ", ".join(f"({k:.4f},{l:.4f}->{kp:.4f})" for k, l, kp in trajM[:5])
            print(f"        W_M^(p) first 5 steps: [{steps_preview}, ... -> {trajM[-1][2]:.4f}] | r in [{min(rsM):.4f}, {max(rsM):.4f}]")
    print("    (B) Coupled Markov Log-PWL Shifts (c_G, c_B) & Adverse-Exit Margins:")
    for p, cG, cB, WG0, WB0, mG, mB, TG, TB, eMG, eMB, eHG, eHB_s in appendix_5B:
        print(
            f"      p={100*p:4.1f}% | (c_G,c_B)=({cG:.4f},{cB:.4f}) | W_G={WG0:.4f}, W_B={WB0:.4f} | "
            f"stay=({mG:.3f},{mB:.3f}) | T*=({TG},{TB}) | exit(M:G={eMG:+.3f},B={eMB:+.3f}; H:G={eHG:+.3f},B_32bx={eHB_s:+.3f})"
        )


if __name__ == "__main__":
    verify_barriers()
    verify_prop1_double_star()
    verify_theorem3_star()
    verify_theorem10()
    verify_theorem11_stochastic()
    print("\nALL ANALYTICAL AND NUMERICAL CHECKS PASSED SUCCESSFULLY.")
