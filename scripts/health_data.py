# scripts/health_data.py

"""Health data templates and answer strings.

This module centralizes all health‑related templates and corresponding answer
messages used by the data‑generation script. Keeping the data separate from the
generation logic makes the code cleaner and allows other parts of the project
(e.g., the chatbot response generator) to import the same definitions.
"""

# 1. DIZZINESS

dizziness_templates = {
    "ar": [
        "حاسس بدوخة شديدة", "عندي دوار جامد ومش متزن", "حاسة بدوخة ومش قادرة أقف",
        "دماغي بتلف بيا أوي", "عندي دوار ومش قادرة أركز", "حاسس بالدوخة من الصبح",
        "دماغي تقيلة وبحس بدوخة لما أتحرك", "الدنيا بتلف بيا أعمل ايه؟", "دوار شديد ومعدتي تعباني",
        "بحس بدوخة لما أقوم من الكرسي", "حاسس إني هغمى عليا من الدوخة", "الدوخة مش راضية تروح",
        "عندي عدم اتزان ودوخة مستمرة", "دوار مفاجئ وصداع شديد", "مش قادر أصلب طولي بسبب الدوخة",
        "حاسس بدوران في راسي أعمل ايه؟", "كل ما أحرك راسي بحس بدوخة", "دوخة شديدة وزغللة في العين"
    ],
    "en": [
        "I feel very dizzy", "I have severe vertigo", "my head is spinning", "I feel lightheaded and unbalanced",
        "I am feeling dizzy and cannot stand up", "vertigo is killing me what should I do", "I feel like fainting because of dizziness",
        "my head feels heavy and dizzy", "having continuous dizziness since morning", "feel dizzy when I move my head",
        "unbalanced and dizzy help me", "severe dizziness and blurred vision", "I feel unsteady and lightheaded",
        "everything is spinning around me", "how to treat sudden dizziness", "vertigo and headache at the same time",
        "I feel extremely dizzy right now", "dizziness is not stopping"
    ],
    "mixed": [
        "please حاسس بدوخة", "my head بتلف جامد ومش قادر", "I feel dizzy ومش متزن خالص",
        "عندي vertigo شديد أعمل ايه", "help me حاسة بدوخة ومش قادرة", "feel lightheaded وتعبان جداً",
        "I have severe vertigo وصداع شديد", "please tell me ليه بحس بدوخة",
        "unbalanced وحاسس بدوران في راسي", "dizziness مستمرة معايا من الصبح",
        "feel dizzy لما بقوم من الكرسي", "الدنيا بتلف بيا and I feel lightheaded",
        "vertigo شديد وزغللة في العين", "I feel unsteady ومش قادر أقف"
    ]
}

dizziness_answer_ar = "الدوخة أو الدوار ممكن يحصلوا بسبب الجلوس الطويل، أو تغير مفاجئ في ضغط الدم، أو قلة شرب المية. من فضلك خد نفس عميق، استند كويس على الكرسي، واشرب مية. لو الدوخة مستمرة أو معاها زغللة، كلم حد من جهات الاتصال الموثوقة أو طبيبك فوراً."

dizziness_answer_en = "Dizziness or vertigo can occur due to prolonged sitting, sudden changes in blood pressure, or dehydration. Please take deep breaths, lean back safely in your chair, and drink some water. If the dizziness persists or is accompanied by blurred vision, contact your trusted contacts or doctor immediately."

# 2. FATIGUE

