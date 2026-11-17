import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import brentq

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

# Box (7.3) parameters
A_min, A_max = 0.749, 0.751
beta_min, beta_max = 0.9699, 0.9701
q_min, q_max = 0.9199, 0.9201
eta_min, eta_max = 0.6999, 0.7001
b, h = 0.10, 0.28


def F_A(A, K, L):
    return A * (2.0 * K * L / (K + L)) ** 1.5


def dF_dL(A, K, L):
    return 1.5 * A * ((2.0 * K * L / (K + L)) ** 0.5) * (2.0 * K ** 2 / (K + L) ** 2)


def exact_kappa(A_val, delta_val=0.08):
    coeffs = [-delta_val**2, -3 * delta_val**2, 8 * (A_val**2) - 3 * delta_val**2, -delta_val**2]
    roots = np.roots(coeffs)
    real_pos = sorted([np.real(rt) for rt in roots if np.isreal(rt) and np.real(rt) > 0])
    return real_pos[0]


C_max_plus = q_max * h + F_A(A_max, h, 1.0) - b
R_hat = -0.996
Delta_2 = 0.2997
B_max_paper = R_hat / (1.0 - beta_min) - Delta_2 / (1.0 - beta_min**2)
B_star_new = (R_hat - Delta_2) / (1.0 - beta_min)
slope_min = eta_min * q_min / C_max_plus


# ==============================================================================
# FIGURE 1: State-Dependent Affine Barrier vs. Milei-Reidel (2026) Barrier
# ==============================================================================
def make_fig1(lang):
    K_grid = np.linspace(b, h, 300)
    c_witness = q_min * K_grid + F_A(A_min, K_grid, 0.68) - 0.135
    u_witness_1 = eta_min * np.log(c_witness) + (1.0 - eta_min) * np.log(1.0 - 0.68)
    u_witness_2 = eta_max * np.log(c_witness) + (1.0 - eta_max) * np.log(1.0 - 0.68)
    W_M_curve = np.minimum(u_witness_1, u_witness_2) + beta_max * (-33.103)
    Psi_sharp_curve = 0.4 * K_grid - 5.0 / np.sqrt(K_grid) - 18.5 - 10.0 / 301.0
    B_0_curve = np.full_like(K_grid, B_max_paper)
    B_1_curve = B_star_new - slope_min * (h - K_grid)

    T_vals = np.arange(1, 51)
    T_even = np.arange(2, 51, 2)
    prefix_paper = B_max_paper + (beta_max**T_even) * (-27.83 - B_max_paper)
    prefix_new_uniform = B_star_new + (beta_max**T_vals) * (-27.83 - B_star_new)
    prefix_new_exact = (B_star_new - slope_min * (h - b)) + (beta_max**T_vals) * (-27.870334 - B_star_new)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.45), dpi=300)
    fig.subplots_adjust(wspace=0.26, bottom=0.15, top=0.87, left=0.08, right=0.97)

    if lang == 'es':
        lbl_psi = r'Techo de continuación $\Psi^\sharp(K) \geq V(K)$'
        lbl_wm = r'Testigo factible $W_M(K)$'
        lbl_b0 = r'Cota de barrera de 2 pasos $B_0$ (Milei-Reidel: $-38.14$)'
        lbl_b1 = r'Nueva barrera afín de 1 paso $B_1(K)$ ($-43.36$ a $-43.05$)'
        ann_m0 = r'Margen original $\geq 2.564$'
        ann_gain = r'Ganancia adicional de calibración ($+4.90$ a $+5.21$)'
        xlab1 = r'Stock de capital en región de tránsito $K \in M = [0.10, 0.28)$'
        ylab1 = r'Bienestar descontado'
        tit1 = r'(a) Calibración de barreras regionales en $M = [0.10, 0.28)$'
        lbl_wmb = r'Piso del testigo en el borde $W_M(0.10) = -35.58$'
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
        lbl_wm = r'Feasible witness $W_M(K)$'
        lbl_b0 = r'2-step block bound $B_0$ (Milei-Reidel: $-38.14$)'
        lbl_b1 = r'New 1-step affine barrier $B_1(K)$ ($-43.36$ to $-43.05$)'
        ann_m0 = r'Original margin $\geq 2.564$'
        ann_gain = r'Additional calibration gain ($+4.90$ to $+5.21$)'
        xlab1 = r'Staging capital stock $K \in M = [0.10, 0.28)$'
        ylab1 = r'Discounted welfare'
        tit1 = r'(a) Regional barrier calibration on $M = [0.10, 0.28)$'
        lbl_wmb = r'Endpoint witness floor $W_M(0.10) = -35.58$'
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
    ax1.annotate(ann_gain, xy=(0.118, -40.7), xytext=(0.118, -40.7), fontsize=8.5, color='#1f4e78', fontweight='bold')
    ax1.set_xlim(0.10, 0.28)
    ax1.set_ylim(-44.8, -23.5)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper left', fontsize=7.6, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, linestyle=':', alpha=0.35)

    ax2.axhline(-35.58, color='#1b7837', linestyle='-', linewidth=1.8, label=lbl_wmb)
    ax2.plot(T_even, prefix_paper, 'o--', color='#d95f02', markersize=3.4, linewidth=1.6, label=lbl_pp)
    ax2.plot(T_vals, prefix_new_uniform, '-', color='#1f4e78', linewidth=2.0, label=lbl_pu)
    ax2.plot(T_vals, prefix_new_exact, '-.', color='#0b2c4d', linewidth=1.6, label=lbl_pe)
    ax2.axvline(46, color='#d95f02', linestyle=':', linewidth=1.2)
    ax2.axvline(23, color='#0b2c4d', linestyle=':', linewidth=1.2)
    ax2.axvline(24, color='#1f4e78', linestyle=':', linewidth=1.2)
    ax2.scatter([46], [-35.5915], color='#d95f02', zorder=5, s=40)
    ax2.scatter([24], [-35.7029], color='#1f4e78', zorder=5, s=40)
    ax2.scatter([23], [-35.7220], color='#0b2c4d', zorder=5, s=40)

    ax2.annotate(ann_new, xy=(23.5, -35.7), xytext=(8.5, -38.8),
                 arrowprops=dict(arrowstyle='->', color='#1f4e78', lw=1.0),
                 fontsize=8.5, color='#1f4e78', fontweight='bold')
    ax2.annotate(ann_old, xy=(46, -35.59), xytext=(29.5, -40.2),
                 arrowprops=dict(arrowstyle='->', color='#d95f02', lw=1.0),
                 fontsize=8.5, color='#d95f02', fontweight='bold')
    ax2.set_xlim(1, 50)
    ax2.set_ylim(-41.5, -27.2)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='upper right', fontsize=7.5, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig1_barrier_{lang}.{ext}'), **kw)
    plt.close()


