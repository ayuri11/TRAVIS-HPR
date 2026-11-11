"""Full-core radial power map at the midplane (rebuilt from the 1/12 wedge) from data/power_density_3d.npy -> ../figures/power_distribution/."""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, '..', 'figures', 'power_distribution')

power_3d = np.load(os.path.join(HERE, 'data', 'power_density_3d.npy'))
midplane = power_3d[:, :, 14] / 1e6

# reconstruct full core from 1/12 wedge
full_core = np.zeros_like(midplane)
for i in range(12):
    rotated = rotate(midplane, angle=i*30, reshape=False, order=1)
    full_core += rotated

# theme
bg_outer    = '#3a3f4a'
bg_panel    = '#2e2e2e'   # dark inner panel back
text_color  = '#ffffff'
spine_color = '#6a7a8a'
title_color = '#ffffff'

fig, ax = plt.subplots(figsize=(7, 6))
fig.patch.set_facecolor(bg_outer)
ax.set_facecolor(bg_panel)

im = ax.imshow(
    full_core.T,
    origin='lower',
    extent=[-60, 60, -60, 60],
    cmap='inferno',
    interpolation='bilinear',
    vmin=0
)

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('Power Density (MW/m³)',
               fontsize=13, color=text_color, labelpad=10)
cbar.ax.yaxis.set_tick_params(color=text_color, labelcolor=text_color)
cbar.outline.set_edgecolor(spine_color)
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'),
         color=text_color, fontsize=11)

# core / reflector boundaries
theta = np.linspace(0, 2*np.pi, 300)
ax.plot(45*np.cos(theta), 45*np.sin(theta),
        '--', color='#ffffff', linewidth=2.5,
        alpha=1.0, label='Core boundary (r = 45 cm)')
ax.plot(60*np.cos(theta), 60*np.sin(theta),
        ':', color='#ffffff', linewidth=2.2,
        alpha=1.0, label='Reflector boundary (r = 60 cm)')

ax.set_xlabel('x (cm)', fontsize=14, color=text_color, labelpad=10)
ax.set_ylabel('y (cm)', fontsize=14, color=text_color, labelpad=10)
ax.set_title(
    'TRAVIS Core — Reconstructed Full-Core Radial Power\n(from 1/12 symmetry, at z = 0)',
    fontsize=13, color=title_color, pad=13
)

ax.tick_params(axis='both', colors=text_color,
               labelsize=12, width=1.8, length=5)
ax.grid(False)
for spine in ax.spines.values():
    spine.set_edgecolor(spine_color)
    spine.set_linewidth(2.0)

legend = ax.legend(
    fontsize=10,
    loc='lower right',
    facecolor='#2a3040',
    edgecolor='#ffffff',
    framealpha=0.92
)
for text in legend.get_texts():
    text.set_color('#ffffff')

plt.tight_layout()
plt.savefig(os.path.join(FIG, 'radial_power_paraview_theme.png'), dpi=300, facecolor=bg_outer)
plt.savefig(os.path.join(FIG, 'radial_power_paraview_theme.pdf'), facecolor=bg_outer)
print("Saved: radial_power_paraview_theme.png and .pdf")
plt.show()
