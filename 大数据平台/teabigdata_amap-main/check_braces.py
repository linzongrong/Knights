
import re

filename = 'src/components/CustomMap.vue'

with open(filename, 'r') as f:
    lines = f.readlines()

content = ""
for line in lines:
    if '</script>' in line:
        break
    content += line

# Count braces
stack = []
for i, char in enumerate(content):
    if char == '{':
        stack.append(i)
    elif char == '}':
        if stack:
            stack.pop()
        else:
            print(f"Excess closing brace at char {i}")

if stack:
    # Find line number of unclosed brace
    unclosed_idx = stack[-1]
    # Count newlines before this index
    lineno = content[:unclosed_idx].count('\n') + 1
    print(f"Unclosed brace at line {lineno}")
    # Context
    start = max(0, lineno - 5)
    end = lineno + 5
    for j in range(start, end):
        if j < len(lines):
            print(f"{j+1}: {lines[j].rstrip()}")
else:
    print("Braces are balanced.")
