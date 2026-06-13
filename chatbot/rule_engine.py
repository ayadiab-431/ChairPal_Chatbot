import yaml
import os

class RuleEngine:
    def __init__(self, overrides_path="config/intent_overrides.yaml"):
        self.overrides = self._load_yaml(overrides_path)
        
    def _load_yaml(self, path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("overrides", []) if data else []
        except Exception as e:
            print(f"Error loading YAML config: {e}")
            return []

    def _matches(self, text: str, rule: dict) -> bool:
        conditions = rule.get("conditions", [])
        for condition in conditions:
            if condition.get("type") == "keyword_match":
                if condition.get("match_all", False) and "keyword_groups" in condition:
                    # Must match at least one keyword in EACH group
                    groups = condition.get("keyword_groups", [])
                    matched_all_groups = True
                    for group in groups:
                        if not any(k in text for k in group):
                            matched_all_groups = False
                            break
                    if matched_all_groups:
                        return True
                else:
                    # Must match at least one keyword in the list
                    keywords = condition.get("keywords", [])
                    if any(k in text for k in keywords):
                        return True
        return False

    def override_intent(self, text: str, current_intent: str, current_confidence: float):
        text_lower = text.lower()
        for rule in self.overrides:
            if self._matches(text_lower, rule):
                return rule.get("target_intent"), max(float(current_confidence), float(rule.get("min_confidence", 0.0)))
        return current_intent, current_confidence