fatigue_templates = {
    "ar": [
        "حاسس بتعب شديد وإرهاق", "أنا مجهد جداً ومش قادر أتحرك", "عندي خمول تام وتعبان خالص",
        "جسمي مكسر وحاسس بإرهاق جامد", "مش قادرة أعمل أي نشاط من التعب", "عندي إرهاق مستمر بقالي أيام",
        "حاسس بضعف في عضلاتي وتعبان", "تعب إرهاق خمول شديد جداً", "حاسس بكسل وتعب ملوش سبب",
        "مش قادر أركز وتعبان أوي", "جسمي كله همدان وحاسس بضعف", "عندي إرهاق وتعب من أقل مجهد",
        "حاسة بتعب وهمدان شديد في جسمي", "الإرهاق مأثر عليا ومش قادر", "عايز أنام وتعبان طول اليوم",
        "حاسس بخمول فظيع ومش قادر أتحرك", "أنا منتهي من التعب والإرهاق", "عندي وهن عام في جسمي"
    ],
    "en": [
        "I feel extremely tired and fatigued", "I am totally exhausted and cannot move", "I have severe fatigue and weakness",
        "my body feels completely worn out", "I feel so fatigued and low on energy", "constant exhaustion for the past few days",
        "I feel fatigued from doing nothing", "muscle weakness and extreme fatigue", "I am tired all the time help me",
        "cannot concentrate due to severe fatigue", "my whole body is exhausted", "feeling fatigued and sluggish today",
        "I am drained of energy completely", "extreme fatigue and lack of sleep", "how to overcome constant tiredness",
        "I feel super exhausted right now", "fatigue is taking over my day"
    ],
    "mixed": [
        "feel exhausted خالص ومش قادر", "tired جداً وحاسس بخمول", "I have extreme fatigue وتعبان أوي",
        "please حسس بـ fatigue شديد", "my body feels worn out وتعبان", "low on energy ومش قادر أتحرك",
        "please tell me ليه حسس بـ fatigue", "exhausted وعندي همدان في جسمي", "muscle weakness وتعب شديد",
        "tired all the time ومجهد جداً", "feel sluggish وهمدان خالص", "extreme fatigue من أقل مجهد",
        "I am drained وتعبان جداً النهاردة", "feel super exhausted ومش طايق نفسي"
    ]
}

fatigue_answer_ar = "الإرهاق والخمول المستمر ممكن يكون بسبب قلة النوم، أو نقص السوائل، أو الجلوس في وضعية واحدة لفترة طويلة. بننصحك تاخد قسط كافي من الراحة، وتغير وضعية جلوسك بالكرسي، وتشرب سوائل كافية. لو التعب مستمر بدون سبب واضح، يفضل تستشير طبيبك."

fatigue_answer_en = "Constant fatigue and sluggishness can result from lack of sleep, dehydration, or sitting in one position for too long. We advise you to get sufficient rest, adjust your seating position, and drink plenty of fluids. If fatigue persists without an obvious reason, please consult your doctor."

# 3. PAIN

pain_templates = {
    "ar": [
        "عندي وجع شديد في ضهري", "حاسس بألم في كتفي ورقبتي", "جسمي بيوجعني أوي ومش مستريح",
        "عندي ألم مستمر من قعدة الكرسي", "كتفي الشمال بيوجعني جداً", "حاسة بوجع في عضمي وعضلاتي",
        "عندي ألم أسفل الظهر فظيع", "ضهري واجعني ومش قادر أقعد", "في ألم شديد في رقبتي أعمل ايه؟",
        "رقبتي بتوجعني أوي ومشدودة", "عندي وجع في دراعي الشمال", "ألم مستمر وصداع شديد في راسي",
        "حاسس بألم في كل حتة في جسمي", "عندي ألم في المفاصل وتعبان", "ضهري وكتفي بيوجعوني جداً",
        "مش قادر أتحمل الوجع ده", "عندي ألم حاد ومفاجئ في ضهري", "الوجع بيزيد لما بتحرك بالكرسي"
    ],
    "en": [
        "I have severe back pain", "my neck and shoulders hurt so much", "I feel constant pain from sitting too long",
        "I am in a lot of pain right now", "my left shoulder hurts badly", "I have terrible lower back pain",
        "my muscles and joints are aching", "constant neck pain help me", "I feel sharp pain in my back",
        "my body hurts and I cannot rest", "unbearable back pain what should I do", "having severe pain since yesterday",
        "my left arm is hurting a lot", "severe pain in joints and bones", "how to relieve sitting back pain",
        "I feel sharp pain when I move", "pain is too high today"
    ],
    "mixed": [
        "please عندي pain في ضهري", "my shoulder بيوجعني أوي ومش مستريح", "I feel severe pain وتعبان جداً",
        "عندي وجع شديد in my back", "my neck is tight وبيوجعني أوي", "unbearable pain ومش قادر أتحمل",
        "please tell me ازاي أخفف الـ pain", "having sharp pain في كتفي ورقبتي", "joints aching وتعبان خالص",
        "back pain فظيع ومش قادر أقعد", "my body hurts وتعبان أوي", "severe pain من قعدة الكرسي",
        "my left arm بيوجعني أوي pain", "feel sharp pain لما بتحرك بالكرسي"
    ]
}