# ==============================================================================
# FIGURE 2: Asymptotic Scaling & Endogenous vs Fixed Labor (Footnote 1 & Thm 3)
# ==============================================================================
def make_fig2(lang):
    A_vals = np.logspace(np.log10(0.75), np.log10(30.0), 250)
    theta, rho, w, delta, beta, eta = 1.5, -1.0, 0.5, 0.08, 0.97, 0.70
    r_exp = theta - 1.0
    c_K = w ** (theta / rho)
    nu = (1.0 - eta) / eta
    D = 1.0 / beta - (1.0 - delta)

    kappa_A = np.array([exact_kappa(a, delta) for a in A_vals])
    kappa_asymp = ((delta / c_K) ** (1.0 / r_exp)) * (A_vals ** (-1.0 / r_exp))
    S_upper_asymp = ((D / c_K) ** (1.0 / r_exp)) * (A_vals ** (-1.0 / r_exp))
    S_thm8_bound = 0.0014025025 / (A_vals ** 2)

    # Exact FOC curves evaluated at benchmark point (k_b, c_b) = (0.002, 0.0001) on critical scale
    k_b, c_b = 0.002, 0.0001
    K_crit = k_b * (A_vals ** (-1.0 / r_exp))
    C_crit = c_b * (A_vals ** (-1.0 / r_exp))
    L_star = np.array([
        brentq(lambda L: dF_dL(a, K_v, L) - nu * C_v / (1.0 - L), K_v / 3.0, 1.0 - 1e-12)
        for a, K_v, C_v in zip(A_vals, K_crit, C_crit)
    ])
    KL_ratio = K_crit / L_star
    leisure_cost = (1.0 - eta) * np.abs(np.log(1.0 - L_star))

    # Verified VFI frontier gap (S_endo / S_fix(1) - 1) across A in [0.75, 30.0]
    A_vfi = np.array([0.75, 1.50, 3.00, 10.0, 30.0])
    frontier_gap_vfi = np.array([1.02078, 1.01183, 1.00717, 1.00371, 1.00255]) - 1.0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4), dpi=300)
    fig.subplots_adjust(wspace=0.26, bottom=0.15, top=0.87, left=0.08, right=0.97)

    if lang == 'es':
        l_thm8 = r'Cota superior explícita Teorema 8 ($.0014025/A^2$)'
        l_sup = r'Cota superior asintótica $(D/c_K)^2 A^{-2}$'
        l_kap = r'Umbral físico exacto $\kappa_A$'
        l_kasy = r'Asintótica física $(\delta/c_K)^2 A^{-2}$'
        l_band = r'Banda de localización de $S_A$ (Trabajo endógeno y fijo)'
        xlab1 = r'Productividad total de los factores $A$ (escala log)'
        ylab1 = r'Umbrales de capital $\kappa_A, S_A$ (escala log)'
        tit1 = r'(a) Ley de escalamiento $S_A = \Theta(A^{-1/(\theta-1)})$'
        l_L = r'Trabajo óptimo en frontera $L^*(A) \propto A^{-1}$'
        l_loss = r'Costo de utilidad del ocio $(1-\eta)|\ln(1-L^*)| \propto A^{-1}$'
        l_KL = r'Razón capital/trabajo $K(A)/L^*(A) \propto A^{-1} \to 0$'
        l_fgap = r'Brecha de fronteras VFI $S_A^{\mathrm{endo}}/S_A^{\mathrm{fix}}(1) - 1 \to 0$'
        l_K = r'Escala crítica de capital $K(A) = k A^{-2}$'
        xlab2 = r'Productividad total de los factores $A$ (escala log)'
        ylab2 = r'Magnitudes FOC $(k=0.002)$ y brecha VFI'
        tit2 = r'(b) Convergencia trabajo endógeno vs. fijo (Nota 1)'
    else:
        l_thm8 = r'Theorem 8 explicit upper bound ($.0014025/A^2$)'
        l_sup = r'Asymptotic upper bound $(D/c_K)^2 A^{-2}$'
        l_kap = r'Exact physical threshold $\kappa_A$'
        l_kasy = r'Physical asymptote $(\delta/c_K)^2 A^{-2}$'
        l_band = r'Localization band of $S_A$ (Endogenous & fixed labor)'
        xlab1 = r'Total factor productivity $A$ (log scale)'
        ylab1 = r'Capital thresholds $\kappa_A, S_A$ (log scale)'
        tit1 = r'(a) Scaling law $S_A = \Theta(A^{-1/(\theta-1)})$'
        l_L = r'Optimal frontier labor $L^*(A) \propto A^{-1}$'
        l_loss = r'Leisure utility cost $(1-\eta)|\ln(1-L^*)| \propto A^{-1}$'
        l_KL = r'Capital-labor ratio $K(A)/L^*(A) \propto A^{-1} \to 0$'
        l_fgap = r'VFI frontier gap $S_A^{\mathrm{endo}}/S_A^{\mathrm{fix}}(1) - 1 \to 0$'
        l_K = r'Critical capital scale $K(A) = k A^{-2}$'
        xlab2 = r'Total factor productivity $A$ (log scale)'
        ylab2 = r'FOC magnitudes $(k=0.002)$ & VFI gap'
        tit2 = r'(b) Endogenous vs. fixed labor convergence (Footnote 1)'

    ax1.loglog(A_vals, S_thm8_bound, '--', color='#d95f02', linewidth=1.7, label=l_thm8)
    ax1.loglog(A_vals, S_upper_asymp, '-', color='#1f4e78', linewidth=2.1, label=l_sup)
    ax1.loglog(A_vals, kappa_A, '-', color='#1b7837', linewidth=2.0, label=l_kap)
    ax1.loglog(A_vals, kappa_asymp, ':', color='#444444', linewidth=1.5, label=l_kasy)
    ax1.fill_between(A_vals, kappa_A, S_upper_asymp, color='#1f4e78', alpha=0.13, label=l_band)
    ax1.set_xlim(0.75, 30.0)
    ax1.set_ylim(4e-7, 6e-2)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper right', fontsize=7.4, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, which='both', linestyle=':', alpha=0.35)

    ax2.loglog(A_vals, L_star, '-', color='#1f4e78', linewidth=2.1, label=l_L)
    ax2.loglog(A_vals, leisure_cost, ':', color='#7b3294', linewidth=2.0, label=l_loss)
    ax2.loglog(A_vals, KL_ratio, '--', color='#d95f02', linewidth=1.8, label=l_KL)
    ax2.loglog(A_vfi, frontier_gap_vfi, 'o-', color='#c00000', markersize=4.5, linewidth=1.7, label=l_fgap)
    ax2.loglog(A_vals, K_crit, '-.', color='#1b7837', linewidth=1.8, label=l_K)
    ax2.set_xlim(0.75, 30.0)
    ax2.set_ylim(1.5e-6, 3.0)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='upper right', fontsize=6.9, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, which='both', linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig2_scaling_{lang}.{ext}'), **kw)
    plt.close()


