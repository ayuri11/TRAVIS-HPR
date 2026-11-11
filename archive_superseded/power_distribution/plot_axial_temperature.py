# plot_axial_temperature.py
# Plots the IVTBC uniform temperature result axially —
# shows constant Tvap and Tm across the core height
# against safety limits, making the margin visually clear

import numpy as np
import matplotlib.pyplot as plt
import json

# =============================================================================
# LOAD DATA
# =============================================================================
# axial positions from Phase 2 (just for the z axis range)
data = np.loadtxt('axial_power_profile.csv', delimiter=',', skiprows=1)
z_cm = data[:, 0]     # axial positions in cm

# IVTBC converged values from Phase 3
with open('../PHASE 3/phase3_ivtbc_results.json', 'r') as f:
    ivtbc = json.load(f)

Tvap_C = ivtbc['results']['ring_0']['Tvap_C']   # 872.47°C
Tm_C   = ivtbc['results']['ring_0']['Tm_C']     # 1013.69°C
T_inf_C = ivtbc['T_inf_C']                      # 517.85°C — coolant temperature

# safety limits
clad_limit  = 900.0    # °C Haynes 230 / FeCrAl cladding
triso_limit = 1600.0   # °C TRISO fission product retention

# =============================================================================
# DARK THEME SETUP
# =============================================================================
bg_color    = '#2e2e2e'
text_color  = '#cccccc'
spine_color = '#666666'
title_color = '#ffffff'

fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# =============================================================================
# SHADED SAFE ZONE — green band between T_inf and cladding limit
# =============================================================================
ax.axvspan(T_inf_C, clad_limit,
           alpha=0.06, color='#2ecc71', label='Safe operating zone')

# =============================================================================
# UNIFORM TEMPERATURE LINES — horizontal across full core height
# these are the IVTBC converged values, constant at all z (uniform assumption)
# =============================================================================
ax.hlines(z_cm, xmin=T_inf_C, xmax=Tvap_C,
          colors='#5b9bd5', linewidth=0, alpha=0)   # invisible, just for fill

# Tvap — blue, full axial span
ax.plot([Tvap_C, Tvap_C], [z_cm.min(), z_cm.max()],
        color='#5b9bd5', linewidth=3.0,
        label=f'$T_{{vap}}$ = {Tvap_C:.1f}°C  (vapor temperature)')

# Tm — orange, full axial span
ax.plot([Tm_C, Tm_C], [z_cm.min(), z_cm.max()],
        color='#e8833a', linewidth=3.0,
        label=f'$T_m$ = {Tm_C:.1f}°C  (graphite surface)')

# T_inf — grey, coolant sink temperature
ax.plot([T_inf_C, T_inf_C], [z_cm.min(), z_cm.max()],
        color='#888888', linewidth=1.8, linestyle='-.',
        label=f'$T_{{∞}}$ = {T_inf_C:.1f}°C  (coolant sink)')

# =============================================================================
# SAFETY LIMIT LINES — vertical dashed
# =============================================================================
ax.plot([clad_limit, clad_limit], [z_cm.min(), z_cm.max()],
        color='#e74c3c', linewidth=1.8, linestyle='--',
        label=f'Cladding limit  {clad_limit:.0f}°C')

ax.plot([triso_limit, triso_limit], [z_cm.min(), z_cm.max()],
        color='#e67e22', linewidth=1.4, linestyle=':',
        label=f'TRISO limit  {triso_limit:.0f}°C')

# =============================================================================
# MARGIN ANNOTATIONS — arrows showing safety gap
# =============================================================================
mid_z = 0.0   # annotate at core midplane

# Tvap → cladding limit margin arrow
ax.annotate('',
    xy=(clad_limit, mid_z + 5),
    xytext=(Tvap_C, mid_z + 5),
    arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=1.4))
ax.text((Tvap_C + clad_limit) / 2, mid_z + 9,
        '27.5°C margin', ha='center', va='bottom',
        fontsize=9, color='#e74c3c')

# Tm → TRISO limit margin arrow
ax.annotate('',
    xy=(triso_limit, mid_z - 10),
    xytext=(Tm_C, mid_z - 10),
    arrowprops=dict(arrowstyle='<->', color='#e67e22', lw=1.4))
ax.text((Tm_C + triso_limit) / 2, mid_z - 15,
        '586.3°C margin', ha='center', va='top',
        fontsize=9, color='#e67e22')

# =============================================================================
# REFERENCE LINES — midplane and fuel boundaries
# =============================================================================
ax.axhline(y=0,   color='#888888', linewidth=1.0, linestyle='--', alpha=0.5)
ax.axhline(y=80,  color='#666666', linewidth=0.8, linestyle=':', alpha=0.5)
ax.axhline(y=-80, color='#666666', linewidth=0.8, linestyle=':', alpha=0.5)

ax.text(520, 81, 'fuel top (+80 cm)',
        fontsize=8, color='#888888', va='bottom')
ax.text(520, -81, 'fuel bottom (−80 cm)',
        fontsize=8, color='#888888', va='top')
ax.text(520, 1,  'midplane',
        fontsize=8, color='#888888', va='bottom')

# =============================================================================
# AXES LABELS, TICKS, SPINES
# =============================================================================
ax.set_xlabel('Temperature (°C)', fontsize=12, color=text_color, labelpad=8)
ax.set_ylabel('Axial position  z (cm)', fontsize=12, color=text_color, labelpad=8)
ax.set_title('AYURI Core — IVTBC Thermal Assessment\n(uniform assumption, 2.5 MWth)',
             fontsize=12, color=title_color, pad=12)

ax.set_xlim(480, 1700)
ax.set_ylim(z_cm.min() - 5, z_cm.max() + 5)

ax.tick_params(axis='both', colors=text_color, labelsize=10)
ax.grid(False)
for spine in ax.spines.values():
    spine.set_edgecolor(spine_color)
    spine.set_linewidth(1.5)

# =============================================================================
# LEGEND
# =============================================================================
ax.legend(fontsize=9, loc='upper right',
          facecolor='#3a3a3a', edgecolor='#555555',
          labelcolor=text_color, framealpha=0.90)

plt.tight_layout()
plt.savefig('axial_temperature_profile_dark.png', dpi=300, facecolor=bg_color)
plt.savefig('axial_temperature_profile_dark.pdf', facecolor=bg_color)
print("Saved: axial_temperature_profile_dark.png and .pdf")
plt.show()