pain_answer_ar = "آلام الظهر والرقبة شائعة بسبب الجلوس لفترات طويلة. يفضل تغير وضعية الكرسي وتجرب تمارين الإطالة البسيطة للكتفين والرقبة الموجودة في قسم التمارين بالتطبيق. لو الألم شديد جداً أو مفاجئ ومستمر، كلم جهات الاتصال الموثوقة واستشر طبيبك."

pain_answer_en = "Back and neck pain are common due to prolonged sitting. We recommend adjusting your chair's position and trying the simple shoulder and neck stretches available in the app's daily support section. If the pain is severe, sudden, or persistent, contact your trusted contacts and consult your doctor."

# 4. SHORTNESS OF BREATH

sob_templates = {
    "ar": [
        "مش عارف أخد نفسي", "عندي ضيق تنفس شديد ومش قادر", "حاسس بكتمة في صدري وخنقة",
        "نفسي ضيق أوي دلوقتي", "حاسة إني بتخنق ومش قادرة أتنفس", "عندي صعوبة في التنفس أعمل إيه؟",
        "حاسس بضيق تنفس وكتمة صدري", "مش قادر أتنفس كويس وتعبان", "كتمة في الصدر وصعوبة أخد النفس",
        "نفسي قصير أوي وبنهج جامد", "حاسس بضيق في صدري لما أتحرك", "عندي خنقة ونفسي ضيق من الصبح",
        "مش عارف أخد نفس عميق خالص", "عندي نهجان وضيق تنفس من أقل حركة", "حاسة بكتمة نفس شديدة وخايفة",
        "نفسي بيتقطع ومش قادر أصلب طولي", "ضيق تنفس وصداع شديد", "حاسس بضيق تنفس وضربات قلبي سريعة"
    ],
    "en": [
        "I cannot breathe properly", "I have severe shortness of breath", "my chest feels tight and I cannot breathe",
        "I am struggling to breathe help me", "shortness of breath is getting worse", "I feel like suffocating",
        "having difficulty in breathing right now", "my breathing is very shallow",
        "I cannot catch my breath", "chest tightness and difficulty breathing",
        "how to treat sudden shortness of breath", "I feel suffocated and scared"
    ]
}

sob_answer_ar = "ضيق التنفس ممكن يكون بسبب التوتر أو المجهود أو وضعية الجلوس. من فضلك اقعد في وضع مستقيم ومريح، خد شهيق بطيء وعميق من الأنف واحبسه ثانيتين وطلعه ببطء من الفم (تنفس الشفاه المضمومة). لو ضيق التنفس شديد جداً أو معاه ألم في الصدر، كلم الطوارئ أو جهات الاتصال فوراً."

sob_answer_en = "Shortness of breath can be caused by anxiety, exertion, or posture. Please sit upright in a comfortable position, take a slow, deep breath through your nose, hold it for two seconds, and exhale slowly through pursed lips. If the shortness of breath is severe or accompanied by chest pain, contact emergency services or your trusted contacts immediately."

# 5. NORMAL HEALTH

