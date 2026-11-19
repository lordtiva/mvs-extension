import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from verify_results import (
    A_MIN,
    A_MAX,
    BETA_MIN,
    BETA_MAX,
    Q_MIN,
    Q_MAX,
    ETA_MIN,
    ETA_MAX,
    B_M,
    H_M,
    F_A,
    dF_dK,
    dF_dL,
    exact_kappa,
    box_worst_u,
    _golden_solve_L,
    _build_slope_tables,
    build_25step_witness_builder,
    solve_vfi_frontiers,
    solve_endo_threshold_vfi,
)

# Resolve workspace output directory dynamically
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure publication-quality academic styling (NeurIPS / Econometrica aesthetic)
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['ytick.major.width'] = 0.8
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'

# Shared calibration constants (Theorem 9* / Lemma 1)
C_max_plus = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
R_hat = -0.996
Delta_2 = 0.2997
B_max_paper = R_hat / (1.0 - BETA_MIN) - Delta_2 / (1.0 - BETA_MIN**2)
B_star_new = (R_hat - Delta_2) / (1.0 - BETA_MIN)
slope_min = ETA_MIN * Q_MIN / C_max_plus


# ==============================================================================
# HELPER SOLVERS FOR VFI CURVES, TRAJECTORIES & RUIN DOOB LOG-PWL CERTIFICATES
# ==============================================================================
def _solve_endo_threshold_norm(A_val):
    """Normalized k = A^2 K continuous golden-section VFI for S_A^{endo}."""
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

    lo_ss = 0.25 * (A_val ** 2)
    hi_ss = max(1e10, 10.0 * np.sqrt(1.5 * c_K / D) * (A_val ** 2.5))
    while df_dk(hi_ss) >= D:
        hi_ss *= 10.0
    if df_dk(lo_ss) <= D:
        return np.nan
    k_ss = brentq(lambda k: df_dk(k) - D, lo_ss, hi_ss)
    k_lo, k_hi = 1e-6, max(1.10 * k_ss, 0.01)

    k_grid = np.unique(np.concatenate([
        np.geomspace(k_lo, 0.00075, 90, endpoint=False),
        np.linspace(0.00075, 0.0032, 260, endpoint=False),
        np.geomspace(0.0032, k_hi, 180),
    ]))
    n_k = len(k_grid)

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

    L_grid = np.unique(np.concatenate([
        np.geomspace(1e-5, 0.05, 20, endpoint=False),
        np.linspace(0.05, 0.999, 45),
    ]))
    f_kL = c_K * (k_grid[:, None] ** 1.5) * ((1.0 + k_grid[:, None] / ((A_val ** 2) * L_grid[None, :])) ** (-1.5))
    y_kL = q * k_grid[:, None] + f_kL
    dis_L = (1.0 - eta) * np.log(1.0 - L_grid[None, :])
    u_endo_grid = np.full((n_k, n_k), -1e9)
    for start in range(0, n_k, 90):
        end = min(n_k, start + 90)
        c_blk = y_kL[start:end, None, :] - k_grid[None, :, None]
        u_blk = np.where(c_blk > 1e-15, eta * np.log(np.maximum(c_blk, 1e-30)) + dis_L[:, None, :], -1e9)
        u_endo_grid[start:end, :] = np.max(u_blk, axis=2)

    s_cand_e = 1.0 - np.geomspace(1e-5, 0.15, 20)
    kp_tail_e = y_kL[:, -1][:, None] * s_cand_e[None, :]
    u_tail_e = np.full((n_k, len(s_cand_e)), -1e9)
    for j in range(len(s_cand_e)):
        _, u_tail_e[:, j] = _golden_solve_L(k_grid, kp_tail_e[:, j], f_norm, q, eta)

    V_endo = V_cake_const + (eta / (1.0 - beta)) * np.log(k_grid)
    y_max_row = y_kL[:, -1]
    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0
    for _ in range(120):
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
        _, u1 = _golden_solve_L(k_grid, x1, f_norm, q, eta)
        _, u2 = _golden_solve_L(k_grid, x2, f_norm, q, eta)
        f1 = u1 + beta * interp_V(x1, V_endo)
        f2 = u2 + beta * interp_V(x2, V_endo)
        for _g in range(12):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            _, u1n = _golden_solve_L(k_grid, x1n, f_norm, q, eta)
            _, u2n = _golden_solve_L(k_grid, x2n, f_norm, q, eta)
            f1n = np.where(mr, f2, u1n + beta * interp_V(x1n, V_endo))
            f2n = np.where(mr, u2n + beta * interp_V(x2n, V_endo), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        pol_endo = np.where(f1 > f2, x1, x2)
        _, u_pol_e = _golden_solve_L(k_grid, pol_endo, f_norm, q, eta)
        V_eval = np.maximum(f1, f2)
        for _h in range(90):
            Ve_n = u_pol_e + beta * interp_V(pol_endo, V_eval)
            if np.max(np.abs(Ve_n - V_eval)) < 1e-10:
                V_eval = Ve_n
                break
            V_eval = Ve_n
        if np.max(np.abs(V_eval - V_endo)) < 1e-9:
            V_endo = V_eval
            break
        V_endo = V_eval

    pos = np.where((pol_endo - k_grid) > 1e-8)[0]
    if len(pos) == 0:
        return np.nan
    i_jump = int(pos[0])
    k_sub = np.linspace(k_grid[i_jump - 1], k_grid[i_jump], 20)
    diffs = []
    for ks in k_sub:
        ys = q * ks + f_norm(ks, 1.0)
        kd = np.linspace(max(1e-7, 0.90 * ks), ks, 25)
        _, ud = _golden_solve_L(np.full_like(kd, ks), kd, f_norm, q, eta)
        vd = np.max(ud + beta * interp_V(kd, V_endo))
        if ys > ks + 1e-12:
            ku = np.linspace(ks, ys - 1e-12, 25)
            _, uu = _golden_solve_L(np.full_like(ku, ks), ku, f_norm, q, eta)
            vu = np.max(uu + beta * interp_V(ku, V_endo))
        else:
            vu = -1e9
        diffs.append(vu - vd)
    pos_s = np.where(np.array(diffs) >= 0)[0]
    if len(pos_s) > 0 and pos_s[0] > 0:
        idx0 = pos_s[0]
        kS = k_sub[idx0 - 1] + abs(diffs[idx0 - 1]) / (abs(diffs[idx0 - 1]) + abs(diffs[idx0])) * (k_sub[idx0] - k_sub[idx0 - 1])
    else:
        kS = 0.5 * (k_grid[i_jump - 1] + k_grid[i_jump])
    return float(kS / (A_val ** 2))


def _solve_vfi_trajectory(A_val, K_0=0.06, g_rate=0.0, n_steps=44):
    """Solve continuous golden-section VFI policy and simulate trajectory from K_0."""
    beta, eta, q = 0.97, 0.70, 0.92
    q_eff = q / (1.0 + g_rate)
    A_eff = A_val / (1.0 + g_rate)
    Ks = np.unique(np.concatenate([
        np.geomspace(1e-4, 0.02, 70, endpoint=False),
        np.linspace(0.02, 0.40, 240, endpoint=False),
        np.geomspace(0.40, 4.2, 110),
    ]))
    nk = len(Ks)
    Ls = np.unique(np.concatenate([
        np.geomspace(1e-4, 0.08, 18, endpoint=False),
        np.linspace(0.08, 0.999, 55),
    ]))
    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0

    def f_K(K, L):
        return F_A(A_eff, K, L)

    y_kL = q_eff * Ks[:, None] + f_K(Ks[:, None], Ls[None, :])
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
        _, ut[:, j] = _golden_solve_L(Ks, kpt[:, j], f_K, q_eff, eta)
    V_cake_const = (eta / (1.0 - beta)) * (
        np.log((1.0 - beta) * q_eff) + (beta / (1.0 - beta)) * np.log(beta * q_eff)
    )
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
        hi = np.where(
            use,
            np.minimum(np.maximum(lot, hit), ym - 1e-12),
            np.minimum(Ks[np.minimum(nk - 1, jb + 1)], ym - 1e-12),
        )
        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        _, u1 = _golden_solve_L(Ks, x1, f_K, q_eff, eta)
        _, u2 = _golden_solve_L(Ks, x2, f_K, q_eff, eta)
        f1 = u1 + beta * interp_V(x1, V)
        f2 = u2 + beta * interp_V(x2, V)
        for _g in range(14):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            _, u1n = _golden_solve_L(Ks, x1n, f_K, q_eff, eta)
            _, u2n = _golden_solve_L(Ks, x2n, f_K, q_eff, eta)
            f1n = np.where(mr, f2, u1n + beta * interp_V(x1n, V))
            f2n = np.where(mr, u2n + beta * interp_V(x2n, V), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        pol = np.where(f1 > f2, x1, x2)
        _, up = _golden_solve_L(Ks, pol, f_K, q_eff, eta)
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

    K_hat = float(K_0)
    traj = [K_hat]
    for t in range(n_steps):
        K_hat = float(np.interp(K_hat, Ks, pol))
        traj.append(K_hat * ((1.0 + g_rate) ** (t + 1)))
    return np.array(traj)


def _compute_ruin_doob_data():
    """Compute exact Proposition 4* box-uniform log-PWL + b_max Doob deadlines T*(p) and p_cert."""
    _, _, _, eval_witness = build_25step_witness_builder()
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
    Ls_m = np.unique(np.concatenate([
        [0.0],
        np.geomspace(1e-5, 0.08, 18, endpoint=False),
        np.linspace(0.08, 0.999, 52),
    ]))
    s_cand_m = 1.0 - np.geomspace(1e-6, 0.15, 20)
    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0
    phi_loc = np.clip((np.log(0.060) - lks_m) / np.log(0.060 / 0.012), 0.0, 1.0)

    def get_u(ka, La, kpa):
        cv = Q_MAX * ka + F_A(A_MAX, ka, La) - kpa
        lc = np.log(np.maximum(cv, 1e-30))
        ll = np.log(1.0 - La)
        uv = np.maximum(ETA_MIN * lc + (1.0 - ETA_MIN) * ll, ETA_MAX * lc + (1.0 - ETA_MAX) * ll)
        return np.where(cv > 1e-15, uv, -1e9 + cv)

    def solve_L(ka, kpa):
        u0 = get_u(ka, np.zeros_like(ka), kpa)
        lo = np.full_like(ka, 1e-7)
        hi = np.full_like(ka, 1.0 - 1e-9)
        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        f1, f2 = get_u(ka, x1, kpa), get_u(ka, x2, kpa)
        for _ in range(18):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            f1n = np.where(mr, f2, get_u(ka, x1n, kpa))
            f2n = np.where(mr, get_u(ka, x2n, kpa), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        Lb = 0.5 * (lo + hi)
        ub = get_u(ka, Lb, kpa)
        return np.where(u0 > ub, 0.0, Lb), np.maximum(u0, ub)

    y = Q_MAX * ks_m[:, None] + F_A(A_MAX, ks_m[:, None], Ls_m[None, :])
    um = np.full((nk_m, nk_m), -1e9)
    ll_m = np.log(1.0 - Ls_m[None, :])
    for i in range(nk_m):
        cm = y[i, None, :] - ks_m[:, None]
        lc_m = np.log(np.maximum(cm, 1e-30))
        uv = np.maximum(ETA_MIN * lc_m + (1.0 - ETA_MIN) * ll_m, ETA_MAX * lc_m + (1.0 - ETA_MAX) * ll_m)
        um[i, :] = np.max(np.where(cm > 1e-15, uv, -1e9), axis=1)
    ym = y[:, -1]
    kpt = ym[:, None] * s_cand_m[None, :]
    ut = np.zeros_like(kpt)
    for j in range(len(s_cand_m)):
        _, ut[:, j] = solve_L(ks_m, kpt[:, j])
    u0_mat = get_u(ks_m[:, None], 0.0, ks_m[None, :])

    def solve_single_pwl(bv):
        s_lo_tail = ETA_MIN / (1.0 - bv)
        d_hi_tail = ETA_MAX / (1.0 - bv)

        def interp(V, kp):
            lk = np.log(np.maximum(kp, 1e-30))
            r = np.interp(np.clip(lk, lks_m[0], lks_m[-1]), lks_m, V)
            r = np.where(kp < ks_m[0], V[0] + s_lo_tail * (lk - lks_m[0]), r)
            return np.where(kp > ks_m[-1], V[-1] + d_hi_tail * (lk - lks_m[-1]), r)

        Vc = s_lo_tail * (np.log((1.0 - bv) * Q_MAX) + (bv / (1.0 - bv)) * np.log(bv * Q_MAX))
        V = np.where(ks_m > 0.0016, -25.0, Vc + s_lo_tail * lks_m)
        for _ in range(40):
            vg = um + bv * V[None, :]
            jb = np.argmax(vg, axis=1)
            bg = vg[np.arange(nk_m), jb]
            vt = ut + bv * interp(V, kpt)
            sb = np.argmax(vt, axis=1)
            bt = vt[np.arange(nk_m), sb]
            uset = bt > bg
            lot = kpt[np.arange(nk_m), np.maximum(0, sb - 1)]
            hit = kpt[np.arange(nk_m), np.minimum(len(s_cand_m) - 1, sb + 1)]
            lo = np.where(uset, np.minimum(lot, hit), ks_m[np.maximum(0, jb - 1)])
            hi = np.where(
                uset,
                np.minimum(np.maximum(lot, hit), ym - 1e-12),
                np.minimum(ks_m[np.minimum(nk_m - 1, jb + 1)], ym - 1e-12),
            )
            x1 = hi - inv_phi * (hi - lo)
            x2 = lo + inv_phi * (hi - lo)
            _, u1 = solve_L(ks_m, x1)
            _, u2 = solve_L(ks_m, x2)
            f1 = u1 + bv * interp(V, x1)
            f2 = u2 + bv * interp(V, x2)
            for _g in range(10):
                mr = f1 < f2
                lo = np.where(mr, x1, lo)
                hi = np.where(mr, hi, x2)
                x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
                x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
                _, u1n = solve_L(ks_m, x1n)
                _, u2n = solve_L(ks_m, x2n)
                f1n = np.where(mr, f2, u1n + bv * interp(V, x1n))
                f2n = np.where(mr, u2n + bv * interp(V, x2n), f1)
                x1, x2, f1, f2 = x1n, x2n, f1n, f2n
            pol_int = np.where(f1 > f2, x1, x2)
            _, up_int = solve_L(ks_m, pol_int)
            val_int = up_int + bv * interp(V, pol_int)
            jb0 = np.argmax(u0_mat + bv * V[None, :], axis=1)
            lo0 = ks_m[np.maximum(0, jb0 - 1)]
            hi0 = np.maximum(lo0, np.minimum(ks_m[np.minimum(nk_m - 1, jb0 + 1)], Q_MAX * ks_m - 1e-12))
            z1 = hi0 - inv_phi * (hi0 - lo0)
            z2 = lo0 + inv_phi * (hi0 - lo0)
            g1 = get_u(ks_m, 0.0, z1) + bv * interp(V, z1)
            g2 = get_u(ks_m, 0.0, z2) + bv * interp(V, z2)
            for _g0 in range(10):
                mr0 = g1 < g2
                lo0 = np.where(mr0, z1, lo0)
                hi0 = np.where(mr0, hi0, z2)
                z1n = np.where(mr0, z2, hi0 - inv_phi * (hi0 - lo0))
                z2n = np.where(mr0, lo0 + inv_phi * (hi0 - lo0), z1)
                g1n = np.where(mr0, g2, get_u(ks_m, 0.0, z1n) + bv * interp(V, z1n))
                g2n = np.where(mr0, get_u(ks_m, 0.0, z2n) + bv * interp(V, z2n), g1)
                z1, z2, g1, g2 = z1n, z2n, g1n, g2n
            pol0 = np.where(g1 > g2, z1, z2)
            up0 = get_u(ks_m, 0.0, pol0)
            use0 = (up0 + bv * interp(V, pol0)) > val_int
            pol = np.where(use0, pol0, pol_int)
            up = np.where(use0, up0, up_int)
            Ve = V.copy()
            for _h in range(180):
                Vn = up + bv * interp(Ve, pol)
                if np.max(np.abs(Vn - Ve)) < 1e-9:
                    Ve = Vn
                    break
                Ve = Vn
            if np.max(np.abs(Ve - V)) < 1e-8:
                V = Ve
                break
            V = Ve
        return V

    def certify_single_logpwl(V_arr, bv, s_tail, D_hi, tol=4e-4):
        x_cut = float(ks_m[-1])
        tail_knots = np.array([68.0, 78.0, 90.0])
        ks_ext = np.concatenate([ks_m, tail_knots])
        lks_ext = np.log(ks_ext)
        nk_ext = len(ks_ext)
        V_ext = np.concatenate([V_arr, V_arr[-1] + D_hi * np.log(tail_knots / x_cut)])
        s_arr = np.diff(V_ext) / np.diff(lks_ext)
        smin_tbl, smax_tbl = _build_slope_tables(s_arr)

        def eval_V(k_arr):
            lk = np.log(np.maximum(k_arr, 1e-30))
            r = np.interp(np.clip(lk, lks_ext[0], lks_ext[-1]), lks_ext, V_ext)
            r = np.where(k_arr < ks_ext[0], V_ext[0] + s_tail * (lk - lks_ext[0]), r)
            return np.where(k_arr > ks_ext[-1], V_ext[-1] + D_hi * (lk - lks_ext[-1]), r)

        def deriv_bounds(kL, kR):
            iL = np.clip(np.searchsorted(ks_ext, kL, side='right') - 1, 0, nk_ext - 2)
            iR = np.maximum(iL, np.clip(np.searchsorted(ks_ext, kR, side='left') - 1, 0, nk_ext - 2))
            lo_s, hi_s = smin_tbl[iL, iR], smax_tbl[iL, iR]
            below = kL < ks_ext[0]
            above = kR > ks_ext[-1]
            lo_s = np.where(above, np.minimum(lo_s, D_hi), lo_s)
            hi_s = np.where(above, np.maximum(hi_s, D_hi), hi_s)
            return (
                np.where(below, np.minimum(lo_s, s_tail), lo_s) / kR,
                np.where(below, np.maximum(hi_s, s_tail), hi_s) / kL,
            )

        r_top = Q_MAX + F_A(A_MAX, ks_m[0], 1.0) / ks_m[0]
        c_slo = ETA_MIN + bv * s_tail
        s_lo_opt = (bv * s_tail) / c_slo
        tail_lo_val = float(
            ETA_MIN * np.log((1.0 - s_lo_opt) * ks_m[0])
            + bv * s_tail * np.log(s_lo_opt)
            + c_slo * np.log(r_top)
            + bv * V_arr[0]
            - V_arr[0]
        )
        x_end = float(ks_ext[-1])
        F_inf = A_MAX * (2.0 ** 1.5)
        Y_end = Q_MAX * x_end + F_inf
        V1 = float(np.interp(np.log(1.0), lks_m, V_arr))
        tail_hi_lt1 = float(ETA_MAX * np.log(Y_end) + bv * V1 - V_ext[-1])
        idx1 = max(0, int(np.searchsorted(ks_m, 1.0)) - 1)
        sl_min = float(np.min((np.diff(V_arr[idx1:]) / np.diff(lks_m[idx1:])) / ks_m[idx1 + 1:]))
        c_star = ETA_MAX / (bv * sl_min)
        x_cross = (x_cut + c_star - F_inf) / Q_MAX
        x_peak = D_hi * max(x_cut - F_inf, 1.0) / ((D_hi - ETA_MAX) * Q_MAX)
        tail_hi_mid = max(
            float(
                ETA_MAX * np.log(max(c_star, Q_MAX * xv + F_inf - x_cut))
                + bv * (V_arr[-1] + sl_min * (Q_MAX * xv + F_inf - max(c_star, Q_MAX * xv + F_inf - x_cut) - x_cut))
                - (V_arr[-1] + D_hi * np.log(xv / x_cut))
            )
            for xv in (x_end, x_cross, x_peak, 2.0 * x_end, 1e6)
            if xv >= x_end
        )
        c_dhi = ETA_MAX + bv * D_hi
        s_hi_opt = (bv * D_hi) / c_dhi
        tail_hi_log = float(
            ETA_MAX * np.log(1.0 - s_hi_opt)
            + bv * D_hi * np.log(s_hi_opt)
            + c_dhi * np.log(Y_end / x_end)
            + ETA_MAX * np.log(x_end)
            + (bv * D_hi - D_hi) * np.log(x_end / x_cut)
            + bv * V_arr[-1]
            - V_arr[-1]
        )
        tail_hi_val = max(tail_hi_lt1, tail_hi_mid, tail_hi_log)

        xg = np.geomspace(ks_m[0], x_end, 48)
        Lg = np.concatenate([[0.0], np.geomspace(1e-5, 0.999, 22)])
        sg = np.linspace(0.05, 0.998, 22)
        Y_g = Q_MAX * xg[:, None] + F_A(A_MAX, xg[:, None], Lg[None, :])
        c_g = Y_g[:, :, None] * (1.0 - sg[None, None, :])
        y_g = Y_g[:, :, None] * sg[None, None, :]
        ec_g = np.where(c_g < 1.0, ETA_MIN, ETA_MAX)
        val_g = ec_g * np.log(c_g) + (1.0 - ETA_MAX) * np.log(1.0 - Lg[None, :, None]) + bv * eval_V(y_g) - eval_V(xg[:, None, None])
        xm_s = np.sqrt(ks_m[:-1] * ks_m[1:])[:, None, None]
        Lm_s = np.array([0.0, 0.37, 0.50, 0.62, 0.72, 0.85])[None, :, None]
        sm_s = np.array([0.82, 0.90, 0.955, 0.985, 0.9979])[None, None, :]
        Ym_s = Q_MAX * xm_s + F_A(A_MAX, xm_s, Lm_s)
        cm_s = Ym_s * (1.0 - sm_s)
        ecm_s = np.where(cm_s < 1.0, ETA_MIN, ETA_MAX)
        val_ms = ecm_s * np.log(cm_s) + (1.0 - ETA_MAX) * np.log(1.0 - Lm_s) + bv * eval_V(Ym_s * sm_s) - eval_V(xm_s)
        best_lb = max(tail_lo_val, tail_hi_val, float(np.max(val_g)), float(np.max(val_ms)))
        target = best_lb + tol

        xs_b = np.unique(np.concatenate([ks_m[::10], [x_cut, 68.0, 78.0, 90.0]]))
        Ls_b = np.concatenate([[0.0, 0.2, 0.5, 0.7], np.linspace(0.8, 0.99, 6, endpoint=False), [0.99, 0.999, 1.0]])
        ss_b = np.concatenate([[0.0, 0.3, 0.65], np.linspace(0.75, 0.99, 8, endpoint=False), [0.99, 0.996, 0.998, 0.999, 1.0]])
        gxL, gLL, gsL = np.meshgrid(xs_b[:-1], Ls_b[:-1], ss_b[:-1], indexing='ij')
        gxR, gLR, gsR = np.meshgrid(xs_b[1:], Ls_b[1:], ss_b[1:], indexing='ij')
        bxL, bxR, bLL, bLR, bsL, bsR = gxL.ravel(), gxR.ravel(), gLL.ravel(), gLR.ravel(), gsL.ravel(), gsR.ravel()
        for _ in range(60):
            Y_min = Q_MAX * bxL + F_A(A_MAX, bxL, bLL)
            Y_max = Q_MAX * bxR + F_A(A_MAX, bxR, bLR)
            c_max = np.maximum((1.0 - bsL) * Y_max, 1e-300)
            ec_max = np.where(c_max < 1.0, ETA_MIN, ETA_MAX)
            ub_mono = (
                np.where(bsL >= 1.0, -1e9, ec_max * np.log(c_max))
                + (1.0 - ETA_MAX) * np.log(np.maximum(1.0 - bLL, 1e-300))
                + np.where(bsR <= 0.0, -1e9, bv * eval_V(bsR * Y_max))
                - eval_V(bxL)
            )
            xm, Lm, sm = 0.5 * (bxL + bxR), 0.5 * (bLL + bLR), 0.5 * (bsL + bsR)
            hx, hL, hs = 0.5 * (bxR - bxL), 0.5 * (bLR - bLL), 0.5 * (bsR - bsL)
            Ym = Q_MAX * xm + F_A(A_MAX, xm, Lm)
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
                Yx_lo = Q_MAX + np.minimum(dF_dK(A_MAX, xLv, LLv), dF_dK(A_MAX, xRv, LLv))
                Yx_hi = Q_MAX + np.maximum(np.maximum(dF_dK(A_MAX, xLv, LRv), dF_dK(A_MAX, xRv, LRv)), dF_dK(A_MAX, px_hi, LRv))
                pL_hi = np.clip(xRv / 4.0, LLv, LRv)
                YL_lo = np.minimum(dF_dL(A_MAX, xLv, LLv), dF_dL(A_MAX, xLv, LRv))
                YL_hi = np.maximum(np.maximum(dF_dL(A_MAX, xRv, LLv), dF_dL(A_MAX, xRv, LRv)), dF_dL(A_MAX, xRv, pL_hi))
                fp_y_lo, fp_y_hi = deriv_bounds(y_min_v, y_max_v)
                fp_x_lo, fp_x_hi = deriv_bounds(xLv, xRv)
                cross_c1 = (c_min[valid_c] < 1.0) & (c_max[valid_c] >= 1.0)
                best_eta_ub = np.full(np.sum(valid_c), -1e9)
                err_x_v = np.zeros(np.sum(valid_c))
                err_L_v = np.zeros(np.sum(valid_c))
                err_s_v = np.zeros(np.sum(valid_c))
                for ec in (ETA_MIN, ETA_MAX):
                    mask_ec = (c_min[valid_c] < 1.0) if ec == ETA_MIN else (c_max[valid_c] >= 1.0)
                    ec_lo = np.where(cross_c1, ETA_MIN, ec)
                    ec_hi = np.where(cross_c1, ETA_MAX, ec)
                    hm = ec * np.log(cm[valid_c]) + (1.0 - ETA_MAX) * np.log(1.0 - Lmv) + bv * eval_V(smv * Ymv) - eval_V(xmv)
                    A_lo = ec_lo / Y_max_v + bv * sLv * fp_y_lo
                    A_hi_b = ec_hi / Y_min_v + bv * sRv * fp_y_hi
                    sx = np.maximum(np.abs(A_lo * Yx_lo - fp_x_hi), np.abs(A_hi_b * Yx_hi - fp_x_lo)) * hxv
                    sL = np.maximum(np.abs(A_lo * YL_lo - (1.0 - ETA_MAX) / (1.0 - LRv)), np.abs(A_hi_b * YL_hi - (1.0 - ETA_MAX) / (1.0 - LLv))) * hLv
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
            if not np.any(keep):
                return float(target)
            bxL, bxR, bLL, bLR, bsL, bsR = bxL[keep], bxR[keep], bLL[keep], bLR[keep], bsL[keep], bsR[keep]
            xm, Lm, sm = xm[keep], Lm[keep], sm[keep]
            ex, eL_err, es = ex[keep], eL_err[keep], es[keep]
            Ym_k = Q_MAX * xm + F_A(A_MAX, xm, Lm)
            cm_k = (1.0 - sm) * Ym_k
            ecm_k = np.where(cm_k < 1.0, ETA_MIN, ETA_MAX)
            lb_k = np.where(
                (Lm < 1.0) & (sm > 0.0) & (sm < 1.0),
                ecm_k * np.log(np.maximum(cm_k, 1e-300))
                + (1.0 - ETA_MAX) * np.log(np.maximum(1.0 - Lm, 1e-300))
                + bv * eval_V(sm * Ym_k)
                - eval_V(xm),
                -1e9,
            )
            if np.max(lb_k) > best_lb:
                best_lb = float(np.max(lb_k))
                target = best_lb + tol
            if len(bxL) <= 1000:
                bxL, bxR = np.concatenate([bxL, xm, bxL, xm, bxL, xm, bxL, xm]), np.concatenate([xm, bxR, xm, bxR, xm, bxR, xm, bxR])
                bLL, bLR = np.concatenate([bLL, bLL, Lm, Lm, bLL, bLL, Lm, Lm]), np.concatenate([Lm, Lm, bLR, bLR, Lm, Lm, bLR, bLR])
                bsL, bsR = np.concatenate([bsL, bsL, bsL, bsL, sm, sm, sm, sm]), np.concatenate([sm, sm, sm, sm, bsR, bsR, bsR, bsR])
            else:
                m1 = (ex >= eL_err) & (ex >= es)
                m2 = (~m1) & (eL_err >= es)
                m3 = (~m1) & (~m2)
                axL, axR, aLL, aLR, asL, asR = bxL.copy(), bxR.copy(), bLL.copy(), bLR.copy(), bsL.copy(), bsR.copy()
                bxLc, bxRc, bLLc, bLRc, bsLc, bsRc = bxL.copy(), bxR.copy(), bLL.copy(), bLR.copy(), bsL.copy(), bsR.copy()
                axR[m1] = xm[m1]; bxLc[m1] = xm[m1]
                aLR[m2] = Lm[m2]; bLLc[m2] = Lm[m2]
                asR[m3] = sm[m3]; bsLc[m3] = sm[m3]
                bxL, bxR = np.concatenate([axL, bxLc]), np.concatenate([axR, bxRc])
                bLL, bLR = np.concatenate([aLL, bLLc]), np.concatenate([aLR, bLRc])
                bsL, bsR = np.concatenate([asL, bsLc]), np.concatenate([asR, bsRc])
        raise RuntimeError("Ruin Doob B&B did not converge")

    def stay_gap_fn(p_v):
        b_min = BETA_MIN * (1.0 - p_v)
        b_max = BETA_MAX * (1.0 - p_v)
        WM, _, _ = eval_witness(b_max, B_M, b_solve=b_max, eta_mode='outer')
        D2_p = (ETA_MIN * b_min * Q_MIN * (H_M - B_M)) / C_max_plus
        B1_b_p = (R_hat - D2_p) / (1.0 - b_min) - slope_min * (H_M - B_M)
        return WM - B1_b_p

    p_cert = brentq(stay_gap_fn, 0.015, 0.025, xtol=1e-5)

    p_grid = np.array([
        0.0000, 0.00125, 0.0025, 0.00375, 0.0050, 0.00625, 0.0075, 0.00875,
        0.0100, 0.01125, 0.0125, 0.01375, 0.0150, 0.01625, 0.0175, 0.0185,
        0.0192, 0.0196, 0.0200, 0.0202, 0.02035, 0.02040, 0.020425,
    ])
    T_star_list = []
    P_doob_list = []
    for p in p_grid:
        b_min = BETA_MIN * (1.0 - p)
        b_max = BETA_MAX * (1.0 - p)
        WM, _, _ = eval_witness(b_max, B_M, b_solve=b_max, eta_mode='outer')
        s_lo_u = ETA_MIN / (1.0 - b_min)
        d_hi_u = ETA_MAX / (1.0 - b_max)
        Vp_1 = solve_single_pwl(b_min) + (0.030 / (1.0 - b_min)) * phi_loc
        dp_ub_lo = certify_single_logpwl(Vp_1, b_min, s_lo_u, d_hi_u)
        dp_ub_hi = certify_single_logpwl(Vp_1, b_max, s_lo_u, d_hi_u)
        c_pwl = max((dp_ub_lo + 0.0002) / (1.0 - b_min), (dp_ub_hi + 0.0002) / (1.0 - b_max))
        psi_28 = float(np.interp(np.log(H_M), lks_m, Vp_1)) + c_pwl
        D2_p = (ETA_MIN * b_min * Q_MIN * (H_M - B_M)) / C_max_plus
        B_star_p = (R_hat - D2_p) / (1.0 - b_min)
        B1_b_p = B_star_p - slope_min * (H_M - B_M)
        T_star = int(np.ceil(np.log((WM - B1_b_p) / (psi_28 - B_star_p)) / np.log(b_max)))
        T_star_list.append(T_star)
        P_doob_list.append((1.0 - p) ** T_star)

    T_arr = np.array(T_star_list)
    P_arr = np.array(P_doob_list)
    # Verify exact parity with verify_results.py Proposition 4* Ruin Doob
    for pv, Tv in [(0.0, 22), (0.005, 25), (0.010, 30), (0.015, 40), (0.020, 84)]:
        idx = int(np.argmin(np.abs(p_grid - pv)))
        assert T_arr[idx] == Tv, f"Ruin Doob mismatch at p={pv}: got {T_arr[idx]} vs {Tv}"
    idx_2pct = int(np.argmin(np.abs(p_grid - 0.020)))
    assert abs(P_arr[idx_2pct] - 0.1832) < 0.001
    assert abs(p_cert - 0.020434) < 5e-4
    return {
        'p_grid': p_grid,
        'T_star': T_arr,
        'P_doob': P_arr,
        'p_cert': p_cert,
        'T_2pct': int(T_arr[idx_2pct]),
        'P_doob_2pct': float(P_arr[idx_2pct]),
    }


def precompute_figure_data():
    """Precompute all VFI and stochastic barrier datasets once for both ES and EN figures."""
    print("Precomputing VFI frontiers (Fig 2)...")
    A_vfi = np.array([0.75, 1.50, 3.00, 10.0, 30.0, 100.0])
    vfi_res = [solve_vfi_frontiers(float(a)) for a in A_vfi]
    kS_fix = np.array([r[0] for r in vfi_res])
    kS_endo = np.array([r[1] for r in vfi_res])
    fig2_data = {
        'A_vfi': A_vfi,
        'kS_fix': kS_fix,
        'kS_endo': kS_endo,
        'S_fix': kS_fix / (A_vfi ** 2),
        'S_endo': kS_endo / (A_vfi ** 2),
        'frontier_gap': (kS_endo / kS_fix) - 1.0,
    }

    print("Precomputing VFI U-curve S(tau) (Fig 3)...")
    A0, alpha_pub, delta, beta, theta, eta = 1.45, 0.25, 0.08, 0.97, 1.5, 0.70
    q = 1.0 - delta
    D = 1.0 / beta - q
    nu = (1.0 - eta) / eta
    c_K = 0.5 ** (-1.5)
    H_a = ((2.0 * 0.5 / 1.5) ** 1.5) / 0.5
    A_rep = delta / H_a
    tau_opt = alpha_pub / (1.0 + alpha_pub)
    tau_min = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_rep, 1e-9, tau_opt)
    tau_max = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_rep, tau_opt, 1.0 - 1e-9)

    def planner_ss_resid(u, A_v):
        L = (D / (1.5 * A_v * (2.0 ** 1.5) * (u ** 0.5) * ((1.0 + u) ** (-2.5)))) ** 2
        if L >= 1.0:
            return -1e3 - L
        K = u * L
        C = F_A(A_v, K, L) - delta * K
        if C <= 0.0:
            return -1e3
        return dF_dL(A_v, K, L) * (1.0 - L) - nu * C

    A_SN = brentq(
        lambda Av: max(planner_ss_resid(u, Av) for u in np.geomspace(0.05, 1.5, 800)),
        0.095,
        0.105,
        xtol=1e-9,
    )
    tau_1_SN = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_SN, 1e-9, tau_opt)
    tau_2_SN = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_SN, tau_opt, 1.0 - 1e-9)

    # Global survival (Skiba/Maxwell) threshold A_* verified in verify_results.py
    A_star = 0.0996091
    tau_1 = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_star, 1e-9, tau_opt)
    tau_2 = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_star, tau_opt, 1.0 - 1e-9)
    tau_t8_lo = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - 0.749, 1e-9, tau_opt)
    tau_t8_hi = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - 0.749, tau_opt, 1.0 - 1e-9)

    A_cross = brentq(
        lambda Av: solve_endo_threshold_vfi(Av)[1] - ((D / c_K) ** 2) / (Av ** 2),
        0.100,
        0.120,
        xtol=2e-5,
    )
    tau_c1 = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_cross, 1e-9, tau_opt)
    tau_c2 = brentq(lambda t: A0 * (t ** alpha_pub) * (1.0 - t) - A_cross, tau_opt, 1.0 - 1e-9)

    A_max_curve = A0 * (tau_opt ** alpha_pub) * (1.0 - tau_opt)
    A_knots_lo = [0.09975, 0.0998, 0.1000, 0.1015, 0.1035, 0.1060, 0.1080, A_cross, 0.1125, 0.1160, 0.1200]
    A_knots_hi = [0.130, 0.150, 0.180, 0.220, 0.280, 0.360, 0.480, 0.620, A_max_curve]
    A_vfi_list, S_vfi_list = [], []
    for av in A_knots_lo:
        surv, Sv = solve_endo_threshold_vfi(float(av))
        if surv:
            A_vfi_list.append(float(av))
            S_vfi_list.append(float(Sv))
    for av in A_knots_hi:
        Sv = _solve_endo_threshold_norm(float(av))
        A_vfi_list.append(float(av))
        S_vfi_list.append(float(Sv))
    A_vfi_arr = np.array(A_vfi_list)
    S_vfi_arr = np.array(S_vfi_list)
    k_vfi_interp = PchipInterpolator(A_vfi_arr, (A_vfi_arr ** 2) * S_vfi_arr)

    fig3_data = {
        'A0': A0,
        'alpha_pub': alpha_pub,
        'delta': delta,
        'c_K': c_K,
        'D': D,
        'A_rep': A_rep,
        'tau_opt': tau_opt,
        'tau_min': tau_min,
        'tau_max': tau_max,
        'A_SN': A_SN,
        'tau_1_SN': tau_1_SN,
        'tau_2_SN': tau_2_SN,
        'A_star': A_star,
        'tau_1': tau_1,
        'tau_2': tau_2,
        'tau_t8_lo': tau_t8_lo,
        'tau_t8_hi': tau_t8_hi,
        'A_cross': A_cross,
        'tau_c1': tau_c1,
        'tau_c2': tau_c2,
        'A_min_vfi': float(A_vfi_arr[0]),
        'A_max_curve': A_max_curve,
        'k_vfi_interp': k_vfi_interp,
    }

    print("Precomputing VFI trajectories (Fig 4a) and Ruin Doob curve (Fig 4b)...")
    t_grid = np.arange(0, 45)
    fig4_data = {
        't_grid': t_grid,
        'N_f_star': (0.75 / A_star) ** 2,
        'traj_Nf1_g025': _solve_vfi_trajectory(0.75, K_0=0.06, g_rate=0.025, n_steps=44),
        'traj_Nf1_g0': _solve_vfi_trajectory(0.75, K_0=0.06, g_rate=0.0, n_steps=44),
        'traj_Nf2_g0': _solve_vfi_trajectory(0.75 / (2.0 ** 0.5), K_0=0.06, g_rate=0.0, n_steps=44),
        'traj_Nf60_g0': _solve_vfi_trajectory(0.75 / (60.0 ** 0.5), K_0=0.06, g_rate=0.0, n_steps=44),
        'doob': _compute_ruin_doob_data(),
    }
    return fig2_data, fig3_data, fig4_data


