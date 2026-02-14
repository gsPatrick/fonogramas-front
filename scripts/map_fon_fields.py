
def print_with_ruler(label, line):
    print(f"\n=== {label} (len={len(line)}) ===")
    print(line)
    
    # Ruler 1: 0123456789...
    ruler1 = ""
    for i in range(len(line)):
        ruler1 += str(i % 10)
    print(ruler1)
    
    # Ruler 2: 00000000001111111111...
    ruler2 = ""
    for i in range(len(line)):
        ruler2 += str(int(i / 10) % 10)
    print(ruler2)
    
    # Ruler 3: Hundreds
    ruler3 = ""
    for i in range(len(line)):
        ruler3 += str(int(i / 100) % 10)
    print(ruler3)

with open('txt ecad.txt', 'r', encoding='latin-1', errors='replace') as f:
    lines = [l.rstrip() for l in f.readlines()]

# Get first FON1
fon1 = next((l for l in lines if '0661FON1' in l), None)
if fon1:
    print_with_ruler("FON1 Sample", fon1)

# Get first FON2
fon2 = next((l for l in lines if '0661FON2' in l), None)
if fon2:
    print_with_ruler("FON2 Sample", fon2)

# Get first FON3
fon3 = next((l for l in lines if '0661FON3' in l), None)
if fon3:
    print_with_ruler("FON3 Sample", fon3)
