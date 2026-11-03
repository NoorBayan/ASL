import re
from typing import Tuple, Optional

class ProvenanceAnchorEngine:
    def __init__(self):
        pass

    def extract_clean_text_and_offsets(self, tagged_text: str) -> List[Tuple[str, int, int, str]]:
        tag_pattern = re.compile(r'<([a-zA-Z0-9_\u0621-\u064A]+)(?:\s+id="([^"]+)")?>(.*?)</\1>', re.DOTALL)
        results = []
        
        for match in tag_pattern.finditer(tagged_text):
            tag_name = match.group(1)
            span_id = match.group(2) if match.group(2) else ""
            inner_content = match.group(3).strip()
            start_pos = match.start()
            end_pos = match.end()
            results.append((inner_content, start_pos, end_pos, tag_name))
            
        return results

    def verify_exact_character_bounds(self, source_text: str, start_char: int, end_char: int, expected_text: str) -> bool:
        if start_char < 0 or end_char > len(source_text) or start_char >= end_char:
            return False
        extracted = source_text[start_char:end_char].strip()
        normalized_extracted = re.sub(r'\s+', ' ', extracted)
        normalized_expected = re.sub(r'\s+', ' ', expected_text.strip())
        return normalized_extracted == normalized_expected
