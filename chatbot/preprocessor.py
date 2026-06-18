import re

class Preprocessor:
    def __init__(self):
        # Match consecutive repeated punctuations (e.g., !!! -> !, ??? -> ?, ... -> .)
        self.repeated_punct_regex = re.compile(r'([!?.,])\1+')
        
    def clean(self, text: str) -> str:
        if not text:
            return ""
            
        # 1. Lowercase English characters
        text = text.lower()
        
        # 2. Normalize repeated punctuations (e.g. !! -> !, ?? -> ?)
        # Using a regex to replace consecutive matches of the same punctuation with a single occurrence
        text = self.repeated_punct_regex.sub(r'\1', text)
        
        # 3. Standardize spaces (replace multiple whitespace characters with a single space)
        text = re.sub(r'\s+', ' ', text)
        
        # 4. Strip leading and trailing whitespace
        text = text.strip()
        
        return text
        
    def detect_language(self, text: str) -> str:
        if not text:
            return "en"
            
        # Remove spaces to count actual characters
        clean_text = text.replace(" ", "")
        if not clean_text:
            return "en"
            
        # Count Arabic characters using unicode range \u0600-\u06FF
        arabic_chars_count = len(re.findall(r'[\u0600-\u06FF]', clean_text))
        total_chars_count = len(clean_text)
        
        # If Arabic character ratio is > 30%, identify as "ar", otherwise "en"
        arabic_ratio = arabic_chars_count / total_chars_count
        return "ar" if arabic_ratio > 0.3 else "en"

if __name__ == "__main__":
    # Quick sanity check
    preprocessor = Preprocessor()
    test_inputs = [
        "ازاي اربط الكرسي بالواي فاي؟!!!",
        "please هل 15% battery كفاية؟  شكراً",
        "I need to know: Where is the nearest ramp? ASAP."
    ]
    for inp in test_inputs:
        cleaned = preprocessor.clean(inp)
        lang = preprocessor.detect_language(cleaned)
        print(f"Input: {inp}\nCleaned: {cleaned}\nLanguage: {lang}\n" + "-"*30)