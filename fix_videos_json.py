def fix_videos_json():
    try:
        # Read the entire file
        with open('videos.json', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Original file has {len(lines)} lines")
        
        # Find all lines that contain only a closing bracket ']'
        closing_bracket_lines = []
        for i, line in enumerate(lines):
            if line.strip() == ']':
                closing_bracket_lines.append(i)
        
        print(f"Found closing brackets at lines: {closing_bracket_lines}")
        
        # The last closing bracket should be at the very end
        # Remove all other closing brackets
        if len(closing_bracket_lines) > 1:
            # Remove all but the last closing bracket
            fixed_lines = []
            for i, line in enumerate(lines):
                # Skip all closing brackets except potentially the last one
                if i in closing_bracket_lines[:-1]:
                    continue
                fixed_lines.append(line)
            
            # Make sure the last line is just the closing bracket
            if fixed_lines[-1].strip() != ']':
                # Add the closing bracket at the end
                fixed_lines.append(']\n')
            else:
                # Ensure the last line is just the bracket with proper formatting
                fixed_lines[-1] = ']\n'
                
            print(f"Fixed file will have {len(fixed_lines)} lines")
            
            # Write the fixed content to a new file
            with open('videos_fixed.json', 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
                
            print("Fixed JSON saved to videos_fixed.json")
            
            # Try to validate the fixed file
            import json
            with open('videos_fixed.json', 'r', encoding='utf-8') as f:
                fixed_data = json.load(f)
            print(f"Fixed JSON successfully parsed with {len(fixed_data)} entries")
            
        else:
            print("No structural issues found in the JSON file")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_videos_json()