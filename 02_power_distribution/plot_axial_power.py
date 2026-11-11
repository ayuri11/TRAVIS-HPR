"""Axial power profile figure from data/axial_power_profile.csv -> ../figures/power_distribution/ (run from any directory)."""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, '..', 'figures', 'power_distribution')

df = pd.read_csv(os.path.join(HERE, 'data', 'axial_power_profile.csv'))
z        = df.iloc[:, 0].values
power    = df.iloc[:, 1].values
power_MW = power / 1e6

# theme
bg_outer   = '#3a3f4a'   # dark grey outer — ParaView window tone, dark enough for white text
bg_panel   = '#2e333d'   # darker grey-blue panel — distinct from outer
text_color = '#ffffff'
spine_color= '#6a7a8a'
ref_color  = '#9aaabb'
line_color = '#5b9bd5'   # blue curve
fill_color = '#1e3a5a'   # deep blue fill
title_color= '#ffffff'

fig, ax = plt.subplots(figsize=(6, 9))
fig.patch.set_facecolor(bg_outer)
ax.set_facecolor(bg_panel)

ax.fill_betweenx(z, power_MW, alpha=0.60, color=fill_color)

ax.plot(power_MW, z, 'o-',
        color=line_color,
        linewidth=3.0,
        markersize=6,
        markerfacecolor=line_color,
        markeredgecolor=bg_panel,
        markeredgewidth=1.5)

ax.axhline(y=0,   color=ref_color, linestyle='--',
           linewidth=1.5, label='Core midplane', alpha=0.9)
ax.axhline(y=80,  color=ref_color, linestyle=':',
           linewidth=1.2, label='Fuel boundary', alpha=0.75)
ax.axhline(y=-80, color=ref_color, linestyle=':',
           linewidth=1.2, alpha=0.75)

ax.set_xlabel('Power Density (MW/m³)',
              fontsize=15, color=text_color, labelpad=10)
ax.set_ylabel('Axial Position z (cm)',
              fontsize=15, color=text_color, labelpad=10)
ax.set_title('TRAVIS Core — Axial Power Distribution\n(normalized to 2.5 MWth)',
             fontsize=14, color=title_color, pad=14)

ax.tick_params(axis='both', colors=text_color,
               labelsize=13, width=1.5, length=5)
ax.grid(False)
for spine in ax.spines.values():
    spine.set_edgecolor(spine_color)
    spine.set_linewidth(2.0)

ax.legend(fontsize=12,
          facecolor='#2a3040',
          edgecolor=spine_color,
          labelcolor=text_color,
          framealpha=0.92,
          loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(FIG, 'axial_power_paraview_theme.png'), dpi=300, facecolor=bg_outer)
plt.savefig(os.path.join(FIG, 'axial_power_paraview_theme.pdf'), facecolor=bg_outer)
print("Saved: axial_power_paraview_theme.png and .pdf")
plt.show()
