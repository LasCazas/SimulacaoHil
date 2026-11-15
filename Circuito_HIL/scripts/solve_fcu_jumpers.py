import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from grid_router import GridRouter
from auto_route_perfect import esp_pins, pcm_pins, u3_pins, j1_pins, r1_p1, r1_p2, c1_p1, c1_p2, r2_p1, r2_p2, c2_p1, c2_p2, pin_nets

print("ESP pins:")
print("Pin 8:", esp_pins[8])
print("Pin 9:", esp_pins[9])
print("Pin 10:", esp_pins[10])
print("Pin 11:", esp_pins[11])
print("Pin 29:", esp_pins[29])

print("\nPCM pins:")
print("PCM 1:", pcm_pins[1])
print("PCM 3:", pcm_pins[3])
print("PCM 4:", pcm_pins[4])
print("PCM 5:", pcm_pins[5])
print("PCM 7:", pcm_pins[7])

print("\nR/C pins:")
print("R1 p2:", r1_p2)
print("R2 p2:", r2_p2)

print("\nU3 pins:")
print("U3 pin 1:", u3_pins[1])
print("U3 pin 7:", u3_pins[7])
