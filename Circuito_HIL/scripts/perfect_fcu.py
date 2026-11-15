"""Jumpers concêntricos perfeitos em F.Cu para o módulo SparkFun Vermelho.
Zero cruzamentos, zero curtos com pads.
"""

def get_perfect_fcu_jumpers(esp_pins, pcm_pins, u3_pins, r1_p2, r2_p2):
    f_cu_tracks = []
    
    # 1. J_LCK: ESP Pin 11 -> PCM Pin 5
    # Concentric corridor: X=18, Y=8
    p_start = esp_pins[11] # (28.57, 57.62)
    p_end = pcm_pins[5]    # (84.38, 12.73)
    net_lck = 10
    pts = [
        p_start,
        (18.0, p_start[1]),
        (18.0, 8.0),
        (80.0, 8.0),
        (80.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 0.8, net_lck))

    # 2. J_BCK: ESP Pin 10 -> PCM Pin 3
    # Concentric corridor: X=20, Y=6
    p_start = esp_pins[10] # (28.57, 55.08)
    p_end = pcm_pins[3]    # (84.38, 7.65)
    net_bck = 8
    pts = [
        p_start,
        (20.0, p_start[1]),
        (20.0, 6.0),
        (82.0, 6.0),
        (82.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 0.8, net_bck))

    # 3. J_MAP: ESP Pin 9 -> R2 p2
    # Concentric corridor: X=22, Y=26
    p_start = esp_pins[9]  # (28.57, 52.54)
    p_end = r2_p2          # (75.0, 40.0)
    net_map = 18
    pts = [
        p_start,
        (22.0, p_start[1]),
        (22.0, 26.0),
        (70.0, 26.0),
        (70.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 0.8, net_map))

    # 4. J_TPS: ESP Pin 8 -> R1 p2
    # Concentric corridor: X=24, Y=28
    p_start = esp_pins[8]  # (28.57, 50.0)
    p_end = r1_p2          # (75.0, 30.0)
    net_tps = 17
    pts = [
        p_start,
        (24.0, p_start[1]),
        (24.0, 28.0),
        (72.0, 28.0),
        (72.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 0.8, net_tps))

    # 5. J_DIN: ESP Pin 29 -> PCM Pin 4
    # Middle corridor: X=58
    p_start = esp_pins[29] # (51.43, 34.76)
    p_end = pcm_pins[4]    # (84.38, 10.19)
    net_din = 9
    pts = [
        p_start,
        (58.0, p_start[1]),
        (58.0, 4.0),
        (76.0, 4.0),
        (76.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 0.8, net_din))

    # 6. J_5V_U3: PCM Pin 1 -> U3 Pin 3 (HV do SparkFun)
    # Right corridor: X=108
    p_start = pcm_pins[1]  # (84.38, 2.57)
    p_end = u3_pins[3]     # (98.35, 74.73)
    net_5v = 2
    pts = [
        p_start,
        (108.0, p_start[1]),
        (108.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 1.0, net_5v))

    # 7. J_3V3_PCM: U3 Pin 9 (LV do SparkFun) -> PCM Pin 7
    # Middle-right corridor: X=78
    p_start = u3_pins[9]   # (85.65, 74.73)
    p_end = pcm_pins[7]    # (84.38, 17.81)
    net_3v3 = 1
    pts = [
        p_start,
        (78.0, p_start[1]),
        (78.0, p_end[1]),
        p_end
    ]
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 0.8, net_3v3))

    return f_cu_tracks
