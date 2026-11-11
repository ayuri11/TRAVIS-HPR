# plot_ring_temperatures.py
# Bar chart of Tvap and Tm per heat pipe ring from Phase 3 IVTBC results
# shows safety margins visually against cladding and TRISO limits

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json

# =============================================================================
# LOAD PHASE 3 IVTBC RESULTS
# =============================================================================
with open('../PHASE 3/phase3_ivtbc_results.json', 'r') as f:
    ivtbc = json.load(f)

rings       = list(ivtbc['results'].keys())           # ['ring_0','ring_1',...]
ring_labels = ['Ring 0\n(r=2.65cm)', 'Ring 1\n(r=8.15cm)',
               'Ring 2\n(r=13.65cm)', 'Ring 3\n(r=19.15cm)']

Tvap_vals = [ivtbc['results'][r]['Tvap_C'] for r in rings]
Tm_vals   = [ivtbc['results'][r]['Tm_C']   for r in rings]
T_inf_C   = ivtbc['T_inf_C']

# safety limits
clad_limit  = 900.0
triso_limit = 1600.0

# =============================================================================
# DARK THEME SETUP
# =============================================================================
bg_color    = '#2e2e2e'
text_color  = '#cccccc'
spine_color = '#666666'
title_color = '#ffffff'

x      = np.arange(len(rings))
width  = 0.32

fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# =============================================================================
# BARS
# =============================================================================
bars_tvap = ax.bar(x - width/2, Tvap_vals, width,
                   color='#5b9bd5', alpha=0.88,
                   label=f'$T_{{vap}}$ — vapor temperature',
                   zorder=3)

bars_tm   = ax.bar(x + width/2, Tm_vals, width,
                   color='#e8833a', alpha=0.88,
                   label=f'$T_m$ — graphite surface',
                   zorder=3)

# =============================================================================
# SAFETY LIMIT LINES
# =============================================================================
ax.axhline(y=clad_limit, color='#e74c3c', linewidth=1.8,
           linestyle='--', zorder=4,
           label=f'Cladding limit  {clad_limit:.0f}°C')

ax.axhline(y=triso_limit, color='#e67e22', linewidth=1.4,
           linestyle=':', zorder=4,
           label=f'TRISO limit  {triso_limit:.0f}°C')

ax.axhline(y=T_inf_C, color='#888888', linewidth=1.4,
           linestyle='-.', zorder=4,
           label=f'$T_{{∞}}$ coolant  {T_inf_C:.1f}°C')

# =============================================================================
# VALUE LABELS ON BARS
# =============================================================================
for bar in bars_tvap:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f'{bar.get_height():.1f}°C',
            ha='center', va='bottom', fontsize=9,
            color='#5b9bd5', fontweight='500')

for bar in bars_tm:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f'{bar.get_height():.1f}°C',
            ha='center', va='bottom', fontsize=9,
            color='#e8833a', fontweight='500')

# =============================================================================
# MARGIN ANNOTATIONS — on ring_0 bars (all rings identical)
# =============================================================================
# Tvap → cladding limit
ax.annotate('',
    xy=(x[0] - width/2, clad_limit),
    xytext=(x[0] - width/2, Tvap_vals[0]),
    arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=1.4))
ax.text(x[0] - width/2 - 0.22, (clad_limit + Tvap_vals[0])/2,
        '27.5°C', ha='right', va='center',
        fontsize=8.5, color='#e74c3c')

# Tm → TRISO limit — annotate on ring_0 Tm bar
ax.annotate('',
    xy=(x[0] + width/2, triso_limit),
    xytext=(x[0] + width/2, Tm_vals[0]),
    arrowprops=dict(arrowstyle='<->', color='#e67e22', lw=1.4))
ax.text(x[0] + width/2 + 0.22, (triso_limit + Tm_vals[0])/2,
        '586.3°C', ha='left', va='center',
        fontsize=8.5, color='#e67e22')

# =============================================================================
# SAFE ZONE SHADING — between T_inf and cladding limit
# =============================================================================
ax.axhspan(T_inf_C, clad_limit,
           alpha=0.05, color='#2ecc71', zorder=0)

# =============================================================================
# AXES, TICKS, LABELS, SPINES
# =============================================================================
ax.set_xticks(x)
ax.set_xticklabels(ring_labels, fontsize=10, color=text_color)
ax.set_ylabel('Temperature (°C)', fontsize=12, color=text_color, labelpad=8)
ax.set_title('AYURI Core — IVTBC Ring Temperature Assessment\n'
             '(uniform assumption, 2.5 MWth, 259 heat pipes)',
             fontsize=12, color=title_color, pad=12)

ax.set_ylim(400, 1750)
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

# =============================================================================
# CAPILLARY UTILIZATION ANNOTATION
# =============================================================================
ax.text(0.02, 0.04,
        'Capillary utilization: 37%  (limit < 50%)  ✓',
        transform=ax.transAxes,
        fontsize=9, color='#2ecc71',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#3a3a3a',
                  edgecolor='#2ecc71', alpha=0.85))

plt.tight_layout()
plt.savefig('ring_temperature_chart_dark.png', dpi=300, facecolor=bg_color)
plt.savefig('ring_temperature_chart_dark.pdf', facecolor=bg_color)
print("Saved: ring_temperature_chart_dark.png and .pdf")
plt.show()
