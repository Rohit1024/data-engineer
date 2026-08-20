#!/usr/bin/env python3
import re
import subprocess
import tempfile
import os
import glob
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def validate_block(item):
    file_path, idx, block = item
    cleaned_block = block.strip()
    with tempfile.NamedTemporaryFile('w', suffix='.mmd', delete=False) as tmp:
        tmp.write(cleaned_block)
        tmp_path = tmp.name
    
    out_svg = tmp_path + '.svg'
    try:
        res = subprocess.run(['npx', '-y', '@mermaid-js/mermaid-cli', '-i', tmp_path, '-o', out_svg], capture_output=True, text=True)
        if res.returncode != 0:
            return (file_path, idx, cleaned_block, res.stderr.strip())
        return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(out_svg):
            os.remove(out_svg)

def main():
    pattern = 'docs/**/*.md'
    files = glob.glob(pattern, recursive=True)
    print(f"Scanning {len(files)} markdown files for Mermaid blocks...")
    
    items = []
    for file_path in sorted(files):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = re.findall(r'```\s*mermaid\s*\n(.*?)\n```', content, re.DOTALL)
        for idx, block in enumerate(blocks, 1):
            items.append((file_path, idx, block))
            
    print(f"Found {len(items)} Mermaid diagrams across the project. Validating concurrently...")
    
    errors = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(validate_block, item): item for item in items}
        for future in as_completed(futures):
            res = future.result()
            if res:
                file_path, idx, code, err = res
                print(f"❌ ERROR in {file_path} (diagram #{idx}):")
                print(err)
                print("--- Code ---")
                print(code)
                print("------------\n")
                errors.append(res)

    print(f"\n==========================================")
    print(f"Mermaid Syntax Verification Report:")
    print(f"Total diagrams validated: {len(items)}")
    print(f"Total syntax errors: {len(errors)}")
    print(f"==========================================")
    
    if errors:
        sys.exit(1)
    else:
        print("✅ All Mermaid diagrams passed syntax validation successfully!")

if __name__ == '__main__':
    main()