# ==============================================================================
# FIGURE 3: Institutional U-Curve for Minimum Viable Scale (Section 4.3 Extension)
# ==============================================================================
def make_fig3(lang):
    tau_grid = np.concatenate([np.logspace(-6, np.log10(0.015), 250), np.linspace(0.015, 0.97, 500)])
    alpha_pub = 0.25
    A_0 = 1.45
    theta, rho, w, delta, beta = 1.5, -1.0, 0.5, 0.08, 0.97
    c_K = w ** (theta / rho)
    D = 1.0 / beta - (1.0 - delta)
    k_a = 0.5
    H_a = ((2.0 * k_a / (k_a + 1.0)) ** 1.5) / k_a
    A_rep = delta / H_a  # 0.07348469
    tau_opt = alpha_pub / (1.0 + alpha_pub)  # 0.20

    A_eff = A_0 * (tau_grid ** alpha_pub) * (1.0 - tau_grid)
    tau_min_crit = brentq(lambda t: A_0 * (t**alpha_pub) * (1.0 - t) - A_rep, 1e-9, tau_opt)
    tau_max_crit = brentq(lambda t: A_0 * (t**alpha_pub) * (1.0 - t) - A_rep, tau_opt, 1.0 - 1e-9)

    valid = (tau_grid >= 0.008) & (tau_grid <= 0.935)
    tau_valid = tau_grid[valid]
    A_valid = A_eff[valid]
    kappa_tau = np.array([exact_kappa(a, delta) for a in A_valid])
    S_upper_tau = ((D / c_K) ** 2) / (A_valid ** 2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4), dpi=300)
    fig.subplots_adjust(wspace=0.26, bottom=0.15, top=0.87, left=0.08, right=0.97)

    if lang == 'es':
        l_ae = r'Productividad neta $A_e(\tau) = A_0 \tau^\alpha (1-\tau)$'
        l_lin = r'Pérdida lineal pura $A(1-\tau)$ (Sección 4.3 original)'
        l_rep = r'Umbral de reposición física $A_{\mathrm{rep}} = 0.0735$'
        l_opt = r'Carga óptima $\tau^* = \frac{\alpha}{1+\alpha} = 0.20$'
        l_ext = r'Extinción global ($A_e(\tau) \leq A_{\mathrm{rep}}$)'
        xlab1 = r'Carga tributaria / regulatoria $\tau \in (0, 1)$'
        ylab1 = r'Productividad efectiva $A_e(\tau)$'
        tit1 = r'(a) Productividad neta con infraestructura pública y distorsión'
        l_S = r'Cota superior certificada $\overline{S}(\tau)$'
        l_K = r'Piso de mantenimiento físico $\kappa(\tau)$'
        l_liq = r'Banda de localización $(\kappa(\tau), \overline{S}(\tau))$'
        l_an = r'Trampa de anarquía ($\tau < \tau_{\min} \approx 6.6\times 10^{-6}$)'
        l_ov = r'Trampa de sobre-regulación ($\tau > \tau_{\max} \approx 0.949$)'
        ann_min = r'Mínimo de $\overline{S}(\tau)$ y $\kappa(\tau)$ en $\tau^* = 0.20$'
        xlab2 = r'Carga tributaria / regulatoria $\tau \in (0, 1)$'
        ylab2 = r'Umbrales de capital $\kappa(\tau), \overline{S}(\tau)$ (escala log)'
        tit2 = r'(b) Curva en U de la cota certificada $\overline{S}(\tau)$ y $\kappa(\tau)$'
    else:
        l_ae = r'Net productivity $A_e(\tau) = A_0 \tau^\alpha (1-\tau)$'
        l_lin = r'Pure linear wedge $A(1-\tau)$ (Original Sec. 4.3)'
        l_rep = r'Physical replacement threshold $A_{\mathrm{rep}} = 0.0735$'
        l_opt = r'Optimal burden $\tau^* = \frac{\alpha}{1+\alpha} = 0.20$'
        l_ext = r'Global extinction ($A_e(\tau) \leq A_{\mathrm{rep}}$)'
        xlab1 = r'Fiscal / regulatory wedge $\tau \in (0, 1)$'
        ylab1 = r'Effective productivity $A_e(\tau)$'
        tit1 = r'(a) Net productivity with public infrastructure and distortion'
        l_S = r'Certified upper bound $\overline{S}(\tau)$'
        l_K = r'Physical maintenance floor $\kappa(\tau)$'
        l_liq = r'Localization band $(\kappa(\tau), \overline{S}(\tau))$'
        l_an = r'Anarchy trap ($\tau < \tau_{\min} \approx 6.6\times 10^{-6}$)'
        l_ov = r'Over-regulation trap ($\tau > \tau_{\max} \approx 0.949$)'
        ann_min = r'Minimum of $\overline{S}(\tau)$ and $\kappa(\tau)$ at $\tau^* = 0.20$'
        xlab2 = r'Fiscal / regulatory wedge $\tau \in (0, 1)$'
        ylab2 = r'Capital thresholds $\kappa(\tau), \overline{S}(\tau)$ (log scale)'
        tit2 = r'(b) Institutional U-Curve for $\overline{S}(\tau)$ and $\kappa(\tau)$'

    ax1.plot(tau_grid, A_eff, '-', color='#1f4e78', linewidth=2.2, label=l_ae)
    ax1.plot(tau_grid, A_0 * 0.67 * (1.0 - tau_grid), '--', color='#888888', linewidth=1.4, label=l_lin)
    ax1.axhline(A_rep, color='#c00000', linestyle=':', linewidth=1.6, label=l_rep)
    ax1.axvline(tau_opt, color='#1b7837', linestyle='--', linewidth=1.3, label=l_opt)
    ax1.axvspan(0.0, max(tau_min_crit, 0.008), color='#c00000', alpha=0.12)
    ax1.axvspan(tau_max_crit, 0.98, color='#c00000', alpha=0.14, label=l_ext)
    ax1.scatter([tau_max_crit], [A_rep], color='#c00000', s=32, zorder=5)

    ax1.set_xlim(0.0, 0.98)
    ax1.set_ylim(0.0, 1.08)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper right', fontsize=7.3, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, linestyle=':', alpha=0.35)

    ax2.semilogy(tau_valid, S_upper_tau, '-', color='#1f4e78', linewidth=2.2, label=l_S)
    ax2.semilogy(tau_valid, kappa_tau, '--', color='#1b7837', linewidth=1.8, label=l_K)
    ax2.fill_between(tau_valid, kappa_tau, S_upper_tau, color='#d95f02', alpha=0.18, label=l_liq)
    ax2.axvline(tau_opt, color='#1b7837', linestyle='--', linewidth=1.3)
    ax2.axvspan(0.0, 0.008, color='#c00000', alpha=0.12, label=l_an)
    ax2.axvspan(tau_max_crit, 0.98, color='#800000', alpha=0.16, label=l_ov)
    ax2.scatter([tau_opt], [S_upper_tau.min()], color='#1f4e78', s=36, zorder=5)

    ax2.annotate(ann_min, xy=(tau_opt, S_upper_tau.min()),
                 xytext=(0.25, 0.0115),
                 arrowprops=dict(arrowstyle='->', color='#1f4e78', lw=1.1),
                 fontsize=8.5, color='#1f4e78', fontweight='bold')
    ax2.set_xlim(0.0, 0.98)
    ax2.set_ylim(7e-4, 0.45)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='upper center', fontsize=7.2, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, which='both', linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig3_ucurve_{lang}.{ext}'), **kw)
    plt.close()


