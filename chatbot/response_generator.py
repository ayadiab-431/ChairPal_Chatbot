import os
import json
import re
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

try:
    from chatbot.preprocessor import Preprocessor
except ModuleNotFoundError:
    from preprocessor import Preprocessor

class ResponseGenerator:
    def __init__(self, dataset_path: str = "data/merged_dataset.jsonl"):
        self.preprocessor = Preprocessor()
        self.dataset = []
        
        # Load Merged Cleaned Dataset
        if os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.dataset.append(json.loads(line))
        else:
            # Fallback to load default datasets if merged is not found
            for path in ["chairpal_dataset.jsonl", "data/health_intents_dataset.jsonl"]:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                self.dataset.append(json.loads(line))
                                
        # 3. Categorize by Intent and Language
        # Structure: self.intent_map[intent][lang] = list of {"question": str, "answer": str}
        self.intent_map = {}
        for item in self.dataset:
            intent = item["intent"]
            lang = item["language"]
            
            if intent not in self.intent_map:
                self.intent_map[intent] = {}
            if lang not in self.intent_map[intent]:
                self.intent_map[intent][lang] = []
                
            self.intent_map[intent][lang].append({
                "question": self.preprocessor.clean(item["question"]),
                "answer": item["answer"]
            })
            
        # Standard Fallback Answers
        self.fallback_answers = {
            "ar": "عذراً، أنا مصمم لمساعدتك في كل ما يخص كرسي Chairpal الذكي وتطبيق الموبايل والحساسات فقط، وليس لدي معلومات عن موضوعات خارجية خارج نطاق المشروع.",
            "en": "I'm sorry, I am designed to assist you only with the Chairpal smart wheelchair, mobile app, and sensors. I do not have information on external topics outside the scope of this project."
        }
        
        # Load Semantic RAG Engine
        self.semantic_model = None
        self.semantic_index = None
        try:
            self.semantic_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
            index_path = "data/semantic_index.pkl"
            self.candidate_embeddings = {}
            if os.path.exists(index_path):
                print(f"Loading semantic index from {index_path}...")
                with open(index_path, "rb") as f:
                    index_data = pickle.load(f)
                    
                all_embeddings = index_data.get("embeddings", [])
                all_metadata = index_data.get("metadata", [])
                
                # Reorganize by intent -> language
                for i, meta in enumerate(all_metadata):
                    intent_key = meta.get("intent", "")
                    lang_key = meta.get("language", "")
                    
                    if intent_key not in self.candidate_embeddings:
                        self.candidate_embeddings[intent_key] = {}
                    if lang_key not in self.candidate_embeddings[intent_key]:
                        self.candidate_embeddings[intent_key][lang_key] = []
                        
                    self.candidate_embeddings[intent_key][lang_key].append(all_embeddings[i])
                
                # Convert lists to numpy arrays
                for intent_key in self.candidate_embeddings:
                    for lang_key in self.candidate_embeddings[intent_key]:
                        self.candidate_embeddings[intent_key][lang_key] = np.array(self.candidate_embeddings[intent_key][lang_key])
                
                print("Question embeddings loaded successfully from disk!")
            else:
                print(f"Warning: {index_path} not found. Semantic RAG might be impaired. Please run 04_build_semantic_index.py")
        except Exception as e:
            print(f"Failed to load Semantic Model/Index: {e}")
            

        self.vector_indexes = {}
        
    def generate(self, intent: str, cleaned_query: str, detected_language: str, 
                 user_context: dict = None, conversation_context: list = None, confidence: float = 1.0) -> str:
        
        def normalize_arabic(text: str) -> str:
            text = re.sub(r'[\u064B-\u0652]', '', text)
            text = re.sub(r'[أإآ]', 'ا', text)
            text = re.sub(r'ة', 'ه', text)
            text = re.sub(r'ى', 'ي', text)
            return text

        # Override intent to bot_identity for clear identity/project/app queries
        query_norm = normalize_arabic(cleaned_query.lower())
        
        # 1. Intercept slow wheelchair queries
        slow_keywords_ar = ["بطيء", "بطيئ", "مش راضي يتحرك", "مش بيتحرك", "واقف مش بيتحرك", "حركته بطيئه"]
        slow_keywords_en = ["slow", "not moving", "stopped moving", "won't move", "won't drive"]
        is_slow_query = any(kw in query_norm for kw in slow_keywords_ar) or any(kw in query_norm for kw in slow_keywords_en)
        if is_slow_query:
            if detected_language == "ar":
                ans = "لو الكرسي مش بيتحرك أو بطيء، اتأكد الأول إن البطارية مش فاضية، وإن الكرسي مش على وضع الـ (Manual Freewheel)."
            else:
                ans = "If the wheelchair is not moving or is moving slow, first ensure that the battery is not empty and that the chair is not in Manual Freewheel mode."
            ans = self._inject_context(ans, "wheelchair_usage", detected_language, user_context)
            return ans.replace("***", "").replace("**", "").replace("*", "")

        # 2. Intercept obstacle avoidance / autonomous navigation queries
        obstacle_phrases_ar = ["تفادي العقبات", "يتفادى العقبات", "تجنب الاصطدام", "يمشي لوحده", "التوجيه الذاتي", "الملاحة الذاتية", "تفادي العوائق", "بيمشي لوحده", "يتفادى عقبات"]
        obstacle_phrases_en = ["avoid obstacles", "obstacle avoidance", "autonomous navigation", "drive itself", "self driving", "steer itself", "does it navigate", "navigate itself"]
        is_obstacle_query = any(phrase in query_norm for phrase in obstacle_phrases_ar) or any(phrase in query_norm for phrase in obstacle_phrases_en)
        if is_obstacle_query:
            if detected_language == "ar":
                ans = (
                    "الكرسي بيتفادى العقبات ذاتياً بالاعتماد على نظام ذكي متكامل:\n"
                    "1. مستشعرات الـ Lidar وحساسات الموجات فوق الصوتية (Ultrasonic): متثبتة في الكرسي عشان ترصد أي عقبات مفاجئة في كل الاتجاهات باستمرار.\n"
                    "2. خوارزمية A* (A-Star): بتستخدمها وحدة التحكم لحساب أقصر وأأمن مسار لتفادي العقبة تلقائياً والوصول للهدف بأمان."
                )
            else:
                ans = (
                    "The wheelchair avoids obstacles autonomously using an integrated smart system:\n"
                    "1. Lidar and Ultrasonic Sensors: Mounted on the wheelchair to continuously detect sudden obstacles in all directions.\n"
                    "2. A* (A-Star) Algorithm: Used by the microcontroller to calculate the shortest and safest path to automatically avoid the obstacle and reach the destination safely."
                )
            ans = self._inject_context(ans, "navigation", detected_language, user_context)
            return ans.replace("***", "").replace("**", "").replace("*", "")

        # (Nutrition, Exercise, and Stairs queries are now handled natively via intent classification)

        # 3. App keywords and action/feature override for bot_identity
        # Only override if the user is asking WHAT the app IS / what its FEATURES are,
        # NOT for how-to/instructional questions that happen to mention the word 'app'.
        is_bot_query = any(kw in query_norm for kw in ["انت مين", "مين انت", "who are you", "what are you"])
        is_project_query = any(kw in query_norm for kw in [
            "فكرة المشروع", "فكره المشروع", "عن المشروع",
            "مشروع chairpal", "مشروع تشيربال",
            "project idea", "about the project"
        ])
        # Use strict exact phrases only — avoid matching generic how-to questions
        is_app_query = any(kw in query_norm for kw in [
            "مميزات التطبيق", "التطبيق بيعمل ايه", "بيعمل ايه التطبيق",
            "ميزات التطبيق", "وظائف التطبيق",
            "app features", "what does the app do", "what can the app do",
            "what is the app", "tell me about the app"
        ])
        
        if is_bot_query or is_project_query or is_app_query:
            intent = "bot_identity"

        # 4. Intercept greeting queries to provide a warm and simple welcome instead of full description
        if intent == "greeting":
            if detected_language == "ar":
                ans = "أهلاً بك! يسعدني التحدث معك، كيف يمكنني مساعدتك اليوم؟ ♿✨"
            else:
                ans = "Hello! Great to chat with you. How can I help you today? ♿✨"
            ans = self._inject_context(ans, "greeting", detected_language, user_context)
            return ans.replace("***", "").replace("**", "").replace("*", "")

        # 1. Handle Fallback
        if intent == "fallback" or intent not in self.intent_map:
            return self.fallback_answers.get(detected_language, self.fallback_answers["ar"])
            
        # 2. Filter dataset by intent and target language
        # Mixed language queries can match either 'ar' or 'mixed' target items
        target_langs = [detected_language]
        if detected_language == "ar":
            target_langs.append("mixed")
        elif detected_language == "en":
            target_langs.append("mixed")
            
        candidates = []
        for l in target_langs:
            if l in self.intent_map[intent]:
                candidates.extend(self.intent_map[intent][l])
                
        # If no candidates in specific language, fall back to any available language under this intent
        if not candidates:
            for l in self.intent_map[intent]:
                candidates.extend(self.intent_map[intent][l])
                
        if not candidates:
            return self.fallback_answers.get(detected_language, self.fallback_answers["ar"])
            
        # 3. Semantic Similarity Search (RAG Engine)
        if not candidates:
            return self.fallback_answers.get(detected_language, self.fallback_answers["ar"])
            
        filtered_query = cleaned_query.strip()
        answers = [c["answer"] for c in candidates]
        best_score = 0.0
        best_idx = 0
        
        if not filtered_query:
            best_score = 0.0
            best_idx = 0
        else:
            try:
                if self.semantic_model:
                    # Semantic Search
                    query_embedding = self.semantic_model.encode([filtered_query], convert_to_numpy=True)
                    
                    # Fetch precomputed embeddings if available
                    candidate_embeddings = None
                    if hasattr(self, "candidate_embeddings") and intent in self.candidate_embeddings and detected_language in self.candidate_embeddings[intent]:
                        candidate_embeddings = self.candidate_embeddings[intent][detected_language]
                    
                    if candidate_embeddings is None:
                        # Fallback to encoding on the fly
                        candidate_questions = [c["question"] for c in candidates]
                        candidate_embeddings = self.semantic_model.encode(candidate_questions, convert_to_numpy=True)
                    
                    sims = cosine_similarity(query_embedding, candidate_embeddings).flatten()
                    
                    # Top-K Retrieval
                    TOP_K = min(5, len(sims))
                    top_indices = np.argsort(sims)[-TOP_K:][::-1]
                    top_scores = sims[top_indices]
                    
                    best_idx = self._rerank_by_keyword_overlap(top_indices, top_scores, candidates, filtered_query)
                    best_score = sims[best_idx]
                    
                    # Similarity Threshold
                    SIMILARITY_THRESHOLD = 0.55
                    if best_score < SIMILARITY_THRESHOLD:
                        print(f"Low similarity {best_score:.3f} for: {filtered_query}")
                        return self.fallback_answers.get(detected_language, self.fallback_answers["ar"])
                else:
                    # Very basic fallback if model failed to load
                    best_score = 0.0
                    best_idx = 0
            except Exception as e:
                print(f"Search error: {e}")
                best_score = 0.0
                best_idx = 0
                
        # Determine if the query is off-topic
        is_off_topic = False
        if intent not in {"greeting", "thanks", "wheelchair_stop_reason", "connect_wheelchair"}:
            if intent == "bot_identity":
                identity_keywords = {
                    "انت", "انتي", "اسم", "كرسي", "شات", "بوت", "مساعد", "مشروع", "تشيربال", "chairpal", 
                    "فكر", "تطبيق", "ميز", "خصائص", "عملك", "صنعك", "برنامج", "features", 
                    "project", "app", "chatbot", "you", "name", "ابلكيشن", "موبيل", "موبايل"
                }
                # Normalize query words
                query_words = re.sub(r'[^\w\s]', ' ', query_norm).split()
                has_identity_kw = any(any(kw in w for kw in identity_keywords) for w in query_words)
                
                # Check for "مين" or English who/what in valid contexts to prevent off-topic matching
                has_valid_min = any(phrase in query_norm for phrase in ["مين انت", "مين معايا", "مين بيكلم", "مين الي", "مين اللي"])
                has_valid_who = any(phrase in query_norm for phrase in ["who is this", "who is speaking", "who am i talking to", "who built", "who created"])
                
                if not (has_identity_kw or has_valid_min or has_valid_who):
                    is_off_topic = True
                if not filtered_query.strip():
                    is_off_topic = True
                    
        if is_off_topic:
            if detected_language == "ar":
                final_answer = "عذراً، أنا مصمم لمساعدتك في كل ما يخص كرسي Chairpal الذكي وتطبيق الموبايل والحساسات فقط، وليس لدي معلومات عن موضوعات خارجية خارج نطاق المشروع."
            else:
                final_answer = "I'm sorry, I am designed to assist you only with the Chairpal smart wheelchair, mobile app, and sensors. I do not have information on external topics outside the scope of this project."
        else:
            final_answer = answers[best_idx]
            
            # Special handling for custom intents
            if intent == "wheelchair_stop_reason":
                obstacle_detected = False
                obstacle_distance = 0.0
                nav_env = user_context.get("navigation_environment", {}) if user_context else {}
                if isinstance(nav_env, dict) and nav_env:
                    obs_det = nav_env.get("obstacle_detection", {}) or {}
                    obstacle_detected = obs_det.get("obstacle_detected", False)
                    obstacle_distance = obs_det.get("obstacle_distance_cm", 0.0)
                    
                emergency_data = user_context.get("emergency", {}) if user_context else {}
                emergency_active = False
                emergency_type = ""
                if isinstance(emergency_data, dict) and emergency_data:
                    emergency_active = emergency_data.get("active", False)
                    emergency_type = emergency_data.get("emergency_type", "")
                    
                health_data = user_context.get("health", {}) if user_context else {}
                heart_rate = 75.0
                temperature = 37.0
                abnormal_posture = False
                if isinstance(health_data, dict) and health_data:
                    hr_data = health_data.get("heart_rate", {}) or {}
                    heart_rate = hr_data.get("value", 75.0)
                    temp_data = health_data.get("temperature", {}) or {}
                    temperature = temp_data.get("value", 37.0)
                    mpu_data = health_data.get("mpu_monitoring", {}) or {}
                    abnormal_posture = mpu_data.get("abnormal_posture_detected", False)
                else:
                    legacy_sensors = user_context.get("sensor_data", {}) if user_context else {}
                    if legacy_sensors:
                        heart_rate = legacy_sensors.get("heart_rate", 75.0)
                        temperature = legacy_sensors.get("temperature", 37.0)
                        mpu_status = legacy_sensors.get("mpu_status", "normal")
                        abnormal_posture = (mpu_status == "fainting_detected")
                        
                battery_pct = 100.0
                wheelchair_data = user_context.get("wheelchair", {}) if user_context else {}
                if isinstance(wheelchair_data, dict) and wheelchair_data:
                    battery_pct = wheelchair_data.get("battery_percentage", 100.0)
                else:
                    battery_pct = user_context.get("battery_level", 100.0) if user_context else 100.0
                    
                # Formulate response
                if detected_language == "ar":
                    if emergency_active:
                        if emergency_type == "collision_risk":
                            final_answer = f"الكرسي وقف تلقائياً لتفادي الاصطدام بوجود عائق قدامه على مسافة {obstacle_distance} سم."
                        elif emergency_type == "health_risk":
                            posture_str = " مع وضعية جلوس غير مريحة" if abnormal_posture else ""
                            final_answer = f"الكرسي وقف تلقائياً كإجراء أمان عشان رصدنا حالة تعب: نبضات قلبك مرتفعة ({heart_rate} نبضة/دقيقة) وحرارتك ({temperature}°م){posture_str}. بننصحك بالاستراحة فوراً."
                        elif emergency_type == "fall_detected":
                            final_answer = "تنبيه طارئ: تم رصد حالة سقوط مفاجئ للكرسي! تم إرسال استغاثة طوارئ لجهات الاتصال الموثوقة فوراً لتأمين سلامتك."
                        elif emergency_type == "battery_critical":
                            final_answer = f"الكرسي وقف بسبب انخفاض مستوى البطارية الحرج ({battery_pct}%). يرجى شحن الكرسي فوراً."
                        elif emergency_type == "manual_emergency_stop":
                            final_answer = "تم تفعيل التوقف الطارئ اليدوي للكرسي. للبدء مجدداً، تأكد من تحرير زر الطوارئ."
                        else:
                            if obstacle_detected:
                                final_answer = f"الكرسي وقف تلقائياً لتفادي الاصطدام بوجود عائق قدامه على مسافة {obstacle_distance} سم."
                            else:
                                final_answer = "تم إيقاف الكرسي كإجراء أمان طارئ. يرجى مراجعة التطبيق لمعرفة تفاصيل التنبيه."
                    elif obstacle_detected:
                        final_answer = f"الكرسي وقف تلقائياً لوجود عائق على مسافة {obstacle_distance} سم."
                    elif battery_pct < 20:
                        final_answer = f"الكرسي وقف بسبب ضعف شحن البطارية الحرج ({battery_pct}%)."
                    else:
                        final_answer = "الكرسي واقف حالياً وفي حالة استعداد. يمكنك توجيهه من خلال التطبيق أو الجويستيك."
                else:
                    if emergency_active:
                        if emergency_type == "collision_risk":
                            final_answer = f"The wheelchair stopped automatically to avoid a collision because an obstacle was detected in front of it at a distance of {obstacle_distance} cm."
                        elif emergency_type == "health_risk":
                            posture_str = " with an abnormal sitting posture" if abnormal_posture else ""
                            final_answer = f"The wheelchair stopped automatically as a safety measure because we detected: high heart rate ({heart_rate} bpm) and temperature ({temperature}°C){posture_str}. We advise you to rest immediately."
                        elif emergency_type == "fall_detected":
                            final_answer = "Emergency alert: A sudden wheelchair fall was detected! An emergency SOS has been sent to your caregivers immediately to ensure your safety."
                        elif emergency_type == "battery_critical":
                            final_answer = f"The wheelchair stopped due to a critical battery level ({battery_pct}%). Please charge it immediately."
                        elif emergency_type == "manual_emergency_stop":
                            final_answer = "The manual emergency stop has been triggered. To start again, ensure the emergency button is released."
                        else:
                            if obstacle_detected:
                                final_answer = f"The wheelchair stopped automatically because an obstacle was detected in front of it at a distance of {obstacle_distance} cm."
                            else:
                                final_answer = "The wheelchair has been stopped due to an emergency. Please check the app for alert details."
                    elif obstacle_detected:
                        final_answer = f"The wheelchair stopped automatically because an obstacle was detected at a distance of {obstacle_distance} cm."
                    elif battery_pct < 20:
                        final_answer = f"The wheelchair stopped due to a low battery ({battery_pct}%)."
                    else:
                        final_answer = "The wheelchair is currently stopped and in idle mode. You can move it using the app or joystick."
            elif intent == "connect_wheelchair":
                if detected_language == "ar":
                    final_answer = (
                        "لربط الكرسي المتحرك بالتطبيق، اتبع الخطوات التالية:\n"
                        "1. تأكد من تشغيل الواي فاي (Wi-Fi) والموقع (Location) على هاتفك.\n"
                        "2. شغل الكرسي المتحرك من خلال زر التشغيل الرئيسي.\n"
                        "3. افتح تطبيق Chairpal واذهب إلى الإعدادات ثم 'ربط الكرسي'.\n"
                        "4. سيبدأ التطبيق بالبحث عن الكرسي، اضغط عليه لعمل اقتران (Pairing).\n"
                        "5. بمجرد الاتصال، ستظهر لك علامة الاتصال باللون الأخضر وتبدأ قراءات الحساسات بالظهور."
                    )
                else:
                    final_answer = (
                        "To connect the wheelchair to the app, follow these steps:\n"
                        "1. Make sure Wi-Fi and Location are enabled on your phone.\n"
                        "2. Turn on the wheelchair using the main power button.\n"
                        "3. Open the Chairpal app, go to Settings, and select 'Connect Wheelchair'.\n"
                        "4. The app will search for the wheelchair, tap on it to pair.\n"
                        "5. Once connected, a green status indicator will appear and sensor readings will start displaying."
                    )
            elif intent == "bot_identity":
                query_norm = normalize_arabic(cleaned_query.lower())
                
                app_keywords = ["تطبيق", "ابلكيشن", "موبيل", "موبايل", "برنامج", "ميزه", "مميز", "خاصي", "وظيف", "app", "applic", "feature"]
                project_keywords = ["مشروع", "فكر", "project", "idea", "concept"]
                
                query_words = re.sub(r'[^\w\s]', ' ', query_norm).split()
                
                has_app = any(any(kw in w for kw in app_keywords) for w in query_words)
                has_project = any(any(kw in w for kw in project_keywords) for w in query_words)
                
                if has_app:
                    if detected_language == "ar":
                        final_answer = (
                            "تطبيق Chairpal الذكي بيوفرلك كذا ميزة أساسية لمساعدتك:\n"
                            "1. مراقبة المؤشرات الحيوية: بتابع نبضات قلبك وحرارتك باستمرار من حساسات الكرسي.\n"
                            "2. رصد حالات السقوط (MPU): لو حصل أي سقوط مفاجئ، برسل تنبيه طوارئ SOS فوراً لجهات اتصالك.\n"
                            "3. التحكم بالكرسي: تقدر تتحرك يدوي بالجويستيك، لاسلكي بالواي فاي، أو توجيه ذاتي لتفادي العقبات."
                        )
                    else:
                        final_answer = (
                            "The Chairpal mobile app offers several key features:\n"
                            "1. Vital Signs Monitoring: Tracks your heart rate and body temperature continuously via wheelchair sensors.\n"
                            "2. Fall Detection (MPU): Sends immediate SOS alerts to emergency contacts in case of a fall.\n"
                            "3. Wheelchair Control: Supports manual joystick control, wireless Wi-Fi control, and autonomous navigation to avoid obstacles."
                        )
                elif has_project:
                    if detected_language == "ar":
                        final_answer = (
                            "مشروع Chairpal هو دمج الذكاء الاصطناعي مع الكراسي المتحركة الكهربائية لتوفير استقلالية وأمان كامل لمستخدمي الكراسي المتحركة. المشروع بيربط الكرسي بتطبيق موبايل وحساسات ذكية."
                        )
                    else:
                        final_answer = (
                            "The Chairpal project integrates artificial intelligence with electric wheelchairs to provide full independence and safety for wheelchair users by connecting the wheelchair to a mobile app and smart sensors."
                        )
                else:
                    # Default Bot Identity response (chatbot identity & what it does, no project idea)
                    if detected_language == "ar":
                        final_answer = (
                            "أنا مساعد Chairpal الذكي! ♿✨ أنا متصل بحساسات كرسيّك لمراقبة حالتك وصحتك ومساعدتك في الملاحة والتحكم وتنبيهك في حالات الطوارئ."
                        )
                    else:
                        final_answer = (
                            "I am the Chairpal Smart Assistant! ♿✨ I am connected to your wheelchair's sensors to monitor your health, assist you with navigation and control, and alert you in emergencies."
                        )
            
        # 4. Personalization & Dynamic Sensor Injection
        final_answer = self._inject_context(final_answer, intent, detected_language, user_context)
        
        # 4.1 Trip Information Integration (Destination & Status)
        if intent in {"wheelchair_stop_reason", "navigation"} and user_context:
            trip_data = user_context.get("trip", {})
            if isinstance(trip_data, dict) and trip_data.get("active_trip", False):
                dest_data = trip_data.get("destination", {})
                dest_name = dest_data.get("name", "")
                dest_category = dest_data.get("category", "")
                floor_name = dest_data.get("floor", {}).get("name", "") if isinstance(dest_data.get("floor"), dict) else ""
                trip_status = trip_data.get("trip_status", "paused")
                
                if detected_language == "ar":
                    status_map = {
                        "moving": "جاري الحركة",
                        "paused": "متوقفة مؤقتاً",
                        "completed": "مكتملة",
                        "cancelled": "ملغاة",
                        "emergency_stopped": "متوقفة اضطرارياً للطوارئ"
                    }
                    trip_status_ar = status_map.get(trip_status, trip_status)
                    trip_info = f"\n\n📍 بخصوص رحلتكِ الحالية إلى {dest_name} ({dest_category}) في {floor_name}، فهي حالياً {trip_status_ar}."
                else:
                    trip_info = f"\n\n📍 Regarding your current trip to {dest_name} ({dest_category}) on {floor_name}, it is currently {trip_status}."
                
                final_answer += trip_info

        # 4.2 Arabic Gender-Awareness / Feminization
        if detected_language == "ar" and user_context:
            user_data = user_context.get("user", {})
            gender = None
            if isinstance(user_data, dict):
                gender = user_data.get("gender")
            if gender == "female":
                final_answer = self._adapt_gender_ar(final_answer)

        # Strip all markdown bold/triple asterisks from the output
        final_answer = final_answer.replace("***", "").replace("**", "").replace("*", "")
        
        return final_answer
        
    def _inject_context(self, answer: str, intent: str, lang: str, user_context: dict) -> str:
        if not user_context:
            return answer
            
        name = user_context.get("name")
        
        # B. Inject Sensor Readings & Warnings
        health_intents = {"sensor_interpretation", "fatigue", "pain", "shortness_of_breath", "normal_health"}
        
        warning_str = ""
        metrics_block = ""
        
        # Extract variables from user_context (supporting both nested and flat schemas)
        heart_rate = 75.0
        temperature = 37.0
        movement = "active"
        mpu_status = "normal"
        
        health_data = user_context.get("health", {})
        if isinstance(health_data, dict) and health_data:
            hr_data = health_data.get("heart_rate", {}) or {}
            hr_raw = hr_data.get("value", 75.0)
            heart_rate = float(hr_raw) if hr_raw is not None else 75.0
            temp_data = health_data.get("temperature", {}) or {}
            temp_raw = temp_data.get("value", 37.0)
            temperature = float(temp_raw) if temp_raw is not None else 37.0
            mpu_data = health_data.get("mpu_monitoring", {}) or {}
            if mpu_data.get("abnormal_posture_detected", False) or mpu_data.get("fall_risk_detected", False):
                mpu_status = "fainting_detected"
        else:
            legacy_sensors = user_context.get("sensor_data", {})
            if isinstance(legacy_sensors, dict) and legacy_sensors:
                hr_raw = legacy_sensors.get("heart_rate", 75.0)
                heart_rate = float(hr_raw) if hr_raw is not None else 75.0
                temp_raw = legacy_sensors.get("temperature", 37.0)
                temperature = float(temp_raw) if temp_raw is not None else 37.0
                movement = legacy_sensors.get("movement", "active")
                mpu_status = legacy_sensors.get("mpu_status", "normal")
                
        has_sensors = bool(user_context.get("health") or user_context.get("sensor_data"))
        
        if intent in health_intents and has_sensors:
            
            # Load thresholds from config
            import json
            import os
            config_path = "config/health_thresholds.json"
            thresholds = {
                "heart_rate_high": 100.0,
                "heart_rate_low": 50.0,
                "temperature_high": 38.0,
                "temperature_low": 35.5,
                "battery_critical": 20.0
            }
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        thresholds.update(json.load(f))
                except Exception as e:
                    pass

            # Determine warnings with non-assertive medical language
            has_warning = False
            if mpu_status == "fainting_detected":
                has_warning = True
                warning_str = "🚨 تنبيه طارئ: تم رصد ما قد يشير لحالة سقوط مفاجئ! سيتم إرسال استغاثة طوارئ فوراً لجهات اتصالك للمساعدة." if lang == "ar" else "🚨 Emergency alert: A potential fall has been detected! An SOS alert is being sent to your emergency contacts."
            elif heart_rate > thresholds["heart_rate_high"]:
                has_warning = True
                warning_str = f"⚠️ تنبيه: يُلاحظ من القراءات ارتفاع في معدل نبضات القلب ({heart_rate} نبضة/دقيقة). قد تشير هذه القراءات إلى حاجتك للراحة." if lang == "ar" else f"⚠️ Alert: Readings suggest an elevated heart rate ({heart_rate} bpm). You may need to rest."
            elif heart_rate < thresholds["heart_rate_low"]:
                has_warning = True
                warning_str = f"⚠️ تنبيه: يُلاحظ انخفاض في معدل نبضات القلب ({heart_rate} نبضة/دقيقة). قد تشير بعض القراءات إلى تغيرات تستدعي الانتباه الطبي." if lang == "ar" else f"⚠️ Alert: Readings suggest a low heart rate ({heart_rate} bpm). We advise consulting a doctor."
            elif temperature > thresholds["temperature_high"]:
                has_warning = True
                warning_str = f"⚠️ تنبيه: يُلاحظ ارتفاع في درجة حرارة الجسم ({temperature}°م). يرجى شرب المياة والاستراحة." if lang == "ar" else f"⚠️ Alert: Readings suggest a high body temperature ({temperature}°C). Please stay hydrated."
            elif temperature < thresholds["temperature_low"]:
                has_warning = True
                warning_str = f"⚠️ تنبيه: يُلاحظ انخفاض في درجة حرارة الجسم ({temperature}°م). يرجى التدفئة." if lang == "ar" else f"⚠️ Alert: Readings suggest a low body temperature ({temperature}°C). Please warm up."
                
            # If warning is active, override positive answers that might contradict it
            if has_warning:
                if intent == "normal_health":
                    if lang == "ar":
                        answer = "مؤشراتك الحيوية فيها بعض الاختلافات وغير مستقرة حالياً. يرجى الحذر والراحة."
                    else:
                        answer = "Your vital signs are showing some unusual readings and are not stable. Please rest and stay safe."
                else:
                    pos_ar = "مؤشراتك الحيوية ممتازة وتحت المراقبة المستمرة! نبضات القلب ودرجة الحرارة في المعدلات الطبيعية الآمنة، وجسمك في حالة مستقرة تماماً."
                    caution_ar = "مؤشراتك الحيوية حالياً تحت المراقبة المستمرة. تم رصد بعض القراءات غير المستقرة التي تتطلب منك الحذر والاستراحة."
                    if pos_ar in answer:
                        answer = answer.replace(pos_ar, caution_ar)
                        
                    pos_en = "Your vital signs are excellent and under continuous monitoring! Your heart rate and body temperature are within the safe normal ranges, and your overall health status is completely stable."
                    caution_en = "Your vital signs are currently under continuous monitoring. Some unusual readings have been detected that require caution and rest."
                    if pos_en in answer:
                        answer = answer.replace(pos_en, caution_en)
            
            # Prepare translation for movement
            movement_translation = {
                "low": "منخفضة (بننصحك تغير وضعيتك لتجنب الآلام)" if lang == "ar" else "Low (we advise changing your posture to avoid stiffness)",
                "medium": "معتدلة" if lang == "ar" else "Medium",
                "active": "نشطة وممتازة" if lang == "ar" else "Active and excellent"
            }
            movement_str = movement_translation.get(movement, movement)
            
            # Generate Health Metrics block
            if lang == "ar":
                metrics_block = (
                    f"\n\n📊 قراءات حساساتك الحالية:\n"
                    f"- نبضات القلب: {heart_rate} نبضة/دقيقة\n"
                    f"- درجة حرارة الجسم: {temperature}°م\n"
                    f"- حالة الحركة والنشاط: {movement_str}"
                )
            else:
                metrics_block = (
                    f"\n\n📊 Your current sensor readings:\n"
                    f"- Heart Rate: {heart_rate} bpm\n"
                    f"- Body Temperature: {temperature}°C\n"
                    f"- Activity Level: {movement_str}"
                )
                
        # A. Prepend Name if available (only for dialogue/supportive intents)
        name_allowed_intents = {"greeting", "thanks", "emotional_support", "pain", "fatigue", "shortness_of_breath", "normal_health"}
        if name and intent in name_allowed_intents:
            if lang == "ar":
                if not answer.startswith("يا"):
                    answer = f"يا {name}، {answer}"
            else:
                if not answer.lower().startswith("hello") and not answer.lower().startswith("hi"):
                    answer = f"Hello {name}, {answer}"
                    
        # C. Assemble final response: Warning first, then Answer with Name, then Metrics
        if warning_str:
            answer = f"{warning_str}\n\n{answer}"
            
        if metrics_block:
            answer = f"{answer}{metrics_block}"

        urgent_health_intents = {"fatigue", "pain", "shortness_of_breath"}
        if warning_str or intent in urgent_health_intents:
            safety_note = (
                "\n\nملاحظة سلامة: هذه إرشادات مساعدة وليست بديلاً عن الطبيب أو الطوارئ. إذا كانت الأعراض شديدة أو مستمرة، تواصل مع طبيبك أو خدمات الطوارئ فوراً."
                if lang == "ar"
                else "\n\nSafety note: This guidance is not a substitute for a doctor or emergency care. If symptoms are severe or persistent, contact your doctor or emergency services immediately."
            )
            if safety_note.strip() not in answer:
                answer = f"{answer}{safety_note}"
            
        return answer

    def _adapt_gender_ar(self, text: str) -> str:
        if not text:
            return ""
            
        # Precise replacements to feminize without breaking core words
        replacements = {
            r"\bأهلاً بك\b": "أهلاً بكِ",
            r"\bأهلاً بك\s": "أهلاً بكِ ",
            r"\bمساعدك\b": "مساعدتكِ",
            r"\bمساعدك\s": "مساعدتكِ ",
            r"\bمساعدكِ الذكي\b": "مساعدتكِ الذكية",
            r"\bقلبك\b": "قلبكِ",
            r"\bحرارتك\b": "حرارتكِ",
            r"\bننصحك\b": "ننصحكِ",
            r"\bبننصحك\b": "بننصحكِ",
            r"\bتأكد\b": "تأكدي",
            r"\bشغّل\b": "شغّلي",
            r"\bافتح\b": "افتحي",
            r"\bادخل\b": "ادخلي",
            r"\bواضغط\b": "واضغطي",
            r"\bواختار\b": "واختاري",
            r"\bاختار\b": "اختاري",
            r"\bسجل\b": "سجلي",
            r"\bتعدل\b": "تعدلي",
            r"\bتعمل\b": "تعملي",
            r"\bبيوفرلك\b": "بيوفرلكِ",
            r"\bبوضحلك\b": "بوضحلكِ",
            r"\bتفكيرك\b": "تفكيركِ",
            r"\bتفيدك\b": "تفيدكِ",
            r"\bمعك\b": "معكِ",
            r"\bمساعدتك\b": "مساعدتكِ",
            r"\bعمرك\b": "عمركِ",
            r"\bحاسس\b": "حاسة",
            r"\bتشعر\b": "تشعرين",
            r"\bتعبان\b": "تعبانة",
            r"\bمريض\b": "مريضة",
            r"\bعايز\b": "عايزة",
            r"\bصحتك\b": "صحتكِ",
            r"\bكرسيك\b": "كرسيكِ",
            r"\bتطبيقك\b": "تطبيقكِ",
            r"\bأدعمك\b": "أدعمكِ",
            r"\bأسمعك\b": "أسمعكِ",
            r"\bلخدمتك\b": "لخدمتكِ",
            r"\bجلستك\b": "جلستكِ",
            r"\bمؤشراتك\b": "مؤشراتكِ",
            r"\bحساساتك\b": "حساساتكِ",
            r"\bتنبيهك\b": "تنبيهكِ",
            r"\bوجهتك\b": "وجهتكِ",
            r"\bرحلتك\b": "رحلتكِ",
            r"\bعليك\b": "عليكِ",
            r"\bلك\b": "لكِ",
            r"\bمعاكي\b": "معاكِ",
            r"\bمعاك\b": "معاكِ"
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
            
        return text

    def _clean_medical_language(self, text: str) -> str:
        # Avoid giving absolute medical advice
        text = text.replace("بننصحك بالراحة", "قد تشير القراءات إلى حاجتك للراحة")
        text = text.replace("نبضات قلبك مرتفعة", "يُلاحظ من القراءات ارتفاع في معدل نبضات القلب")
        text = text.replace("Your heart rate is elevated", "Readings suggest an elevated heart rate")
        text = text.replace("عندك مشكلة صحية", "قد تشير بعض القراءات إلى تغيرات تستدعي الانتباه")
        return text

    def _rerank_by_keyword_overlap(self, top_indices, top_scores, candidates, query):
        query_words = set(query.lower().split())
        best_idx = top_indices[0]
        best_combined_score = -1.0
        
        for idx, score in zip(top_indices, top_scores):
            ans_text = candidates[idx].get("question", "").lower()
            ans_words = set(ans_text.split())
            overlap = len(query_words.intersection(ans_words))
            combined = score + (overlap * 0.05)
            if combined > best_combined_score:
                best_combined_score = combined
                best_idx = idx
        return int(best_idx)



if __name__ == "__main__":
    # Test response generator
    try:
        generator = ResponseGenerator()
        preprocessor = Preprocessor()
        
        q = "معدل الـ heart rate ده ايه؟"
        cleaned = preprocessor.clean(q)
        lang = preprocessor.detect_language(cleaned)
        
        user_ctx = {
            "name": "أحمد",
            "sensor_data": {
                "heart_rate": 105,
                "temperature": 37.2,
                "movement": "low",
                "mpu_status": "normal"
            }
        }
        
        ans = generator.generate("sensor_interpretation", cleaned, lang, user_ctx)
        # We can't print non-ASCII easily on Windows stdout safely without encode, but let's print a check
        print(f"Query: {q}")
        print(f"Generated length: {len(ans)}")
        print("Test passed successfully!")
    except Exception as e:
        print(f"Error testing response generator: {e}")
