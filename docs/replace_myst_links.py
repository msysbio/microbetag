import re
import sys
from pathlib import Path

def replace_myst_target_blank_links(text):
    """
    Replace [Text](URL){target="_blank"} with <a href="URL" target="_blank">Text</a>
    """
    pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)\{target="_blank"\}')
    return pattern.sub(r'<a href="\2" target="_blank">\1</a>', text)

def main(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)

    content = path.read_text(encoding='utf-8')
    updated_content = replace_myst_target_blank_links(content)

    # Overwrite the original file (optional: write to a new file instead)
    path.write_text(updated_content, encoding='utf-8')
    print(f"Updated links in: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python replace_myst_links.py <path-to-file.md>")
        sys.exit(1)
    
    main(sys.argv[1])

