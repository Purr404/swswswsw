# fix_indent.py - copy and paste this entire code
import re

def fix_all_indentation(filename):
    print(f"📋 Reading {filename}...")
    with open(filename, 'r') as f:
        content = f.read()
    
    # 1. Replace ALL tabs with 4 spaces
    print("🔧 Replacing tabs with spaces...")
    content = content.replace('\t', '    ')
    
    # 2. Fix mixed indentation
    print("🔧 Fixing indentation levels...")
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if not line.strip():  # Empty line
            fixed_lines.append('')
            continue
        
        # Count leading spaces
        leading = len(line) - len(line.lstrip())
        
        # Check if this line continues from previous line
        if i > 0 and lines[i-1].strip() and lines[i-1].rstrip().endswith(('(', '[', '{', '\\')):
            # Continuation line - should be indented more
            if leading < 8:  # Less than 8 spaces for continuation
                line = ' ' * 8 + line.lstrip()
                print(f"   Line {i+1}: Fixed continuation line")
        else:
            # Normal line - ensure multiple of 4
            if leading % 4 != 0:
                new_leading = (leading // 4) * 4
                line = ' ' * new_leading + line.lstrip()
                if leading != new_leading:
                    print(f"   Line {i+1}: Fixed from {leading} to {new_leading} spaces")
        
        fixed_lines.append(line)
    
    # Write back
    print(f"💾 Writing fixed file...")
    with open(filename, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Successfully fixed {filename}")

# Run it on bot.py
if __name__ == "__main__":
    fix_all_indentation('/app/bot.py')