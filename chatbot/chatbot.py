import os

try:
    from chatbot.preprocessor import Preprocessor
    from chatbot.intent_classifier import IntentClassifier
    from chatbot.memory import ConversationMemory
    from chatbot.response_generator import ResponseGenerator
    from chatbot.rule_engine import RuleEngine
except ModuleNotFoundError:
    from preprocessor import Preprocessor
    from intent_classifier import IntentClassifier
    from memory import ConversationMemory
    from response_generator import ResponseGenerator
    from rule_engine import RuleEngine

class ChairpalChatbot:
    def __init__(self, model_path: str = "models/intent_classifier.ftz", 
                 dataset_path: str = "data/merged_dataset.jsonl",
                 fallback_threshold: float = 0.25,
                 session_ttl_hours: int = 1):
        
        self.preprocessor = Preprocessor()
        self.classifier = IntentClassifier(model_path=model_path, fallback_threshold=fallback_threshold)
        self.memories = {}
        self.session_ttl = session_ttl_hours * 3600
        self.responder = ResponseGenerator(dataset_path=dataset_path)
        self.rule_engine = RuleEngine()
        
    def _cleanup_expired_sessions(self):
        import time
        now = time.time()
        expired = [uid for uid, mem in self.memories.items() if (now - mem.last_access_time) > self.session_ttl]
        for uid in expired:
            del self.memories[uid]
            
    def _get_memory(self, user_id: str) -> ConversationMemory:
        self._cleanup_expired_sessions()
        memory_key = str(user_id or "anonymous")
        if memory_key not in self.memories:
            self.memories[memory_key] = ConversationMemory()
        return self.memories[memory_key]

    def respond(self, user_input: str, user_context: dict = None, user_id: str = "anonymous") -> dict:
        if not user_context:
            user_context = {}
        else:
            user_context = dict(user_context)

        memory = self._get_memory(user_id)
            
        # 1. Clean input (Name extraction from text disabled, relies exclusively on backend payload)
        clean_text = self.preprocessor.clean(user_input)
        clean_text_lower = clean_text.lower().strip()
            
        # 2. Detect language
        lang = self.preprocessor.detect_language(clean_text)

        if self._is_name_recall_query(clean_text_lower):
            response = self._get_name_recall_response(lang, user_context)
            memory.add_turn(
                user_msg=user_input,
                bot_response=response,
                intent="name_recall",
                confidence=1.0
            )
            return {
                "response": response,
                "intent": "name_recall",
                "confidence": 1.0,
                "language": lang,
                "user_name": user_context.get("name")
            }
        
        # 3. Detect conversational repair
        if self._is_conversational_repair(clean_text_lower, lang):
            last_turn = memory.get_last_turn()
            if last_turn:
                last_intent = last_turn.get("intent", "fallback")
                response = self._get_simplified_response(last_intent, lang, user_context)
                
                # Store this repair turn in memory, continuing the same intent context
                memory.add_turn(
                    user_msg=user_input,
                    bot_response=response,
                    intent=last_intent,
                    confidence=1.0
                )
                
                return {
                    "response": response,
                    "intent": last_intent,
                    "confidence": 1.0,
                    "language": lang,
                    "user_name": user_context.get("name")
                }
        
        # 4. Intent Classification
        intent, confidence = self.classifier.predict(clean_text)
        intent, confidence = self._override_intent(clean_text_lower, intent, confidence)
        
        # 5. Generate Response using RAG Engine & Context
        response = self.responder.generate(
            intent=intent,
            cleaned_query=clean_text,
            detected_language=lang,
            user_context=user_context,
            conversation_context=memory.get_context(),
            confidence=confidence
        )
        
        # 6. Store in memory
        memory.add_turn(
            user_msg=user_input,
            bot_response=response,
            intent=intent,
            confidence=confidence
        )
        
        return {
            "response": response,
            "intent": intent,
            "confidence": float(confidence),
            "language": lang,
            "user_name": user_context.get("name"),
            "reason": self._build_explanation(intent, float(confidence), clean_text),
            "intent_history": memory.get_last_n_intents(5)
        }

    def _build_explanation(self, intent: str, confidence: float, query: str) -> str:
        if confidence >= 0.90:
            return f"High confidence match for '{intent}' intent (score: {confidence:.2f})"
        elif confidence >= 0.60:
            return f"Moderate confidence match for '{intent}' intent (score: {confidence:.2f})"
        else:
            return f"Low confidence — fell back to '{intent}' (score: {confidence:.2f})"

    def _is_name_recall_query(self, text: str) -> bool:
        name_recall_phrases = [
            "انا اسمي ايه", "أنا اسمي ايه", "اسمي ايه", "اسمي إيه",
            "فاكر اسمي", "عارف اسمي", "هو انت فاكر اسمي",
            "what is my name", "do you remember my name", "remember my name"
        ]
        return any(phrase in text for phrase in name_recall_phrases)

    def _get_name_recall_response(self, lang: str, user_context: dict) -> str:
        name = user_context.get("name") if user_context else None
        if name:
            if lang == "ar":
                return f"أيوه، اسمك {name}."
            return f"Yes, your name is {name}."

        if lang == "ar":
            return "لسه معرفتش اسمك. تقدر تضيفه أو تعدله من إعدادات الملف الشخصي في التطبيق."
        return "I do not know your name yet. You can add or update it in the app's profile settings."

    def _override_intent(self, text: str, intent: str, confidence: float):
        return self.rule_engine.override_intent(text, intent, confidence)


    def _is_conversational_repair(self, text: str, lang: str) -> bool:
        repair_keywords_ar = ["مش فاهم", "وضح", "مش واضح", "وضحلي", "يعني ايه", "مش فاهمة", "وضحلي اكتر", "ايه"]
        repair_keywords_en = ["understand", "mean", "explain", "clarify", "pardon", "what"]
        
        words = text.split()
        if not words:
            return False
            
        # Strict rule: Repair queries are usually very short. If the user writes a full sentence, it's NOT a repair query.
        if len(words) > 4:
            return False
            
        if lang == "ar":
            # Exact match or very short keyword inclusion
            return text in repair_keywords_ar or any(k == text or k in text for k in repair_keywords_ar)
        else:
            return text in repair_keywords_en or any(k == text or k in text for k in repair_keywords_en)

    def _get_simplified_response(self, intent: str, lang: str, user_context: dict) -> str:
        name = user_context.get("name") if user_context else None
        
        simplified_map = {
            "ar": {
                "wheelchair_usage": "ببساطة، الكرسي بيتحرك بـ 3 طرق: إما يدوي بالجويستيك المادي، أو بالموبايل لاسلكياً بالواي فاي، أو تسيبه يمشي لوحده للمكان اللي تحدده على الخريطة في التطبيق.",
                "sensor_interpretation": "قصدي إن حساسات الكرسي بتقيس نبضات قلبك وحرارتك باستمرار عشان تتأكد إن صحتك كويسة، وبتنبهك لو فيه أي حاجة مش طبيعية.",
                "app_help": "بوضحلك إزاي تستخدم التطبيق، زي إنك تسجل حساب مستخدم أو منظمة، أو تعدل إعداداتك، أو تعمل إعادة تعيين للباسورد لو نسيته.",
                "connect_wheelchair": "عشان تربط الكرسي، ادخل على أيقونة (E-Chair)، اسمح باتصال الواي فاي، ولما تظهر قائمة الكراسي القريبة اضغط (Connect) جنب اسم كرسيك للبدء بالتحكم.",
                "navigation": "الملاحة يعني الكرسي بيستخدم خريطة في التطبيق عشان يمشي لوحده، وبيختار أقصر وأأمن طريق، وبيتفادى أي عقبات تظهر قدامه تلقائياً.",
                "emotional_support": "أنا هنا عشان أسمعك وأدعمك نفسياً لو حاسس بتعب أو ضيق، وكمان بوضحلك إرشادات صحية بسيطة عشان تخفف من تعبك.",
                "daily_support": "بساعدك في تنظيم يومك، زي تفكيرك بمواعيد الأكل والعلاج وتغيير جلستك لتجنب التعب والإجهاد.",
                "greeting": "أهلاً بيك! أنا برحب بيك وبسألك إزاي أقدر أساعدك النهاردة بالكرسي أو التطبيق.",
                "thanks": "على الرحب والسعة! أنا هنا دايماً لخدمتك ومساعدتك في أي وقت.",
                "bot_identity": "ببساطة، أنا شات بوت ذكي مدمج في كرسي Chairpal لمراقبة صحتك، وتسهيل حركتك وتوجيه الكرسي ذاتياً.",
                "fallback": "كنت بقول إني مساعدك الذكي لكرسي Chairpal، وممكن تسألني عن صحتك أو الحركية أو التطبيق."
            },
            "en": {
                "wheelchair_usage": "Simply put, the wheelchair can be moved in 3 ways: using the physical joystick, using the mobile app over Wi-Fi, or letting it drive itself automatically to a location you choose on the map.",
                "sensor_interpretation": "I mean that the wheelchair's sensors continuously measure your heart rate and body temperature to make sure you are healthy, and warn you if anything is abnormal.",
                "app_help": "I am explaining how to use the app, like signing up as a user or organization, changing your settings, or resetting your password if you forgot it.",
                "connect_wheelchair": "To connect, tap the (E-Chair) icon, allow Wi-Fi connection, and when nearby wheelchairs appear, tap (Connect) next to your chair to start controlling it.",
                "navigation": "Navigation means the wheelchair uses a map in the app to drive itself, choosing the shortest and safest path while avoiding any obstacles automatically.",
                "emotional_support": "I am here to support you emotionally if you feel down, and to suggest health tips to relieve your discomfort.",
                "daily_support": "I help you organize your day, like medication timings, meals, and changing your posture to avoid fatigue.",
                "greeting": "Hello! I was just welcoming you and asking how I can help you today with the wheelchair or app.",
                "thanks": "You're welcome! I am always here to support and assist you.",
                "bot_identity": "Simply, I am a smart chatbot built into the Chairpal wheelchair to monitor your health, and assist you with autonomous movement.",
                "fallback": "I was saying that I am your smart helper for the Chairpal wheelchair. You can ask me about your health, movement, or the app."
            }
        }
        
        repairs = simplified_map.get(lang, simplified_map["ar"])
        response = repairs.get(intent, repairs["fallback"])
        
        name_allowed_intents = {"greeting", "thanks", "emotional_support", "pain", "fatigue", "shortness_of_breath", "normal_health"}
        if name and intent in name_allowed_intents:
            if lang == "ar":
                response = f"يا {name}، {response}"
            else:
                response = f"Hello {name}, {response}"
                
        return response

if __name__ == "__main__":
    # Test orchestrator
    try:
        chatbot = ChairpalChatbot()
        
        # Simulating conversation flow
        queries = [
            ("أهلاً، اسمي مازن", {}),
            ("كيفية توصيل الكرسي بالواي فاي؟", {}),
            ("مش فاهم", {}),
            ("حاسس بصعوبة في التنفس أعمل ايه؟", {
                "sensor_data": {
                    "heart_rate": 105,
                    "temperature": 37.1,
                    "movement": "low",
                    "mpu_status": "normal"
                }
            })
        ]
        
        print("Starting simulated conversation test...\n")
        for query, ctx in queries:
            print(f"User: {query}")
            res = chatbot.respond(query, user_context=ctx)
            print(f"Bot Intent: {res['intent']} (Confidence: {res['confidence']:.2%})")
            print(f"Bot Response:\n{res['response']}")
            print("-"*50)
            
        print("Simulated conversation test passed successfully!")
    except Exception as e:
        print(f"Error testing chatbot orchestrator: {e}")
