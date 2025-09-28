import json

def check_json():
    try:
        # Try to parse the JSON file
        with open('videos.json', 'r', encoding='utf-8') as f:
            # Read the first 1000 characters to check the beginning
            beginning = f.read(1000)
            print("Beginning of file:")
            print(beginning[:200])
            print("...")
            print(beginning[-200:])
            
        # Now try to parse the entire file
        with open('videos.json', 'r', encoding='utf-8') as f:
            # Try to load and parse the JSON
            data = json.load(f)
            print(f"\nSuccessfully parsed JSON with {len(data)} entries")
            
            # Check the structure of the first few entries
            print("\nFirst entry:")
            if data:
                print(json.dumps(data[0], indent=2))
                
            # Check the structure of the last few entries
            print("\nLast entry:")
            if data:
                print(json.dumps(data[-1], indent=2))
                
    except json.JSONDecodeError as e:
        print(f"JSON parsing error at position {e.pos}: {e.msg}")
        # Try to read around the error position
        with open('videos.json', 'r', encoding='utf-8') as f:
            content = f.read()
            start = max(0, e.pos - 100)
            end = min(len(content), e.pos + 100)
            print(f"Content around error position {e.pos}:")
            print(content[start:end])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_json()