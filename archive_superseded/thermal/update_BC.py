import os
import numpy as np

h1a = 800.0
r1 = 1.0 / h1a
gap_correction = 124.0
hp_radius = 0.00795
hp_length = 1.60
q_pipe_avg = 17123.0

def get_latest_time(case_dir):
    times = []
    for entry in os.listdir(case_dir):
        try:
            times.append(float(entry))
        except ValueError:
            continue
    return max(times) if times else None

def read_wall_temperature(case_dir, time):
    time_str = str(int(time)) if time == int(time) else str(time)
    T_file = os.path.join(case_dir, time_str, "solid", "T")
    with open(T_file) as f:
        content = f.read()
    lines = content.split("
")
    temps = []
    reading = False
    count = 0
    expected = 0
    for line in lines:
        s = line.strip()
        if "internalField" in line and "nonuniform" in line:
            reading = False
            continue
        if s.isdigit() and not reading:
            expected = int(s)
            reading = True
            count = 0
            continue
        if reading and count < expected:
            try:
                temps.append(float(s))
                count += 1
            except ValueError:
                continue
    T_avg = np.mean(temps) if temps else 900.0
    print(f"  Avg graphite T: {T_avg:.2f} K")
    return T_avg

def compute_Tvap(T_wall):
    area = 2 * 3.14159 * hp_radius * hp_length
    q_flux = q_pipe_avg / area
    delta_T = q_flux * r1
    Tvap = T_wall - delta_T + gap_correction
    print(f"  Heat flux: {q_flux:.1f} W/m2")
    print(f"  Delta T:   {delta_T:.2f} K")
    print(f"  Tvap:      {Tvap:.2f} K")
    return Tvap

def update_heatpipe_BC(case_dir, Tvap):
    T_file = os.path.join(case_dir, "0", "solid", "T")
    with open(T_file) as f:
        content = f.read()
    lines = content.split("
")
    new_lines = []
    in_hp = False
    for line in lines:
        if "heatpipe_wall" in line:
            in_hp = True
        if in_hp and "Ta" in line and "uniform" in line:
            new_lines.append(f"        Ta              uniform {Tvap:.4f};")
            in_hp = False
            continue
        new_lines.append(line)
    with open(T_file, "w") as f:
        f.write("
".join(new_lines))
    print(f"  BC updated: Ta = {Tvap:.4f} K")

if __name__ == "__main__":
    case_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 40)
    latest = get_latest_time(case_dir)
    print(f"Latest time: {latest}")
    T_wall = read_wall_temperature(case_dir, latest)
    Tvap = compute_Tvap(T_wall)
    update_heatpipe_BC(case_dir, Tvap)
    print("Done.")
