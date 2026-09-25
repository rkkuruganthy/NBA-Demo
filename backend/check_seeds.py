import sys
with open('graph/seed.cypher', 'r') as f:
    content = f.read()
header = "// ============================================================\n// E-COMMERCE POPULATION SEED"
ecom_block = content.split(header)[1]
statements = [s.strip() for s in ecom_block.split(';')]
print(f"Total statements separated by semicolon: {len(statements)}")
for i, stmt in enumerate(statements[:5]):
    clean_lines = [line for line in stmt.split('\n') if not line.strip().startswith('//')]
    clean_stmt = '\n'.join(clean_lines).strip()
    print(f"--- Stmt {i} length: {len(clean_stmt)}")
    print(clean_stmt)
