# nuclear_fix.py - Copy and paste ALL of this
import re

def nuclear_indentation_fix(filename):
    print(f"🚀 Starting nuclear indentation fix for {filename}...")
    
    # Read the file
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # First, create a backup
    backup_name = filename + '.backup'
    with open(backup_name, 'w') as f:
        f.writelines(lines)
    print(f"📦 Created backup: {backup_name}")
    
    fixed_lines = []
    indent_level = 0
    in_multiline = False
    
    for line_num, line in enumerate(lines, 1):
        # Clean the line
        line = line.rstrip('\n')
        
        # Skip empty lines
        if not line.strip():
            fixed_lines.append('')
            continue
        
        # Remove all leading whitespace and tabs
        clean_line = line.lstrip()
        
        # Count dedents based on line content
        if clean_line and not in_multiline:
            # Check for lines that should reduce indentation
            if clean_line.startswith(('return ', 'break ', 'continue ', 'pass', 'elif ', 'else:', 'except ', 'finally:')):
                indent_level = max(0, indent_level - 1)
            
            # Special case for lines ending with certain keywords
            if any(line.rstrip().endswith(word) for word in ['return', 'break', 'continue', 'pass']):
                indent_level = max(0, indent_level - 1)
        
        # Calculate indentation
        current_indent = indent_level * 4
        
        # Add the properly indented line
        fixed_line = ' ' * current_indent + clean_line
        fixed_lines.append(fixed_line)
        
        # Update indent level for next line
        if not in_multiline:
            # Check if line starts a new block
            if clean_line.endswith(':'):
                if not clean_line.strip().startswith(('elif ', 'else:', 'except ', 'finally:', '#')):
                    indent_level += 1
            # Check if line ends with multiline starters
            elif any(clean_line.endswith(char) for char in ['(', '[', '{']):
                in_multiline = True
                indent_level += 1
        else:
            # Check if multiline ends
            if not any(clean_line.endswith(char) for char in [',', '(', '[', '{', '\\']):
                in_multiline = False
                indent_level = max(0, indent_level - 1)
    
    # Write the fixed file
    with open(filename, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Successfully re-indented {filename}")
    print(f"📊 Original lines: {len(lines)}, Fixed lines: {len(fixed_lines)}")
    
    # Show the problematic area
    print("\n🔍 Lines 1255-1265 (after fix):")
    for i in range(1254, 1266):
        if i < len(fixed_lines):
            line_num = i + 1
            line = fixed_lines[i]
            indent = len(line) - len(line.lstrip())
            print(f"{line_num:4} [{indent} spaces]: {line}")

# Run the fix
nuclear_indentation_fix('/app/bot.py')