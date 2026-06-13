import os
import fasttext
try:
    from chatbot.preprocessor import Preprocessor
except ModuleNotFoundError:
    from preprocessor import Preprocessor

class IntentClassifier:
    def __init__(self, model_path: str = "models/intent_classifier.ftz", fallback_threshold: float = 0.30):
        self.preprocessor = Preprocessor()
        self.fallback_threshold = fallback_threshold
        self.model_path = self._resolve_model_path(model_path)
        
        self.model = fasttext.load_model(self.model_path)

    def _resolve_model_path(self, model_path: str) -> str:
        if os.path.exists(model_path):
            return model_path

        if model_path == "models/intent_classifier.ftz":
            fallback_path = "models/intent_classifier.bin"
            if os.path.exists(fallback_path):
                return fallback_path

        raise FileNotFoundError(
            f"Trained model not found at {model_path}. Please run training or add the quantized model first."
        )
            
    def predict(self, text: str):
        # 1. Clean the text
        cleaned_text = self.preprocessor.clean(text)
        if not cleaned_text:
            return "fallback", 0.0
            
        # 2. Predict intent and probability
        labels, probabilities = self.model.predict(cleaned_text, k=1)
        
        intent = labels[0].replace("__label__", "")
        confidence = probabilities[0]
        
        # 3. Apply fallback threshold
        if confidence < self.fallback_threshold:
            return "fallback", confidence
            
        return intent, confidence

if __name__ == "__main__":
    # Test classifier
    try:
        classifier = IntentClassifier()
        test_queries = [
            "ازاي اربط الكرسي بالواي فاي؟",
            "حاسس بدوخة شديدة ومش قادر أقف",
            "نبضي وحرارتي كويسين دلوقتي؟",
            "أهلاً وسهلاً بك"
        ]
        for query in test_queries:
            intent, conf = classifier.predict(query)
            print(f"Query: {query}\nIntent: {intent} (Confidence: {conf:.2%})\n" + "-"*30)
    except Exception as e:
        print(f"Error testing classifier: {e}")
