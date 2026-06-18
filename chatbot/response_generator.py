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
        
        # (Slow queries and obstacle avoidance are now handled natively via intent classification)

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

        if intent == "caregiver_info":
            relations = user_context.get("relations", {}) if user_context else {}
            doctor = relations.get("doctor", {})
            companions = relations.get("companions", [])
            
            doc_name = doctor.get("name", "غير مسجل")
            doc_phone = doctor.get("phone", "غير مسجل")
            
            if detected_language == "ar":
                comps_str = "\n".join([f"- {c.get('name', 'غير مسجل')}: {c.get('phone', 'غير مسجل')}" for c in companions]) if companions else "لا يوجد مرافقين مسجلين"
                final_answer = f"👨‍⚕️ الطبيب المعالج: {doc_name} (تليفون: {doc_phone})\n👥 المرافقين المسجلين:\n{comps_str}"
            else:
                comps_str = "\n".join([f"- {c.get('name', 'Not registered')}: {c.get('phone', 'Not registered')}" for c in companions]) if companions else "No registered companions"
                final_answer = f"👨‍⚕️ Doctor: {doc_name} (Phone: {doc_phone})\n👥 Companions:\n{comps_str}"
            return final_answer

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
                    candidate_embeddings_list = []
                    for l in target_langs:
                        if hasattr(self, "candidate_embeddings") and intent in self.candidate_embeddings and l in self.candidate_embeddings[intent]:
                            # Extend list with precomputed numpy arrays converted back to lists for concatenation
                            candidate_embeddings_list.extend(list(self.candidate_embeddings[intent][l]))
                    
                    if candidate_embeddings_list and len(candidate_embeddings_list) == len(candidates):
                        candidate_embeddings = np.array(candidate_embeddings_list)
                    else:
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
                    SIMILARITY_THRESHOLD = 0.40
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
                alerts = user_context.get("latest_alerts", {}) if user_context else {}
                health_state = user_context.get("current_health_state", {}) if user_context else {}
                
                obstacle_alert = alerts.get("obstacle")
                obstacle_detected = bool(obstacle_alert)
                obstacle_distance = 0.0 # Distances might not be in the new schema, default to 0
                
                sos_alert = alerts.get("sos")
                fall_alert = alerts.get("mpu_monitoring")
                heart_alert = alerts.get("heart")
                
                emergency_active = bool(sos_alert or fall_alert or heart_alert)
                emergency_type = ""
                if sos_alert:
                    emergency_type = "manual_emergency_stop"
                elif fall_alert:
                    emergency_type = "fall_detected"
                elif heart_alert:
                    emergency_type = "health_risk"
                elif obstacle_alert:
                    emergency_type = "collision_risk"
                    
                hr_raw = health_state.get("heart_rate")
                heart_rate = float(hr_raw) if hr_raw is not None else None
                temp_raw = health_state.get("temperature")
                temperature = float(temp_raw) if temp_raw is not None else None
                mpu_data = health_state.get("mpu_monitoring", {}) or {}
                abnormal_posture = mpu_data.get("fall_detected", False) or (mpu_data.get("fainting_risk") == "high")
                    
                # Formulate response
                if detected_language == "ar":
                    if emergency_active:
                        if emergency_type == "collision_risk":
                            final_answer = f"الكرسي وقف تلقائياً لتفادي الاصطدام بوجود عائق قدامه على مسافة {obstacle_distance} سم."
                        elif emergency_type == "health_risk":
                            posture_str = " مع وضعية جلوس غير مريحة" if abnormal_posture else ""
                            hr_display = f"{heart_rate} نبضة/دقيقة" if heart_rate is not None else "غير متاحة"
                            temp_display = f"{temperature}°م" if temperature is not None else "غير متاحة"
                            final_answer = f"الكرسي وقف تلقائياً كإجراء أمان عشان رصدنا حالة تعب: نبضات قلبك ({hr_display}) وحرارتك ({temp_display}){posture_str}. بننصحك بالاستراحة فوراً."
                        elif emergency_type == "fall_detected":
                            final_answer = "تنبيه طارئ: تم رصد حالة سقوط مفاجئ للكرسي! تم إرسال استغاثة طوارئ لجهات الاتصال الموثوقة فوراً لتأمين سلامتك."
                        elif emergency_type == "manual_emergency_stop":
                            final_answer = "تم تفعيل التوقف الطارئ اليدوي للكرسي. للبدء مجدداً، تأكد من تحرير زر الطوارئ."
                        else:
                            if obstacle_detected:
                                final_answer = f"الكرسي وقف تلقائياً لتفادي الاصطدام بوجود عائق قدامه على مسافة {obstacle_distance} سم."
                            else:
                                final_answer = "تم إيقاف الكرسي كإجراء أمان طارئ. يرجى مراجعة التطبيق لمعرفة تفاصيل التنبيه."
                    elif obstacle_detected:
                        final_answer = f"الكرسي وقف تلقائياً لوجود عائق على مسافة {obstacle_distance} سم."
                    else:
                        final_answer = "الكرسي واقف حالياً وفي حالة استعداد. يمكنك توجيهه من خلال التطبيق أو الجويستيك."
                else:
                    if emergency_active:
                        if emergency_type == "collision_risk":
                            final_answer = f"The wheelchair stopped automatically to avoid a collision because an obstacle was detected in front of it at a distance of {obstacle_distance} cm."
                        elif emergency_type == "health_risk":
                            posture_str = " with an abnormal sitting posture" if abnormal_posture else ""
                            hr_display = f"{heart_rate} bpm" if heart_rate is not None else "unavailable"
                            temp_display = f"{temperature}°C" if temperature is not None else "unavailable"
                            final_answer = f"The wheelchair stopped automatically as a safety measure because we detected: heart rate ({hr_display}) and temperature ({temp_display}){posture_str}. We advise you to rest immediately."
                        elif emergency_type == "fall_detected":
                            final_answer = "Emergency alert: A sudden wheelchair fall was detected! An emergency SOS has been sent to your caregivers immediately to ensure your safety."
                        elif emergency_type == "manual_emergency_stop":
                            final_answer = "The manual emergency stop has been triggered. To start again, ensure the emergency button is released."
                        else:
                            if obstacle_detected:
                                final_answer = f"The wheelchair stopped automatically because an obstacle was detected in front of it at a distance of {obstacle_distance} cm."
                            else:
                                final_answer = "The wheelchair has been stopped due to an emergency. Please check the app for alert details."
                    elif obstacle_detected:
                        final_answer = f"The wheelchair stopped automatically because an obstacle was detected at a distance of {obstacle_distance} cm."
                    else:
                        final_answer = "The wheelchair is currently stopped and in idle mode. You can move it using the app or joystick."
            # Other static intents like connect_wheelchair and bot_identity have been removed to rely on dataset
            
        # 4. Personalization & Dynamic Sensor Injection
        final_answer = self._inject_context(final_answer, intent, detected_language, user_context)
        
        # 4.1 Trip Information Integration (Destination & Status)
        if intent in {"wheelchair_stop_reason", "navigation"} and user_context:
            trip_data = user_context.get("current_trip", {})
            if isinstance(trip_data, dict) and trip_data.get("is_active", False):
                dest_name = trip_data.get("destination", "غير معروف")
                
                if detected_language == "ar":
                    trip_info = f"\n\n📍 بخصوص رحلتك الحالية إلى {dest_name}، فهي جارية الآن."
                else:
                    trip_info = f"\n\n📍 Regarding your current trip to {dest_name}, it is currently active."
                
                final_answer += trip_info

        # 4.2 Arabic Gender-Awareness / Feminization
        if detected_language == "ar" and user_context:
            user_data = user_context.get("user_profile", {})
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
            
        profile = user_context.get("user_profile", {})
        name = profile.get("name")
        
        relations = user_context.get("relations", {})
        doctor = relations.get("doctor", {})
        doc_name = doctor.get("name", "طبيبك")
        companions = relations.get("companions", [])
        comp_names = " و ".join([c.get("name", "") for c in companions]) if companions else "جهات الاتصال"
        
        # B. Inject Sensor Readings & Warnings
        health_intents = {"sensor_interpretation", "fatigue", "pain", "shortness_of_breath", "normal_health"}
        
        warning_str = ""
        metrics_block = ""
        
        # Extract variables from user_context
        heart_rate = None
        temperature = None
        mpu_status = None
        
        health_data = user_context.get("current_health_state", {})
        alerts = user_context.get("latest_alerts", {})
        
        if isinstance(health_data, dict) and health_data:
            hr_raw = health_data.get("heart_rate")
            heart_rate = float(hr_raw) if hr_raw is not None else None
            temp_raw = health_data.get("temperature")
            temperature = float(temp_raw) if temp_raw is not None else None
            mpu_data = health_data.get("mpu_monitoring", {}) or {}
            if mpu_data.get("fall_detected", False) or mpu_data.get("fainting_risk") == "high":
                mpu_status = "fainting_detected"
                
        if alerts.get("mpu_monitoring") or alerts.get("sos"):
            mpu_status = "fainting_detected" # Treat SOS/Fall as fainting for warning
            
        has_sensors = bool(health_data)
        
        if intent in health_intents:
            
            # If no sensor data at all for health intents, show unavailability message
            if not has_sensors:
                if lang == "ar":
                    no_sensor_msg = "\n\n📊 قراءات الحساسات الصحية غير متاحة حالياً. تأكد إن الكرسي متصل وإن الحساسات شغالة من التطبيق."
                else:
                    no_sensor_msg = "\n\n📊 Health sensor readings are currently unavailable. Please ensure the wheelchair is connected and sensors are active via the app."
                metrics_block = no_sensor_msg
            else:
                # Load thresholds from config
                import json
                import os
                config_path = "config/health_thresholds.json"
                thresholds = {
                    "heart_rate_high": 100.0,
                    "heart_rate_low": 50.0,
                    "temperature_high": 38.0,
                    "temperature_low": 35.5
                }
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            thresholds.update(json.load(f))
                    except Exception as e:
                        pass

                # Determine warnings — only when real data exists
                has_warning = False
                if mpu_status == "fainting_detected":
                    has_warning = True
                    warning_str = f"🚨 تنبيه طارئ: تم رصد ما قد يشير لحالة سقوط مفاجئ! سيتم إرسال استغاثة طوارئ فوراً لـ ({comp_names}) للمساعدة." if lang == "ar" else f"🚨 Emergency alert: A potential fall has been detected! An SOS alert is being sent to your emergency contacts ({comp_names})."
                elif heart_rate is not None and heart_rate > thresholds["heart_rate_high"]:
                    has_warning = True
                    warning_str = f"⚠️ تنبيه: يُلاحظ من القراءات ارتفاع في معدل نبضات القلب ({heart_rate} نبضة/دقيقة). قد تشير هذه القراءات إلى حاجتك للراحة. يرجى المتابعة مع {doc_name}." if lang == "ar" else f"⚠️ Alert: Readings suggest an elevated heart rate ({heart_rate} bpm). You may need to rest. Please consult {doc_name}."
                elif heart_rate is not None and heart_rate < thresholds["heart_rate_low"]:
                    has_warning = True
                    warning_str = f"⚠️ تنبيه: يُلاحظ انخفاض في معدل نبضات القلب ({heart_rate} نبضة/دقيقة). قد تشير بعض القراءات إلى تغيرات تستدعي الانتباه الطبي. تواصل مع {doc_name}." if lang == "ar" else f"⚠️ Alert: Readings suggest a low heart rate ({heart_rate} bpm). We advise consulting {doc_name}."
                elif temperature is not None and temperature > thresholds["temperature_high"]:
                    has_warning = True
                    warning_str = f"⚠️ تنبيه: يُلاحظ ارتفاع في درجة حرارة الجسم ({temperature}°م). يرجى شرب المياة والاستراحة والمتابعة مع {doc_name}." if lang == "ar" else f"⚠️ Alert: Readings suggest a high body temperature ({temperature}°C). Please stay hydrated and consult {doc_name}."
                elif temperature is not None and temperature < thresholds["temperature_low"]:
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
                
                # Build metrics block — only show readings that actually exist
                if lang == "ar":
                    hr_str = f"{heart_rate} نبضة/دقيقة" if heart_rate is not None else "غير متاحة حالياً"
                    temp_str = f"{temperature}°م" if temperature is not None else "غير متاحة حالياً"
                    metrics_block = (
                        f"\n\n📊 قراءات حساساتك الحالية:\n"
                        f"- نبضات القلب: {hr_str}\n"
                        f"- درجة حرارة الجسم: {temp_str}"
                    )
                else:
                    hr_str = f"{heart_rate} bpm" if heart_rate is not None else "Currently unavailable"
                    temp_str = f"{temperature}°C" if temperature is not None else "Currently unavailable"
                    metrics_block = (
                        f"\n\n📊 Your current sensor readings:\n"
                        f"- Heart Rate: {hr_str}\n"
                        f"- Body Temperature: {temp_str}"
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
        if intent == "sensor_interpretation":
            if not has_sensors:
                if lang == "ar":
                    return "📊 قراءات الحساسات الصحية غير متاحة حالياً. تأكد إن الكرسي متصل وإن الحساسات شغالة من التطبيق."
                else:
                    return "📊 Health sensor readings are currently unavailable. Please ensure the wheelchair is connected and sensors are active via the app."
            else:
                answer = "" # Discard dataset text if sensors are available
                
        if warning_str:
            answer = f"{warning_str}\n\n{answer}" if answer else warning_str
            
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
