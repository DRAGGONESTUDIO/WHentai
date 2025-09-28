def count_json_objects():
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Count opening braces that represent objects
        # We'll look for patterns that indicate the start of a video object
        object_count = 0
        in_string = False
        escape_next = False
        
        i = 0
        while i < len(content):
            char = content[i]
            
            # Handle string literals (ignore braces inside strings)
            if escape_next:
                escape_next = False
            elif char == '\\':
                escape_next = True
            elif char == '"':
                in_string = not in_string
            # Count opening braces that are not inside strings
            elif char == '{' and not in_string:
                # Check if this looks like a video object by looking for title field
                # Look ahead a bit to see if we have a title field
                lookahead = content[i:i+50] if i+50 < len(content) else content[i:]
                if '"title"' in lookahead or '"thumbnail"' in lookahead:
                    object_count += 1
                    
            i += 1
            
            # Print progress every 5000 objects
            if object_count % 5000 == 0 and object_count != 0:
                print(f"Found {object_count} objects so far...")
                
        print(f"Total objects found: {object_count}")
        
        # Also check if the file ends correctly
        if content.strip().endswith(']'):
            print("File ends with closing bracket as expected")
        else:
            print("File does not end with closing bracket")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_json_objects()