# ==============================================================================
# FIGURE 4: Structural Extensions — Growth & Stochastic Bellman Barriers
# ==============================================================================
def make_fig4(lang):
    t_grid = np.arange(0, 45)
    g_rate = 0.025
    K_hat_M1 = 0.34 - (0.34 - 0.06) * np.exp(-0.11 * t_grid)
    K_real_hockey = ((1.0 + g_rate) ** t_grid) * K_hat_M1
    K_stationary_orig = K_hat_M1
    K_hat_fragmented = 0.06 * (0.91 ** t_grid)
    K_real_fragmented = ((1.0 + g_rate) ** t_grid) * K_hat_fragmented

    p_hazard = np.linspace(0.0, 0.0285, 285)
    surv_46 = (1.0 - p_hazard) ** 46
    surv_23 = (1.0 - p_hazard) ** 23

    # Endogenous Stochastic Doob Certificate T*(p) under beta_eff = beta*(1-p) (verified in verify_results.py)
    p_doob_knots = np.array([
        0.0000, 0.0012, 0.0024, 0.0036, 0.0048, 0.0050, 0.0060, 0.0072,
        0.0084, 0.0100, 0.0121, 0.0133, 0.0150, 0.0169, 0.0181, 0.0193, 0.0200, 0.0205
    ])
    T_doob_knots = np.array([21, 22, 23, 24, 24, 24, 25, 26, 28, 29, 32, 34, 38, 45, 51, 62, 74, 97], dtype=float)
    p_doob_fine = np.linspace(0.0, 0.0205, 160)
    T_interp = np.interp(p_doob_fine, p_doob_knots, T_doob_knots)
    surv_doob = (1.0 - p_doob_fine) ** T_interp
    surv_23_sub = (1.0 - p_doob_fine) ** 23
    p_cert = 0.0207

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4), dpi=300)
    fig.subplots_adjust(wspace=0.25, bottom=0.15, top=0.87, left=0.07, right=0.97)

    if lang == 'es':
        l_h = r'Crecimiento sostenido «Palo de Hockey» $K_t = (1+g)^t \hat{K}_t$ ($M=1$)'
        l_s = r'Modelo original acotado por techo estacionario $K_p^+$ ($g=0$)'
        l_f = r'Fragmentación empresarial ($M=2$, $A_{\mathrm{ef}} = A/M^{\theta-1} \Rightarrow$ Extinción)'
        l_t = r'Umbral región productiva $\hat{h} = 0.28$'
        xlab1 = r'Períodos de tiempo $t$'
        ylab1 = r'Stock de capital real $K_t$'
        tit1 = r'(a) Escala empresarial ($M$) y crecimiento sin techo ($g > 0$)'
        l_doob = r'Doob endógeno $(1-p)^{T^*(p)}$ (anticipando $\tilde{\beta}_p$)'
        l_23 = r'Cota determinista ingenua $(1-p)^{23}$ ($p=0$ fijo)'
        l_46 = r'Bloques deterministas originales $(1-p)^{46}$'
        l_cert = r'Ruptura 1 paso $p_{\mathrm{cert}} \approx 2.07\%$'
        l_gap = r'Sobreestimación por ignorar anticipación'
        ann_2pct = 'p = 2.0%: T*=74\n22.4% vs. 62.8%'
        xlab2 = r'Riesgo anual anticipado de colapso $p$ (%)'
        ylab2 = r'Probabilidad certificada de llegar a $H$ (%)'
        tit2 = r'(b) Certificado estocástico de Doob $T^*(p)$ frente a $T^*=23$'
    else:
        l_h = r'Sustained hockey-stick growth $K_t = (1+g)^t \hat{K}_t$ ($M=1$)'
        l_s = r'Original model bounded by stationary ceiling $K_p^+$ ($g=0$)'
        l_f = r'Firm fragmentation ($M=2$, $A_{\mathrm{eff}} = A/M^{\theta-1} \Rightarrow$ Extinction)'
        l_t = r'Productive region threshold $\hat{h} = 0.28$'
        xlab1 = r'Time periods $t$'
        ylab1 = r'Real capital stock $K_t$'
        tit1 = r'(a) Firm scale ($M$) and unbounded growth ($g > 0$)'
        l_doob = r'Endogenous Doob $(1-p)^{T^*(p)}$ (anticipating $\tilde{\beta}_p$)'
        l_23 = r'Naive deterministic bound $(1-p)^{23}$ (fixed $p=0$)'
        l_46 = r'Original deterministic block bound $(1-p)^{46}$'
        l_cert = r'1-step breakdown $p_{\mathrm{cert}} \approx 2.07\%$'
        l_gap = r'Overstatement if anticipation ignored'
        ann_2pct = 'p = 2.0%: T*=74\n22.4% vs. 62.8%'
        xlab2 = r'Anticipated annual crisis hazard $p$ (%)'
        ylab2 = r'Certified probability of reaching $H$ (%)'
        tit2 = r'(b) Endogenous Stochastic Doob $T^*(p)$ vs. fixed $T^*=23$'

    ax1.plot(t_grid, K_real_hockey, '-', color='#1f4e78', linewidth=2.3, label=l_h)
    ax1.plot(t_grid, K_stationary_orig, '--', color='#1b7837', linewidth=1.8, label=l_s)
    ax1.plot(t_grid, K_real_fragmented, '-.', color='#c00000', linewidth=2.0, label=l_f)
    ax1.axhline(0.28, color='#666666', linestyle=':', linewidth=1.1, label=l_t)
    ax1.set_xlim(0, 44)
    ax1.set_ylim(0, 1.15)
    ax1.set_xlabel(xlab1, fontsize=9.5)
    ax1.set_ylabel(ylab1, fontsize=9.5)
    ax1.set_title(tit1, fontsize=10, pad=8)
    ax1.legend(loc='upper left', fontsize=7.3, frameon=True, facecolor='white', framealpha=0.95)
    ax1.grid(True, linestyle=':', alpha=0.35)

    ax2.plot(p_doob_fine * 100, surv_doob * 100, '-', color='#1f4e78', linewidth=2.4, label=l_doob)
    ax2.plot(p_hazard * 100, surv_23 * 100, '--', color='#1b7837', linewidth=1.8, label=l_23)
    ax2.plot(p_hazard * 100, surv_46 * 100, '-.', color='#d95f02', linewidth=1.6, label=l_46)
    ax2.axvline(p_cert * 100, color='#c00000', linestyle=':', linewidth=1.6, label=l_cert)
    mask_over = surv_23_sub > surv_doob
    ax2.fill_between(p_doob_fine[mask_over] * 100, surv_doob[mask_over] * 100, surv_23_sub[mask_over] * 100,
                     color='#c00000', alpha=0.12, label=l_gap)
    ax2.scatter([2.0], [100 * (0.98 ** 74)], color='#1f4e78', s=34, zorder=5)
    ax2.scatter([2.0], [100 * (0.98 ** 23)], color='#1b7837', s=28, zorder=5)
    ax2.annotate(ann_2pct, xy=(2.0, 22.42), xytext=(2.12, 12.0),
                 arrowprops=dict(arrowstyle='->', color='#1f4e78', lw=1.0),
                 bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#1f4e78', lw=0.7, alpha=0.95),
                 fontsize=7.3, color='#1f4e78', fontweight='bold')
    ax2.set_xlim(0, 2.85)
    ax2.set_ylim(-2, 105)
    ax2.set_xlabel(xlab2, fontsize=9.5)
    ax2.set_ylabel(ylab2, fontsize=9.5)
    ax2.set_title(tit2, fontsize=10, pad=8)
    ax2.legend(loc='lower left', fontsize=6.8, frameon=True, facecolor='white', framealpha=0.95)
    ax2.grid(True, linestyle=':', alpha=0.35)

    for ext in ['svg', 'png']:
        kw = {'dpi': 300} if ext == 'png' else {}
        plt.savefig(os.path.join(OUT_DIR, f'fig4_structural_{lang}.{ext}'), **kw)
    plt.close()


if __name__ == '__main__':
    for lang in ['es', 'en']:
        make_fig1(lang)
        make_fig2(lang)
        make_fig3(lang)
        make_fig4(lang)
    print(f"Generated all 16 figure files cleanly in {OUT_DIR}")