# ==============================================================================
# FIGURE 1: State-Dependent Affine Barrier vs. Milei-Reidel (2026) Barrier
# ==============================================================================
def make_fig1(lang):
    K_grid = np.linspace(B_M, H_M, 300)
    c_witness = Q_MIN * K_grid + F_A(A_MIN, K_grid, 0.68) - 0.135
    W_M_curve = box_worst_u(c_witness, 0.68) + BETA_MAX * (-33.103)
    Psi_sharp_curve = 0.4 * K_grid - 5.0 / np.sqrt(K_grid) - 18.5 - 10.0 / 301.0
    Psi_sharp_h = float(Psi_sharp_curve[-1])
    B_0_curve = np.full_like(K_grid, B_max_paper)
    B_1_curve = B_star_new - slope_min * (H_M - K_grid)

    T_vals = np.arange(1, 51)
    T_even = np.arange(2, 51, 2)
    prefix_paper = B_max_paper + (BETA_MAX ** T_even) * (-27.83 - B_max_paper)
    prefix_new_uniform = B_star_new + (BETA_MAX ** T_vals) * (-27.83 - B_star_new)
    prefix_new_exact = float(B_1_curve[0]) + (BETA_MAX ** T_vals) * (Psi_sharp_h - B_star_new)

    y_wm0 = float(W_M_curve[0])
    y_pp_46 = float(prefix_paper[T_even == 46][0])
    y_pu_24 = float(prefix_new_uniform[T_vals == 24][0])
    y_pe_23 = float(prefix_new_exact[T_vals == 23][0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.45), dpi=300)
    fig.subplots_adjust(wspace=0.26, bottom=0.15, top=0.87, left=0.08, right=0.97)

    if lang == 'es':
        lbl_psi = r'Techo de continuación $\Psi^\sharp(K) \geq V(K)$'
        lbl_wm = r'Testigo factible $W_M(K)$ (MR-Tabla 4)'
        lbl_b0 = r'Barrera 2 pasos $B_0$ (Milei-Reidel: $-38.14$)'
        lbl_b1 = r'Nueva barrera afín 1 paso $B_1(K)$ ($-43.36$ a $-43.05$)'
        ann_m0 = r'Margen original $\geq 2.564$'
        ann_gain = r'Ganancia adicional de calibración ($+4.90$ a $+5.21$)'
        xlab1 = r'Stock de capital en región de tránsito $K \in M = [0.10, 0.28)$'
        ylab1 = r'Bienestar descontado'
        tit1 = r'(a) Calibración de barreras regionales en $M = [0.10, 0.28)$'
        lbl_wmb = r'Piso del testigo $W_M(0.10) = -35.58$ (MR-Tabla 4)'
        lbl_pp = r'Cota de prefijo por pares (Milei-Reidel, $\tau_H \leq 46$)'
        lbl_pu = r'Nueva cota uniforme 1 paso ($\tau_H \leq 24$)'
        lbl_pe = r'Nueva cota estado a estado con $\Psi^\sharp$ ($\tau_H \leq 23$)'
        ann_new = r'$\tau_H \leq 23$–$24$' + '\n(Nuevo límite)'
        ann_old = r'$\tau_H \leq 46$' + '\n(Milei-Reidel)'
        xlab2 = r'Períodos consecutivos de permanencia en $M$ ($T$)'
        ylab2 = r'Cota superior de bienestar del prefijo'
        tit2 = r'(b) Reducción a la mitad del plazo máximo de entrada $\tau_H$'
    else:
        lbl_psi = r'Continuation ceiling $\Psi^\sharp(K) \geq V(K)$'
        lbl_wm = r'Feasible witness $W_M(K)$ (MR-Table 4)'
        lbl_b0 = r'2-step block bound $B_0$ (Milei-Reidel: $-38.14$)'
        lbl_b1 = r'New 1-step affine barrier $B_1(K)$ ($-43.36$ to $-43.05$)'
        ann_m0 = r'Original margin $\geq 2.564$'
        ann_gain = r'Additional calibration gain ($+4.90$ to $+5.21$)'
        xlab1 = r'Staging capital stock $K \in M = [0.10, 0.28)$'
        ylab1 = r'Discounted welfare'
        tit1 = r'(a) Regional barrier calibration on $M = [0.10, 0.28)$'
        lbl_wmb = r'Endpoint floor $W_M(0.10) = -35.58$ (MR-Table 4)'
        lbl_pp = r'Pairwise prefix bound (Milei-Reidel, $\tau_H \leq 46$)'
        lbl_pu = r'New 1-step uniform bound ($\tau_H \leq 24$)'
        lbl_pe = r'New state-matched bound with $\Psi^\sharp$ ($\tau_H \leq 23$)'
        ann_new = r'$\tau_H \leq 23$–$24$' + '\n(New deadline)'
        ann_old = r'$\tau_H \leq 46$' + '\n(Milei-Reidel)'
        xlab2 = r'Consecutive staying periods in $M$ ($T$)'
        ylab2 = r'Staying prefix welfare ceiling'
        tit2 = r'(b) Halving the certified entry deadline $\tau_H$'

    ax1.plot(K_grid, Psi_sharp_curve, color='#444444', linestyle=':', linewidth=1.6, label=lbl_psi)
    ax1.plot(K_grid, W_M_curve, color='#1b7837', linestyle='-', linewidth=2.0, label=lbl_wm)
    ax1.plot(K_grid, B_0_curve, color='#d95f02', linestyle='--', linewidth=1.8, label=lbl_b0)
    ax1.plot(K_grid, B_1_curve, color='#1f4e78', linestyle='-', linewidth=2.3, label=lbl_b1)
    ax1.fill_between(K_grid, B_0_curve, W_M_curve, color='#d95f02', alpha=0.10)
    ax1.fill_between(K_grid, B_1_curve, B_0_curve, color='#1f4e78', alpha=0.14)

    ax1.annotate(ann_m0, xy=(0.145, -36.85), xytext=(0.145, -36.85), fontsize=8.5, color='#b34800', fontweight='bold')
    ax1.annotate(ann_gain, xy=(0.116, -40.7), xytext=(0.116, -40.7), fontsize=8.5, color='#1f4e78', fontweight='bold')
    ax1.set_xlim(0.10, 0.28)
    ax1.set_ylim(-44.8, -23.5)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper left', fontsize=7.5, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, linestyle=':', alpha=0.35)

    ax2.axhline(y_wm0, color='#1b7837', linestyle='-', linewidth=1.8, label=lbl_wmb)
    ax2.plot(T_even, prefix_paper, 'o--', color='#d95f02', markersize=3.4, linewidth=1.6, label=lbl_pp)
    ax2.plot(T_vals, prefix_new_uniform, '-', color='#1f4e78', linewidth=2.0, label=lbl_pu)
    ax2.plot(T_vals, prefix_new_exact, '-.', color='#0b2c4d', linewidth=1.6, label=lbl_pe)
    ax2.axvline(46, color='#d95f02', linestyle=':', linewidth=1.2)
    ax2.axvline(23, color='#0b2c4d', linestyle=':', linewidth=1.2)
    ax2.axvline(24, color='#1f4e78', linestyle=':', linewidth=1.2)
    ax2.scatter([46], [y_pp_46], color='#d95f02', zorder=5, s=40)
    ax2.scatter([24], [y_pu_24], color='#1f4e78', zorder=5, s=40)
    ax2.scatter([23], [y_pe_23], color='#0b2c4d', zorder=5, s=40)

    ax2.annotate(ann_new, xy=(23.3, 0.5 * (y_pe_23 + y_pu_24)), xytext=(8.5, -39.0),
                 arrowprops=dict(arrowstyle='->', color='#1f4e78', lw=1.0),
                 fontsize=8.5, color='#1f4e78', fontweight='bold')
    ax2.annotate(ann_old, xy=(46, y_pp_46), xytext=(29.5, -40.2),
                 arrowprops=dict(arrowstyle='->', color='#d95f02', lw=1.0),
                 fontsize=8.5, color='#d95f02', fontweight='bold')
    ax2.set_xlim(1, 50)
    ax2.set_ylim(-41.5, -27.2)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='upper right', fontsize=7.4, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig1_barrier_{lang}.{ext}'), **kw)
    plt.close()


