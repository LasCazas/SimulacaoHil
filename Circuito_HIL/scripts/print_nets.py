import re

with open('Circuito_HIL/Circuito_HIL_updated.net', 'r', encoding='utf-8') as f:
    text = f.read()

net_blocks = re.findall(r'\(net\s+\(code\s+"(\d+)"\)\s+\(name\s+"([^"]+)"\)(.*?)\n\t\t\)', text, re.DOTALL)
print(f"Total de redes: {len(net_blocks)}")
for code, name, body in net_blocks:
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
    if len(nodes) > 1:
        node_str = ", ".join([f"{r}.{p}" for r, p in nodes])
        print(f"Net {code} ({name}): [{node_str}]")