normal_templates = {
    "ar": [
        "صحتي عاملة ايه دلوقتي؟", "نبضي وحرارتي كويسين؟", "طمني على حالتي الصحية",
        "هل مؤشراتي الحيوية طبيعية؟", "قراءات جسمي كويسة ولا فيها مشكلة؟", "نبضات قلبي تمام؟",
        "درجة حرارتي كويسة دلوقتي؟", "طمني على نبض قلبي والحرارة", "هل صحتي كويسة النهاردة؟",
        "ممكن تشيك على المؤشرات الحيوية بتاعتي؟", "طمني قراءات الحساسات سليمة؟", "عايز أعرف حالتي الصحية عامة",
        "هل صحتي مستقرة دلوقتي؟", "نبضي سليم وحرارتي مضبوطة؟", "طمني على وضعي الصحي بالكامل",
        "قراءات جسمي كويسة؟", "هل أنا في أمان صحي دلوقتي؟", "طمني على مؤشراتي في الداشبورد"
    ],
    "en": [
        "How is my health status today?", "Are my heart rate and temperature normal?", "Is my health okay right now?",
        "Please check my vital signs", "Are my vital data within the normal range?", "Is my heart rate fine?",
        "How are my health readings looking?", "Tell me if my health is good today", "Are my dashboard readings normal?",
        "Is my temperature okay?", "Can you check my health status?", "Are my vital signs stable?",
        "Am I healthy right now?", "Check my heart rate and temp please", "Is my medical status fine?",
        "How is my overall health?", "Are there any health issues in my readings?"
    ],
    "mixed": [
        "طمني على my health دلوقتي", "Are my vital signs كويسين؟", "check my readings وطمني",
        "نبضي وحرارتي are they normal?", "my heart rate والحرارة كويسين؟", "please check my vital signs دلوقت",
        "dashboard readings كويسة ولا لأ؟", "Is my health status مستقر؟", "طمني my temperature طبيعية؟",
        "my vitals are they okay?", "check my heart rate وطمني", "health status بتاعي كويس؟",
        "Are my readings طبيعية وبخير؟", "check my health readings دلوقت"
    ]
}

normal_answer_ar = "مؤشراتك الحيوية ممتازة وتحت المراقبة المستمرة! نبضات القلب ودرجة الحرارة في المعدلات الطبيعية الآمنة، وجسمك في حالة مستقرة تماماً. استمر في الحفاظ على صحتك وشرب المية بانتظام."

normal_answer_en = "Your vital signs are excellent and under continuous monitoring! Your heart rate and body temperature are within the safe normal ranges, and your overall health status is completely stable. Keep staying active and drinking water regularly."

# 6. WHEELCHAIR USAGE MOVEMENT

wheelchair_movement_templates = {
    "ar": [
        "ازاي احرك الكرسي؟", "طريقة تحريك الكرسي", "ازاي الكرسي بيتحرك؟", "كيفية تحريك الكرسي بالـ joystick",
        "ازاي اتحرك بالكرسي", "طريقة حركة الكرسي", "عايز احرك الكرسي", "تحريك الكرسي", "ازاي امشي الكرسي",
        "طريقة تشغيل وحركة الكرسي", "طريقة التحكم في حركة الكرسي", "ازاي امشي بالكرسي", "طريقة المشي بالكرسي"
    ],
    "en": [
        "how do I move the wheelchair?", "how to move the chair", "how does the chair move?", "how to drive the wheelchair",
        "how to control wheelchair movement", "moving the chair", "how can I move the wheelchair?", "how to move using joystick"
    ],
    "mixed": [
        "ازاي احرك الكرسي using joystick", "طريقة تحريك الكرسي بالـ joystick", "ازاي الـ chair بيتحرك",
        "how to move الكرسي", "طريقة الـ movement للكرسي"
    ]
}

wheelchair_movement_answer_ar = "لو الكرسي مش بيتحرك أو بطيء، اتأكد الأول إن البطارية مش فاضية، وإن الكرسي مش على وضع الـ (Manual Freewheel)."

wheelchair_movement_answer_en = "If the chair is not moving or is slow, first ensure the battery is not empty and the chair is not in Manual Freewheel mode."
