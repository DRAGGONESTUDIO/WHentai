import json

def validate_json_structure():
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to parse incrementally to find where it fails
        print("Checking JSON structure...")
        
        # First try to parse the whole thing
        try:
            data = json.loads(content)
            print(f"Successfully parsed entire JSON with {len(data)} entries")
            return
        except json.JSONDecodeError as e:
            print(f"Failed to parse entire JSON at position {e.pos}: {e.msg}")
            
        # Now try to parse progressively larger chunks to find the breaking point
        chunk_size = 100000  # Start with 100KB chunks
        position = 0
        
        while position < len(content):
            # Try to find a reasonable breaking point (end of an object)
            end_pos = min(position + chunk_size, len(content))
            
            # Look for the end of an object before the chunk end
            if end_pos < len(content):
                # Look for the end of an object (},) or (} ])
                search_area = content[end_pos-50:end_pos+50] if end_pos+50 < len(content) else content[end_pos-50:]
                comma_pos = search_area.find('},')
                bracket_pos = search_area.find('}]')
                
                if comma_pos != -1:
                    end_pos = end_pos - 50 + comma_pos + 2
                elif bracket_pos != -1:
                    end_pos = end_pos - 50 + bracket_pos + 2
            
            chunk = content[position:end_pos]
            
            try:
                # Try to parse this chunk as a JSON array
                if position == 0:
                    # First chunk needs to start with [
                    if not chunk.strip().startswith('['):
                        print(f"First chunk doesn't start with [: {chunk[:50]}...")
                        break
                    # Try to parse what we can
                    partial_data = json.loads(chunk + ']')  # Close the array temporarily
                    print(f"First chunk parsed successfully with {len(partial_data)} entries")
                else:
                    # Middle chunks
                    if chunk.strip().startswith(','):
                        chunk = '[' + chunk[1:]  # Make it a valid array
                    else:
                        chunk = '[' + chunk
                    partial_data = json.loads(chunk + ']')  # Close the array temporarily
                    print(f"Chunk at position {position} parsed with {len(partial_data)} entries")
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse chunk at position {position} (around file position {position + e.pos}): {e.msg}")
                # Show the problematic area
                start = max(position, position + e.pos - 100)
                end = min(len(content), position + e.pos + 100)
                print(f"Content around error:")
                print(repr(content[start:end]))
                break
                
            position = end_pos
            
            # Stop after a few chunks for debugging
            if position > 300000:  # About 300KB
                print("Stopping early for debugging...")
                break
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    validate_json_structure()