# ==============================================================================
# FIGURE 2: Asymptotic Scaling & Endogenous vs Fixed Labor (Footnote 1 & Thm 3*)
# ==============================================================================
def make_fig2(lang, fig2_data):
    A_vals = np.logspace(np.log10(0.70), np.log10(118.0), 300)
    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    r_exp = theta - 1.0
    c_K = w ** (theta / rho)
    nu = (1.0 - eta) / eta
    D = 1.0 / beta - (1.0 - delta)

    kappa_A = np.array([exact_kappa(a, delta) for a in A_vals])
    kappa_asymp = ((delta / c_K) ** (1.0 / r_exp)) * (A_vals ** (-1.0 / r_exp))
    S_upper_asymp = ((D / c_K) ** (1.0 / r_exp)) * (A_vals ** (-1.0 / r_exp))
    S_thm8_bound = 0.0014025025 / (A_vals ** 2)

    A_vfi = fig2_data['A_vfi']
    S_fix_vfi = fig2_data['S_fix']
    S_endo_vfi = fig2_data['S_endo']
    frontier_gap_vfi = fig2_data['frontier_gap']

    # Exact FOC curves evaluated at fixed benchmark point (k_b, c_b) = (0.002, 1e-4)
    k_b, c_b = 0.002, 0.0001
    K_crit = k_b * (A_vals ** (-1.0 / r_exp))
    C_crit = c_b * (A_vals ** (-1.0 / r_exp))
    L_star = np.array([
        brentq(lambda L: dF_dL(a, K_v, L) - nu * C_v / (1.0 - L), K_v / 3.0, 1.0 - 1e-12)
        for a, K_v, C_v in zip(A_vals, K_crit, C_crit)
    ])
    KL_ratio = K_crit / L_star
    leisure_cost = (1.0 - eta) * np.abs(np.log(1.0 - L_star))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.5), dpi=300)
    fig.subplots_adjust(wspace=0.27, bottom=0.15, top=0.87, left=0.08, right=0.97)

    if lang == 'es':
        l_sup = r'Envolvente asintótica $(D/c_K)^2 A^{-2}$'
        l_thm8 = r'Cota explícita Teorema 8 ($0.0014025/A^2$)'
        l_kap = r'Umbral físico exacto $\kappa_A$'
        l_kasy = r'Límite físico $(\delta/c_K)^2 A^{-2}$'
        l_band = r'Banda certificada Teo. 8 $(\kappa_A, 0.0014025/A^2)$'
        l_endo = r'Frontera VFI endógena $S_A^{\mathrm{endo}}$'
        l_fix = r'Frontera VFI trabajo fijo $S_A^{\mathrm{fix}}(1)$'
        inset_tit = r'Escala normalizada $A^2 S_A$'
        xlab1 = r'Productividad total de los factores $A$ (escala log)'
        ylab1 = r'Umbrales de capital $\kappa_A, S_A$ (escala log)'
        tit1 = r'(a) Ley de escalamiento $S_A = \Theta(A^{-1/(\theta-1)})$'
        l_L = r'Trabajo FOC en $(k,c)=(0.002,10^{-4})$: $L_A^* \propto A^{-1}$'
        l_loss = r'Costo de ocio en $(k,c)$: $(1-\eta)|\ln(1-L_A^*)| \propto A^{-1}$'
        l_KL = r'Razón $K_b(A)/L_A^*$ en $(k,c)$ ($\propto A^{-1} \to 0$)'
        l_fgap = r'Brecha VFI de fronteras $S_A^{\mathrm{endo}}/S_A^{\mathrm{fix}}(1) - 1$ (subpolinómica)'
        l_K = r'Capital fijo de referencia $K_b(A) = 0.002 A^{-2}$'
        ann_flat = (
            r'Brecha global VFI se aplana:' + '\n'
            + r'ascenso lento $O(1/\log\log A)$' + '\n'
            + r'vs. FOC local $\propto A^{-1}$'
        )
        xlab2 = r'Productividad total de los factores $A$ (escala log)'
        ylab2 = r'Magnitudes FOC $(k,c)=(0.002,10^{-4})$ y brecha VFI'
        tit2 = r'(b) Convergencia trabajo endógeno vs. fijo (Nota 1)'
    else:
        l_sup = r'Asymptotic envelope $(D/c_K)^2 A^{-2}$'
        l_thm8 = r'Theorem 8 explicit bound ($0.0014025/A^2$)'
        l_kap = r'Exact physical threshold $\kappa_A$'
        l_kasy = r'Physical asymptote $(\delta/c_K)^2 A^{-2}$'
        l_band = r'Theorem 8 certified band $(\kappa_A, 0.0014025/A^2)$'
        l_endo = r'VFI endogenous frontier $S_A^{\mathrm{endo}}$'
        l_fix = r'VFI fixed-labor frontier $S_A^{\mathrm{fix}}(1)$'
        inset_tit = r'Rescaled thresholds $A^2 S_A$'
        xlab1 = r'Total factor productivity $A$ (log scale)'
        ylab1 = r'Capital thresholds $\kappa_A, S_A$ (log scale)'
        tit1 = r'(a) Scaling law $S_A = \Theta(A^{-1/(\theta-1)})$'
        l_L = r'FOC labor at $(k,c)=(0.002,10^{-4})$: $L_A^* \propto A^{-1}$'
        l_loss = r'Leisure cost at $(k,c)$: $(1-\eta)|\ln(1-L_A^*)| \propto A^{-1}$'
        l_KL = r'Ratio $K_b(A)/L_A^*$ at $(k,c)$ ($\propto A^{-1} \to 0$)'
        l_fgap = r'VFI frontier gap $S_A^{\mathrm{endo}}/S_A^{\mathrm{fix}}(1) - 1$ (sub-polynomial)'
        l_K = r'Benchmark capital $K_b(A) = 0.002 A^{-2}$'
        ann_flat = (
            r'Global VFI gap flattens:' + '\n'
            + r'ultraslow $O(1/\log\log A)$ climb' + '\n'
            + r'vs. local FOC $\propto A^{-1}$'
        )
        xlab2 = r'Total factor productivity $A$ (log scale)'
        ylab2 = r'FOC magnitudes $(k,c)=(0.002,10^{-4})$ & VFI gap'
        tit2 = r'(b) Endogenous vs. fixed labor convergence (Footnote 1)'

    ax1.loglog(A_vals, S_upper_asymp, ':', color='#444444', linewidth=1.4, label=l_sup)
    ax1.loglog(A_vals, S_thm8_bound, '--', color='#d95f02', linewidth=1.7, label=l_thm8)
    ax1.loglog(A_vals, kappa_A, '-', color='#1b7837', linewidth=2.0, label=l_kap)
    ax1.loglog(A_vals, kappa_asymp, ':', color='#888888', linewidth=1.2, label=l_kasy)
    ax1.fill_between(A_vals, kappa_A, S_thm8_bound, color='#1f4e78', alpha=0.14, label=l_band)
    ax1.loglog(A_vfi, S_endo_vfi, 'o', color='#c00000', markersize=4.6, zorder=5, label=l_endo)
    ax1.loglog(A_vfi, S_fix_vfi, 's', markerfacecolor='none', markeredgecolor='#0b2c4d',
               markeredgewidth=1.25, markersize=6.4, zorder=6, label=l_fix)
    ax1.set_xlim(0.70, 118.0)
    ax1.set_ylim(2.5e-8, 6e-2)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper right', fontsize=6.6, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, which='both', linestyle=':', alpha=0.35)

    # Bottom-left inset resolving A^2 * S_A^{endo} vs A^2 * S_A^{fix}(1) inside Theorem 8 band
    ax1_in = inset_axes(ax1, width='36%', height='31%', loc='lower left',
                        bbox_to_anchor=(0.08, 0.07, 0.90, 0.90), bbox_transform=ax1.transAxes)
    ax1_in.semilogx(A_vals, (A_vals ** 2) * S_thm8_bound, '--', color='#d95f02', linewidth=1.2)
    ax1_in.semilogx(A_vals, (A_vals ** 2) * kappa_A, '-', color='#1b7837', linewidth=1.3)
    ax1_in.fill_between(A_vals, (A_vals ** 2) * kappa_A, (A_vals ** 2) * S_thm8_bound, color='#1f4e78', alpha=0.13)
    ax1_in.semilogx(A_vfi, fig2_data['kS_endo'], 'o-', color='#c00000', markersize=3.0, linewidth=1.1)
    ax1_in.semilogx(A_vfi, fig2_data['kS_fix'], 's--', markerfacecolor='none', markeredgecolor='#0b2c4d',
                    color='#0b2c4d', markeredgewidth=0.9, markersize=4.1, linewidth=0.95)
    ax1_in.set_xlim(0.70, 118.0)
    ax1_in.set_ylim(0.00075, 0.00148)
    ax1_in.set_yticks([0.0008, 0.0011, 0.0014])
    ax1_in.set_yticklabels(['8e-4', '1.1e-3', '1.4e-3'], fontsize=6.2)
    ax1_in.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    ax1_in.tick_params(axis='x', labelsize=6.2)
    ax1_in.set_title(inset_tit, fontsize=7.0, pad=2)
    ax1_in.grid(True, which='major', linestyle=':', alpha=0.35)

    ax2.loglog(A_vals, L_star, '-', color='#1f4e78', linewidth=2.1, label=l_L)
    ax2.loglog(A_vals, leisure_cost, ':', color='#7b3294', linewidth=2.0, label=l_loss)
    ax2.loglog(A_vals, KL_ratio, '--', color='#d95f02', linewidth=1.8, label=l_KL)
    ax2.loglog(A_vfi, frontier_gap_vfi, 'o-', color='#c00000', markersize=4.4, linewidth=1.7, label=l_fgap)
    ax2.loglog(A_vals, K_crit, '-.', color='#1b7837', linewidth=1.8, label=l_K)
    ax2.annotate(
        ann_flat,
        xy=(A_vfi[4], frontier_gap_vfi[4]),
        xytext=(10.5, 9.5e-6),
        arrowprops=dict(arrowstyle='->', color='#c00000', lw=1.0, connectionstyle='arc3,rad=-0.12'),
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#c00000', lw=0.7, alpha=0.95),
        fontsize=6.9,
        color='#9b0000',
        zorder=7,
    )
    ax2.set_xlim(0.70, 118.0)
    ax2.set_ylim(1.0e-7, 3.0)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.0)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='upper right', fontsize=6.6, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, which='both', linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig2_scaling_{lang}.{ext}'), **kw)
    plt.close()


