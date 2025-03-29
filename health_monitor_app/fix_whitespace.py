"""
Script to fix trailing whitespace in routes.py file
"""
import os
import re

def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from a file"""
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Count lines with trailing whitespace
    pattern = re.compile(r'[ \t]+$', re.MULTILINE)
    matches = pattern.findall(content)
    whitespace_count = len(matches)
    
    # Fix trailing whitespace
    fixed_content = pattern.sub('', content)
    
    # Write back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)
    
    print(f"Fixed {whitespace_count} instances of trailing whitespace in {file_path}")
    
    # Verify the fix worked
    with open(file_path, 'r', encoding='utf-8') as file:
        fixed_content = file.read()
    
    remaining_matches = pattern.findall(fixed_content)
    print(f"After fix: {len(remaining_matches)} instances of trailing whitespace remaining")
    
    print("Example lines with trailing whitespace (if any):")
    lines = fixed_content.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'[ \t]+$', line):
            print(f"Line {i+1}: '{line}'")
            if len(remaining_matches) >= 5:
                print("... (more lines omitted)")
                break

if __name__ == "__main__":
    # Path to routes.py
    routes_path = os.path.join('app', 'health_data', 'routes.py')
    
    # Check if file exists
    if not os.path.exists(routes_path):
        print(f"File not found: {routes_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        if os.path.exists('app'):
            print(f"Files in app directory: {os.listdir('app')}")
            if os.path.exists(os.path.join('app', 'health_data')):
                print(f"Files in health_data directory: {os.listdir(os.path.join('app', 'health_data'))}")
    else:
        # Fix trailing whitespace
        fix_trailing_whitespace(routes_path) 