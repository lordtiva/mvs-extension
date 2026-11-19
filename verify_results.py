"""
Reproducible numerical & analytical interval verification script for:
  "State-Dependent Affine Bellman Barriers, Asymptotic Equivalence,
   and the Institutional U-Curve" (Marcelo Segura, 2026)

Verifies:
  1. Lemma 1, Theorem 9*, Proposition 1*, and Corollary 1* (one-step affine barriers, M0 anchor, & [beta_-, beta_+] continuum).
  2. Proposition 1** & Table 2 (outward-rounded interval arithmetic & Wronskian monotonicity without grid dependence).
  3. Theorem 3* & Table 3 (exact FOC scaling + 880-point two-zone continuous-state normalized VFI + escape-time check).
  4. Theorem 10, Table 4, & Proposition 2* (Barro-CES institutional U-curve, A_SN vs A_* extinction thresholds, & 2x2 Jacobians).
  5. Lemma 2, Proposition 4*, & Table 5 (Endogenous Doob deadlines T*(p), 2-state Markov barriers, and anticipating VFI).

Usage:
  python verify_results.py
"""

from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import math
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq, minimize


# ---------------------------------------------------------------------------
# Zero-dependency outward-rounded interval arithmetic (stdlib decimal)
# ---------------------------------------------------------------------------
class Interval:
    """Outward-rounded closed interval [lo, hi] using 50-digit Decimal arithmetic."""

    PREC = 50

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        self.lo = self._to_dec(lo, ROUND_FLOOR)
        self.hi = self._to_dec(hi, ROUND_CEILING)
        assert self.lo <= self.hi, f"Invalid interval [{self.lo}, {self.hi}]"

    @classmethod
    def _to_dec(cls, x, rounding):
        with localcontext() as ctx:
            ctx.prec = cls.PREC
            ctx.rounding = rounding
            if isinstance(x, Decimal):
                return +x
            if isinstance(x, int):
                return Decimal(x)
            if isinstance(x, str):
                return +Decimal(x)
            return +Decimal.from_float(float(x))

    @classmethod
    def _raw(cls, lo, hi):
        obj = cls.__new__(cls)
        obj.lo = lo
        obj.hi = hi
        return obj

    def __add__(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = self.lo + o.lo
            ctx.rounding = ROUND_CEILING
            hi = self.hi + o.hi
        return Interval._raw(lo, hi)

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return Interval._raw(-self.hi, -self.lo)

    def __sub__(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = self.lo - o.hi
            ctx.rounding = ROUND_CEILING
            hi = self.hi - o.lo
        return Interval._raw(lo, hi)

    def __rsub__(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        return o.__sub__(self)

    def __mul__(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        pairs = [(self.lo, o.lo), (self.lo, o.hi), (self.hi, o.lo), (self.hi, o.hi)]
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = min(a * b for a, b in pairs)
            ctx.rounding = ROUND_CEILING
            hi = max(a * b for a, b in pairs)
        return Interval._raw(lo, hi)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError("Interval divisor spans zero")
        pairs = [(self.lo, o.lo), (self.lo, o.hi), (self.hi, o.lo), (self.hi, o.hi)]
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = min(a / b for a, b in pairs)
            ctx.rounding = ROUND_CEILING
            hi = max(a / b for a, b in pairs)
        return Interval._raw(lo, hi)

    def __rtruediv__(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        return o.__truediv__(self)

    def sqrt(self):
        assert self.lo >= 0
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = self.lo.sqrt()
            ctx.rounding = ROUND_CEILING
            hi = self.hi.sqrt()
        return Interval._raw(lo, hi)

    def ln(self):
        assert self.lo > 0
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = self.lo.ln().next_minus()
            ctx.rounding = ROUND_CEILING
            hi = self.hi.ln().next_plus()
        return Interval._raw(lo, hi)

    def pow_int(self, n):
        assert isinstance(n, int) and n >= 0
        if n == 0:
            return Interval("1")
        if n == 1:
            return self
        if n % 2 == 0 and self.lo <= 0 <= self.hi:
            with localcontext() as ctx:
                ctx.prec = self.PREC
                ctx.rounding = ROUND_CEILING
                return Interval._raw(Decimal(0), max(abs(self.lo), abs(self.hi)) ** n)
        with localcontext() as ctx:
            ctx.prec = self.PREC
            ctx.rounding = ROUND_FLOOR
            lo = self.lo ** n
            ctx.rounding = ROUND_CEILING
            hi = self.hi ** n
        return Interval._raw(min(lo, hi), max(lo, hi))

    def pow_half_int(self, num_halves):
        if num_halves == 0:
            return Interval("1")
        k = abs(num_halves)
        p = self.pow_int(k // 2) if k % 2 == 0 else self.pow_int(k).sqrt()
        return p if num_halves > 0 else Interval("1") / p

    def abs(self):
        if self.lo >= 0:
            return self
        if self.hi <= 0:
            return -self
        return Interval._raw(Decimal(0), max(-self.lo, self.hi))

    def hull(self, other):
        o = other if isinstance(other, Interval) else Interval(other)
        return Interval._raw(min(self.lo, o.lo), max(self.hi, o.hi))

    def to_float_bounds(self):
        lo_f = float(self.lo)
        if Decimal.from_float(lo_f) > self.lo:
            lo_f = math.nextafter(lo_f, -math.inf)
        hi_f = float(self.hi)
        if Decimal.from_float(hi_f) < self.hi:
            hi_f = math.nextafter(hi_f, math.inf)
        return lo_f, hi_f


def iv_F_A(A, K, L):
    return A * (Interval("2") * K * L / (K + L)).pow_half_int(3)


def iv_box_worst_u(c, L):
    """Outward-rounded minimum period utility over eta in [0.6999, 0.7001] at interval (c, L)."""
    e_lo, e_hi = Interval("0.6999"), Interval("0.7001")
    one = Interval("1")
    lc = c.ln()
    ll = (one - L).ln()
    u1 = e_lo * lc + (one - e_lo) * ll
    u2 = e_hi * lc + (one - e_hi) * ll
    return Interval._raw(min(u1.lo, u2.lo), min(u1.hi, u2.hi))


def iv_E_plus_exact(A_hi, q_hi, K, a, l0):
    """Outward-rounded tangent adverse-exit envelope max_{eta in box} E^+(K, a; l0)."""
    one = Interval("1")
    two_3_2 = Interval("2").pow_half_int(3)
    t = Interval("1.5") * A_hi * two_3_2 * K.pow_half_int(5) * l0.pow_half_int(1) * (K + l0).pow_half_int(-5)
    S = q_hi * K + iv_F_A(A_hi, K, l0) + (one - l0) * t
    c_sup = S - a
    vals = []
    for eta in (Interval("0.6999"), Interval("0.7001")):
        om_raw = (one - eta) * c_sup / t
        om_L = Interval._raw(min(om_raw.lo, Decimal(1)), min(om_raw.hi, Decimal(1)))
        c_opt = c_sup - t * om_L
        vals.append(eta * c_opt.ln() + (one - eta) * om_L.ln())
    return Interval._raw(max(v.lo for v in vals), max(v.hi for v in vals))


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
    Y_lo = Q_MAX * x_lo + F_A(A_hi, x_lo, 1.0)
    Y_lo_ratio = Y_lo / x_lo
    assert Y_lo_ratio < b_max ** 2, f"Lower tail ratio {Y_lo_ratio:.6f} >= b_max^2 {b_max**2:.6f}"
    # Verify total discrepancy <= 0 at x = x_lo (including -(1 - b_max) * c_shift) and monotone upper bound on (0, x_lo]
    assert Y_lo < 1.0, f"Lower tail Y_lo={Y_lo:.6f} >= 1.0"
    d_lo_dx_lb = ETA_MIN / x_lo - a_c * (1.0 - b_max * Y_lo_ratio) + 0.5 * b_c * (b_max / np.sqrt(Y_lo_ratio) - 1.0) * (x_lo ** -1.5)
    assert d_lo_dx_lb > 0.0, f"Lower tail upper-bound derivative not positive at x_lo: {d_lo_dx_lb}"
    lo_val = (
        ETA_MIN * np.log(Y_lo)
        + b_max * (a_c * Y_lo - b_c * (Y_lo ** -0.5))
        - (a_c * x_lo - b_c * (x_lo ** -0.5))
        - (1.0 - b_max) * c_shift
    )
    assert lo_val <= 0.0, f"Lower tail discrepancy at x_lo positive: {lo_val}"
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
# 1. Lemma 1, Theorem 9*, Proposition 1* & Corollary 1*
# ---------------------------------------------------------------------------
def verify_barriers():
    print("=" * 72)
    print("1. LEMMA 1, THEOREM 9*, PROPOSITION 1* & COROLLARY 1* (AFFINE BARRIERS)")
    print("=" * 72)

    C_max_plus = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
    R_hat = -0.996
    Delta_2 = 0.2997
    Delta_2_exact = (ETA_MIN * BETA_MIN * Q_MIN * (H_M - B_M)) / C_max_plus

    B_star = (R_hat - Delta_2) / (1.0 - BETA_MIN)
    slope = (ETA_MIN * Q_MIN) / C_max_plus
    B1_b = B_star - slope * (H_M - B_M)

    # Exact MR-Table 4 witness floor W_M(0.10) from (l_M, s_M, T_M) = (0.68, 0.135, -33.103)
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

    # Corollary 1*: Sharpened M0 witness (0.05 -> 0.0595 -> 0.0755 -> 0.100), L=(0.45, 0.50, 0.60)
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

    # Corollary 1* unification with 25-step W_M^(0) and continuously certified Psi^(0) (a=0.45, b=5.0)
    _, _, _, eval_witness = build_25step_witness_builder()
    W_M_25_bmax, traj_25_bmax, _ = eval_witness(BETA_MAX, B_M, b_solve=BETA_MAX, eta_mode="outer")
    W_M_25_bmin, _, _ = eval_witness(BETA_MIN, B_M, b_solve=BETA_MIN, eta_mode="outer")
    W_M0_u1_25 = sum((BETA_MAX ** t) * u for t, u in enumerate(u1_us)) + (BETA_MAX ** 3) * W_M_25_bmax

    c0_bmax, d0_ub, d0_lb, tail0_marg = certify_psi_centered(A_MAX, BETA_MAX, 0.45, 5.0, tol=2e-4, buffer=0.0005)
    c0_bmin, d0_ub_min, _, tail0_marg_min = certify_psi_centered(A_MAX, BETA_MIN, 0.45, 5.0, tol=2e-4, buffer=0.0005)
    c0_unif = max(c0_bmax, c0_bmin)
    Psi0_10_unif = 0.45 * B_M - 5.0 * (B_M ** -0.5) + c0_unif
    Psi0_28_unif = 0.45 * H_M - 5.0 * (H_M ** -0.5) + c0_unif

    # Box-uniform independent endpoints (T=22, T0=9)
    J_T21_indep = B1_b + (BETA_MAX ** 21) * (Psi0_28_unif - B_star)
    J_T22_indep = B1_b + (BETA_MAX ** 22) * (Psi0_28_unif - B_star)

    # True continuous [BETA_MIN, BETA_MAX] 8-subinterval certification for tau_H <= 21 (Corollary 1*):
    # On each [bL, bR], certify a SINGLE Psi^(0) at both bL and bR (c0_j = max(c0(bL), c0(bR))),
    # bounded below by W_M(bR) (all r_t < 0 => decreasing in beta) and above by B_1(0.10; bL) + bR^21 * (Psi^(0)(0.28) - B_*(bR)).
    n_bsub = 8
    b_edges = np.linspace(BETA_MIN, BETA_MAX, n_bsub + 1)
    end_certs = {float(b): certify_psi_centered(A_MAX, float(b), 0.45, 5.0, tol=2e-4, buffer=0.0005) for b in b_edges}
    sub_gaps_T21 = []
    sub_trajs_R = []
    for j in range(n_bsub):
        bL, bR = float(b_edges[j]), float(b_edges[j + 1])
        c0_j = max(end_certs[bL][0], end_certs[bR][0])
        Psi0_28_j = 0.45 * H_M - 5.0 * (H_M ** -0.5) + c0_j
        WM_R, traj_R, _ = eval_witness(bR, B_M, b_solve=bR, eta_mode="outer")
        D2_L = (ETA_MIN * bL * Q_MIN * (H_M - B_M)) / C_max_plus
        Bs_L = (R_hat - D2_L) / (1.0 - bL)
        B1b_L = Bs_L - slope * (H_M - B_M)
        D2_R = (ETA_MIN * bR * Q_MIN * (H_M - B_M)) / C_max_plus
        Bs_R = (R_hat - D2_R) / (1.0 - bR)
        J21_ub = B1b_L + (bR ** 21) * (Psi0_28_j - Bs_R)
        sub_gaps_T21.append((bL, bR, c0_j, WM_R - J21_ub))
        sub_trajs_R.append((bL, bR, c0_j, traj_R))

    slope0 = (ETA_MIN * Q_MIN) / C_max0
    B0_1_grid = B0_star - slope0 * (h0 - k0_grid)
    J_T0_9_grid = B0_1_grid + (BETA_MAX ** 9) * (Psi0_10_unif - B0_star)
    J_T0_9_b0 = float(J_T0_9_grid[0])
    min_gap_T0_9 = float(np.min(W_M0_k0_grid - J_T0_9_grid))

    # Outward-rounded Interval cross-certification (Lemma 1, Theorem 9*, Proposition 1*, Corollary 1*)
    iv_A_MIN, iv_A_MAX = Interval("0.749"), Interval("0.751")
    iv_B_MIN, iv_B_MAX = Interval("0.9699"), Interval("0.9701")
    iv_Q_MIN, iv_Q_MAX = Interval("0.9199"), Interval("0.9201")
    iv_E_MIN, iv_E_MAX = Interval("0.6999"), Interval("0.7001")
    iv_B_M, iv_H_M = Interval("0.10"), Interval("0.28")
    iv_one = Interval("1")

    iv_C_max_plus = iv_Q_MAX * iv_H_M + iv_F_A(iv_A_MAX, iv_H_M, iv_one) - iv_B_M
    iv_Delta_2_exact = (iv_E_MIN * iv_B_MIN * iv_Q_MIN * (iv_H_M - iv_B_M)) / iv_C_max_plus
    iv_B_star = (Interval("-0.996") - Interval("0.2997")) / (iv_one - iv_B_MIN)
    iv_slope = (iv_E_MIN * iv_Q_MIN) / iv_C_max_plus
    iv_B1_b = iv_B_star - iv_slope * (iv_H_M - iv_B_M)
    iv_c_M_10 = iv_Q_MIN * iv_B_M + iv_F_A(iv_A_MIN, iv_B_M, Interval("0.68")) - Interval("0.135")
    iv_W_M_10 = iv_box_worst_u(iv_c_M_10, Interval("0.68")) + iv_B_MAX * Interval("-33.103")
    iv_margin_unif = Interval("-35.58") - iv_B_star
    iv_margin_state = Interval("-35.58") - iv_B1_b
    iv_J_T24 = iv_B_star + iv_B_MAX.pow_int(24) * (Interval("-27.83") - iv_B_star)
    iv_slack_T23 = (Interval("-35.58") - iv_B1_b) - iv_B_MAX.pow_int(23) * (Interval("-27.83") - iv_B_star)

    iv_b0, iv_h0 = Interval("0.05"), Interval("0.10")
    iv_C_max0 = iv_Q_MAX * iv_h0 + iv_F_A(iv_A_MAX, iv_h0, iv_one) - iv_b0
    iv_Delta_0_exact = (iv_E_MIN * iv_B_MIN * iv_Q_MIN * (iv_h0 - iv_b0)) / iv_C_max0
    iv_B0_star = (Interval("-1.827") - Interval("0.3115")) / (iv_one - iv_B_MIN)
    iv_orig_us = [
        iv_box_worst_u(iv_Q_MIN * Interval(str(k)) + iv_F_A(iv_A_MIN, Interval(str(k)), Interval(str(L))) - Interval(str(kp)), Interval(str(L)))
        for k, kp, L in orig_steps
    ]
    iv_W_M0_orig = iv_orig_us[0] + iv_B_MAX * iv_orig_us[1] + iv_B_MAX.pow_int(2) * iv_orig_us[2] + iv_B_MAX.pow_int(3) * iv_W_M_10
    iv_u1_us = [
        iv_box_worst_u(iv_Q_MIN * Interval(str(k)) + iv_F_A(iv_A_MIN, Interval(str(k)), Interval(str(L))) - Interval(str(kp)), Interval(str(L)))
        for k, kp, L in u1_steps
    ]
    iv_W_M0_u1_old = iv_u1_us[0] + iv_B_MAX * iv_u1_us[1] + iv_B_MAX.pow_int(2) * iv_u1_us[2] + iv_B_MAX.pow_int(3) * iv_W_M_10

    def iv_eval_traj(traj_pts, b_iv):
        rs_iv = []
        for ii, (K_p, L_p, Kp_p) in enumerate(traj_pts):
            Kn_p = Kp_p if ii + 1 < len(traj_pts) else K_p
            c_iv = iv_Q_MIN * Interval(K_p) + iv_F_A(iv_A_MIN, Interval(K_p), Interval(L_p)) - Interval(Kn_p)
            ec_iv = iv_E_MAX if c_iv.hi < 1 else (iv_E_MIN if c_iv.lo >= 1 else iv_E_MIN.hull(iv_E_MAX))
            rs_iv.append(ec_iv * c_iv.ln() + (iv_one - iv_E_MIN) * (iv_one - Interval(L_p)).ln())
        tot = Interval("0")
        for tt, r_iv in enumerate(rs_iv[:-1]):
            tot = tot + b_iv.pow_int(tt) * r_iv
        return tot + b_iv.pow_int(len(rs_iv) - 1) * rs_iv[-1] / (iv_one - b_iv)

    iv_sub_min_gap = Decimal("1e9")
    for bL, bR, c0_j, traj_R in sub_trajs_R:
        iv_bL, iv_bR = Interval(bL), Interval(bR)
        iv_WM_R = iv_eval_traj(traj_R, iv_bR)
        iv_D2_L = (iv_E_MIN * iv_bL * iv_Q_MIN * (iv_H_M - iv_B_M)) / iv_C_max_plus
        iv_Bs_L = (Interval("-0.996") - iv_D2_L) / (iv_one - iv_bL)
        iv_B1b_L = iv_Bs_L - iv_slope * (iv_H_M - iv_B_M)
        iv_D2_R = (iv_E_MIN * iv_bR * iv_Q_MIN * (iv_H_M - iv_B_M)) / iv_C_max_plus
        iv_Bs_R = (Interval("-0.996") - iv_D2_R) / (iv_one - iv_bR)
        iv_Psi28 = Interval("0.45") * iv_H_M - Interval("5.0") * iv_H_M.pow_half_int(-1) + Interval(c0_j)
        iv_J21_ub = iv_B1b_L + iv_bR.pow_int(21) * (iv_Psi28 - iv_Bs_R)
        iv_gap = iv_WM_R - iv_J21_ub
        assert iv_gap.lo > 0, f"Outward-rounded T=21 subinterval [{bL},{bR}] failed: {iv_gap.lo}"
        iv_sub_min_gap = min(iv_sub_min_gap, iv_gap.lo)

    assert iv_Delta_2_exact.lo > Decimal("0.2997")
    assert iv_B_star.hi <= Decimal("-43.0465115") and iv_B1_b.hi <= Decimal("-43.355593")
    assert iv_W_M_10.lo > Decimal("-35.58")
    assert iv_margin_unif.lo > Decimal("7.4665") and iv_margin_state.lo > Decimal("7.77559")
    assert iv_J_T24.hi < Decimal("-35.58") and iv_slack_T23.lo > Decimal("0.2056")
    assert iv_Delta_0_exact.lo > Decimal("0.3115") and iv_B0_star.hi <= Decimal("-71.0465115")
    assert iv_W_M0_orig.lo > Decimal("-43.845") and iv_W_M0_u1_old.lo > Decimal("-43.541")

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
    print(f"  Cor. 1* M0 path u = {[round(x, 6) for x in u1_us]}")
    print(f"    W_M0(0.05; old tail)   = {W_M0_u1_old:.6f} (all K0 in [0.05, 0.10) temp. liq. >= {W_M0_k0_grid[0]:.6f})")
    print(f"    W_M0(0.05; 25-st tail) = {W_M0_u1_25:.6f} (using W_M^(0)(0.10; beta_+) = {W_M_25_bmax:.6f})")
    print(f"  Cor. 1* Psi^(0) cert : c0(b+)={c0_bmax:.6f}, c0_unif(box)={c0_unif:.6f} (B&B d(b+) in [{d0_lb:.6f}, {d0_ub:.6f}], tail={min(tail0_marg, tail0_marg_min):.4f})")
    print(f"    Psi^(0)_unif(0.10) = {Psi0_10_unif:.6f}, Psi^(0)_unif(0.28) = {Psi0_28_unif:.6f}")
    print(f"    tau_.1 <= 9 (box-unif B^(0)): J(9;0.05) = {J_T0_9_b0:.6f} < {W_M0_u1_old:.6f} (min gap on M0 = +{min_gap_T0_9:.4f})")
    print(f"    tau_H param (indep box): T=21 gap = {W_M_25_bmax - J_T21_indep:+.6f} (fails), T=22 gap = {W_M_25_bmax - J_T22_indep:+.6f} (passes)")
    print(f"    tau_H param ({n_bsub}-subinterval continuum [0.9699, 0.9701], single Psi^(0) per subinterval): T=21 min gap = +{min(g for _, _, _, g in sub_gaps_T21):.6f} (Interval lb = +{float(iv_sub_min_gap):.6f})")

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
    assert all(g > 0.02 for _, _, _, g in sub_gaps_T21)


def verify_restricted_M_vfi():
    """Compare tau_H <= 23 against the exact restricted DP on M=[0.10, 0.28),
    the optimal regional staying barrier B_opt, and unrestricted VFI entry times."""
    print("\n  [Slack decomposition on M = [0.10, 0.28): B_1 vs B_opt / Restricted DP / VFI]")
    M_grid = np.linspace(B_M, H_M - 1e-5, 181)
    inv_phi = (np.sqrt(5.0) - 1.0) / 2.0

    def _rho_mat(A_v, q_v, e_v=None):
        lo = np.full((len(M_grid), len(M_grid)), 1e-8)
        hi = np.full((len(M_grid), len(M_grid)), 1.0 - 1e-9)

        def _gu(La):
            c = q_v * M_grid[:, None] + F_A(A_v, M_grid[:, None], La) - M_grid[None, :]
            lc = np.log(np.maximum(c, 1e-30))
            ll = np.log(1.0 - La)
            if e_v is None:
                uv = np.maximum(ETA_MIN * lc + (1.0 - ETA_MIN) * ll, ETA_MAX * lc + (1.0 - ETA_MAX) * ll)
            else:
                uv = e_v * lc + (1.0 - e_v) * ll
            return np.where(c > 1e-15, uv, -1e9 + c)

        u0 = _gu(np.zeros_like(lo))
        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        f1, f2 = _gu(x1), _gu(x2)
        for _ in range(20):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
            f1n = np.where(mr, f2, _gu(x1n))
            f2n = np.where(mr, _gu(x2n), f1)
            x1, x2, f1, f2 = x1n, x2n, f1n, f2n
        return np.maximum(u0, _gu(0.5 * (lo + hi)))

    # 1. Exact box-upper restricted DP (Psi^sharp vs MR-Table 4 W_M) and optimal staying barrier B_opt
    Psi_sharp = 0.4 * M_grid - 5.0 * (M_grid ** (-0.5)) - 18.5 - 10.0 / 301.0
    c_M = Q_MIN * M_grid + F_A(A_MIN, M_grid, 0.68) - 0.135
    W_M_lb = box_worst_u(c_M, 0.68) + BETA_MAX * (-33.103)
    rho_up = _rho_mat(A_MAX, Q_MAX, e_v=None)

    J_dp = Psi_sharp.copy()
    gaps_dp = {}
    for T in range(1, 12):
        J_dp = np.max(rho_up + BETA_MAX * J_dp[None, :], axis=1)
        gaps_dp[T] = float(np.max(J_dp - W_M_lb))

    B_opt = np.full_like(M_grid, -40.0)
    for _ in range(1000):
        Bn = np.max(rho_up + BETA_MIN * B_opt[None, :], axis=1)
        if np.max(np.abs(Bn - B_opt)) < 1e-10:
            B_opt = Bn
            break
        B_opt = Bn
    inf_W_B = float(np.min(W_M_lb - B_opt))
    sup_Psi_B = float(np.max(Psi_sharp - B_opt))
    gap_Bopt_T8 = inf_W_B - (BETA_MAX ** 8) * sup_Psi_B
    gap_Bopt_T9 = inf_W_B - (BETA_MAX ** 9) * sup_Psi_B

    # 2. Unrestricted center VFI (A=0.75, beta=0.97, q=0.92, eta=0.70) and true restricted DP vs V
    A_c, b_c, q_c, e_c = 0.75, 0.97, 0.92, 0.70
    K_g = np.unique(np.concatenate([
        np.geomspace(1e-4, 0.095, 100, endpoint=False),
        np.linspace(0.095, 0.285, 190, endpoint=False),
        np.geomspace(0.285, 4.0, 220),
    ]))
    solve_L_c = lambda ka, kpa: _golden_solve_L(ka, kpa, lambda k, L: F_A(A_c, k, L), q_c, e_c)

    def _iv(kp, Va):
        r = np.interp(np.clip(kp, K_g[0], K_g[-1]), K_g, Va)
        return np.where(kp < K_g[0], Va[0] + (e_c / (1.0 - b_c)) * np.log(np.maximum(kp, 1e-30) / K_g[0]), r)

    y_max = q_c * K_g + F_A(A_c, K_g, 0.9999)
    s_cand = 1.0 - np.geomspace(1e-5, 0.25, 65)
    kp_c = y_max[:, None] * s_cand[None, :]
    u_c = np.zeros_like(kp_c)
    for j in range(len(s_cand)):
        _, u_c[:, j] = solve_L_c(K_g, kp_c[:, j])
    V_cake0 = (e_c / (1.0 - b_c)) * (np.log((1.0 - b_c) * q_c) + (b_c / (1.0 - b_c)) * np.log(b_c * q_c))
    V_c = np.where(K_g > 0.002, -30.0, V_cake0 + (e_c / (1.0 - b_c)) * np.log(K_g))
    for _ in range(120):
        Vn = np.max(u_c + b_c * _iv(kp_c, V_c), axis=1)
        if np.max(np.abs(Vn - V_c)) < 1e-7:
            V_c = Vn
            break
        V_c = Vn
    for _ in range(80):
        idx = np.argmax(u_c + b_c * _iv(kp_c, V_c), axis=1)
        lo = y_max * s_cand[np.maximum(0, idx - 1)]
        hi = y_max * s_cand[np.minimum(len(s_cand) - 1, idx + 1)]
        x1 = hi - inv_phi * (hi - lo)
        x2 = lo + inv_phi * (hi - lo)
        _, u1 = solve_L_c(K_g, x1)
        _, u2 = solve_L_c(K_g, x2)
        f1 = u1 + b_c * _iv(x1, V_c)
        f2 = u2 + b_c * _iv(x2, V_c)
        for _g in range(18):
            mr = f1 < f2
            lo = np.where(mr, x1, lo)
            hi = np.where(mr, hi, x2)
            x1 = np.where(mr, x2, hi - inv_phi * (hi - lo))
            x2 = np.where(mr, lo + inv_phi * (hi - lo), x1)
            _, u1n = solve_L_c(K_g, x1)
            _, u2n = solve_L_c(K_g, x2)
            f1 = np.where(mr, f2, u1n + b_c * _iv(x1, V_c))
            f2 = np.where(mr, u2n + b_c * _iv(x2, V_c), f1)
        pol_c = 0.5 * (lo + hi)
        _, up = solve_L_c(K_g, pol_c)
        Vn = up + b_c * _iv(pol_c, V_c)
        for _h in range(40):
            Vh = up + b_c * _iv(pol_c, Vn)
            if np.max(np.abs(Vh - Vn)) < 1e-10:
                Vn = Vh
                break
            Vn = Vh
        if np.max(np.abs(Vn - V_c)) < 1e-9:
            V_c = Vn
            break
        V_c = Vn

    max_tau_vfi = 0
    for k0 in M_grid:
        k = float(k0)
        t = 0
        while k < H_M and t < 50:
            k = float(np.interp(k, K_g, pol_c))
            t += 1
        max_tau_vfi = max(max_tau_vfi, t)

    V_M_true = np.interp(M_grid, K_g, V_c)
    rho_c = _rho_mat(A_c, q_c, e_v=e_c)
    J_true = V_M_true.copy()
    gaps_true = {}
    for T in range(1, 7):
        J_true = np.max(rho_c + b_c * J_true[None, :], axis=1)
        gaps_true[T] = (float(np.max(J_true - V_M_true)), float(J_true[0] - V_M_true[0]))

    print(f"    Box-upper restricted DP (Psi^sharp vs W_M): T=8 gap={gaps_dp[8]:+.6f}, T=9 gap={gaps_dp[9]:+.6f} (tau_H^DP = 9)")
    print(f"    Optimal regional barrier B_opt on M: [{B_opt[0]:.6f}, {B_opt[-1]:.6f}] -> T=8 gap={gap_Bopt_T8:+.6f}, T=9 gap={gap_Bopt_T9:+.6f}")
    print(f"    Center VFI (A=0.75, beta=0.97): V(0.10)={V_M_true[0]:.6f}, max_{{K0 in M}} tau_H^VFI = {max_tau_vfi}")
    print(f"    True restricted DP vs V(K): T=1..6 max = {[round(gaps_true[t][0], 6) for t in range(1, 7)]}")
    print(f"      at K0=0.10: T=1..6 = {[round(gaps_true[t][1], 6) for t in range(1, 7)]}")

    assert gaps_dp[8] > 0.0 and gaps_dp[9] < -0.50
    assert abs(B_opt[0] - (-56.794979)) < 1e-4 and abs(B_opt[-1] - (-52.457990)) < 1e-4
    assert gap_Bopt_T8 < 0.0 and gap_Bopt_T9 > 0.45
    assert max_tau_vfi == 4
    assert gaps_true[4][0] < -0.15 and gaps_true[5][0] < -0.70


# ---------------------------------------------------------------------------
# 2. Proposition 1** (Analytical interval arithmetic & Wronskian monotonicity)
# ---------------------------------------------------------------------------
def t_func(K, l0):
    return dF_dL(A_MAX, K, l0)


def t_prime(K, l0):
    return 1.5 * A_MAX * (2.0 ** 1.5) * 2.5 * (K ** 1.5) * (l0 ** 1.5) * ((K + l0) ** (-3.5))


def t_double_prime(K, l0):
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

    # Outward-rounded Interval helpers for Proposition 1** cross-certification
    iv_A_MIN, iv_A_MAX = Interval("0.749"), Interval("0.751")
    iv_Q_MIN, iv_Q_MAX = Interval("0.9199"), Interval("0.9201")
    iv_E_MIN, iv_E_MAX = Interval("0.6999"), Interval("0.7001")
    iv_B_MIN, iv_B_MAX = Interval("0.9699"), Interval("0.9701")
    iv_one = Interval("1")
    iv_two32 = Interval("2").pow_half_int(3)
    iv_sq73 = Interval("73").sqrt()
    iv_sq63 = Interval("63").sqrt()

    def iv_dFdK(A, K, L):
        return Interval("1.5") * A * iv_two32 * K.pow_half_int(1) * L.pow_half_int(5) * (K + L).pow_half_int(-5)

    def iv_d2FdK2(A, K, L):
        return Interval("0.75") * A * iv_two32 * L.pow_half_int(5) * (L - Interval("4") * K) * K.pow_half_int(-1) * (K + L).pow_half_int(-7)

    def iv_dFdL(A, K, L):
        return Interval("1.5") * A * iv_two32 * K.pow_half_int(5) * L.pow_half_int(1) * (K + L).pow_half_int(-5)

    def iv_tp(K, l0):
        return Interval("1.5") * iv_A_MAX * iv_two32 * Interval("2.5") * K.pow_half_int(3) * l0.pow_half_int(3) * (K + l0).pow_half_int(-7)

    def iv_tpp(K, l0):
        return Interval("1.5") * iv_A_MAX * iv_two32 * Interval("2.5") * l0.pow_half_int(3) * K.pow_half_int(1) * (K + l0).pow_half_int(-9) * (Interval("1.5") * l0 - Interval("2") * K)

    def iv_clip_pt(kc, kL, kR):
        if kc.hi <= kL.lo or kc.lo >= kR.hi:
            return None
        return Interval._raw(max(kc.lo, kL.lo), min(kc.hi, kR.hi))

    for name, cfg in regions.items():
        l_X, s_X, _, a, l0 = cfg["l_X"], cfg["s_X"], cfg["T_X"], cfg["a"], cfg["l0"]
        assert l0 >= cfg["k_max"] / 2.0, f"Global tangency dominance l0 >= sup(X)/2 failed on {name}"
        if name == "M":
            edges_q = np.linspace(cfg["k_min"], cfg["k_max"], cfg["n_q"] + 1)
            edges_q_str = ["0.10", "0.145", "0.19", "0.235", "0.28"]
            edges_d2_str = [str(Decimal("0.10") + Decimal(i) * Decimal("0.0225")) for i in range(9)]
        else:
            edges_q = np.array([0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80])
            edges_q_str = ["0.28", "0.36", "0.45", "0.54", "0.63", "0.72", "0.80"]
            edges_d2_str = [str(Decimal("0.28") + Decimal(i) * Decimal("0.052")) for i in range(11)]

        iv_lX, iv_sX, iv_a, iv_l0 = Interval(str(l_X)), Interval(str(s_X)), Interval(str(a)), Interval(str(l0))
        iv_S = lambda K: iv_Q_MAX * K + iv_F_A(iv_A_MAX, K, iv_l0) + (iv_one - iv_l0) * iv_dFdL(iv_A_MAX, K, iv_l0)
        iv_Sp = lambda K: iv_Q_MAX + iv_dFdK(iv_A_MAX, K, iv_l0) + (iv_one - iv_l0) * iv_tp(K, iv_l0)
        iv_c = lambda K: iv_Q_MIN * K + iv_F_A(iv_A_MIN, K, iv_lX) - iv_sX
        iv_cp = lambda K: iv_Q_MIN + iv_dFdK(iv_A_MIN, K, iv_lX)

        Q_bounds, iv_Q_bounds = [], []
        d1_bounds, iv_d1_bounds = [], []
        for (kL, kR), (kLs, kRs) in zip(zip(edges_q[:-1], edges_q[1:]), zip(edges_q_str[:-1], edges_q_str[1:])):
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

            # Outward-rounded Interval cross-certification of Q_X and Delta'_X
            ikL, ikR = Interval(kLs), Interval(kRs)
            ikm = Interval("0.5") * (ikL + ikR)
            iQm = iv_Sp(ikm) * iv_c(ikm) - iv_cp(ikm) * (iv_S(ikm) - iv_a)
            id2F = [ikL, ikR]
            for sgn in (Interval("-1"), Interval("1")):
                pt_c = iv_clip_pt(iv_l0 * (Interval("7") + sgn * iv_sq73) / Interval("24"), ikL, ikR)
                if pt_c is not None:
                    id2F.append(pt_c)
            ikc_q = iv_l0 / Interval("4")
            if (pt_q := iv_clip_pt(ikc_q, ikL, ikR)) is not None:
                id2F.append(pt_q)
            itpp = [ikL, ikR]
            for sgn in (Interval("-1"), Interval("1")):
                pt_c = iv_clip_pt(iv_l0 * (Interval("9") + sgn * iv_sq63) / Interval("12"), ikL, ikR)
                if pt_c is not None:
                    itpp.append(pt_c)
            ikc_t = Interval("0.75") * iv_l0
            if (pt_t := iv_clip_pt(ikc_t, ikL, ikR)) is not None:
                itpp.append(pt_t)
            id2Fc = [ikL, ikR]
            for sgn in (Interval("-1"), Interval("1")):
                pt_c = iv_clip_pt(iv_lX * (Interval("7") + sgn * iv_sq73) / Interval("24"), ikL, ikR)
                if pt_c is not None:
                    id2Fc.append(pt_c)
            if (pt_c := iv_clip_pt(iv_lX / Interval("4"), ikL, ikR)) is not None:
                id2Fc.append(pt_c)
            iSpp_hi = max(iv_d2FdK2(iv_A_MAX, pt, iv_l0).abs().hi for pt in id2F) + (iv_one - iv_l0).hi * max(iv_tpp(pt, iv_l0).abs().hi for pt in itpp)
            icpp_hi = max(iv_d2FdK2(iv_A_MIN, pt, iv_lX).abs().hi for pt in id2Fc)
            iQp_max = Interval(iSpp_hi) * iv_c(ikR) + Interval(icpp_hi) * (iv_S(ikR) - iv_a)
            iQ_ub = iQm + Interval("0.5") * (ikR - ikL) * iQp_max
            iv_Q_bounds.append(iQ_ub.to_float_bounds()[1])
            assert iQ_ub.hi < 0, f"Interval Q_ub >= 0 on [{kLs},{kRs}]: {iQ_ub.hi}"

            icp_min = Interval(min(iv_cp(ikL).lo, iv_cp(ikR).lo))
            ic_dFk = [ikL, ikR] + ([pt_q] if (pt_q := iv_clip_pt(ikc_q, ikL, ikR)) is not None else [])
            ic_tp = [ikL, ikR] + ([pt_t] if (pt_t := iv_clip_pt(ikc_t, ikL, ikR)) is not None else [])
            iSp_max = iv_Q_MAX + Interval(max(iv_dFdK(iv_A_MAX, p, iv_l0).hi for p in ic_dFk)) + (iv_one - iv_l0) * Interval(max(iv_tp(p, iv_l0).hi for p in ic_tp))
            iR_lb = (iv_S(ikR) - iv_a) / iv_c(ikR)
            inum_lb = iv_E_MIN * icp_min * iR_lb - iSp_max
            iS_aL, iS_aR = iv_S(ikL) - iv_a, iv_S(ikR) - iv_a
            idenom = iS_aR if inum_lb.lo >= 0 else (iS_aL if inum_lb.hi <= 0 else iS_aL.hull(iS_aR))
            id1_lb = inum_lb / idenom + (iv_one - iv_E_MAX) * Interval("2.5") * iv_l0 / (ikR * (ikR + iv_l0))
            iv_d1_bounds.append(id1_lb.to_float_bounds()[0])
            assert id1_lb.lo > 0, f"Interval Delta'_X <= 0 on [{kLs},{kRs}]: {id1_lb.lo}"

        # Second derivative interval bounds on n_d2 equal subintervals
        edges_d2 = np.linspace(cfg["k_min"], cfg["k_max"], cfg["n_d2"] + 1)
        d2_bounds, iv_d2_bounds = [], []
        for (kL, kR), (kLs, kRs) in zip(zip(edges_d2[:-1], edges_d2[1:]), zip(edges_d2_str[:-1], edges_d2_str[1:])):
            cands_dFk = [kL, kR] + ([l0 / 4.0] if kL < l0 / 4.0 < kR else [])
            cands_tp = [kL, kR] + ([0.75 * l0] if kL < 0.75 * l0 < kR else [])
            Sp_ub = Q_MAX + max(dF_dK(A_MAX, p, l0) for p in cands_dFk) + (1.0 - l0) * max(t_prime(p, l0) for p in cands_tp)
            cp_lb = min(c_prime(kL, l_X), c_prime(kR, l_X))
            R_lb = (S_val(kR, l0) - a) / c_val(kR, l_X, s_X)
            t1_num = Sp_ub ** 2 - ETA_MIN * (cp_lb * R_lb) ** 2
            t1_ub = t1_num / ((S_val(kL, l0) - a) ** 2 if t1_num >= 0 else (S_val(kR, l0) - a) ** 2)

            # When c_X'' >= 0 (occurring on [0.10, l_M/4 = 0.17)), multiply by ETA_MAX
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

            # Outward-rounded Interval cross-certification of Delta''_X
            ikL, ikR = Interval(kLs), Interval(kRs)
            ikc_q, ikc_t = iv_l0 / Interval("4"), Interval("0.75") * iv_l0
            ic_dFk = [ikL, ikR] + ([pt_q] if (pt_q := iv_clip_pt(ikc_q, ikL, ikR)) is not None else [])
            ic_tp = [ikL, ikR] + ([pt_t] if (pt_t := iv_clip_pt(ikc_t, ikL, ikR)) is not None else [])
            iSp_ub = iv_Q_MAX + Interval(max(iv_dFdK(iv_A_MAX, p, iv_l0).hi for p in ic_dFk)) + (iv_one - iv_l0) * Interval(max(iv_tp(p, iv_l0).hi for p in ic_tp))
            icp_lb = Interval(min(iv_cp(ikL).lo, iv_cp(ikR).lo))
            iR_lb = (iv_S(ikR) - iv_a) / iv_c(ikR)
            it1_num = iSp_ub.pow_int(2) - iv_E_MIN * (icp_lb * iR_lb).pow_int(2)
            iSaL2, iSaR2 = (iv_S(ikL) - iv_a).pow_int(2), (iv_S(ikR) - iv_a).pow_int(2)
            it1_ub = it1_num / (iSaL2 if it1_num.lo >= 0 else (iSaR2 if it1_num.hi <= 0 else iSaL2.hull(iSaR2)))

            icands_cpp = [ikL, ikR]
            for sgn in (Interval("-1"), Interval("1")):
                pt_c = iv_clip_pt(iv_lX * (Interval("7") + sgn * iv_sq73) / Interval("24"), ikL, ikR)
                if pt_c is not None:
                    icands_cpp.append(pt_c)
            if (pt_c := iv_clip_pt(iv_lX / Interval("4"), ikL, ikR)) is not None:
                icands_cpp.append(pt_c)
            icpp_ub = Interval(max(iv_d2FdK2(iv_A_MIN, p, iv_lX).hi for p in icands_cpp))
            if icpp_ub.lo >= 0:
                it2_ub = iv_E_MAX * icpp_ub / iv_c(ikL)
            elif icpp_ub.hi <= 0:
                it2_ub = iv_E_MIN * icpp_ub / iv_c(ikR)
            else:
                it2_ub = (iv_E_MAX * Interval._raw(Decimal(0), icpp_ub.hi) / iv_c(ikL)) + (iv_E_MIN * Interval._raw(icpp_ub.lo, Decimal(0)) / iv_c(ikR))

            iSpp_L = [ikL, ikR] + ([pt_q] if (pt_q := iv_clip_pt(ikc_q, ikL, ikR)) is not None else [])
            for sgn in (Interval("-1"), Interval("1")):
                pt_c = iv_clip_pt(iv_l0 * (Interval("7") + sgn * iv_sq73) / Interval("24"), ikL, ikR)
                if pt_c is not None:
                    iSpp_L.append(pt_c)
            iSpp_t = [ikL, ikR] + ([pt_t] if (pt_t := iv_clip_pt(ikc_t, ikL, ikR)) is not None else [])
            for sgn in (Interval("-1"), Interval("1")):
                pt_c = iv_clip_pt(iv_l0 * (Interval("9") + sgn * iv_sq63) / Interval("12"), ikL, ikR)
                if pt_c is not None:
                    iSpp_t.append(pt_c)
            iSpp_lb = Interval(min(iv_d2FdK2(iv_A_MAX, p, iv_l0).lo for p in iSpp_L)) + (iv_one - iv_l0) * Interval(min(iv_tpp(p, iv_l0).lo for p in iSpp_t))
            imSpp = -iSpp_lb
            iSaL, iSaR = iv_S(ikL) - iv_a, iv_S(ikR) - iv_a
            it3_ub = imSpp / (iSaL if imSpp.lo >= 0 else (iSaR if imSpp.hi <= 0 else iSaL.hull(iSaR)))
            it4_ub = (iv_one - iv_E_MAX) * (Interval("-2.5") * iv_l0 * (Interval("2") * ikR + iv_l0)) / (ikR.pow_int(2) * (ikR + iv_l0).pow_int(2))
            id2_ub = it1_ub + it2_ub + it3_ub + it4_ub
            iv_d2_bounds.append(id2_ub.to_float_bounds()[1])
            assert id2_ub.hi < 0, f"Interval Delta''_X >= 0 on [{kLs},{kRs}]: {id2_ub.hi}"

        # Interior u*(K) = (1 - eta)(S(K) - a)/t(K) range on region
        Ks_dense = np.linspace(cfg["k_min"], cfg["k_max"], 1000)
        t_dense = t_func(Ks_dense, l0)
        S_dense = S_val(Ks_dense, l0)
        u_lo = float(np.min((1.0 - ETA_MAX) * (S_dense - a) / t_dense))
        u_hi = float(np.max((1.0 - ETA_MIN) * (S_dense - a) / t_dense))

        d1_right = d1_exact(cfg["k_max"], cfg)
        print(f"  Region {name}:")
        print(f"    Wronskian Q_{name} <= {[round(float(x), 5) for x in Q_bounds]} (Interval max {max(iv_Q_bounds):.5f})")
        print(f"    Delta'_{name}     >= {[round(float(x), 4) for x in d1_bounds]} (Interval min {min(iv_d1_bounds):.4f})")
        print(f"    Delta''_{name}    <= {[round(float(x), 4) for x in d2_bounds[:4]]} ... (max {max(d2_bounds):.4f}, Interval max {max(iv_d2_bounds):.4f} < 0)")
        print(f"    Delta'_{name}(right) = +{d1_right:.6f} | u*(K) in [{u_lo:.4f}, {u_hi:.4f}] < 1 => L* >= {1.0 - u_hi:.4f}")
        assert u_hi < 1.0
        if name == "M":
            assert abs(d2_bounds[0] - (-421.1331)) < 0.01
            assert abs(u_hi - 0.6808) < 0.001

    # Variational Values & H1 Downward Kink Verification
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

    print(f"  Variational FOC: L*(0.28)={L_star_028:.6f}, L*(0.10)={L_star_010:.6f}, L_tan(0.10;0.44) in [{L_tan_010_em:.6f}, {L_tan_010_ep:.6f}]")
    print(f"  H1 Downward Kinks: k_W={k_kink_W:.6f} (W': {W_p_left:.6f} -> {W_p_right:.6f}), k_E={k_kink_E:.6f} ((-E+)': {mE_p_left:.6f} -> {mE_p_right:.6f})")
    assert abs(L_star_028 - 0.569743) < 1e-4 and abs(L_star_010 - 0.437261) < 1e-4
    assert abs(L_tan_010_ep - 0.433840) < 1e-4
    assert abs(k_kink_W - 0.406819) < 1e-5 and W_p_right < W_p_left
    assert abs(k_kink_E - 0.573570) < 1e-5 and mE_p_right < mE_p_left

    # Exact left-endpoint adverse-exit margins (Prop 1** part 2) + Outward-rounded Interval cross-certification
    def margin_left(K, l_X, s_X, T_X, a, l0, Psi_sharp_a):
        c = Q_MIN * K + F_A(A_MIN, K, l_X) - s_X
        W_X = float(box_worst_u(c, l_X)) + BETA_MAX * T_X
        E_plus = E_plus_exact(A_MAX, Q_MAX, K, a, l0)
        return W_X - (E_plus + BETA_MIN * Psi_sharp_a)

    def iv_margin_left(K_s, lX_s, sX_s, TX_s, a_s, l0_s, iv_Psi_a):
        K_iv, lX_iv, sX_iv, a_iv, l0_iv = Interval(K_s), Interval(lX_s), Interval(sX_s), Interval(a_s), Interval(l0_s)
        c_iv = iv_Q_MIN * K_iv + iv_F_A(iv_A_MIN, K_iv, lX_iv) - sX_iv
        W_iv = iv_box_worst_u(c_iv, lX_iv) + iv_B_MAX * Interval(TX_s)
        E_iv = iv_E_plus_exact(iv_A_MAX, iv_Q_MAX, K_iv, a_iv, l0_iv)
        return W_iv - (E_iv + iv_B_MIN * iv_Psi_a)

    Psi_010 = 0.4 * 0.10 - 5.0 / np.sqrt(0.10) - 18.5
    Psi_s_010 = Psi_010 - 10.0 / 301.0
    Psi_028 = 0.4 * 0.28 - 5.0 / np.sqrt(0.28) - 18.5
    Psi_s_028 = Psi_028 - 10.0 / 301.0

    iv_Psi_010 = Interval("0.4") * Interval("0.10") - Interval("5") * Interval("0.10").pow_half_int(-1) - Interval("18.5")
    iv_Psi_s_010 = iv_Psi_010 - Interval("10") / Interval("301")
    iv_Psi_028 = Interval("0.4") * Interval("0.28") - Interval("5") * Interval("0.28").pow_half_int(-1) - Interval("18.5")
    iv_Psi_s_028 = iv_Psi_028 - Interval("10") / Interval("301")

    m_M_sharp = margin_left(0.10, 0.68, 0.135, -33.103, 0.10, 0.44, Psi_s_010)
    m_M_psi = margin_left(0.10, 0.68, 0.135, -33.103, 0.10, 0.44, Psi_010)
    m_H_60 = margin_left(0.28, 0.72, 0.375, -27.164, 0.28, 0.60, Psi_s_028)
    m_H_57 = margin_left(0.28, 0.72, 0.375, -27.164, 0.28, 0.57, Psi_s_028)
    m_H_57_psi = margin_left(0.28, 0.72, 0.375, -27.164, 0.28, 0.57, Psi_028)

    iv_m_M_sharp = iv_margin_left("0.10", "0.68", "0.135", "-33.103", "0.10", "0.44", iv_Psi_s_010)
    iv_m_M_psi = iv_margin_left("0.10", "0.68", "0.135", "-33.103", "0.10", "0.44", iv_Psi_010)
    iv_m_H_60 = iv_margin_left("0.28", "0.72", "0.375", "-27.164", "0.28", "0.60", iv_Psi_s_028)
    iv_m_H_57 = iv_margin_left("0.28", "0.72", "0.375", "-27.164", "0.28", "0.57", iv_Psi_s_028)
    iv_m_H_57_psi = iv_margin_left("0.28", "0.72", "0.375", "-27.164", "0.28", "0.57", iv_Psi_028)

    print(f"  K=0.10 (l0=0.44): margin(Psi#) = {m_M_sharp:.6f} (Interval lb={iv_m_M_sharp.to_float_bounds()[0]:.6f}), margin(Psi) = {m_M_psi:.6f} (Interval lb={iv_m_M_psi.to_float_bounds()[0]:.6f})")
    print(f"  K=0.28 (l0=0.60): margin(Psi#) = {m_H_60:.6f} (Interval lb={iv_m_H_60.to_float_bounds()[0]:.6f})")
    print(f"  K=0.28 (l0=0.57): margin(Psi#) = {m_H_57:.6f} (Interval lb={iv_m_H_57.to_float_bounds()[0]:.6f}), margin(Psi) = {m_H_57_psi:.6f} (Interval lb={iv_m_H_57_psi.to_float_bounds()[0]:.6f})")

    assert m_M_sharp > 0.0947 and m_M_psi > 0.0624
    assert m_H_60 > 0.0561 and m_H_57 > 0.0571 and m_H_57_psi > 0.0249
    assert iv_m_M_sharp.lo > Decimal("0.0947") and iv_m_M_psi.lo > Decimal("0.0624")
    assert iv_m_H_60.lo > Decimal("0.0561") and iv_m_H_57.lo > Decimal("0.0571") and iv_m_H_57_psi.lo > Decimal("0.0249")


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


def solve_vfi_frontiers(A_val, beta=0.97, k_band=(0.00078, 0.00102), return_policy=False):
    theta, rho, w, delta, eta = 1.5, -1.0, 0.5, 0.08, 0.70
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
    while df_dk(lo_ss) <= D and lo_ss > 1e-6:
        lo_ss *= 0.5
    hi_ss = max(1e10, 10.0 * np.sqrt(1.5 * c_K / D) * (A_val ** 2.5))
    while df_dk(hi_ss) >= D:
        hi_ss *= 10.0
    k_ss = brentq(lambda k: df_dk(k) - D, lo_ss, hi_ss)
    k_lo, k_hi = 1e-6, 1.10 * k_ss

    # 880-point concentrated 3-region grid in k = A^2 K
    k_b0, k_b1 = k_band
    k_grid = np.unique(np.concatenate([
        np.geomspace(k_lo, k_b0, 160, endpoint=False),
        np.linspace(k_b0, k_b1, 360, endpoint=False),
        np.geomspace(k_b1, k_hi, 360),
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
    k_init = 0.00082 if abs(k_b0 - 0.00078) < 1e-8 else 0.5 * (k_b0 + k_b1)
    V_fix = np.where(
        k_grid > k_init,
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

    idx_m = np.where((k_grid >= k_b0) & (k_grid <= k_b1))[0]
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
    if return_policy:
        return k_S_fix, k_S_endo, dW_plus, pol_endo, k_grid, solve_L_vec, f_norm
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

    # Weak patience check: beta = 0.90 satisfies beta*theta = 1.35 > 1 while violating (2.3): beta*(q+theta*delta) = 0.936 < 1
    beta_wk = 0.90
    D_wk = 1.0 / beta_wk - (1.0 - delta)
    print(f"\n  [Weak Patience Regime: beta={beta_wk:.2f}, beta*(q+theta*delta)={beta_wk*(1-delta+theta*delta):.3f} < 1 < beta*theta={beta_wk*theta:.2f}, (D/c_K)^2={(D_wk/c_K)**2:.6f}]")
    prev_fix_wk = 1.0
    prev_rat_wk = 2.0
    for A_val in [1.5, 100.0, 1e8]:
        kSf_wk, kSe_wk, dWp_wk = solve_vfi_frontiers(A_val, beta=beta_wk, k_band=(0.0014, 0.0026))
        rat_wk = kSe_wk / kSf_wk
        print(f"    A={A_val:8.1e}: A^2*S_fix={kSf_wk:.6f}, A^2*S_endo={kSe_wk:.6f}, ratio={rat_wk:.5f}, dW+={dWp_wk:.2f}")
        assert kSf_wk < kSe_wk < (D_wk / c_K) ** 2
        assert kSf_wk < prev_fix_wk and rat_wk < prev_rat_wk
        prev_fix_wk, prev_rat_wk = kSf_wk, rat_wk
    assert kSe_wk < 0.00180 and rat_wk < 1.005

    # Section 4 escape-time scaling T_esc(A) along pi^+ from S_A to K_esc = 0.01 vs A^{-d/[r(1+d)]} = A^{-1}
    print("\n  [Asymptotic Escape Time T_esc(A) along pi^+ from S_A (Theorem 3* Part 2)]")
    for A_val in [1.0, 10.0, 100.0, 1000.0, 1e6]:
        _, kS_e, _, pol_e, k_g, solve_Lv, f_n = solve_vfi_frontiers(A_val, return_policy=True)
        idx_start = int(np.searchsorted(k_g, kS_e))
        k_cur = float(k_g[idx_start])
        dW_traj = 0.0
        T_esc = None
        for t in range(400):
            kp = float(np.interp(k_cur, k_g, pol_e))
            _, u_et = solve_Lv(np.array([k_cur]), np.array([kp]))
            c_ft = (1.0 - delta) * k_cur + float(f_n(k_cur, 1.0)) - kp
            dW_traj += (beta ** t) * (eta * np.log(c_ft) - float(u_et[0]))
            if T_esc is None and (k_cur / (A_val ** 2)) >= 0.01:
                T_esc = t
            k_cur = kp
        assert T_esc is not None and dW_traj > 0.5
        if A_val >= 100.0:
            assert (beta ** T_esc) > (A_val ** -1.0)
        if A_val >= 1000.0:
            assert (beta ** T_esc) > 10.0 * (A_val ** -1.0)
        print(f"    A={A_val:8.1e}: T_esc(K>=0.01)={T_esc:3d}, beta^T_esc={beta**T_esc:.5f}, A^-1={A_val**-1:.1e}, ratio={(beta**T_esc)*A_val:.2f}, dW_plus(pi+)={dW_traj:.4f}")


# ---------------------------------------------------------------------------
# 4. Theorem 10, Table 4, & Structural Extensions (Prop. 2*, Footnote 2)
# ---------------------------------------------------------------------------
def verify_theorem10():
    print("\n" + "=" * 72)
    print("4. THEOREM 10, TABLE 4, PROP. 2* & FOOTNOTE 2")
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

    # Exact endogenous MGR saddle-node A_SN vs true global survival threshold A_*
    def planner_ss_resid(u, A_v):
        L = (D / (1.5 * A_v * (2.0 ** 1.5) * (u ** 0.5) * ((1.0 + u) ** (-2.5)))) ** 2
        if L >= 1.0:
            return -1e3 - L
        K = u * L
        C = F_A(A_v, K, L) - delta * K
        if C <= 0.0:
            return -1e3
        return dF_dL(A_v, K, L) * (1.0 - L) - nu * C

    def get_planner_ss(A_v):
        us = np.geomspace(0.05, 1.5, 2000)
        vals = np.array([planner_ss_resid(u, A_v) for u in us])
        roots = []
        for ii in range(len(us) - 1):
            if vals[ii] > -100.0 and vals[ii + 1] > -100.0 and vals[ii] * vals[ii + 1] <= 0.0:
                ur = brentq(planner_ss_resid, us[ii], us[ii + 1], args=(A_v,), xtol=1e-12)
                Lr = (D / (1.5 * A_v * (2.0 ** 1.5) * (ur ** 0.5) * ((1.0 + ur) ** (-2.5)))) ** 2
                Kr = ur * Lr
                Cr = F_A(A_v, Kr, Lr) - delta * Kr
                Vss = (eta * np.log(Cr) + (1.0 - eta) * np.log(1.0 - Lr)) / (1.0 - beta)
                roots.append((Kr, Lr, Vss))
        return roots

    def solve_pchip_vfi_near_sn(A_v):
        """Converged C^1 PCHIP VFI initialized from above + direct V_ss(K_hi) vs liquidating trajectory check."""
        rts = get_planner_ss(A_v)
        K_hi, _, V_ss = rts[-1]
        V_cake_const = (eta / (1.0 - beta)) * (np.log((1.0 - beta) * q) + (beta / (1.0 - beta)) * np.log(beta * q))
        Ks = np.unique(np.concatenate([
            np.geomspace(1e-4, 0.05, 45, endpoint=False),
            np.linspace(0.05, 0.16, 40, endpoint=False),
            np.linspace(0.16, 0.23, 280, endpoint=False),
            np.geomspace(0.23, 0.80, 45),
        ]))
        nk = len(Ks)
        Ls = np.unique(np.concatenate([np.geomspace(1e-4, 0.08, 16, endpoint=False), np.linspace(0.08, 0.999, 44)]))
        dis_L = (1.0 - eta) * np.log(1.0 - Ls[None, :])
        f_K = lambda K, L: F_A(A_v, K, L)
        y_kL = q * Ks[:, None] + f_K(Ks[:, None], Ls[None, :])
        u_g = np.full((nk, nk), -1e9)
        for ii in range(nk):
            cb = y_kL[ii, None, :] - Ks[:, None]
            u_g[ii, :] = np.max(np.where(cb > 1e-15, eta * np.log(np.maximum(cb, 1e-30)) + dis_L, -1e9), axis=1)
        inv_phi = (np.sqrt(5.0) - 1.0) / 2.0
        V = np.full(nk, V_ss + 2.0)

        def interp_V(Kp, Vc, pc=None):
            v = pc(np.clip(Kp, Ks[0], Ks[-1])) if pc is not None else np.interp(np.clip(Kp, Ks[0], Ks[-1]), Ks, Vc)
            return np.where(Kp < Ks[0], Vc[0] + (eta / (1.0 - beta)) * np.log(np.maximum(Kp, 1e-30) / Ks[0]), v)

        for it in range(350):
            pc = PchipInterpolator(Ks, V)
            jb = np.argmax(u_g + beta * V[None, :], axis=1)
            lo = Ks[np.maximum(0, jb - 1)]
            hi = np.minimum(Ks[np.minimum(nk - 1, jb + 1)], y_kL[:, -1] - 1e-12)
            lo = np.minimum(lo, hi * 0.999)
            x1 = hi - inv_phi * (hi - lo)
            x2 = lo + inv_phi * (hi - lo)
            _, u1 = _golden_solve_L(Ks, x1, f_K, q, eta)
            _, u2 = _golden_solve_L(Ks, x2, f_K, q, eta)
            f1 = u1 + beta * interp_V(x1, V, pc)
            f2 = u2 + beta * interp_V(x2, V, pc)
            for _g in range(18):
                mr = f1 < f2
                lo = np.where(mr, x1, lo)
                hi = np.where(mr, hi, x2)
                x1n = np.where(mr, x2, hi - inv_phi * (hi - lo))
                x2n = np.where(mr, lo + inv_phi * (hi - lo), x1)
                _, u1n = _golden_solve_L(Ks, x1n, f_K, q, eta)
                _, u2n = _golden_solve_L(Ks, x2n, f_K, q, eta)
                f1n = np.where(mr, f2, u1n + beta * interp_V(x1n, V, pc))
                f2n = np.where(mr, u2n + beta * interp_V(x2n, V, pc), f1)
                x1, x2, f1, f2 = x1n, x2n, f1n, f2n
            pol = np.where(f1 > f2, x1, x2)
            Vn = np.maximum(f1, f2)
            if it % 5 == 4:
                _, up = _golden_solve_L(Ks, pol, f_K, q, eta)
                for _h in range(120):
                    pc_e = PchipInterpolator(Ks, Vn)
                    Vnn = up + beta * interp_V(pol, Vn, pc_e)
                    if np.max(np.abs(Vnn - Vn)) < 1e-11:
                        Vn = Vnn
                        break
                    Vn = Vnn
            if np.max(np.abs(Vn - V)) < 1e-9:
                V = Vn
                break
            V = Vn
        m = (Ks >= 0.16) & (Ks <= 0.22)
        pos = np.where((pol[m] - Ks[m]) > 1e-8)[0]
        surv = len(pos) > 0
        S_val = float(Ks[m][pos[0]]) if surv else np.nan
        k_sim, W_sim = K_hi, 0.0
        for t_s in range(1200):
            kp = float(np.interp(k_sim, Ks, pol))
            if kp <= Ks[0]:
                W_sim += (beta ** t_s) * (V_cake_const + (eta / (1.0 - beta)) * np.log(k_sim))
                break
            _, ut_s = _golden_solve_L(np.array([k_sim]), np.array([kp]), f_K, q, eta)
            W_sim += (beta ** t_s) * float(ut_s[0])
            k_sim = kp
        return surv, S_val, V_ss, W_sim, k_sim, K_hi

    A_SN = brentq(lambda Av: max(planner_ss_resid(u, Av) for u in np.geomspace(0.05, 1.5, 800)), 0.095, 0.105, xtol=1e-9)
    tau_1_SN = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_SN, 1e-9, 0.20)
    tau_2_SN = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_SN, 0.20, 1.0 - 1e-9)

    # Locate true global survival threshold A_* (in (0.09955, 0.09980)) by bisection on PCHIP VFI + V_ss vs liquidating W_sim
    surv_pre, _, Vss_pre, Wsim_pre, Kend_pre, Khi_pre = solve_pchip_vfi_near_sn(0.099600)
    surv_post, S_post, Vss_post, Wsim_post, Kend_post, Khi_post = solve_pchip_vfi_near_sn(0.099620)
    assert (not surv_pre) and Wsim_pre > Vss_pre and Kend_pre < 0.001
    assert surv_post and abs(Wsim_post - Vss_post) < 1e-5 and abs(Kend_post - Khi_post) < 1e-4
    lo_As, hi_As = 0.099600, 0.099620
    for _ in range(10):
        mid_As = 0.5 * (lo_As + hi_As)
        surv_m, _, _, _, _, _ = solve_pchip_vfi_near_sn(mid_As)
        if surv_m:
            hi_As = mid_As
        else:
            lo_As = mid_As
    A_star = 0.5 * (lo_As + hi_As)

    tau_1_star = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_star, 1e-9, 0.20)
    tau_2_star = brentq(lambda t: A0 * (t ** alpha) * (1.0 - t) - A_star, 0.20, 1.0 - 1e-9)

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
    print(f"  MGR saddle-node: A_SN = {A_SN:.7f} -> (tau_1_SN, tau_2_SN) = ({tau_1_SN:.6e}, {tau_2_SN:.6f})")
    print(f"  Global survival: A_*  = {A_star:.7f} -> (tau_1_*,  tau_2_*)  = ({tau_1_star:.6e}, {tau_2_star:.6f})")
    print(f"    (At A=0.099600 < A_*: W_ext(K_hi)={Wsim_pre:.6f} > V_ss={Vss_pre:.6f}, K_end={Kend_pre:.5f}; at A=0.099620 > A_*: W_sim=V_ss={Vss_post:.6f}, S={S_post:.5f})")
    print(f"  Asymptotic bound crossing: A_cross = {A_cross:.6f} -> (tau_c1, tau_c2) = ({tau_cross_1:.6e}, {tau_cross_2:.6f})")
    print(f"  Theorem 8 finite-A domain (Ae >= 0.749): [{tau_t8_lo:.6f}, {tau_t8_hi:.6f}]")
    print(f"  VFI economic extinction checks: tau=2e-5 (Ae={Ae_low:.6f}) survives={surv_low}; tau=0.94 (Ae={Ae_high:.6f}) survives={surv_high}")

    assert abs(A_rep - 0.073485) < 1e-5 and abs(tau_max - 0.948649) < 1e-5
    assert abs(A_SN - 0.0995245) < 1e-5 and 0.09955 < A_star < 0.09980 and A_SN < A_star
    assert abs(tau_1_SN - 2.2197e-5) < 1e-7 and abs(tau_2_SN - 0.930108) < 1e-5
    assert tau_1_star > tau_1_SN and tau_2_star < tau_2_SN
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
            econ_tag = " [ECONOMIC EXTINCTION: Ae < A_*]" if Ae < A_star else (" [S_endo > Sbar]" if Ae < A_cross else "")
            print(f"  tau={tau:7.2e}  Ae={Ae:.4f}  Ae/Arep={ratio:5.2f}  kappa={kap:.6f}  Sbar_asy={Sbar:.6f}{econ_tag}")
        else:
            print(f"  tau={tau:7.2e}  Ae={Ae:.4f}  Ae/Arep={ratio:5.2f}  (global physical extinction)")
            if tau == 5e-6:
                assert round(Ae, 4) == 0.0686

    # Barro rule tau* = gamma and Prop. 2*(1) fragmentation counts (N_{f,SN}, N_{f,*}, N_{f,rep})
    gamma_barro = alpha / (1.0 + alpha)
    tau_barro = alpha / (1.0 + alpha)
    N_f_rep = (0.75 / A_rep) ** (1.0 / (theta - 1.0))
    N_f_SN = (0.75 / A_SN) ** (1.0 / (theta - 1.0))
    N_f_star = (0.75 / A_star) ** (1.0 / (theta - 1.0))
    print(f"  Barro & Fragmentation: tau* = gamma = {tau_barro:.2f} (alpha={alpha}); N_{{f,*}} = {N_f_star:.2f} vs N_{{f,SN}} = {N_f_SN:.2f} vs N_{{f,rep}} = {N_f_rep:.2f}")
    assert abs(tau_barro - gamma_barro) < 1e-12
    assert abs(N_f_rep - 104.17) < 0.05 and abs(N_f_SN - 56.79) < 0.05 and N_f_star < N_f_SN

    # Proposition 2* decentralized equilibria (K_lo, K_hi), planner thresholds, & 2x2 Jacobian stability
    print("\n  [Prop. 2* Decentralized Steady States (K_lo, K_hi), Planner VFI S(A_mkt) & 2x2 Jacobian Eigenvalues]")
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

            def dec_jacobian_eigs(K, L):
                coef = (theta / mu) if mode == "overhead" else 1.0
                C = coef * F_A(0.75, K, L) - delta * K
                eps_L = 1e-7
                FLL = (dF_dL(0.75, K, L + eps_L) - dF_dL(0.75, K, L - eps_L)) / (2.0 * eps_L)
                FKL = d2F_dKdL(0.75, K, L)
                FKK = d2F_dK2(0.75, K, L)
                FK, FL = dF_dK(0.75, K, L), dF_dL(0.75, K, L)
                dg_dL = (-FL + (1.0 - L) * FLL) / mu
                dL_dK = -(((1.0 - L) * FKL) / mu) / dg_dL
                dL_dC = nu / dg_dL
                Phi_K = q + coef * (FK + FL * dL_dK)
                Phi_C = coef * FL * dL_dC - 1.0
                A_c = C * beta * (FKL * dL_dC) / mu
                B_k = C * beta * (FKK + FKL * dL_dK) / mu
                J = np.array([[Phi_K, Phi_C], [B_k * Phi_K / (1.0 - A_c), (1.0 + B_k * Phi_C) / (1.0 - A_c)]])
                return np.linalg.eigvals(J)

            eigs_lo = dec_jacobian_eigs(K_lo, L_lo)
            eigs_hi = dec_jacobian_eigs(K_hi, L_hi)
            mags_lo = np.sort(np.abs(eigs_lo))
            reals_hi = np.sort(np.real(eigs_hi))
            assert np.all(np.abs(np.imag(eigs_lo)) > 0.1) and mags_lo[0] > 1.0, f"K_lo not spiral source: {eigs_lo}"
            assert np.all(np.abs(np.imag(eigs_hi)) < 1e-9) and 0.0 < reals_hi[0] < 1.0 < reals_hi[1], f"K_hi not saddle: {eigs_hi}"
            print(
                f"    mu={mu:.1f} ({mode:8s}): A_mkt={A_mkt:.4f}, S(A_mkt)={S_mkt:.6f} | "
                f"K_lo={K_lo:.6f} (L={L_lo:.4f}, spiral |lam|={mags_lo[0]:.4f}>1), "
                f"K_hi={K_hi:.6f} (L={L_hi:.4f}, saddle lam=({reals_hi[0]:.4f}, {reals_hi[1]:.4f}))"
            )
            assert K_lo > S_mkt

    # Footnote 2 continuous AK regime check at h = 0.28
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
    print(f"  [Footnote 2] Continuous AK at h=0.28: V_AK(0.28) = +{V_AK_028:.4f} >> Psi#(0.28) = {Psi_sharp_028:.6f}")
    assert V_AK_028 > 240.0 and V_AK_028 > Psi_sharp_028


# ---------------------------------------------------------------------------
# 5. Proposition 4*, Table 5, Patience/Recovery Sensitivity & Technical Appendix
# ---------------------------------------------------------------------------
def _build_slope_tables(slopes_arr):
    m = len(slopes_arr)
    smin = np.full((m, m), np.inf)
    smax = np.full((m, m), -np.inf)
    for i in range(m):
        smin[i, i:] = np.minimum.accumulate(slopes_arr[i:])
        smax[i, i:] = np.maximum.accumulate(slopes_arr[i:])
    return smin, smax


_HB_AB_MIN, _HB_AB_MAX = 0.349, 0.351
_HB_R_REC = 1.0 / 3.0
_HB_KS_M = np.unique(np.concatenate([
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
_HB_LKS_M = np.log(_HB_KS_M)
_HB_NK_M = len(_HB_KS_M)
_HB_LS_M = np.unique(np.concatenate([[0.0], np.geomspace(1e-5, 0.08, 18, endpoint=False), np.linspace(0.08, 0.999, 52)]))
_HB_S_CAND = 1.0 - np.geomspace(1e-6, 0.15, 20)
_HB_INV_PHI = (np.sqrt(5.0) - 1.0) / 2.0
_HB_PHI_LOC = np.clip((np.log(0.060) - _HB_LKS_M) / np.log(0.060 / 0.012), 0.0, 1.0)
_HB_KS_WIT = np.unique(np.concatenate([
    _HB_KS_M,
    np.geomspace(0.006, 0.05, 220, endpoint=False),
    np.geomspace(0.05, 0.28, 280, endpoint=False),
    np.geomspace(0.28, 1.5, 160, endpoint=False),
]))
_HB_LKS_WIT = np.log(_HB_KS_WIT)
_HB_N_WIT = len(_HB_KS_WIT)
_WORKER_STATE_CACHE = {}


def _hb_get_u(Av, q_v, is_upper, eL, eU, ka, La, kpa):
    cv = q_v * ka + F_A(Av, ka, La) - kpa
    lc = np.log(np.maximum(cv, 1e-30))
    ll = np.log(1.0 - La)
    ua = eL * lc + (1.0 - eL) * ll
    ub = eU * lc + (1.0 - eU) * ll
    uv = np.maximum(ua, ub) if is_upper else np.minimum(ua, ub)
    return np.where(cv > 1e-15, uv, -1e9 + cv)


def _hb_solve_L(Av, q_v, is_upper, eL, eU, ka, kpa):
    u0 = _hb_get_u(Av, q_v, is_upper, eL, eU, ka, np.zeros_like(ka), kpa)
    lo = np.full_like(ka, 1e-7)
    hi = np.full_like(ka, 1.0 - 1e-9)
    x1 = hi - _HB_INV_PHI * (hi - lo)
    x2 = lo + _HB_INV_PHI * (hi - lo)
    f1 = _hb_get_u(Av, q_v, is_upper, eL, eU, ka, x1, kpa)
    f2 = _hb_get_u(Av, q_v, is_upper, eL, eU, ka, x2, kpa)
    for _ in range(18):
        mr = f1 < f2
        lo = np.where(mr, x1, lo)
        hi = np.where(mr, hi, x2)
        x1n = np.where(mr, x2, hi - _HB_INV_PHI * (hi - lo))
        x2n = np.where(mr, lo + _HB_INV_PHI * (hi - lo), x1)
        f1n = np.where(mr, f2, _hb_get_u(Av, q_v, is_upper, eL, eU, ka, x1n, kpa))
        f2n = np.where(mr, _hb_get_u(Av, q_v, is_upper, eL, eU, ka, x2n, kpa), f1)
        x1, x2, f1, f2 = x1n, x2n, f1n, f2n
    Lb = 0.5 * (lo + hi)
    ub = _hb_get_u(Av, q_v, is_upper, eL, eU, ka, Lb, kpa)
    return np.where(u0 > ub, 0.0, Lb), np.maximum(u0, ub)


def _hb_precompute_state_pwl(A_v, q_v, is_upper, eL=ETA_MIN, eU=ETA_MAX):
    key = (float(A_v), float(q_v), bool(is_upper), float(eL), float(eU))
    if key in _WORKER_STATE_CACHE:
        return _WORKER_STATE_CACHE[key]
    y = q_v * _HB_KS_M[:, None] + F_A(A_v, _HB_KS_M[:, None], _HB_LS_M[None, :])
    um = np.full((_HB_NK_M, _HB_NK_M), -1e9)
    ll_m = np.log(1.0 - _HB_LS_M[None, :])
    for i in range(_HB_NK_M):
        cm = y[i, None, :] - _HB_KS_M[:, None]
        lc_m = np.log(np.maximum(cm, 1e-30))
        ua = eL * lc_m + (1.0 - eL) * ll_m
        ub = eU * lc_m + (1.0 - eU) * ll_m
        uv = np.maximum(ua, ub) if is_upper else np.minimum(ua, ub)
        um[i, :] = np.max(np.where(cm > 1e-15, uv, -1e9), axis=1)
    ym = y[:, -1]
    kpt = ym[:, None] * _HB_S_CAND[None, :]
    ut = np.zeros_like(kpt)
    for j in range(len(_HB_S_CAND)):
        _, ut[:, j] = _hb_solve_L(A_v, q_v, is_upper, eL, eU, _HB_KS_M, kpt[:, j])
    u0_mat = _hb_get_u(A_v, q_v, is_upper, eL, eU, _HB_KS_M[:, None], 0.0, _HB_KS_M[None, :])
    res = dict(A=A_v, qv=q_v, is_upper=is_upper, eL=eL, eU=eU, u=um, u0=u0_mat, ym=ym, kpt=kpt, ut=ut)
    _WORKER_STATE_CACHE[key] = res
    return res


def _hb_pack_markov_pwl(AG_v, AB_v, q_v, is_upper, eL=ETA_MIN, eU=ETA_MAX):
    sG = _hb_precompute_state_pwl(AG_v, q_v, is_upper, eL, eU)
    sB = _hb_precompute_state_pwl(AB_v, q_v, is_upper, eL, eU)
    return dict(
        AG=AG_v, AB=AB_v, qv=q_v, is_upper=is_upper, eL=eL, eU=eU,
        uG=sG["u"], uG0=sG["u0"], ymG=sG["ym"], kptG=sG["kpt"], utG=sG["ut"],
        uB=sB["u"], uB0=sB["u0"], ymB=sB["ym"], kptB=sB["kpt"], utB=sB["ut"],
    )


def _hb_solve_markov_pwl(pre, bv, p, init=None, return_pol=False, tol_out=1e-8):
    eL, eU, q_v, is_upper = pre["eL"], pre["eU"], pre["qv"], pre["is_upper"]
    ec0 = eL if is_upper else eU
    s_lo_tail = ec0 / (1.0 - bv)
    d_hi_tail = (eU if is_upper else eL) / (1.0 - bv)

    def interp(V, kp):
        lk = np.log(np.maximum(kp, 1e-30))
        r = np.interp(np.clip(lk, _HB_LKS_M[0], _HB_LKS_M[-1]), _HB_LKS_M, V)
        r = np.where(kp < _HB_KS_M[0], V[0] + s_lo_tail * (lk - _HB_LKS_M[0]), r)
        return np.where(kp > _HB_KS_M[-1], V[-1] + d_hi_tail * (lk - _HB_LKS_M[-1]), r)

    if init is not None:
        VG, VB = init[0].copy(), init[1].copy()
    else:
        Vc = s_lo_tail * (np.log((1.0 - bv) * q_v) + (bv / (1.0 - bv)) * np.log(bv * q_v))
        VG = np.where(_HB_KS_M > 0.0016, -25.0, Vc + s_lo_tail * _HB_LKS_M)
        VB = VG.copy() - 4.0

    for _ in range(40):
        EVG = (1.0 - p) * VG + p * VB
        EVB = _HB_R_REC * VG + (1.0 - _HB_R_REC) * VB
        pols, ups = [], []
        for uM, uM0, EV, Av, ym, kpt, ut in [
            (pre["uG"], pre["uG0"], EVG, pre["AG"], pre["ymG"], pre["kptG"], pre["utG"]),
            (pre["uB"], pre["uB0"], EVB, pre["AB"], pre["ymB"], pre["kptB"], pre["utB"]),
        ]:
            vg = uM + bv * EV[None, :]
            jb = np.argmax(vg, axis=1)
            bg = vg[np.arange(_HB_NK_M), jb]
            vt = ut + bv * interp(EV, kpt)
            sb = np.argmax(vt, axis=1)
            bt = vt[np.arange(_HB_NK_M), sb]
            uset = bt > bg
            lot = kpt[np.arange(_HB_NK_M), np.maximum(0, sb - 1)]
            hit = kpt[np.arange(_HB_NK_M), np.minimum(len(_HB_S_CAND) - 1, sb + 1)]
            lo = np.where(uset, np.minimum(lot, hit), _HB_KS_M[np.maximum(0, jb - 1)])
            hi = np.where(uset, np.minimum(np.maximum(lot, hit), ym - 1e-12), np.minimum(_HB_KS_M[np.minimum(_HB_NK_M - 1, jb + 1)], ym - 1e-12))
            x1 = hi - _HB_INV_PHI * (hi - lo)
            x2 = lo + _HB_INV_PHI * (hi - lo)
            _, u1 = _hb_solve_L(Av, q_v, is_upper, eL, eU, _HB_KS_M, x1)
            _, u2 = _hb_solve_L(Av, q_v, is_upper, eL, eU, _HB_KS_M, x2)
            f1 = u1 + bv * interp(EV, x1)
            f2 = u2 + bv * interp(EV, x2)
            for _g in range(10):
                mr = f1 < f2
                lo = np.where(mr, x1, lo)
                hi = np.where(mr, hi, x2)
                x1n = np.where(mr, x2, hi - _HB_INV_PHI * (hi - lo))
                x2n = np.where(mr, lo + _HB_INV_PHI * (hi - lo), x1)
                _, u1n = _hb_solve_L(Av, q_v, is_upper, eL, eU, _HB_KS_M, x1n)
                _, u2n = _hb_solve_L(Av, q_v, is_upper, eL, eU, _HB_KS_M, x2n)
                f1n = np.where(mr, f2, u1n + bv * interp(EV, x1n))
                f2n = np.where(mr, u2n + bv * interp(EV, x2n), f1)
                x1, x2, f1, f2 = x1n, x2n, f1n, f2n
            pol_int = np.where(f1 > f2, x1, x2)
            _, up_int = _hb_solve_L(Av, q_v, is_upper, eL, eU, _HB_KS_M, pol_int)
            val_int = up_int + bv * interp(EV, pol_int)
            jb0 = np.argmax(uM0 + bv * EV[None, :], axis=1)
            lo0 = _HB_KS_M[np.maximum(0, jb0 - 1)]
            hi0 = np.maximum(lo0, np.minimum(_HB_KS_M[np.minimum(_HB_NK_M - 1, jb0 + 1)], q_v * _HB_KS_M - 1e-12))
            z1 = hi0 - _HB_INV_PHI * (hi0 - lo0)
            z2 = lo0 + _HB_INV_PHI * (hi0 - lo0)
            g1 = _hb_get_u(Av, q_v, is_upper, eL, eU, _HB_KS_M, 0.0, z1) + bv * interp(EV, z1)
            g2 = _hb_get_u(Av, q_v, is_upper, eL, eU, _HB_KS_M, 0.0, z2) + bv * interp(EV, z2)
            for _g0 in range(10):
                mr0 = g1 < g2
                lo0 = np.where(mr0, z1, lo0)
                hi0 = np.where(mr0, hi0, z2)
                z1n = np.where(mr0, z2, hi0 - _HB_INV_PHI * (hi0 - lo0))
                z2n = np.where(mr0, lo0 + _HB_INV_PHI * (hi0 - lo0), z1)
                g1n = np.where(mr0, g2, _hb_get_u(Av, q_v, is_upper, eL, eU, _HB_KS_M, 0.0, z1n) + bv * interp(EV, z1n))
                g2n = np.where(mr0, _hb_get_u(Av, q_v, is_upper, eL, eU, _HB_KS_M, 0.0, z2n) + bv * interp(EV, z2n), g1)
                z1, z2, g1, g2 = z1n, z2n, g1n, g2n
            pol0 = np.where(g1 > g2, z1, z2)
            up0 = _hb_get_u(Av, q_v, is_upper, eL, eU, _HB_KS_M, 0.0, pol0)
            use0 = (up0 + bv * interp(EV, pol0)) > val_int
            pols.append(np.where(use0, pol0, pol_int))
            ups.append(np.where(use0, up0, up_int))
        polG, polB = pols
        upG, upB = ups
        VGe, VBe = VG.copy(), VB.copy()
        for _h in range(180):
            EVGe = (1.0 - p) * VGe + p * VBe
            EVBe = _HB_R_REC * VGe + (1.0 - _HB_R_REC) * VBe
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
    return VG, VB


def _hb_certify_logpwl_sens_band(Av, V_self, EV, bL, bR, tol=3e-4, q_hi=Q_MAX, s_tail_arg=None, d_hi_arg=None, eL=ETA_MIN, eU=ETA_MAX):
    """Continuously certify log-PWL super-barrier on ALL (0, inf) x [bL, bR] simultaneously."""
    s_tail = eL / (1.0 - bL) if s_tail_arg is None else float(s_tail_arg)
    D_hi = eU / (1.0 - bR) if d_hi_arg is None else float(d_hi_arg)
    assert s_tail <= eL / (1.0 - bL) + 1e-12 and D_hi >= eU / (1.0 - bR) - 1e-12
    x_cut = float(_HB_KS_M[-1])
    tail_knots = np.array([68.0, 78.0, 90.0])
    ks_ext = np.concatenate([_HB_KS_M, tail_knots])
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

    r_top = q_hi + F_A(Av, _HB_KS_M[0], 1.0) / _HB_KS_M[0]
    assert r_top < 1.0, f"Lower tail contraction failed: {r_top} >= 1.0"
    x_end = float(ks_ext[-1])
    F_inf = Av * (2.0 ** 1.5)
    Y_end = q_hi * x_end + F_inf
    assert Y_end < x_end
    V1 = float(np.interp(np.log(1.0), _HB_LKS_M, EV))
    idx1 = max(0, int(np.searchsorted(_HB_KS_M, 1.0)) - 1)
    sl_min = float(np.min((np.diff(EV[idx1:]) / np.diff(_HB_LKS_M[idx1:])) / _HB_KS_M[idx1 + 1:]))
    assert sl_min > 0.0 and np.all(EV[idx1:] <= EV[-1] - sl_min * (x_cut - _HB_KS_M[idx1:]) + 1e-12)

    def tails_for_b(bv):
        c_slo = eL + bv * s_tail
        s_lo_opt = (bv * s_tail) / c_slo
        tail_lo = float(
            eL * np.log((1.0 - s_lo_opt) * _HB_KS_M[0])
            + bv * s_tail * np.log(s_lo_opt)
            + c_slo * np.log(r_top)
            + bv * EV[0]
            - V_self[0]
        )
        tail_hi_lt1 = float(eU * np.log(Y_end) + bv * V1 - V_self_ext[-1])
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
        tail_hi = max(tail_hi_lt1, tail_hi_mid, tail_hi_log)
        assert tail_hi < 0.0, f"Upper tail [90, inf) not negative at b={bv}: {tail_hi:.4f}"
        return tail_lo, tail_hi

    t_lo_L, t_hi_L = tails_for_b(bL)
    t_lo_R, t_hi_R = tails_for_b(bR)
    tail_max = max(t_lo_L, t_hi_L, t_lo_R, t_hi_R)

    xg = np.geomspace(_HB_KS_M[0], x_end, 48)
    Lg = np.concatenate([[0.0], np.geomspace(1e-5, 0.999, 22)])
    sg = np.linspace(0.05, 0.998, 22)
    Y_g = q_hi * xg[:, None] + F_A(Av, xg[:, None], Lg[None, :])
    c_g = Y_g[:, :, None] * (1.0 - sg[None, None, :])
    y_g = Y_g[:, :, None] * sg[None, None, :]
    ec_g = np.where(c_g < 1.0, eL, eU)
    ev_g = eval_V(EV_ext, y_g)
    b_g = np.where(ev_g < 0.0, bL, bR)
    val_g = ec_g * np.log(c_g) + (1.0 - eU) * np.log(1.0 - Lg[None, :, None]) + b_g * ev_g - eval_V(V_self_ext, xg[:, None, None])

    xm_s = np.sqrt(_HB_KS_M[:-1] * _HB_KS_M[1:])[:, None, None]
    Lm_s = np.array([0.0, 0.37, 0.50, 0.62, 0.72, 0.85])[None, :, None]
    sm_s = np.array([0.82, 0.90, 0.955, 0.985, 0.9979])[None, None, :]
    Ym_s = q_hi * xm_s + F_A(Av, xm_s, Lm_s)
    cm_s = Ym_s * (1.0 - sm_s)
    ecm_s = np.where(cm_s < 1.0, eL, eU)
    ev_ms = eval_V(EV_ext, Ym_s * sm_s)
    b_ms = np.where(ev_ms < 0.0, bL, bR)
    val_ms = ecm_s * np.log(cm_s) + (1.0 - eU) * np.log(1.0 - Lm_s) + b_ms * ev_ms - eval_V(V_self_ext, xm_s)
    best_lb = max(tail_max, float(np.max(val_g)), float(np.max(val_ms)))
    target = best_lb + tol

    xs_b = np.unique(np.concatenate([_HB_KS_M[::10], [x_cut, 68.0, 78.0, 90.0]]))
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
        ev_mono = eval_V(EV_ext, bsR * Y_max)
        b_mono = np.where(ev_mono < 0.0, bL, bR)
        ub_mono = (
            np.where(bsL >= 1.0, -1e9, ec_max * np.log(c_max))
            + (1.0 - eU) * np.log(np.maximum(1.0 - bLL, 1e-300))
            + np.where(bsR <= 0.0, -1e9, b_mono * ev_mono)
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
            ev_mid = eval_V(EV_ext, smv * Ymv)
            V_self_mid = eval_V(V_self_ext, xmv)
            best_eta_ub = np.full(np.sum(valid_c), -1e9)
            err_x_v = np.zeros(np.sum(valid_c))
            err_L_v = np.zeros(np.sum(valid_c))
            err_s_v = np.zeros(np.sum(valid_c))
            for ec in (eL, eU):
                mask_ec = (c_min[valid_c] < 1.0) if ec == eL else (c_max[valid_c] >= 1.0)
                ec_lo = np.where(cross_c1, eL, ec)
                ec_hi = np.where(cross_c1, eU, ec)
                base_m = ec * np.log(cm[valid_c]) + (1.0 - eU) * np.log(1.0 - Lmv) - V_self_mid
                for bv_end in (bL, bR):
                    hm = base_m + bv_end * ev_mid
                    A_lo = ec_lo / Y_max_v + bv_end * sLv * fp_y_lo
                    A_hi_b = ec_hi / Y_min_v + bv_end * sRv * fp_y_hi
                    sx = np.maximum(np.abs(A_lo * Yx_lo - fp_x_hi), np.abs(A_hi_b * Yx_hi - fp_x_lo)) * hxv
                    sL = np.maximum(np.abs(A_lo * YL_lo - (1.0 - eU) / (1.0 - LRv)), np.abs(A_hi_b * YL_hi - (1.0 - eU) / (1.0 - LLv))) * hLv
                    ss_e = np.maximum(np.abs(-ec_hi / (1.0 - sRv) + bv_end * Y_min_v * fp_y_lo), np.abs(-ec_lo / (1.0 - sLv) + bv_end * Y_max_v * fp_y_hi)) * hsv
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
            return float(target), float(best_lb), float(tail_max)
        bxL, bxR, bLL, bLR, bsL, bsR = bxL[keep], bxR[keep], bLL[keep], bLR[keep], bsL[keep], bsR[keep]
        xm, Lm, sm = xm[keep], Lm[keep], sm[keep]
        ex, eL_err, es = ex[keep], eL_err[keep], es[keep]
        Ym_k = q_hi * xm + F_A(Av, xm, Lm)
        cm_k = (1.0 - sm) * Ym_k
        ecm_k = np.where(cm_k < 1.0, eL, eU)
        ev_k = eval_V(EV_ext, sm * Ym_k)
        b_k = np.where(ev_k < 0.0, bL, bR)
        lb_k = np.where(
            (Lm < 1.0) & (sm > 0.0) & (sm < 1.0),
            ecm_k * np.log(np.maximum(cm_k, 1e-30)) + (1.0 - eU) * np.log(np.maximum(1.0 - Lm, 1e-30)) + b_k * ev_k - eval_V(V_self_ext, xm),
            -1e9,
        )
        if np.max(lb_k) > best_lb:
            best_lb = float(np.max(lb_k))
            target = best_lb + tol
        if n_keep <= 1000:
            bxL = np.concatenate([bxL, xm, bxL, xm, bxL, xm, bxL, xm])
            bxR = np.concatenate([xm, bxR, xm, bxR, xm, bxR, xm, bxR])
            bLL = np.concatenate([bLL, bLL, Lm, Lm, bLL, bLL, Lm, Lm])
            bLR = np.concatenate([Lm, Lm, bLR, bLR, Lm, Lm, bLR, bLR])
            bsL = np.concatenate([bsL, bsL, bsL, bsL, sm, sm, sm, sm])
            bsR = np.concatenate([sm, sm, sm, sm, bsR, bsR, bsR, bsR])
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
    raise AssertionError("_hb_certify_logpwl_sens_band did not converge within 60 iterations")


def _hb_solve_L_wit(Av, qv, eL, eU, ka, kpa):
    def uf(La):
        cv = qv * ka + F_A(Av, ka, La) - kpa
        lc = np.log(np.maximum(cv, 1e-30))
        ll = np.log(1.0 - La)
        return np.where(cv > 1e-15, np.minimum(eL * lc + (1.0 - eL) * ll, eU * lc + (1.0 - eU) * ll), -1e9 + cv)

    u0 = uf(np.zeros_like(ka))
    lo = np.full_like(ka, 1e-7)
    hi = np.full_like(ka, 1.0 - 1e-9)
    x1 = hi - _HB_INV_PHI * (hi - lo)
    x2 = lo + _HB_INV_PHI * (hi - lo)
    f1, f2 = uf(x1), uf(x2)
    for _ in range(18):
        mr = f1 < f2
        lo = np.where(mr, x1, lo)
        hi = np.where(mr, hi, x2)
        x1n = np.where(mr, x2, hi - _HB_INV_PHI * (hi - lo))
        x2n = np.where(mr, lo + _HB_INV_PHI * (hi - lo), x1)
        f1n = np.where(mr, f2, uf(x1n))
        f2n = np.where(mr, uf(x2n), f1)
        x1, x2, f1, f2 = x1n, x2n, f1n, f2n
    Lb = 0.5 * (lo + hi)
    ub = uf(Lb)
    return np.where(u0 > ub, 0.0, Lb), np.maximum(u0, ub)


def _hb_eval_wit_chain(AG_v, AB_v, qv, eL, eU, bv, p, VG_ref, VB_ref, polG_ref, polB_ref, n_sw=6, half_w=5):
    idx_w05 = int(np.searchsorted(_HB_KS_WIT, 0.05))
    WG = np.interp(_HB_LKS_WIT, _HB_LKS_M, VG_ref)
    WB = np.interp(_HB_LKS_WIT, _HB_LKS_M, VB_ref)
    pG_w = np.exp(np.interp(_HB_LKS_WIT, _HB_LKS_M, np.log(np.maximum(polG_ref, 1e-30))))
    pB_w = np.exp(np.interp(_HB_LKS_WIT, _HB_LKS_M, np.log(np.maximum(polB_ref, 1e-30))))
    jbG = np.clip(np.searchsorted(_HB_KS_WIT, pG_w), 0, _HB_N_WIT - 1)
    jbB = np.clip(np.searchsorted(_HB_KS_WIT, pB_w), 0, _HB_N_WIT - 1)
    offs = np.arange(-half_w, half_w + 1)[None, :]
    c0_t = (1.0 - bv) * qv * _HB_KS_WIT[0]
    u0_t = min(ev * np.log(c0_t) for ev in (eL, eU)) + bv * (eU / (1.0 - bv)) * np.log(bv * qv)
    for _sw in range(n_sw):
        EVG = (1.0 - p) * WG + p * WB
        EVB = _HB_R_REC * WG + (1.0 - _HB_R_REC) * WB
        cG = np.clip(jbG[:, None] + offs, 0, _HB_N_WIT - 1)
        cB = np.clip(jbB[:, None] + offs, 0, _HB_N_WIT - 1)
        _, uGm = _hb_solve_L_wit(AG_v, qv, eL, eU, np.broadcast_to(_HB_KS_WIT[:, None], cG.shape), _HB_KS_WIT[cG])
        _, uBm = _hb_solve_L_wit(AB_v, qv, eL, eU, np.broadcast_to(_HB_KS_WIT[:, None], cB.shape), _HB_KS_WIT[cB])
        bG = np.argmax(uGm + bv * EVG[cG], axis=1)
        bB = np.argmax(uBm + bv * EVB[cB], axis=1)
        jbG = cG[np.arange(_HB_N_WIT), bG]
        uG_on = uGm[np.arange(_HB_N_WIT), bG]
        jbB = cB[np.arange(_HB_N_WIT), bB]
        uB_on = uBm[np.arange(_HB_N_WIT), bB]
        if uG_on[0] <= -1e8:
            jbG[0] = 0
            uG_on[0] = u0_t
        if uB_on[0] <= -1e8:
            jbB[0] = 0
            uB_on[0] = u0_t
        conv_w = False
        for _it in range(1500):
            EVGi = (1.0 - p) * WG + p * WB
            EVBi = _HB_R_REC * WG + (1.0 - _HB_R_REC) * WB
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
    return WG, WB, jbG, jbB, uG_on, uB_on


def _hb_eval_band_W_lb(p, bL, bR, jbG, jbB, uG_on, uB_on, init_neg=None, init_pos=None):
    """Exact feasible lower bound W(beta) >= W_neg(bR) + W_pos(bL) for all beta in [bL, bR]."""
    u_neg_G, u_pos_G = np.minimum(uG_on, 0.0), np.maximum(uG_on, 0.0)
    u_neg_B, u_pos_B = np.minimum(uB_on, 0.0), np.maximum(uB_on, 0.0)
    WGn, WBn = (init_neg[0].copy(), init_neg[1].copy()) if init_neg is not None else (np.zeros(_HB_N_WIT), np.zeros(_HB_N_WIT))
    for _ in range(1500):
        EVG = (1.0 - p) * WGn + p * WBn
        EVB = _HB_R_REC * WGn + (1.0 - _HB_R_REC) * WBn
        WG2 = u_neg_G + bR * EVG[jbG]
        WB2 = u_neg_B + bR * EVB[jbB]
        if max(np.max(np.abs(WG2 - WGn)), np.max(np.abs(WB2 - WBn))) < 1e-11:
            WGn, WBn = WG2, WB2
            break
        WGn, WBn = WG2, WB2
    WGp, WBp = (init_pos[0].copy(), init_pos[1].copy()) if init_pos is not None else (np.zeros(_HB_N_WIT), np.zeros(_HB_N_WIT))
    for _ in range(1500):
        EVG = (1.0 - p) * WGp + p * WBp
        EVB = _HB_R_REC * WGp + (1.0 - _HB_R_REC) * WBp
        WG2 = u_pos_G + bL * EVG[jbG]
        WB2 = u_pos_B + bL * EVB[jbB]
        if max(np.max(np.abs(WG2 - WGp)), np.max(np.abs(WB2 - WBp))) < 1e-11:
            WGp, WBp = WG2, WB2
            break
        WGp, WBp = WG2, WB2
    return WGn + WGp, WBn + WBp, (WGn, WBn), (WGp, WBp)


def _hb_worker_subbox(task):
    p, GL, GU, BL, BU, qL, qU, eLs, eUs, VGm, VBm, pGm, pBm, init_u = task
    P = np.array([[1.0 - p, p], [_HB_R_REC, 1.0 - _HB_R_REC]])
    pre_u = _hb_pack_markov_pwl(GU, BU, qU, True, eLs, eUs)
    WG, WB, jbG, jbB, uG_on, uB_on = _hb_eval_wit_chain(GL, BL, qL, eLs, eUs, BETA_MAX, p, VGm, VBm, pGm, pBm)
    iw_hi = int(np.searchsorted(_HB_KS_WIT, H_M))
    idx_w080 = int(np.searchsorted(_HB_KS_WIT, 0.80))
    ks_h1 = _HB_KS_WIT[iw_hi:idx_w080 + 1]
    t_sb_arr = dF_dL(BU, ks_h1, 0.603)
    c_sb_arr = qU * ks_h1 + F_A(BU, ks_h1, 0.603) + 0.397 * t_sb_arr - H_M
    e_sub_h1 = np.maximum(
        eLs * np.log(c_sb_arr - t_sb_arr * np.minimum(1.0, (1.0 - eLs) * c_sb_arr / t_sb_arr))
        + (1.0 - eLs) * np.log(np.minimum(1.0, (1.0 - eLs) * c_sb_arr / t_sb_arr)),
        eUs * np.log(c_sb_arr - t_sb_arr * np.minimum(1.0, (1.0 - eUs) * c_sb_arr / t_sb_arr))
        + (1.0 - eUs) * np.log(np.minimum(1.0, (1.0 - eUs) * c_sb_arr / t_sb_arr)),
    )
    e_sub = float(e_sub_h1[0])

    state_holder = [init_u, (WG, WB), None]

    def check_band(bL, bR, depth):
        bM = 0.5 * (bL + bR)
        VGu0, VBu0 = _hb_solve_markov_pwl(pre_u, bL, p, init=state_holder[0], tol_out=2e-7)
        state_holder[0] = (VGu0, VBu0)
        bump = (0.045 / (1.0 - bR)) * _HB_PHI_LOC
        VGu, VBu = VGu0 + bump, VBu0 + bump
        dG_b, _, _ = _hb_certify_logpwl_sens_band(GU, VGu, (1.0 - p) * VGu + p * VBu, bL, bR, tol=2.5e-4, q_hi=qU, eL=eLs, eU=eUs)
        dB_b, _, _ = _hb_certify_logpwl_sens_band(BU, VBu, _HB_R_REC * VGu + (1.0 - _HB_R_REC) * VBu, bL, bR, tol=2.5e-4, q_hi=qU, eL=eLs, eU=eUs)
        cGs, cBs = np.linalg.solve(np.eye(2) - bL * P, np.array([dG_b + 2e-5, dB_b + 2e-5]))
        resR = (np.eye(2) - bR * P) @ np.array([cGs, cBs]) - np.array([dG_b + 2e-5, dB_b + 2e-5])
        if np.min(resR) < 0.0:
            dc = -float(np.min(resR)) / (1.0 - bR) + 1e-7
            cGs += dc
            cBs += dc
        pg_s = float(np.interp(np.log(H_M), _HB_LKS_M, VGu)) + cGs
        pb_s = float(np.interp(np.log(H_M), _HB_LKS_M, VBu)) + cBs
        evb_s = _HB_R_REC * pg_s + (1.0 - _HB_R_REC) * pb_s
        _, WB_lb, state_holder[1], state_holder[2] = _hb_eval_band_W_lb(
            p, bL, bR, jbG, jbB, uG_on, uB_on, init_neg=state_holder[1], init_pos=state_holder[2]
        )
        wb_s = float(np.min(WB_lb[_HB_KS_WIT >= H_M]))
        m_band = min(wb_s - (e_sub + bL * evb_s), wb_s - (e_sub + bR * evb_s))
        m_pt_h1 = float(np.min(WB_lb[iw_hi:idx_w080 + 1] - (e_sub_h1 + max(bL * evb_s, bR * evb_s))))
        m_eff = min(m_band, m_pt_h1)
        if m_eff > 0.0 or depth >= 2:
            return m_eff, 1
        m1, c1 = check_band(bL, bM, depth + 1)
        m2, c2 = check_band(bM, bR, depth + 1)
        return min(m1, m2), c1 + c2

    n_init = 12 if p == 0.0 else 8
    b_edges = np.linspace(BETA_MIN, BETA_MAX, n_init + 1)
    m_min = 1e9
    cnt = 0
    for j in range(n_init):
        mj, cj = check_band(float(b_edges[j]), float(b_edges[j + 1]), 0)
        m_min = min(m_min, mj)
        cnt += cj
    return p, m_min, cnt


def verify_prop4_star_stochastic():
    print("\n" + "=" * 72)
    print("5. PROPOSITION 4*, TABLE 5, PATIENCE/RECOVERY SENSITIVITY & APPENDIX")
    print("=" * 72)

    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    q = 1.0 - delta
    A_G, A_B = 0.75, 0.35
    AB_MIN, AB_MAX = _HB_AB_MIN, _HB_AB_MAX
    r_rec = _HB_R_REC
    C_max = Q_MAX * H_M + F_A(A_MAX, H_M, 1.0) - B_M
    R_hat = -0.996

    k_wg, n_kw, build_u_worst, eval_witness = build_25step_witness_builder()
    ks_m = _HB_KS_M
    lks_m = _HB_LKS_M
    inv_phi = _HB_INV_PHI
    phi_loc = _HB_PHI_LOC
    ks_wit = _HB_KS_WIT
    lks_wit = _HB_LKS_WIT
    iw_lo = int(np.searchsorted(ks_wit, B_M))
    iw_hi = int(np.searchsorted(ks_wit, H_M))
    idx_w080 = int(np.searchsorted(ks_wit, 0.80))
    assert ks_wit[iw_lo] == B_M and ks_wit[iw_hi] == H_M

    pre_up = _hb_pack_markov_pwl(A_MAX, AB_MAX, Q_MAX, True)
    pre_lo = _hb_pack_markov_pwl(A_MIN, AB_MIN, Q_MIN, False)
    # Ruin/Expropriation Hazard p in [0%, 2%] (Proposition 4* & Lemma 2, effective beta_eff = beta*(1-p))
    eM_exit = E_plus_exact(A_MAX, Q_MAX, B_M, B_M, 0.44)
    eH_exit = E_plus_exact(A_MAX, Q_MAX, H_M, H_M, 0.57)
    psi_shapes = {0.0: (0.45, 5.0), 0.005: (0.40, 5.0), 0.010: (0.35, 5.0), 0.015: (0.40, 4.8), 0.020: (0.35, 4.8)}
    x_lo_ruin = {0.0: 8e-5}
    p_sing = 1.0 - (Q_MAX ** 0.5) / BETA_MAX

    # Patience breakdown p_pat vs finite-A certification limit p_cert
    p_pat_mid = 1.0 - 1.0 / (beta * (q + theta * delta))
    p_pat_box = 1.0 - 1.0 / (BETA_MIN * (Q_MAX + theta * (1.0 - Q_MAX)))
    kap_075 = exact_kappa(A_G, delta)
    qF_kap = q + dF_dK(A_G, kap_075, 1.0)
    qF_M = [q + dF_dK(A_G, K, 0.68) for K in (0.10, 0.20, 0.28)]
    print(f"  [Patience] p_pat (mid) = {100*p_pat_mid:.4f}% (box {100*p_pat_box:.4f}%), q+F_K(kappa)={qF_kap:.4f} vs q+F_K(M) in [{min(qF_M):.3f}, {max(qF_M):.3f}]")
    print(f"             x^(-1/2) barrier lower-tail singularity limit: p_sing = 1 - sqrt(q+)/beta+ = {100*p_sing:.4f}%")
    assert abs(p_pat_mid - 0.008723) < 1e-5 and abs(p_pat_box - 0.008573) < 1e-5
    assert abs(p_sing - 0.011217) < 1e-5

    def min_c_E_plus(Av, qv, K, a, l0):
        t = dF_dL(Av, K, l0)
        c_sup = qv * K + F_A(Av, K, l0) + (1.0 - l0) * t - a
        return min(c_sup - t * min(1.0, (1.0 - eta_v) * c_sup / t) for eta_v in (ETA_MIN, ETA_MAX))

    def min_deriv_0_k(psi_arr, s_lo_val, K_bound):
        idx_k = int(np.searchsorted(ks_m, K_bound, side="left"))
        seg_d = (np.diff(psi_arr[:idx_k + 1]) / np.diff(lks_m[:idx_k + 1])) / ks_m[1:idx_k + 1]
        return float(min(s_lo_val / ks_m[0], np.min(seg_d)))

    idx_M_lo = int(np.searchsorted(ks_m, B_M))
    idx_M_hi = int(np.searchsorted(ks_m, H_M))
    assert ks_m[idx_M_lo] == B_M and ks_m[idx_M_hi] == H_M
    m_G = (ETA_MIN * Q_MIN) / C_max
    kp_plus = brentq(lambda K: F_A(A_MAX, K, 1.0) - (1.0 - Q_MAX) * K, 1.0, 100.0)

    print("\n  [Ruin Hazard] Endogenous Doob Certificate T*(p) (continuum [b_min, b_max] Psi^(p), <b/<h slopes, H1 & H2=[0.80, inf)):")
    T_prev = 0
    appendix_ruin = []
    eta_max_c_M_ruin = ETA_MAX / min_c_E_plus(A_MIN, Q_MIN, B_M, B_M, 0.44)
    eta_max_c_H_ruin = ETA_MAX / min_c_E_plus(A_MIN, Q_MIN, H_M, H_M, 0.57)
    for p in [0.0, 0.005, 0.010, 0.015, 0.020]:
        b_min = BETA_MIN * (1.0 - p)
        b_max = BETA_MAX * (1.0 - p)
        WM, trajM, rsM = eval_witness(b_max, B_M, b_solve=b_max, eta_mode="outer")
        WH, trajH, rsH = eval_witness(b_max, H_M, b_solve=b_max, eta_mode="outer")
        W80, traj80, rs80 = eval_witness(b_max, 0.80, b_solve=b_max, eta_mode="outer")
        if p in x_lo_ruin:
            a_c, b_c = psi_shapes[p]
            c_par_hi, d_ub_par, d_lb_par, tail_m_par = certify_psi_centered(A_MAX, b_max, a_c, b_c, x_lo=x_lo_ruin[p], tol=2e-4, buffer=0.0005)
            c_par_lo, _, _, _ = certify_psi_centered(A_MAX, b_min, a_c, b_c, x_lo=x_lo_ruin[p], tol=2e-4, buffer=0.0005)
            c_p_par = max(c_par_hi, c_par_lo)
            psi28_par = a_c * H_M - b_c * (H_M ** -0.5) + c_p_par
        else:
            c_p_par = d_ub_par = d_lb_par = tail_m_par = psi28_par = None

        s_lo_u = ETA_MIN / (1.0 - b_min)
        d_hi_u = ETA_MAX / (1.0 - b_max)
        Vp_1, _ = _hb_solve_markov_pwl(pre_up, b_min, 0.0)
        Vp_1 = Vp_1 + (0.045 / (1.0 - b_max)) * phi_loc
        dp_ub, _, tailp_val = _hb_certify_logpwl_sens_band(A_MAX, Vp_1, Vp_1, b_min, b_max, tol=4e-4, s_tail_arg=s_lo_u, d_hi_arg=d_hi_u)
        c_pwl = max((dp_ub + 0.0002) / (1.0 - b_min), (dp_ub + 0.0002) / (1.0 - b_max))
        psi_10 = float(np.interp(np.log(B_M), lks_m, Vp_1)) + c_pwl
        psi_28 = float(np.interp(np.log(H_M), lks_m, Vp_1)) + c_pwl

        # Verify Psi' >= m_G on every log-PWL segment in M=[0.10, 0.28), plus <b and <h derivative conditions
        seg_d_M_ruin = (np.diff(Vp_1[idx_M_lo:idx_M_hi + 1]) / np.diff(lks_m[idx_M_lo:idx_M_hi + 1])) / ks_m[idx_M_lo + 1:idx_M_hi + 1]
        assert np.all(seg_d_M_ruin >= m_G), f"Ruin Psi' < m_G on M: {np.min(seg_d_M_ruin):.4f} < {m_G:.4f}"
        min_dPsi_b = min_deriv_0_k(Vp_1, s_lo_u, B_M)
        min_dPsi_h = min_deriv_0_k(Vp_1, s_lo_u, H_M)
        assert b_min * min_dPsi_b > eta_max_c_M_ruin, f"Ruin <b slope failed: {b_min * min_dPsi_b:.2f} <= {eta_max_c_M_ruin:.2f}"
        assert b_min * min_dPsi_h > eta_max_c_H_ruin, f"Ruin <h slope failed: {b_min * min_dPsi_h:.2f} <= {eta_max_c_H_ruin:.2f}"

        _, L0_w, k1_w = trajM[0]
        tail_after_0 = WM - rsM[0]
        Ks_M_int = np.linspace(B_M, H_M, 51)
        mExitM_cont = min(
            float(box_worst_u(Q_MIN * Ks_M_int[j] + F_A(A_MIN, Ks_M_int[j], L0_w) - k1_w, L0_w))
            + tail_after_0
            - (E_plus_exact(A_MAX, Q_MAX, Ks_M_int[j + 1], B_M, 0.44) + b_min * psi_10)
            for j in range(50)
        )
        _, L0_H, k1_H = trajH[0]
        tail_after_0_H = WH - rsH[0]
        Ks_H1_int = np.linspace(H_M, 0.80, 51)
        mExitH1_cont = min(
            float(box_worst_u(Q_MIN * Ks_H1_int[j] + F_A(A_MIN, Ks_H1_int[j], L0_H) - k1_H, L0_H))
            + tail_after_0_H
            - (E_plus_exact(A_MAX, Q_MAX, Ks_H1_int[j + 1], H_M, 0.57) + b_min * psi_28)
            for j in range(50)
        )
        # H2 = [0.80, inf): l0=0.57 fails tangency l0>=K/2 for K>1.14; global check via F_A(A_+, K, 1) + 25-step witness at 0.80
        _, L0_80, k1_80 = traj80[0]
        tail_after_0_80 = W80 - rs80[0]
        Ks_H2_int = np.geomspace(0.80, kp_plus, 31)
        mExitH2_fin = min(
            float(box_worst_u(Q_MIN * Ks_H2_int[j] + F_A(A_MIN, Ks_H2_int[j], L0_80) - k1_80, L0_80))
            + tail_after_0_80
            - ((ETA_MIN if (Q_MAX * Ks_H2_int[j + 1] + F_A(A_MAX, Ks_H2_int[j + 1], 1.0) - H_M) < 1.0 else ETA_MAX)
               * np.log(Q_MAX * Ks_H2_int[j + 1] + F_A(A_MAX, Ks_H2_int[j + 1], 1.0) - H_M) + b_min * psi_28)
            for j in range(30)
        )
        c_W_kp = Q_MIN * kp_plus + F_A(A_MIN, kp_plus, L0_80) - k1_80
        c_E_inf = Q_MAX * kp_plus + A_MAX * (2.0 ** 1.5) - H_M
        mExitH2_inf = (
            ETA_MAX * np.log(min(c_W_kp / c_E_inf, Q_MIN / Q_MAX))
            + (1.0 - ETA_MAX) * np.log(1.0 - L0_80)
            + tail_after_0_80
            - b_min * psi_28
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
            f"    p={100*p:4.2f}% | b_eff=[{b_min:.4f},{b_max:.4f}] | stay={marg_stay:5.3f} | "
            f"exitM={mExitM:+.3f}(M:{mExitM_cont:+.3f}), H1={mExitH1_cont:+.3f}, H2={min(mExitH2_fin, mExitH2_inf):+.3f} | "
            f"T*(p)={T_star:2d} ({par_str}) | P_Doob={P_doob:.4f} (vs {P_naive:.4f})"
        )
        assert marg_stay > 0.0 and mExitM > 0.0 and mExitM_cont > 0.0 and mExitH > 0.0
        assert mExitH1_cont > 0.0 and mExitH2_fin > 0.0 and mExitH2_inf > 0.0
        assert T_star >= T_prev
        T_prev = T_star
        appendix_ruin.append((p, c_p_par, d_lb_par, d_ub_par, tail_m_par, c_pwl, psi_10, psi_28, tailp_val, WM, WH, trajM, rsM))

    def stay_gap_fn(p_v):
        b_min = BETA_MIN * (1.0 - p_v)
        b_max = BETA_MAX * (1.0 - p_v)
        WM, _, _ = eval_witness(b_max, B_M, b_solve=b_max, eta_mode="outer")
        D2_p = (ETA_MIN * b_min * Q_MIN * (H_M - B_M)) / C_max
        B1_b_p = (R_hat - D2_p) / (1.0 - b_min) - (ETA_MIN * Q_MIN / C_max) * (H_M - B_M)
        return WM - B1_b_p

    p_cert = brentq(stay_gap_fn, 0.015, 0.025, xtol=1e-5)
    print(f"    Ruin H2 scope: l0=0.57 tangency (l0 >= K/2) holds on H1=[0.28,0.80) and fails for K>1.14; global H2=[0.80,inf) bound passes on [0.80, Kp+={kp_plus:.3f}] & [Kp+,inf).")
    print(f"    Certification breakdown limit (1-step affine barrier, b_max witness): p_cert = {100*p_cert:.4f}%")
    assert abs(p_cert - 0.020434) < 0.0005

    # Coupled 2-State Markov Bellman Barrier System (Omega = {G, B}, A_G=0.75 <-> A_B=0.35, r_rec=1/3)
    print("\n  [Markov System] Coupled 2-State Barrier (B_G, B_B), Continuum [beta_-, beta_+] Cover & Uniform Escape:")
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
    m_B = (ETA_MIN * Q_MIN) / C_max_B

    eMG_exit = E_plus_exact(A_MAX, Q_MAX, B_M, B_M, 0.44)
    eMB_exit = E_plus_exact(AB_MAX, Q_MAX, B_M, B_M, 0.478)
    eHG_exit = E_plus_exact(A_MAX, Q_MAX, H_M, H_M, 0.57)
    eHB_exit = E_plus_exact(AB_MAX, Q_MAX, H_M, H_M, 0.603)
    dE_B_28 = (E_plus_exact(AB_MAX, Q_MAX, H_M + 1e-6, H_M, 0.603) - eHB_exit) / 1e-6
    print(f"    (E_B^+)'(0.28) = {dE_B_28:.4f} (50-interval H1 width 0.0104 loses ~{0.0104 * dE_B_28:.3f}, exceeding boundary margin -> H1 continuous cover holds for G; B certified on 32 subboxes x [beta_-, beta_+] at K=0.28 + pointwise H1)")

    eta_max_c_MG = ETA_MAX / min_c_E_plus(A_MIN, Q_MIN, B_M, B_M, 0.44)
    eta_max_c_MB = ETA_MAX / min_c_E_plus(AB_MIN, Q_MIN, B_M, B_M, 0.478)
    eta_max_c_HG = ETA_MAX / min_c_E_plus(A_MIN, Q_MIN, H_M, H_M, 0.57)
    eta_max_c_HB = ETA_MAX / min_c_E_plus(AB_MIN, Q_MIN, H_M, H_M, 0.603)

    p_markov_list = [0.0, 0.005, 0.01, 0.015, 0.02, 0.05, 0.08, 0.12]
    b_edges_outer = np.linspace(BETA_MIN, BETA_MAX, 9)
    aG_pts = np.linspace(A_MIN, A_MAX, 5)
    aB_pts = np.linspace(AB_MIN, AB_MAX, 3)
    q_pts = np.linspace(Q_MIN, Q_MAX, 3)
    e_pts = np.linspace(ETA_MIN, ETA_MAX, 3)

    print("    (8-subinterval [beta_-, beta_+] continuum outer box + all 32 (4x2x2x2) subboxes x [beta_-, beta_+] continuum cover, uniform eps_0, <b/<h slopes)")
    outer_results = {}
    hb_tasks = []
    for p in p_markov_list:
        P = np.array([[1.0 - p, p], [r_rec, 1.0 - r_rec]])
        m_bar = P @ np.array([m_G, m_B])
        Delta = (H_M - B_M) * np.minimum(np.array([ETA_MIN / C_max, ETA_MIN / C_max_B]), BETA_MIN * m_bar)

        # Build stationary on-grid feasible policy once at BETA_MAX for the outer box, then evaluate W_neg(bR) + W_pos(bL) on every subinterval
        VGm, VBm, pGm, pBm = _hb_solve_markov_pwl(pre_lo, BETA_MAX, p, return_pol=True)
        WG_ref, WB_ref, jbG, jbB, uG_on, uB_on = _hb_eval_wit_chain(
            A_MIN, AB_MIN, Q_MIN, ETA_MIN, ETA_MAX, BETA_MAX, p, VGm, VBm, pGm, pBm
        )
        assert np.all(np.diff(WG_ref[iw_lo:iw_hi + 1]) >= 0.0) and np.all(np.diff(WB_ref[iw_lo:iw_hi + 1]) >= 0.0)
        L0_Gh_arr, _ = _hb_solve_L_wit(A_MIN, Q_MIN, ETA_MIN, ETA_MAX, np.array([H_M]), np.array([ks_wit[jbG[iw_hi]]]))
        L0_Gh, k1_Gh = float(L0_Gh_arr[0]), float(ks_wit[jbG[iw_hi]])
        L0_G80_arr, _ = _hb_solve_L_wit(A_MIN, Q_MIN, ETA_MIN, ETA_MAX, np.array([0.80]), np.array([ks_wit[jbG[idx_w080]]]))
        L0_G80, k1_G80 = float(L0_G80_arr[0]), float(ks_wit[jbG[idx_w080]])

        warm_up = None
        init_neg, init_pos = (WG_ref, WB_ref), None
        worst_res = None
        VGu_seed, VBu_seed = None, None
        for j in range(8):
            bL, bR = float(b_edges_outer[j]), float(b_edges_outer[j + 1])
            VGu0, VBu0 = _hb_solve_markov_pwl(pre_up, bL, p, init=warm_up, tol_out=1e-7)
            warm_up = (VGu0, VBu0)
            if j == 7:
                VGu_seed, VBu_seed = VGu0, VBu0
            bump_R = (0.045 / (1.0 - bR)) * phi_loc
            VGu = VGu0 + bump_R
            VBu = VBu0 + bump_R
            EVGp = (1.0 - p) * VGu + p * VBu
            EVBp = r_rec * VGu + (1.0 - r_rec) * VBu
            dG_ub, _, _ = _hb_certify_logpwl_sens_band(A_MAX, VGu, EVGp, bL, bR, tol=2.5e-4)
            dB_ub, _, _ = _hb_certify_logpwl_sens_band(AB_MAX, VBu, EVBp, bL, bR, tol=2.5e-4)
            cG, cB = np.linalg.solve(np.eye(2) - bL * P, np.array([dG_ub + 3e-5, dB_ub + 3e-5]))
            resR = (np.eye(2) - bR * P) @ np.array([cG, cB]) - np.array([dG_ub + 3e-5, dB_ub + 3e-5])
            if np.min(resR) < 0.0:
                dc = -float(np.min(resR)) / (1.0 - bR) + 1e-7
                cG += dc
                cB += dc
            PsiG_arr = VGu + cG
            PsiB_arr = VBu + cB

            # Assert Psi'_omega(x) >= m_omega on every log-PWL segment in M=[0.10, 0.28)
            seg_d_MG = (np.diff(PsiG_arr[idx_M_lo:idx_M_hi + 1]) / np.diff(lks_m[idx_M_lo:idx_M_hi + 1])) / ks_m[idx_M_lo + 1:idx_M_hi + 1]
            seg_d_MB = (np.diff(PsiB_arr[idx_M_lo:idx_M_hi + 1]) / np.diff(lks_m[idx_M_lo:idx_M_hi + 1])) / ks_m[idx_M_lo + 1:idx_M_hi + 1]
            assert np.all(seg_d_MG >= m_G) and np.all(seg_d_MB >= m_B)

            # Continuous <b and <h down-exit derivative conditions across [bL, bR]
            s_lo_L = ETA_MIN / (1.0 - bL)
            assert bL * min_deriv_0_k(EVGp, s_lo_L, B_M) > eta_max_c_MG
            assert bL * min_deriv_0_k(EVBp, s_lo_L, B_M) > eta_max_c_MB
            assert bL * min_deriv_0_k(EVGp, s_lo_L, H_M) > eta_max_c_HG
            assert bL * min_deriv_0_k(EVBp, s_lo_L, H_M) > eta_max_c_HB

            WG_lb, WB_lb, init_neg, init_pos = _hb_eval_band_W_lb(
                p, bL, bR, jbG, jbB, uG_on, uB_on, init_neg=init_neg, init_pos=init_pos
            )
            assert np.all(np.diff(WG_lb[iw_lo:iw_hi + 1]) >= 0.0) and np.all(np.diff(WB_lb[iw_lo:iw_hi + 1]) >= 0.0)
            WG0 = float(np.min(WG_lb[ks_wit >= B_M]))
            WB0 = float(np.min(WB_lb[ks_wit >= B_M]))
            WGh = float(np.min(WG_lb[ks_wit >= H_M]))

            B_star_L = np.linalg.solve(np.eye(2) - bL * P, np.array([R_hat, R_hat_B]) - Delta)
            B_star_R = np.linalg.solve(np.eye(2) - bR * P, np.array([R_hat, R_hat_B]) - Delta)
            B_star_max = np.maximum(B_star_L, B_star_R)
            B_star_min = np.minimum(B_star_L, B_star_R)
            B_b_max = np.array([B_star_max[0] - m_G * (H_M - B_M), B_star_max[1] - m_B * (H_M - B_M)])

            PsiGb = float(np.interp(np.log(B_M), lks_m, PsiG_arr))
            PsiBb = float(np.interp(np.log(B_M), lks_m, PsiB_arr))
            PsiGh = float(np.interp(np.log(H_M), lks_m, PsiG_arr))
            PsiBh = float(np.interp(np.log(H_M), lks_m, PsiB_arr))
            PsiG_ym = float(np.interp(np.log(y_max_exit), lks_m, PsiG_arr))
            PsiB_ym = float(np.interp(np.log(y_max_exit), lks_m, PsiB_arr))

            # Uniform margins across all x0 in M=[0.10, 0.28)
            inf_mG = float(np.min(WG_lb[iw_lo:iw_hi] - (B_star_max[0] + m_G * (ks_wit[iw_lo + 1:iw_hi + 1] - H_M))))
            inf_mB = float(np.min(WB_lb[iw_lo:iw_hi] - (B_star_max[1] + m_B * (ks_wit[iw_lo + 1:iw_hi + 1] - H_M))))
            inf_marg = min(inf_mG, inf_mB)
            margG = WG0 - B_b_max[0]
            margB = WB0 - B_b_max[1]
            max_exit = max(PsiGh - B_star_min[0], PsiBh - B_star_min[1])
            T_G = int(np.ceil(np.log(margG / max_exit) / np.log(bR)))
            T_B = int(np.ceil(np.log(margB / max_exit) / np.log(bR)))

            EVGb_p = (1.0 - p) * PsiGb + p * PsiBb
            EVBb_p = r_rec * PsiGb + (1.0 - r_rec) * PsiBb
            EVGh_p = (1.0 - p) * PsiGh + p * PsiBh
            EVBh_p = r_rec * PsiGh + (1.0 - r_rec) * PsiBh
            mExitMG = WG0 - (eMG_exit + bL * EVGb_p)
            mExitMB = WB0 - (eMB_exit + bL * EVBb_p)
            mExitHG = WGh - (eHG_exit + bL * EVGh_p)

            min_M_G = min(
                float(WG_lb[ii]) - (E_plus_exact(A_MAX, Q_MAX, float(ks_wit[ii + 1]), B_M, 0.44) + bL * EVGb_p)
                for ii in range(iw_lo, iw_hi)
            )
            min_M_B = min(
                float(WB_lb[ii]) - (E_plus_exact(AB_MAX, Q_MAX, float(ks_wit[ii + 1]), B_M, 0.478) + bL * EVBb_p)
                for ii in range(iw_lo, iw_hi)
            )
            # H1=[0.28, 0.80) 50-interval continuous cover and H2=[0.80, inf) global check in G
            tail_HG = float(WG_lb[iw_hi] - uG_on[iw_hi])
            Ks_H1_int = np.linspace(H_M, 0.80, 51)
            mExitH1_G = min(
                float(box_worst_u(Q_MIN * Ks_H1_int[k] + F_A(A_MIN, Ks_H1_int[k], L0_Gh) - k1_Gh, L0_Gh))
                + tail_HG - (E_plus_exact(A_MAX, Q_MAX, Ks_H1_int[k + 1], H_M, 0.57) + bL * EVGh_p)
                for k in range(50)
            )
            tail_G80 = float(WG_lb[idx_w080] - uG_on[idx_w080])
            Ks_H2_int = np.geomspace(0.80, kp_plus, 31)
            mExitH2_G_fin = min(
                float(box_worst_u(Q_MIN * Ks_H2_int[k] + F_A(A_MIN, Ks_H2_int[k], L0_G80) - k1_G80, L0_G80))
                + tail_G80 - ((ETA_MIN if (Q_MAX * Ks_H2_int[k + 1] + F_A(A_MAX, Ks_H2_int[k + 1], 1.0) - H_M) < 1.0 else ETA_MAX)
                              * np.log(Q_MAX * Ks_H2_int[k + 1] + F_A(A_MAX, Ks_H2_int[k + 1], 1.0) - H_M) + bL * EVGh_p)
                for k in range(30)
            )
            c_WG_kp = Q_MIN * kp_plus + F_A(A_MIN, kp_plus, L0_G80) - k1_G80
            c_EG_inf = Q_MAX * kp_plus + A_MAX * (2.0 ** 1.5) - H_M
            mExitH2_G_inf = (
                ETA_MAX * np.log(min(c_WG_kp / c_EG_inf, Q_MIN / Q_MAX))
                + (1.0 - ETA_MAX) * np.log(1.0 - L0_G80) + tail_G80 - bL * EVGh_p
            )
            # Uniform escape probability lower bound eps_0 = inf_{x0 in M, omega in {G,B}} P(tau <= T0) > 0 (1 in denominator, valid as x0 -> h)
            T0_unif = int(np.ceil(np.log(inf_marg / max_exit) / np.log(bR))) + 4
            max_ym_gap = max(PsiG_ym - B_star_min[0], PsiB_ym - B_star_min[1])
            eps_0 = (inf_marg - (bR ** T0_unif) * max_exit) / (1.0 * max_ym_gap - (bR ** T0_unif) * max_exit)

            assert margG > 0.0 and margB > 0.0 and inf_marg > 0.0
            assert min_M_G > 0.0 and min_M_B > 0.0 and mExitHG > 0.0
            assert mExitH1_G > 0.0 and mExitH2_G_fin > 0.0 and mExitH2_G_inf > 0.0
            assert 0.0 < eps_0 <= 1.0

            if worst_res is None:
                worst_res = dict(
                    BG=B_b_max[0], BB=B_b_max[1], cG=cG, cB=cB, WG0=WG0, WB0=WB0,
                    margG=margG, margB=margB, T_G=T_G, T_B=T_B,
                    mExitMG=mExitMG, mExitMB=mExitMB, min_M_G=min_M_G, min_M_B=min_M_B,
                    mExitHG=mExitHG, mExitH1_G=mExitH1_G, mExitH2_G=min(mExitH2_G_fin, mExitH2_G_inf),
                    T0=T0_unif, eps_0=eps_0,
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
                worst_res["mExitH1_G"] = min(worst_res["mExitH1_G"], mExitH1_G)
                worst_res["mExitH2_G"] = min(worst_res["mExitH2_G"], mExitH2_G_fin, mExitH2_G_inf)
                worst_res["T0"] = max(worst_res["T0"], T0_unif)
                worst_res["eps_0"] = min(worst_res["eps_0"], eps_0)
        outer_results[p] = worst_res

        for ie in range(2):
            for iq in range(2):
                for iG in range(4):
                    for iB in range(2):
                        hb_tasks.append((
                            p, aG_pts[iG], aG_pts[iG + 1], aB_pts[iB], aB_pts[iB + 1],
                            q_pts[iq], q_pts[iq + 1], e_pts[ie], e_pts[ie + 1],
                            VGm, VBm, pGm, pBm, (VGu_seed, VBu_seed),
                        ))

    # Certify ALL 32 subboxes x [BETA_MIN, BETA_MAX] continuum for mExitHB_box across all 8 p in parallel
    hb_box_min = {p: 1e9 for p in p_markov_list}
    hb_box_leaves = {p: 0 for p in p_markov_list}
    n_workers = min(12, os.cpu_count() or 4)
    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        for p_res, m_sub, n_lf in pool.map(_hb_worker_subbox, hb_tasks):
            hb_box_min[p_res] = min(hb_box_min[p_res], m_sub)
            hb_box_leaves[p_res] += n_lf

    appendix_markov = []
    for p in p_markov_list:
        wr = outer_results[p]
        m_hb_bx = hb_box_min[p]
        assert m_hb_bx > 0.0, f"Markov 32-subbox [BETA_MIN, BETA_MAX] mExitHB failed at p={p}: {m_hb_bx}"
        print(
            f"    p={100*p:4.1f}% | BG={wr['BG']:7.3f} (marg={wr['margG']:5.2f}, T*_G={wr['T_G']:2d}) | "
            f"BB={wr['BB']:7.3f} (marg={wr['margB']:5.2f}, T*_B={wr['T_B']:2d}) | "
            f"exit(M:G/B={wr['mExitMG']:+.2f}/{wr['mExitMB']:+.3f} [M>={wr['min_M_B']:+.3f}], "
            f"H:G_1={wr['mExitH1_G']:+.2f}, G_2={wr['mExitH2_G']:+.2f}, B_32bx={m_hb_bx:+.4f} [{hb_box_leaves[p]} lf]) | "
            f"eps_0=inf P(tau<={wr['T0']})>={wr['eps_0']:.4f}"
        )
        appendix_markov.append((
            p, wr["cG"], wr["cB"], wr["WG0"], wr["WB0"],
            wr["margG"], wr["margB"], wr["T_G"], wr["T_B"],
            wr["mExitMG"], wr["mExitMB"], wr["mExitHG"], m_hb_bx, wr["T0"], wr["eps_0"],
        ))

    # Markov staying breakdown p_cert^Markov (where margB crosses 0)
    def markov_stay_B_gap(p_v):
        P_v = np.array([[1.0 - p_v, p_v], [r_rec, 1.0 - r_rec]])
        mb = P_v @ np.array([m_G, m_B])
        Del = (H_M - B_M) * np.minimum(np.array([ETA_MIN / C_max, ETA_MIN / C_max_B]), BETA_MIN * mb)
        Bs = np.linalg.solve(np.eye(2) - BETA_MIN * P_v, np.array([R_hat, R_hat_B]) - Del)
        Bb = Bs[1] - m_B * (H_M - B_M)
        _, VBm_v = _hb_solve_markov_pwl(pre_lo, BETA_MAX, p_v)
        return float(np.interp(np.log(B_M), lks_m, VBm_v)) - Bb

    p_cert_markov = brentq(markov_stay_B_gap, 0.12, 0.18, xtol=1e-4)
    print(f"    Markov staying breakdown limit (B-state stay-root extrapolation; exit certs verified over [beta_-, beta_+] on p in {{0%..12%}}): p_cert^Markov = {100*p_cert_markov:.2f}%")
    assert 0.14 < p_cert_markov < 0.17

    # Forward-Looking Stochastic VFI Policy & Threshold Comparison (Continuous Golden-Section Ruin + Markov)
    print("\n  [Stochastic VFI] Forward-Looking Stochastic VFI (Continuous Golden-Section Ruin & Markov):")
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

    def solve_cont_markov_vfi(p_val, r_rec_val):
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
        S_G, S_Bkink, KB_star, kp_m, L_m = solve_cont_markov_vfi(p, r_rec)
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

    # Recovery probability r_rec sensitivity at p = 8%
    print("\n  [Recovery Sensitivity] Recovery probability r_rec sensitivity at p=8.0%:")
    for r_val in (0.20, 1.0 / 3.0, 0.50):
        sg_r, sbk_r, kbs_r, kpm_r, lm_r = solve_cont_markov_vfi(0.08, r_val)
        print(f"    r_rec={r_val:.4f}: S_G={sg_r:.6f}, S_B_kink={sbk_r:.5f}, K_B*={kbs_r:.5f}, K'_G(0.10)={kpm_r:.5f}, L_G={lm_r:.4f}")

    # Technical Appendix Reproducibility Summary
    print("\n  [APPENDIX] Technical Appendix Reproducibility Certificates:")
    print("    (A) Ruin Super-Barriers (Parametric x^(-1/2) for p<1.12%, Continuous Log-PWL for all p in [0%,2%]) & 25-step W_M^(p):")
    for p, c_p_par, d_lb_par, d_ub_par, tail_m_par, c_pwl, psi_10, psi_28, tailp_val, WM, WH, trajM, rsM in appendix_ruin:
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
    print("    (B) Coupled Markov Log-PWL Shifts (c_G, c_B), Adverse-Exit Margins & Uniform Escape:")
    for p, cG, cB, WG0, WB0, mG, mB, TG, TB, eMG, eMB, eHG, eHB_s, T0_u, eps0_u in appendix_markov:
        print(
            f"      p={100*p:4.1f}% | (c_G,c_B)=({cG:.4f},{cB:.4f}) | W_G={WG0:.4f}, W_B={WB0:.4f} | "
            f"stay=({mG:.3f},{mB:.3f}) | T*=({TG},{TB}) | exit(M:G={eMG:+.3f},B={eMB:+.3f}; H:G={eHG:+.3f},B_32bx={eHB_s:+.4f}) | "
            f"eps_0=inf P(tau<={T0_u})>={eps0_u:.4f}"
        )


if __name__ == "__main__":
    verify_barriers()
    verify_restricted_M_vfi()
    verify_prop1_double_star()
    verify_theorem3_star()
    verify_theorem10()
    verify_prop4_star_stochastic()
    print("\nALL ANALYTICAL AND NUMERICAL CHECKS PASSED SUCCESSFULLY.")