# ==============================================================================
# FIGURE 3: Institutional U-Curve for Minimum Viable Scale (Section 5 / Thm 10)
# ==============================================================================
def make_fig3(lang, fig3_data):
    A0 = fig3_data['A0']
    alpha_pub = fig3_data['alpha_pub']
    delta = fig3_data['delta']
    c_K = fig3_data['c_K']
    D = fig3_data['D']
    A_rep = fig3_data['A_rep']
    tau_opt = fig3_data['tau_opt']
    tau_min = fig3_data['tau_min']
    tau_max = fig3_data['tau_max']
    A_SN = fig3_data['A_SN']
    A_star = fig3_data['A_star']
    tau_1 = fig3_data['tau_1']
    tau_2 = fig3_data['tau_2']
    tau_t8_lo = fig3_data['tau_t8_lo']
    tau_t8_hi = fig3_data['tau_t8_hi']
    tau_c2 = fig3_data['tau_c2']
    A_min_vfi = fig3_data['A_min_vfi']
    A_max_curve = fig3_data['A_max_curve']
    k_vfi_interp = fig3_data['k_vfi_interp']

    def A_e_fn(t):
        return A0 * (t ** alpha_pub) * (1.0 - t)

    tau_grid = np.concatenate([
        np.logspace(-7, np.log10(0.015), 250, endpoint=False),
        np.linspace(0.015, 0.98, 700),
    ])
    A_eff = A_e_fn(tau_grid)

    # Physical survival grid (tau_min, tau_max)
    mask_kap = (tau_grid > tau_min * 1.02) & (tau_grid < tau_max * 0.9999)
    tau_kap = tau_grid[mask_kap]
    A_kap = A_eff[mask_kap]
    kappa_tau = np.array([exact_kappa(a, delta) for a in A_kap])

    # Economic survival interval (tau_1, tau_2) densely sampled near both ends
    tau_S = np.unique(np.concatenate([
        np.geomspace(tau_1 * 1.005, 0.005, 140, endpoint=False),
        np.linspace(0.005, 0.90, 320, endpoint=False),
        np.linspace(0.90, tau_2 * 0.99995, 220),
    ]))
    A_S = A_e_fn(tau_S)
    S_asy_tau = ((D / c_K) ** 2) / (A_S ** 2)

    # Actual VFI S(tau) on A_e >= A_min_vfi
    tau_vfi_lo = brentq(lambda t: A_e_fn(t) - A_min_vfi, 1e-9, tau_opt)
    tau_vfi_hi = brentq(lambda t: A_e_fn(t) - A_min_vfi, tau_opt, 1.0 - 1e-9)
    tau_vfi = np.unique(np.concatenate([
        np.geomspace(tau_vfi_lo, 0.005, 120, endpoint=False),
        np.linspace(0.005, 0.90, 280, endpoint=False),
        np.linspace(0.90, tau_vfi_hi, 200),
    ]))
    A_vfi_curve = np.clip(A_e_fn(tau_vfi), A_min_vfi, A_max_curve)
    S_vfi_tau = np.asarray(k_vfi_interp(A_vfi_curve)) / (A_vfi_curve ** 2)

    # Theorem 8 finite-A certified upper bound on [tau_t8_lo, tau_t8_hi] (A_e >= 0.749)
    tau_t8 = np.linspace(tau_t8_lo, tau_t8_hi, 120)
    A_t8 = A_e_fn(tau_t8)
    S_t8_upper = 0.0014025025 / (A_t8 ** 2)
    kappa_t8 = np.array([exact_kappa(a, delta) for a in A_t8])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.5), dpi=300)
    fig.subplots_adjust(wspace=0.25, bottom=0.15, top=0.87, left=0.07, right=0.97)

    if lang == 'es':
        l_ae = r'Productividad neta $A_e(\tau) = A_0 \tau^\alpha (1-\tau)$'
        l_lin = r'Pérdida lineal $A_e(\tau^*) \frac{1-\tau}{1-\tau^*}$ (Sec. 4.3)'
        l_rep = rf'Umbral físico $A_{{\mathrm{{rep}}}} = {A_rep:.4f}$'
        l_astar = rf'Umbral global $A_* = {A_star:.4f}$'
        l_a749 = r'Cota Teorema 8 ($A_e \geq 0.749$)'
        l_opt = r'Carga óptima $\tau^* = \frac{\alpha}{1+\alpha} = 0.20$'
        l_pe = r'Extinción física ($A_e \leq A_{\mathrm{rep}}$)'
        l_ee = r'Extinción económica ($A_{\mathrm{rep}} < A_e \leq A_*$)'
        xlab1 = r'Carga tributaria / regulatoria $\tau \in (0, 1)$'
        ylab1 = r'Productividad efectiva $A_e(\tau)$'
        tit1 = r'(a) Regímenes físicos y económicos de $A_e(\tau)$'
        l_Svfi = r'Frontera real VFI $S(\tau)$ en $(\tau_{1,*}, \tau_{2,*})$'
        l_Sasy = r'Envolvente asintótica Teo. 3 $(D/c_K)^2 A_e^{-2}$'
        l_t8 = r'Cota certificada Teo. 8 ($[0.117, 0.305]$)'
        l_K = r'Piso físico $\kappa(\tau)$ en $(\tau_{\min}, \tau_{\max})$'
        l_ee2 = r'Extinción económica $(\tau_{\min}, \tau_{1,*}] \cup [\tau_{2,*}, \tau_{\max}]$'
        l_pe2 = r'Extinción física $[0, \tau_{\min}] \cup [\tau_{\max}, 1)$'
        ann_min = r'Mínimo en $\tau^* = 0.20$'
        inset_tit = rf'Cruce $\tau_{{c2}} = {tau_c2:.4f}$ y extinción'
        xlab2 = r'Carga tributaria / regulatoria $\tau \in (0, 1)$'
        ylab2 = r'Umbrales de capital $\kappa(\tau), S(\tau)$ (escala log)'
        tit2 = r'(b) Curva en U real $S(\tau)$, envolvente y extinción'
    else:
        l_ae = r'Net productivity $A_e(\tau) = A_0 \tau^\alpha (1-\tau)$'
        l_lin = r'Linear wedge $A_e(\tau^*) \frac{1-\tau}{1-\tau^*}$ (Sec. 4.3)'
        l_rep = rf'Physical floor $A_{{\mathrm{{rep}}}} = {A_rep:.4f}$'
        l_astar = rf'Global threshold $A_* = {A_star:.4f}$'
        l_a749 = r'Theorem 8 threshold ($A_e \geq 0.749$)'
        l_opt = r'Optimal burden $\tau^* = \frac{\alpha}{1+\alpha} = 0.20$'
        l_pe = r'Physical extinction ($A_e \leq A_{\mathrm{rep}}$)'
        l_ee = r'Economic extinction ($A_{\mathrm{rep}} < A_e \leq A_*$)'
        xlab1 = r'Fiscal / regulatory wedge $\tau \in (0, 1)$'
        ylab1 = r'Effective productivity $A_e(\tau)$'
        tit1 = r'(a) Physical and economic regimes of $A_e(\tau)$'
        l_Svfi = r'True VFI frontier $S(\tau)$ on $(\tau_{1,*}, \tau_{2,*})$'
        l_Sasy = r'Thm. 3 asymptotic envelope $(D/c_K)^2 A_e^{-2}$'
        l_t8 = r'Thm. 8 certified bound ($[0.117, 0.305]$)'
        l_K = r'Physical floor $\kappa(\tau)$ on $(\tau_{\min}, \tau_{\max})$'
        l_ee2 = r'Economic extinction $(\tau_{\min}, \tau_{1,*}] \cup [\tau_{2,*}, \tau_{\max}]$'
        l_pe2 = r'Physical extinction $[0, \tau_{\min}] \cup [\tau_{\max}, 1)$'
        ann_min = r'Minimum at $\tau^* = 0.20$'
        inset_tit = rf'Crossing $\tau_{{c2}} = {tau_c2:.4f}$ & extinction'
        xlab2 = r'Fiscal / regulatory wedge $\tau \in (0, 1)$'
        ylab2 = r'Capital thresholds $\kappa(\tau), S(\tau)$ (log scale)'
        tit2 = r'(b) True VFI U-curve $S(\tau)$, envelope & extinction'

    # Panel (a)
    ax1.plot(tau_grid, A_eff, '-', color='#1f4e78', linewidth=2.2, label=l_ae)
    ax1.plot(tau_grid, A_max_curve * (1.0 - tau_grid) / (1.0 - tau_opt), '--', color='#888888', linewidth=1.3, label=l_lin)
    ax1.axhline(A_rep, color='#c00000', linestyle=':', linewidth=1.5, label=l_rep)
    ax1.axhline(A_star, color='#d95f02', linestyle='-.', linewidth=1.4, label=l_astar)
    ax1.axhline(0.749, color='#7b3294', linestyle='--', linewidth=1.1, label=l_a749)
    ax1.axvline(tau_opt, color='#1b7837', linestyle='--', linewidth=1.2, label=l_opt)

    ax1.axvspan(0.0, tau_min, color='#c00000', alpha=0.22)
    ax1.axvspan(tau_max, 0.98, color='#c00000', alpha=0.22, label=l_pe)
    ax1.axvspan(tau_min, tau_1, color='#e69f00', alpha=0.26)
    ax1.axvspan(tau_2, tau_max, color='#e69f00', alpha=0.26, label=l_ee)
    ax1.scatter([tau_min, tau_max], [A_rep, A_rep], color='#c00000', s=24, zorder=5)
    ax1.scatter([tau_1, tau_2], [A_star, A_star], color='#d95f02', s=24, zorder=5)

    ax1.set_xlim(0.0, 0.98)
    ax1.set_ylim(0.0, 1.08)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper right', fontsize=6.6, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, linestyle=':', alpha=0.35)

    # Panel (b)
    ax2.semilogy(tau_vfi, S_vfi_tau, '-', color='#0b2c4d', linewidth=2.2, label=l_Svfi)
    ax2.semilogy(tau_S, S_asy_tau, '--', color='#3b73a8', linewidth=1.6, label=l_Sasy)
    ax2.semilogy(tau_t8, S_t8_upper, '-', color='#d95f02', linewidth=2.5, zorder=4, label=l_t8)
    ax2.fill_between(tau_t8, kappa_t8, S_t8_upper, color='#d95f02', alpha=0.22, zorder=3)
    ax2.semilogy(tau_kap, kappa_tau, '--', color='#1b7837', linewidth=1.7, label=l_K)
    ax2.axvline(tau_opt, color='#1b7837', linestyle=':', linewidth=1.2)

    ax2.axvspan(tau_min, tau_1, color='#e69f00', alpha=0.26)
    ax2.axvspan(tau_2, tau_max, color='#e69f00', alpha=0.26, label=l_ee2)
    ax2.axvspan(0.0, tau_min, color='#c00000', alpha=0.22)
    ax2.axvspan(tau_max, 0.98, color='#c00000', alpha=0.22, label=l_pe2)

    S_min_pt = float(k_vfi_interp(A_max_curve)) / (A_max_curve ** 2)
    ax2.scatter([tau_opt], [S_min_pt], color='#0b2c4d', s=32, zorder=5)
    ax2.annotate(ann_min, xy=(tau_opt, S_min_pt), xytext=(0.225, 0.0052),
                 ha='left',
                 arrowprops=dict(arrowstyle='->', color='#0b2c4d', lw=1.0),
                 bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92),
                 fontsize=7.8, color='#0b2c4d', fontweight='bold', zorder=7)

    ax2.set_xlim(0.0, 0.98)
    ax2.set_ylim(7e-4, 0.95)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='upper center', fontsize=6.3, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, which='both', linestyle=':', alpha=0.35)

    # Clean zoom inset around tau in [0.910, 0.955] showing S(tau) crossing above asymptotic envelope & economic extinction
    ax2_in = inset_axes(ax2, width='39%', height='27%', loc='center',
                        bbox_to_anchor=(0.08, 0.05, 0.90, 0.96), bbox_transform=ax2.transAxes)
    m_in_vfi = (tau_vfi >= 0.910) & (tau_vfi <= 0.955)
    m_in_asy = (tau_S >= 0.910) & (tau_S <= 0.955)
    m_in_kap = (tau_kap >= 0.910) & (tau_kap <= 0.955)
    ax2_in.semilogy(tau_vfi[m_in_vfi], S_vfi_tau[m_in_vfi], '-', color='#0b2c4d', linewidth=1.8)
    ax2_in.semilogy(tau_S[m_in_asy], S_asy_tau[m_in_asy], '--', color='#3b73a8', linewidth=1.4)
    ax2_in.semilogy(tau_kap[m_in_kap], kappa_tau[m_in_kap], '--', color='#1b7837', linewidth=1.4)
    ax2_in.axvspan(tau_2, tau_max, color='#e69f00', alpha=0.28)
    ax2_in.axvspan(tau_max, 0.955, color='#c00000', alpha=0.22)
    ax2_in.axvline(tau_c2, color='#444444', linestyle=':', linewidth=0.9)
    S_cross_pt = ((D / c_K) ** 2) / (A_e_fn(tau_c2) ** 2)
    ax2_in.scatter([tau_c2], [S_cross_pt], color='#c00000', s=18, zorder=6)
    ax2_in.set_xlim(0.910, 0.955)
    ax2_in.set_ylim(0.06, 0.30)
    ax2_in.set_xticks([0.91, 0.93, 0.95])
    ax2_in.set_yticks([0.07, 0.14, 0.25])
    ax2_in.set_yticklabels(['0.07', '0.14', '0.25'], fontsize=6.4)
    ax2_in.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    ax2_in.tick_params(axis='x', labelsize=6.4)
    ax2_in.set_title(inset_tit, fontsize=6.9, pad=2)
    ax2_in.grid(True, which='major', linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig3_ucurve_{lang}.{ext}'), **kw)
    plt.close()


# ==============================================================================
# FIGURE 4: Structural Extensions — Growth, Firm Scale N_f & Stochastic Barriers
# ==============================================================================
def make_fig4(lang, fig4_data):
    t_grid = fig4_data['t_grid']
    N_f_star = fig4_data['N_f_star']
    traj_Nf1_g025 = fig4_data['traj_Nf1_g025']
    traj_Nf1_g0 = fig4_data['traj_Nf1_g0']
    traj_Nf2_g0 = fig4_data['traj_Nf2_g0']
    traj_Nf60_g0 = fig4_data['traj_Nf60_g0']

    doob = fig4_data['doob']
    p_doob_grid = doob['p_grid']
    P_doob = doob['P_doob']
    p_cert = doob['p_cert']
    T_2pct = doob['T_2pct']
    P_doob_2pct = doob['P_doob_2pct']

    p_hazard = np.linspace(0.0, 0.0285, 285)
    surv_46 = (1.0 - p_hazard) ** 46
    surv_23 = (1.0 - p_hazard) ** 23
    surv_23_sub = (1.0 - p_doob_grid) ** 23
    P_23_2pct = (1.0 - 0.02) ** 23

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.5), dpi=300)
    fig.subplots_adjust(wspace=0.25, bottom=0.15, top=0.87, left=0.07, right=0.97)

    if lang == 'es':
        l_h = r'Crecimiento VFI «palo de hockey» ($N_f=1, g=0.025$)'
        l_s1 = r'Trayectoria VFI acotada por $K_p^+$ ($N_f=1, g=0$)'
        l_s2 = r'Supervivencia VFI con $N_f=2, g=0$ ($K_0=0.06 > S$)'
        l_f = rf'Extinción por fragmentación ($N_f=60 > N_{{f,*}}={N_f_star:.2f}$)'
        l_t = r'Umbral región productiva $\hat{h} = 0.28$'
        xlab1 = r'Períodos de tiempo $t$'
        ylab1 = r'Stock de capital real $K_t$ (escala log)'
        tit1 = r'(a) Trayectorias VFI: escala ($N_f$) y crecimiento ($g > 0$)'
        l_doob = r'Doob endógeno $(1-p)^{T^*(p)}$ (anticipando $\tilde{\beta}_p$)'
        l_23 = r'Cota Teorema 9* / MR-Tabla 4 $(1-p)^{23}$ ($p=0$ fijo)'
        l_46 = r'Bloques originales $(1-p)^{46}$ (Milei-Reidel)'
        l_cert = rf'Ruptura 1 paso $p_{{\mathrm{{cert}}}} \approx {100*p_cert:.2f}\%$'
        l_gap = r'Sobreestimación por ignorar anticipación'
        ann_2pct = f'p = 2.0%: T*={T_2pct}\n{100*P_doob_2pct:.1f}% vs. {100*P_23_2pct:.1f}%'
        xlab2 = r'Riesgo anual anticipado de colapso $p$ (%)'
        ylab2 = r'Probabilidad certificada de llegar a $H$ (%)'
        tit2 = r'(b) Certificado estocástico de Doob $T^*(p)$ frente a $T^*=23$'
    else:
        l_h = r'VFI hockey-stick growth ($N_f=1, g=0.025$)'
        l_s1 = r'VFI ceiling trajectory $K_p^+$ ($N_f=1, g=0$)'
        l_s2 = r'VFI survival with $N_f=2, g=0$ ($K_0=0.06 > S$)'
        l_f = rf'Fragmentation extinction ($N_f=60 > N_{{f,*}}={N_f_star:.2f}$)'
        l_t = r'Productive region threshold $\hat{h} = 0.28$'
        xlab1 = r'Time periods $t$'
        ylab1 = r'Real capital stock $K_t$ (log scale)'
        tit1 = r'(a) VFI paths: firm count ($N_f$) and growth ($g > 0$)'
        l_doob = r'Endogenous Doob $(1-p)^{T^*(p)}$ (anticipating $\tilde{\beta}_p$)'
        l_23 = r'Thm. 9* / MR-Table 4 bound $(1-p)^{23}$ (fixed $p=0$)'
        l_46 = r'Original block bound $(1-p)^{46}$ (Milei-Reidel)'
        l_cert = rf'1-step breakdown $p_{{\mathrm{{cert}}}} \approx {100*p_cert:.2f}\%$'
        l_gap = r'Overstatement if anticipation ignored'
        ann_2pct = f'p = 2.0%: T*={T_2pct}\n{100*P_doob_2pct:.1f}% vs. {100*P_23_2pct:.1f}%'
        xlab2 = r'Anticipated annual crisis hazard $p$ (%)'
        ylab2 = r'Certified probability of reaching $H$ (%)'
        tit2 = r'(b) Endogenous Stochastic Doob $T^*(p)$ vs. fixed $T^*=23$'

    ax1.semilogy(t_grid, traj_Nf1_g025, '-', color='#1f4e78', linewidth=2.3, label=l_h)
    ax1.semilogy(t_grid, traj_Nf1_g0, '--', color='#1b7837', linewidth=1.9, label=l_s1)
    ax1.semilogy(t_grid, traj_Nf2_g0, ':', color='#d95f02', linewidth=2.1, label=l_s2)
    ax1.semilogy(t_grid, traj_Nf60_g0, '-.', color='#c00000', linewidth=2.0, label=l_f)
    ax1.axhline(0.28, color='#555555', linestyle=':', linewidth=1.1, label=l_t)
    ax1.scatter([0], [0.06], color='#111111', s=24, zorder=6)
    ax1.set_xlim(0, 44)
    ax1.set_ylim(2e-3, 22.0)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='center right', bbox_to_anchor=(0.985, 0.34), fontsize=6.4, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, which='both', linestyle=':', alpha=0.35)

    ax2.plot(p_doob_grid * 100, P_doob * 100, '-', color='#1f4e78', linewidth=2.4, label=l_doob)
    ax2.plot(p_hazard * 100, surv_23 * 100, '--', color='#1b7837', linewidth=1.8, label=l_23)
    ax2.plot(p_hazard * 100, surv_46 * 100, '-.', color='#d95f02', linewidth=1.6, label=l_46)
    ax2.axvline(p_cert * 100, color='#c00000', linestyle=':', linewidth=1.6, label=l_cert)
    mask_over = surv_23_sub > P_doob
    ax2.fill_between(p_doob_grid[mask_over] * 100, P_doob[mask_over] * 100, surv_23_sub[mask_over] * 100,
                     color='#c00000', alpha=0.12, label=l_gap)
    ax2.scatter([2.0], [100 * P_doob_2pct], color='#1f4e78', s=34, zorder=5)
    ax2.scatter([2.0], [100 * P_23_2pct], color='#1b7837', s=28, zorder=5)
    ax2.annotate(ann_2pct, xy=(2.0, 100 * P_doob_2pct), xytext=(2.10, 9.0),
                 arrowprops=dict(arrowstyle='->', color='#1f4e78', lw=1.0),
                 bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#1f4e78', lw=0.7, alpha=0.95),
                 fontsize=7.3, color='#1f4e78', fontweight='bold')
    ax2.set_xlim(0, 2.85)
    ax2.set_ylim(-2, 105)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='lower left', fontsize=6.6, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig4_structural_{lang}.{ext}'), **kw)
    plt.close()


if __name__ == '__main__':
    fig2_data, fig3_data, fig4_data = precompute_figure_data()
    for lang in ['es', 'en']:
        make_fig1(lang)
        make_fig2(lang, fig2_data)
        make_fig3(lang, fig3_data)
        make_fig4(lang, fig4_data)
    print(f"Generated all 16 figure files cleanly in {OUT_DIR}")
