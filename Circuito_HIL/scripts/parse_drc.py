with open('Circuito_HIL-drc.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
violations = re.findall(r'\[([^\]]+)\]:\s*([^\n]+)\n\s*([^;]+);\s*([^\n]+)\n\s*@\(([^\)]+)\):\s*([^\n]+)\n\s*@\(([^\)]+)\):\s*([^\n]+)', text)
print(f"Total de violações parseadas: {len(violations)}")
from collections import Counter
counts = Counter([v[0] for v in violations])
print("Resumo por tipo:")
for k, v in counts.items():
    print(f"  {k}: {v}")

print("\nPrimeiras 15 violações:")
for i, v in enumerate(violations[:15]):
    print(f"{i+1}. [{v[0]}] {v[1]}")
    print(f"   Item 1: {v[5]} @ ({v[4]})")
    print(f"   Item 2: {v[7]} @ ({v[6]})")
