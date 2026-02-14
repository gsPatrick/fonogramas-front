"""Precise field map for FON1 and FON2"""

with open('txt ecad.txt', 'r', encoding='latin-1', errors='replace') as f:
    lines = f.readlines()

# FON1 with known cod_obra to cross-reference
# Let's use line 1662 which has cod_obra 410079
fon1_lines = [l.rstrip() for l in lines if '0661FON1' in l]

# Use one with a known cod_obra (e.g. 410241 - "EU SEM VOCE" from OBM section)
# OBM1 line 3: ...000000000410241EU SEM VOCE...
# Let's find the matching FON1 
for fl in fon1_lines:
    if '410241' in fl or '410079' in fl:
        print(f"Found matching FON1: len={len(fl)}")
        line = fl
        # Print in chunks
        for i in range(0, len(line), 10):
            end = min(i+10, len(line))
            print(f"  [{i:3d}:{end:3d}] = '{line[i:end]}'")
        print()

# Also analyze a pure numeric FON1 (no ISRC in first field)
print("\n=== FON1 without ISRC (starts 00000) ===")
for fl in fon1_lines:
    if fl[8:20] == '000000000000':
        print(f"Found: len={len(fl)}")
        for i in range(0, min(len(fl), 200), 10):
            end = min(i+10, len(fl))
            print(f"  [{i:3d}:{end:3d}] = '{line[i:end]}'")
        break

# Now FON2
print("\n=== FON2 precise map ===")
fon2_lines = [l.rstrip() for l in lines if '0661FON2' in l]
line = fon2_lines[5]  # pick a representative one
print(f"FON2 len={len(line)}")
for i in range(0, len(line), 10):
    end = min(i+10, len(line))
    print(f"  [{i:3d}:{end:3d}] = '{line[i:end]}'")

# FON3
print("\n=== FON3 precise map ===")
fon3_lines = [l.rstrip() for l in lines if '0661FON3' in l]
line = fon3_lines[0]
print(f"FON3 len={len(line)}")
for i in range(0, len(line), 1):
    end = min(i+1, len(line))
    # just print the whole thing
print(f"Full: '{line}'")

# Also analyze all unique FON1 lengths and FON2 lengths
fon1_lens = set(len(l.rstrip()) for l in lines if '0661FON1' in l)
fon2_lens = set(len(l.rstrip()) for l in lines if '0661FON2' in l)
fon3_lens = set(len(l.rstrip()) for l in lines if '0661FON3' in l)
print(f"\nFON1 unique lengths: {fon1_lens}")
print(f"FON2 unique lengths: {fon2_lens}")
print(f"FON3 unique lengths: {fon3_lens}")

# Check if OBM1 has the same line length
obm1_lens = set(len(l.rstrip()) for l in lines if '0661OBM1' in l or '0662OBM1' in l)
obm2_lens = set(len(l.rstrip()) for l in lines if '0661OBM2' in l or '0662OBM2' in l)
print(f"OBM1 unique lengths: {obm1_lens}")
print(f"OBM2 unique lengths: {obm2_lens}")
