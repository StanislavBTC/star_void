
import sys
import os
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "src"))

from utils.randomness import safe_format, random_prompt_block, random_prompt, AI_PROMPTS_DIR

def test_safe_format():
    print("Testing safe_format...")
    assert safe_format("Hello {name}", name="World") == "Hello World"
    assert safe_format("Hello {name}", missing="key") == "Hello {name}"
    # Test collision with json-like syntax
    assert safe_format('{"key": "{val}"}', val=123) == '{"key": "123"}'
    print("PASS")

def test_prompt_modules():
    print("Testing prompt modules...")
    
    # Setup
    if not AI_PROMPTS_DIR.exists():
        os.makedirs(AI_PROMPTS_DIR)
        
    t1 = AI_PROMPTS_DIR / "test_templ.txt"
    t1.write_text("Hello {user}!", encoding="utf-8")
    
    t2 = AI_PROMPTS_DIR / "test_blocks.txt"
    t2.write_text("Block A\n---\nBlock B", encoding="utf-8")
    
    try:
        # Test 1: Templating
        res = random_prompt("test_templ", user="Stan")
        assert res == "Hello Stan!", f"Got: {res}"
        
        # Test 2: Blocks
        # We run multiple times to hopefully hit both, but strict check is just that it is one of them
        res_block = random_prompt_block("test_blocks")
        assert res_block in ["Block A", "Block B"], f"Got: {res_block}"
        
        # Test 3: Fallback (should not crash)
        random_prompt("non_existent_file_12345")
        
        print("PASS")
        
    finally:
        if t1.exists(): t1.unlink()
        if t2.exists(): t2.unlink()

if __name__ == "__main__":
    test_safe_format()
    test_prompt_modules()
