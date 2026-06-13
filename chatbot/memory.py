import re
import time

class ConversationMemory:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history = []
        self.user_name = None
        self.last_access_time = time.time()
        
        # Regex patterns to capture name in Arabic and English
        self.name_patterns = [
            re.compile(r'(?:اسمي|اسمي هو|انا اسمي|أنا اسمي|لاء انا اسمي|لأ انا اسمي|معاك|معاكي)\s+([أ-يa-zA-Z]+)', re.IGNORECASE),
            re.compile(r'(?:my name is|call me)\s+([أ-يa-zA-Z]+)', re.IGNORECASE)
        ]
        self.invalid_name_tokens = {
            "ايه", "إيه", "اي", "أيه", "اية", "إية", "ما", "ماذا", "مين", "هو",
            "what", "who", "where", "why", "how"
        }
        
    def add_turn(self, user_msg: str, bot_response: str, intent: str, confidence: float):
        self.last_access_time = time.time()
        self.history.append({
            "user": user_msg,
            "bot": bot_response,
            "intent": intent,
            "confidence": confidence
        })
        
        # Limit history size to max_history (remove oldest if exceeded)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
    def get_last_n_intents(self, n: int = 5):
        return [turn["intent"] for turn in self.history[-n:]]
            
    def extract_user_info(self, text: str):
        if not text:
            return
            
        for pattern in self.name_patterns:
            match = pattern.search(text)
            if match:
                candidate = match.group(1).strip(" ؟?!.،,")
                if candidate.lower() in self.invalid_name_tokens:
                    continue
                self.user_name = candidate
                break
                
    def get_last_turn(self):
        if self.history:
            return self.history[-1]
        return None
        
    def get_context(self):
        # Return last 3 conversation turns as list
        return self.history[-3:] if len(self.history) >= 3 else self.history
        
    def clear(self):
        self.history = []
        self.user_name = None

if __name__ == "__main__":
    # Test memory
    memory = ConversationMemory()
    test_phrases = [
        "أهلاً، اسمي أحمد وكنت بسأل عن الكرسي",
        "hello, my name is John, how are you?",
        "أنا اسمي سارة ومبسوطة جداً"
    ]
    for phrase in test_phrases:
        memory.extract_user_info(phrase)
        print(f"Text: '{phrase}'\nExtracted Name: '{memory.user_name}'\n" + "-"*30)
