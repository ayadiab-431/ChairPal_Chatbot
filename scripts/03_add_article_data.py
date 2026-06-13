import os
import json
import random

# Target file
DATASET_FILE = "chairpal_dataset.jsonl"

# 1. Adventurous Activities
adventurous_ar = [
    "ايه الأنشطة المغامرة اللي ممكن أعملها وأنا على الكرسي؟",
    "هل ينفع أركب منطاد أو أعمل باراشوت وأنا بستخدم كرسي متحرك؟",
    "قولي على مغامرات وأنشطة حماسية لذوي الاحتياجات الخاصة",
    "ايه هي الأنشطة الترفيهية المليانة مغامرة لمستخدمي الكراسي؟",
    "عايز أجرب حاجات فيها أدريلانين ومغامرة بالكرسي",
    "هل فيه رياضات خطرة أو أنشطة خارجية تناسب مستخدم الكرسي؟",
    "مغامرات بالكرسي المتحرك زي التزلج أو ركوب المنطاد",
    "عايزة أعمل مغامرات بالكرسي المتحرك تكسر الروتين",
    "ايه أنشطة الـ outdoor اللي فيها إثارة بالكرسي؟",
    "هل أصحاب الكراسي يقدروا يعملوا قفز مظلي أو تزلج مائي؟",
    "أنشطة مغامرة وأدرينالين للي بيستخدم كرسي متحرك",
    "ازاي أكون adventurous وأنا بستخدم كرسي؟",
    "أفكار لمغامرات خارجية بالكرسي المتحرك",
    "هل ممكن أركب منطاد أو أطير بالبراشوت بالكرسي؟",
    "رياضات إثارة ومغامرات ترفيهية بالكرسي المتحرك"
]
adventurous_en = [
    "What adventurous activities can I do as a wheelchair user?",
    "Can wheelchair users go ziplining, skydiving, or hot air ballooning?",
    "Are there extreme sports or outdoor adventures adapted for wheelchair users?",
    "Show me some thrill-seeking activities for people in wheelchairs.",
    "I want to experience adrenaline and adventure in my wheelchair.",
    "Can a wheelchair user go water skiing or snow skiing?",
    "Suggest some outdoor adventure ideas for wheelchair users.",
    "Are there accessible hot air balloon rides for disabled people?",
    "How does adaptive ziplining work for wheelchair users?",
    "Tell me about the iFly All Abilities program for skydiving.",
    "What are some exciting extreme sports for wheelchair users?",
    "I want to do adventurous things in my wheelchair, any tips?",
    "Can I go snow skiing or water skiing with a disability?",
    "Thrill-seeking and outdoor activities for wheelchair users.",
    "Is it safe to go ziplining or skydiving in a wheelchair?"
]
adventurous_mixed = [
    "عايز adventurous activities لمستخدمي الكراسي",
    "هل ينفع أعمل ziplining أو skydiving وأنا على الكرسي؟",
    "قولي على outdoor adventures لذوي الاحتياجات",
    "أفكار thrill-seeking activities بالكرسي المتحرك",
    "هل الـ hot air ballooning متاح لمستخدمي الكراسي؟",
    "عايز أجرب adrenaline adventures بالكرسي",
    "ممكن أعمل water skiing أو snow skiing بالكرسي؟",
    "أنشطة فيها adventure وإثارة للي بيستخدم wheelchair",
    "برنامج iFly All Abilities للـ skydiving ده عبارة عن ايه؟",
    "مغامرات outdoor بالكرسي المتحرك"
]
adventurous_ans_ar = "عشان تكسر الروتين وتعيش مغامرة مميزة، فيه أنشطة كتيرة اتعدلت عشان تناسب مستخدمي الكراسي المتحركة:\n1. ركوب المنطاد (Hot Air Ballooning): بعض الشركات بتوفر سلات مجهزة برامب مائل ومقاعد كهربائية قابلة للتعديل أو جوانب شفافة لرؤية واضحة.\n2. التزحلق على الحبل (Ziplining): زي منصة Gatorland في فلوريدا اللي بتوفر أحزمة أمان متكاملة للطيران فوق البحيرات بمساعدة فريق متخصص.\n3. القفز المظلي الداخلي (Skydiving): برنامج iFly All Abilities بيوفر تجربة الطيران الحر والشعور بخفة الوزن في الهواء.\n4. التزلج على الماء والجليد (Water & Snow Skiing): كراسي تزلج مخصصة ومثبتة بأحزمة أمان كاملة بمرافقة مدربين محترفين لحمايتك وتوجيهك."
adventurous_ans_en = "There are several exciting and adventurous activities adapted for wheelchair users:\n1. Hot Air Ballooning: Many companies offer adapted baskets with ramps, adjustable electric seats, or transparent sides for panoramic views.\n2. Ziplining: Accessible ziplining sites (like Gatorland in Florida) use specialized harnesses and assistants to secure you over lakes and valleys.\n3. Indoor Skydiving: Programs like iFly All Abilities allow you to experience weightlessness and float freely in a wind tunnel.\n4. Water & Snow Skiing: Adaptive sit-down skis with secure chest/arm straps allow you to glide on water or snow with the help of trained guides."

# 2. General Activities & Therapies
therapies_ar = [
    "ايه العلاجات الترفيهية المفيدة لذوي الإعاقة الحركية؟",
    "هل ألعاب الفيديو أو الـ Wii مفيدة للتأهيل؟",
    "فوائد علاج الموسيقى والحدائق لمستخدمي الكراسي",
    "ايه الأنشطة اللي بتساعد في تحسين الحركة والتوازن؟",
    "قولي على أنشطة بتساعد في تنشيط الدورة الدموية للجسم",
    "عايز أعرف فوائد العلاج المائي والسباحة لذوي الإعاقة",
    "ايه هي فكرة الـ music therapy وعلاج الموسيقى؟",
    "هل رعاية النباتات والحدائق بتفيد الصحة النفسية والجسدية؟",
    "أنشطة ترفيهية وعلاجية لمستخدمي الكرسي المتحرك",
    "ازاي الـ Wii Balance Board بتساعد في التأهيل الحركي؟",
    "علاجات وأنشطة ترفيهية للتغلب على الملل بالكرسي",
    "ايه هي فوائد السباحة لعلاج المشاكل العصبية والعمود الفقري؟",
    "أنشطة جماعية لذوي الاحتياجات الخاصة للاندماج الاجتماعي",
    "عايز أفكار لأنشطة ترفيهية في البيت أو برة بالكرسي",
    "فوائد العلاج بالحدائق والزراعة لمستخدمي الكراسي"
]
therapies_en = [
    "What recreational therapies are recommended for wheelchair users?",
    "How can music therapy, Wii therapy, or gardening help my health?",
    "What are the benefits of swimming or aquatic activities for physical disabilities?",
    "Suggest some rehabilitation activities to improve balance and coordination.",
    "Is playing video games like Wii Balance Board helpful for rehabilitation?",
    "What are the physical and psychological benefits of music therapy?",
    "How does gardening or therapeutic horticulture relieve stress?",
    "Why are aquatic activities useful for spinal cord injury rehabilitation?",
    "Recommend recreational activities for social integration of wheelchair users.",
    "What therapies help improve blood circulation and reduce joint pain?",
    "Are there any low-intensity activities to maintain muscle tone?",
    "Tell me about the benefits of therapeutic gardens.",
    "What can I do to stay active and burn calories in a wheelchair?",
    "How does swimming improve motor functions for neurological conditions?",
    "Recreational activities and therapies for physical disabilities."
]
therapies_mixed = [
    "فوائد الـ Wii therapy أو الـ music therapy لذوي الاحتياجات",
    "عايز أنشطة لتحسين الـ balance والتوازن بالكرسي",
    "هل الـ gardening أو علاج الحدائق بيقلل الـ stress؟",
    "فوائد السباحة والـ aquatic activities للتأهيل",
    "عايز ألعاب فيديو للـ rehabilitation والتأهيل الحركي",
    "تأثير الـ music therapy على الحالة النفسية والـ self-esteem",
    "أنشطة للمحافظة على الـ muscle tone بالكرسي",
    "علاجات ترفيهية زي الـ Wii والـ Hydrotherapy",
    "فوائد الـ swimming pool للمشاكل العصبية بالكرسي",
    "أنشطة ترفيهية للـ social integration لذوي الإعاقة"
]
therapies_ans_ar = "هناك أنشطة علاجية وترفيهية ممتازة لتحسين الحركة والحالة النفسية:\n1. العلاج بالموسيقى: يساعد في تحسين الثقة بالنفس، تقليل الألم، وتطوير المهارات الحركية والتوافق من خلال الرقص أو العزف.\n2. العلاج بجهاز الـ Wii: ألعاب الفيديو التي تعتمد على منصات مثل Wii Balance Board تحسن توازن المفاصل، التوافق البصري الحركي، وردود الأفعال تحت إشراف طبيعي.\n3. العلاج بالحدائق (Gardening): العناية بالنباتات تقلل التوتر والإجهاد وتقوي العضلات والروابط النفسية مع الطبيعة.\n4. الأنشطة المائية (السباحة والآكوا جيم): الماء يقلل الجاذبية ويساعد في الاسترخاء وتأهيل إصابات العمود الفقري والجهاز العصبي."
therapies_ans_en = "Recreational therapies offer great physical and cognitive benefits for wheelchair users:\n1. Music Therapy: Enhances self-esteem, reduces pain, and develops motor functions through movement, instrument playing, and coordination.\n2. Wii Therapy: Interactive games using tools like the Wii Balance Board improve joint mobility, balance, hand-eye coordination, and reflexes under therapist supervision.\n3. Horticultural Therapy (Gardening): Caring for plants reduces stress, relieves tension, and fosters emotional connections with nature.\n4. Aquatic Activities (Swimming/Aqua-gym): Water reduces weight-bearing pressure and improves motor skills, making it ideal for neurological and spinal rehabilitation."

# 3. Yoga Poses
yoga_ar = [
    "هي اليوجا حلوة؟",
    "إزاي أعمل يوجا وأنا على الكرسي المتحرك؟",
    "تمارين يوجا مخصصة لمستخدمي الكراسي",
    "قولي على وضعيات يوجا بالكرسي",
    "ازاي أعمل وضعية القطة بالكرسي؟",
    "وضعية النسر يوجا بالكرسي بتتعمل ازاي؟",
    "عايز تمارين إطالة للورك والساق بالكرسي",
    "وضعية الانحناء للأمام والالتواء في اليوجا للكرسي",
    "ما هي فوائد اليوجا لمستخدمي الكراسي المتحركة؟",
    "يوجا الكراسي المتحركة والوضعيات المناسبة لها",
    "تمارين يوجا مريحة لتقليل آلام الظهر ورقبتي",
    "ازاي أعمل الـ Twist والـ Forward Bend بالكرسي؟",
    "عايزة تمارين تنفس يوجا وأنا قاعدة على الكرسي",
    "هل اليوجا بتساعد في تقوية العضلات وتسهيل الانتقال للكرسي؟",
    "إرشادات وضعيات اليوجا لذوي الإعاقة الحركية"
]
yoga_en = [
    "Is yoga good for wheelchair users?",
    "How to practice yoga in a wheelchair?",
    "What are the best adaptive yoga poses?",
    "Explain some wheelchair-friendly yoga stretches.",
    "How to do the Cat Pose in a wheelchair?",
    "Explain the Eagle Pose for wheelchair users.",
    "How to perform the Hip Stretch or Forward Bend?",
    "Tell me about the Twist and Leg Stretch yoga poses.",
    "What are the physical and mental benefits of adaptive yoga?",
    "Can you suggest some seated yoga poses for chronic pain?",
    "Seated yoga routine for flexibility and relaxation.",
    "Seated yoga exercises for wheelchair users.",
    "How does yoga help with wheelchair transfers and bone health?",
    "Step-by-step guide for wheelchair yoga poses.",
    "Seated stretches and breathing exercises in yoga."
]
yoga_mixed = [
    "هي الـ yoga حلوة للـ wheelchair users؟",
    "عايز وضعيات yoga بالكرسي زي Cat pose أو Twist",
    "ازاي أعمل الـ Eagle Pose وأنا على الكرسي؟",
    "تمارين الـ Hip Stretch والـ Leg Stretch بالكرسي",
    "فوائد الـ adaptive yoga لتقليل الألم والـ pain",
    " seated yoga routine للمبتدئين بالكرسي",
    "طريقة الـ Forward Bend في يوجا الكراسي",
    "تمارين الـ breathing واليوجا وأنا قاعد على الكرسي",
    "وضعيات الـ yoga اللي بتساعد في الـ flexibility",
    "يوجا بالكرسي لتقوية الـ muscles والظهر"
]
yoga_ans_ar = "اليوجا ممتازة جداً لمستخدمي الكراسي؛ فهي تقلل الإجهاد، تحسن القوة والمرونة، وتنشط الدورة الدموية. إليك أهم الوضعيات بالكرسي:\n1. وضعية القطة (Cat Pose): استند بيدك على الفخذين، انفخ صدرك شهيقاً، ثم ازفر ببطء مع إمالة الرأس للأسفل وتقويس الظهر للأمام.\n2. وضعية النسر (Eagle Pose): ارفع ذراعيك مثنيين 90 درجة، ثم اعكس ذراعيك فوق بعضهما عند المرفقين مع تلامس ظهر اليدين لمدة 20-30 ثانية.\n3. إطالة الورك (Hip Stretch): ارفع إحدى ساقيك لتتقاطع فوق الأخرى (وضعية رجل على رجل)، وانحنِ للأمام قليلاً مع التنفس بعمق.\n4. الانحناء للأمام (Forward Bend): افرد ظهرك جيداً، ثم انحنِ للأمام من الخصر ببطء مع الإمساك بجوانب الكرسي للدعم.\n5. الالتواء (The Twist): ضع يدك اليمنى على فخذك الأيسر، واستدر برأسك وجذعك للنظر خلف كتفك الأيسر، وكرر للجانب الآخر.\n6. إطالة الساق (Leg Stretch): افرد ظهرك، ارفع ركبتك للأعلى ببطء ممسكاً بساقك أو قصبتك، ثم بدّل للساق الأخرى."
yoga_ans_en = "Yoga is highly beneficial for wheelchair users, improving strength, flexibility, blood circulation, and sleep while reducing chronic pain. Here are 6 adaptive poses:\n1. The Cat Pose: Place your hands on your thighs, inhale, and exhale slowly while arching your back and dropping your chin.\n2. The Eagle Pose: Lift your arms bent at 90 degrees, cross them at the elbows, resting the backs of your hands together for 20-30 seconds.\n3. Hip Stretch: Cross one leg over the other, lean forward slightly from your hips while holding the chair, and breathe deeply.\n4. Forward Bend: Sit tall, exhale and bend forward from your waist while holding onto your wheelchair for support.\n5. The Twist: Rest your right hand on your left leg, exhale and turn to look over your left shoulder, using the armrest for support.\n6. Leg Stretch: Wrap your hands around your shin, lift your knee to a comfortable height, hold for 5 breaths, and repeat on the other side."

# 4. Wheelchair Posture & Configuration
posture_ar = [
    "ازاي أظبط قعدتي على الكرسي المتحرك؟",
    "أهمية الوضعية الصحيحة والجلوس السليم بالكرسي",
    "تأثير مسند القدم ومسند الظهر على الحركة",
    "ازاي أظبط مسند الذراع بالكرسي المتحرك؟",
    "قعدتي مش مريحة على الكرسي أعمل ايه؟",
    "فوائد الجلوس الصحيح ومخاطر الجلوس الغلط بالكرسي",
    "ازاي أوزع وزني صح على الكرسي لتجنب قرح الفراش؟",
    "طريقة ظبط ارتفاع المقعد ومسند الظهر بالكرسي",
    "الجلوس الصحيح لتجنب آلام الكتف والرقبة بالكرسي",
    "ازاي أخفف الضغط على الظهر والأرداف بالكرسي؟",
    "مسند القدم لازم يكون بزاوية كام للركبة؟",
    "المقعد بتاعي واسع أو ضيق زيادة أعمل ايه؟",
    "طول مقعد الكرسي المثالي بيتحسب ازاي؟",
    "تعديل زوايا الكرسي للحصول على أفضل حركة ودفع",
    "أهمية ساند الذراع في تقليل إجهاد الرقبة والكتفين"
]
posture_en = [
    "How to adjust my seating posture in the wheelchair?",
    "Why is correct wheelchair posture important?",
    "What are the rules for adjusting seat height, footrest, and armrest?",
    "My wheelchair seating is uncomfortable, what should I do?",
    "How to relieve pressure on my spine and buttocks in a wheelchair?",
    "What angle should my knees and ankles be on the footrest?",
    "How does wheelchair posture affect shoulder pain and propulsion?",
    "How do I determine the correct seat length and width?",
    "How to adjust the armrest height for neck and shoulder comfort?",
    "What is the role of the backrest in stabilizing my body?",
    "Biomechanical factors in wheelchair functionality and sitting.",
    "Tips to avoid sliding forward in my wheelchair seat.",
    "Why should my elbows be supported at a 90-degree angle?",
    " seeting posture guidelines for manual and electric wheelchairs.",
    "How to prevent pressure sores through correct wheelchair seating."
]
posture_mixed = [
    "ازاي أظبط الـ posture ومسند الظهر بالكرسي؟",
    "أهمية الجلوس السليم لتجنب الـ pressure sores وقرح الفراش",
    "ظبط زاوية الـ footrest ومسند القدم بالكرسي",
    "ازاي المقعد أو الـ seat بيأثر على الـ stability والثبات؟",
    "مسافة الـ popliteal fossa وخلف الركبة المفروض تكون كام؟",
    "عايز أظبط الـ armrest ومسند الذراع عشان رقبتي بتوجعني",
    "قواعد الـ wheelchair posture الصحيحة لتفادي الـ back pain",
    "تعديل الـ seat length والـ width للكرسي",
    "أثر الجلوس الغلط على الـ propulsion ودفع العجلات",
    "ظبط زوايا الكرسي للحفاظ على الـ spine والعمود الفقري"
]
posture_ans_ar = "الوضعية الصحيحة للجلوس تحميك من آلام الظهر والرقبة وتسهل دفع الكرسي. لضبط الكرسي:\n1. المقعد (Seat): يجب ألا يكون واسعاً جداً (يسبب جلوساً غير متماثل) أو طويلاً جداً (يضغط خلف الركبة). الطول المثالي يترك مسافة إصبعين بين حافة المقعد وخلف ركبتك.\n2. مسند القدم (Footrest): يجب أن يكون بزاوية 90 درجة لتريح الركبة والكاحل. لو كان منخفضاً يغير وضع الورك، ولو مرتفعاً يضغط على الأرداف.\n3. مسند الظهر (Backrest): يثبت الجزء العلوي من الجسم لتسهيل حركة الذراعين وتخفيف الحمل.\n4. مسند الذراع (Armrest): يسند الكوعين بزاوية 90 درجة لإراحة عضلات الرقبة والكتفين.\n* ملحوظة: عند أخذ المقاسات، اجلس على سطح صلب بزاوية 90 درجة للركبة والحوض، ويُفضل استشارة فني أطراف صناعية."
posture_ans_en = "Correct wheelchair posture reduces pain, prevents strain, and optimizes propulsion. Adjust key parts as follows:\n1. Seat: Avoid seats that are too wide or too long. The optimal seat length leaves a two-finger gap between the seat edge and the back of your knee.\n2. Footrest: Position it to support knees and ankles at a 90-degree angle. If it's too low, it shifts the hips; if too high, it creates pressure on your buttocks.\n3. Backrest Height: Stabilizes your upper body, which is essential for arm mobility and comfort.\n4. Armrest: Keep elbows supported at 90 degrees to rest your neck and shoulder muscles.\n* Measurement Tip: Take measurements sitting on a flat surface with pelvic, knee, and ankle angles at 90 degrees, and consult a professional technician."

# 5. Seating Measurements
measurements_ar = [
    "ازاي أقيس مقاسات الكرسي عشان قعدتي تبقى صح؟",
    "طريقة أخذ المقاسات لتصميم أو شراء كرسي متحرك",
    "المقاسات الصحيحة لتفصيل كرسي متحرك يناسبني",
    "ازاي أقيس طول وعرض المقعد وعمق الركبة؟",
    "نصائح عند قياس أبعاد الكرسي لذوي الإعاقة",
    "ازاي أقيس مقاس الحوض والفخذين للكرسي؟",
    "خطوات أخذ مقاسات الساقين والظهر للكرسي",
    "عايز أشتري كرسي جديد، أقيس مقاساتي ازاي؟",
    "هل لازم فني متخصص ياخد مقاسات الكرسي؟",
    "ازاي أقيس مسافة خلف الركبة ومسند القدم؟",
    "أخذ القياسات المناسبة للكرسي اليدوي أو الكهربائي",
    "مقاسات الكرسي المتحرك المناسبة لوزني وطولي",
    "نصائح الفحص البدني وقياس أبعاد الكرسي",
    "ازاي أخد مقاس كتفي والظهر للكرسي؟",
    "خطوات قياس الكرسي على سطح صلب"
]
measurements_en = [
    "How do I take measurements for a wheelchair configuration?",
    "What is the correct way to measure my body for a wheelchair?",
    "How to measure seat width, depth, and backrest height?",
    "Steps for taking wheelchair measurements on a flat surface.",
    "How to measure thigh length and calf height for a wheelchair?",
    "Why is taking accurate wheelchair measurements important?",
    "Should I consult an orthopaedic technician for wheelchair sizing?",
    "What measurements are needed to buy a new manual or power wheelchair?",
    "How to measure pelvic and knee angles for wheelchair fit?",
    "Seating measurement guide for disabled adults.",
    "Measuring seat height and footrest clearance correctly.",
    "How to measure back height for upper body stability?",
    "Guide to taking personal measurements for a custom wheelchair.",
    "How does wearing regular clothes affect wheelchair measurements?",
    "What tools are needed to measure for a custom wheelchair size?"
]
measurements_mixed = [
    "طريقة أخذ الـ measurements للكرسي المتحرك",
    "ازاي أقيس الـ seat width والـ seat depth للكرسي؟",
    "خطوات الـ physical assessment لقياس الكرسي",
    "مقاسات الـ wheelchair المناسبة لجسمي وطولي",
    "ازاي أقيس الـ popliteal distance وخلف الركبة؟",
    "نصائح لقياس الـ backrest height ومسند الظهر",
    "هل محتاج orthopaedic technician عشان مقاسات الكرسي؟",
    "طريقة قياس الـ thigh length والـ calf height للكرسي",
    "أخذ مقاسات الكرسي على hard surface وسطح صلب",
    "أبعاد الـ wheelchair المناسبة لوزني وطولي"
]
measurements_ans_ar = "أخذ المقاسات الصحيحة أمر بالغ الأهمية لضمان راحتك واستقلاليتك. إليك الخطوات الأساسية:\n1. الجلوس على سطح صلب: مع استخدام وسادة بسمك لا يزيد عن 2-3 سم للتأكد من دقة القياس.\n2. زوايا الجسم: يجب أن تكون زوايا الحوض والركبتين والكاحلين في وضع قائم (90 درجة تقريباً).\n3. عرض المقعد: يقاس المسافة بين أوسع نقطتين في الوركين، مع ترك مسافة بسيطة للحركة والملابس.\n4. عمق المقعد: يقاس من خلف الحوض إلى خلف الركبة، ويُطرح منه حوالي إصبعين (5 سم) لتجنب الضغط على الأوعية الدموية خلف الركبة.\n5. ارتفاع مسند الظهر والقدمين: يقاس بدقة لتثبيت الجذع وتوزيع الوزن بشكل متساوٍ.\n* يُنصح بزيارة أخصائي أطراف صناعية أو فني مؤهل لتقييم حالتك وأخذ القياسات بدقة."
measurements_ans_en = "Accurate wheelchair measurements are essential to ensure independence and comfort. Here is a guide to taking them:\n1. Sit on a Flat, Hard Surface: Use minimal cushioning (2-3 cm) to get an accurate representation of your sitting profile.\n2. Body Alignment: Ensure your pelvis, knees, and ankles are positioned close to a 90-degree angle.\n3. Seat Width: Measure the widest part of your hips/thighs and add a small margin for clothing and comfort.\n4. Seat Depth: Measure from the back of the pelvis to the back of the knee, subtracting about 2 inches (5 cm) to avoid pressure in the popliteal area.\n5. Footrest & Backrest Height: Measure from the heel to the back of the knee to determine footrest height, and measure your back to determine the ideal support height.\n* Recommendation: Visit a qualified orthopaedic technician to perform a physical assessment and compile the exact wheelchair configuration."

# 6. Nutrition Tips
nutrition_ar = [
    "ايه النصائح الغذائية لمستخدمي الكراسي المتحركة؟",
    "ازاي أتجنب زيادة الوزن والتهابات المسالك البولية بالكرسي؟",
    "أهمية الكالسيوم والبروتين لمستخدمي الكراسي",
    "أكل ايه عشان أحافظ على صحتي وأنا بستخدم كرسي؟",
    "نصائح للتخسيس وتجنب زيادة الوزن لمستخدم الكرسي",
    "عايز أكل صحي يقوي العظام ويمنع هشاشة العظام بالكرسي",
    "مصادر فيتامين د3 والكالسيوم للي مش بيمشي على رجله",
    "فوائد البروتين لالتئام الجروح وقرح الفراش بالكرسي",
    "كمية المية المفروض يشربها مستخدم الكرسي في اليوم",
    "ازاي أحمي نفسي من التهابات البول والقسطرة بالكرسي؟",
    "نظام غذائي لمستخدمي الكراسي المتحركة لزيادة الطاقة",
    "علاقة قلة شرب المية بالتهابات الكلى والبول بالكرسي",
    "أكلات غنية بالكالسيوم وفيتامين د ومفيدة للعظام",
    "كيفية الحفاظ على وزن مثالي وصحة الهضم بالكرسي",
    "نصائح غذائية للوقاية من تدهور الجلد وقرح الجلوس"
]
nutrition_en = [
    "What are the best nutrition tips for wheelchair users?",
    "How to prevent UTIs and manage weight in a wheelchair?",
    "Why do wheelchair users need more calcium, vitamin D3, and protein?",
    "How much water should a wheelchair user drink?",
    "Diet and weight management tips for disabled individuals.",
    "What foods are high in calcium and vitamin D for bone health?",
    "How does protein prevent pressure sores and skin breakdown?",
    "Why are wheelchair users at higher risk for urinary tract infections?",
    "What is the connection between hydration and catheter-related UTIs?",
    "How to reduce calorie intake when using a wheelchair?",
    "Pro nutrition tips for people with mobility impairments.",
    "Best foods to maintain bone mass and avoid osteoporosis.",
    "How does drinking water improve digestion and kidney health?",
    "Recommended daily protein and water intake for wheelchair users.",
    "How to plan a healthy meal when sitting all day."
]
nutrition_mixed = [
    "نصائح للـ nutrition والدايت لمستخدمي الكراسي",
    "ازاي أحمي نفسي من الـ UTIs والتهابات المسالك؟",
    "أهمية الـ calcium والـ vitamin D3 لمنع هشاشة العظام",
    "فوائد الـ protein لالتئام الـ pressure sores وقرح الفراش",
    "حساب الـ calorie intake لمنع زيادة الوزن بالكرسي",
    "أكلات غنية بالـ calcium وفيتامين د3",
    "نصائح للـ hydration وشرب المية لمستخدمي الكراسي",
    "علاقة القسطرة والـ catheter بالتهابات البول والمسالك",
    "دايت صحي لتقوية الـ bone mass والعظام بالكرسي",
    "نظام غذائي متكامل لمستخدمي الـ wheelchair"
]
nutrition_ans_ar = "التغذية السليمة تحميك من زيادة الوزن ومشاكل الهضم وقرح الفراش. إليك أهم النصائح الغذائية:\n1. حساب السعرات: بما أن الحركة أقل، احرص على تناول سعرات حرارية أقل لتجنب زيادة الوزن.\n2. الكالسيوم وفيتامين د3: لتقوية العظام وتجنب هشاشة العظام نتيجة عدم تحميل الوزن. تناول الألبان، السبانخ، التونة، والبيض.\n3. البروتين: ضروري جداً للحفاظ على سلامة الجلد وحمايتك من قرح الفراش، ويساعد في التئام الجروح.\n4. شرب المية: اشرب كميات كافية من الماء يومياً لحماية الكلى والمثانة وغسل البكتيريا، مما يقلل خطر التهابات المسالك البولية (UTIs) الناتجة عن القسطرة."
nutrition_ans_en = "Proper nutrition is key to weight management, preventing UTIs, and skin health for wheelchair users:\n1. Manage Calories: Since energy expenditure is lower, regulate calorie intake to prevent weight gain.\n2. Calcium & Vitamin D3: Critical to prevent osteoporosis from lack of weight-bearing. Eat dairy, spinach, salmon, and egg yolks.\n3. Protein: Essential for maintaining skin integrity, preventing pressure sores, and accelerating wound healing.\n4. Hydration: Drink plenty of water to flush bacteria from the bladder. This is crucial for preventing Urinary Tract Infections (UTIs), especially for those using catheters."

# 7. Sleep Importance
sleep_ar = [
    "عندي مشاكل في النوم، انصحني أنام كويس ازاي؟",
    "أهمية النوم لذوي الاحتياجات الخاصة ومستخدمي الكراسي",
    "ازاي أحسن جودة نومي وأتغلب على الأرق؟",
    "أثر قلة النوم على الألم والتعب بالكرسي",
    "قولي على 5 نصائح للنوم العميق والمريح",
    "عايز حلول للأرق وقلة النوم لذوي الاحتياجات",
    "هل قلة النوم بتزود الإحساس بالألم والتعب؟",
    "نصائح للتخلص من الأرق قبل النوم بساعة بالكرسي",
    "ازاي أنظم مواعيد نومي واستيقاظي في الويكيند؟",
    "تأثير الضوء الأزرق والموبايل على جودة النوم",
    "ازاي زر الغفوة أو الـ snooze بيضر جودة النوم؟",
    "ساعات النوم المثالية لمستخدم الكرسي كام ساعة؟",
    "علاقة النوم بالصحة النفسية والقدرة على التركيز",
    "نصائح لنوم متواصل وعميق لذوي الإعاقة الحركية",
    "طرق تحسين جودة النوم وعلاج مشاكل النوم بالكرسي"
]
sleep_en = [
    "How can I improve my sleep as a wheelchair user?",
    "Why is sleep so important for people with disabilities?",
    "Tips to overcome insomnia and get better rest.",
    "How does lack of sleep affect chronic pain and fatigue?",
    "Give me 5 tips for a better night's sleep.",
    "Why do disabled individuals need more sleep than average?",
    "How to manage my sleep schedule on weekends?",
    "Why is the snooze button bad for REM sleep?",
    "How does blue light from phones affect sleep quality?",
    "Seated daily routine to prepare for bed.",
    "What is the recommended sleep duration for disabled adults?",
    "How does quality rest enhance cognitive and physical functions?",
    "Help with insomnia and sleep deprivation in wheelchairs.",
    "How to associate your bed only with sleeping?",
    "Tips for deep, replenishing sleep with a disability."
]
sleep_mixed = [
    "عايز نصائح للـ sleep عشان عندي أرق",
    "تأثير قلة النوم على الـ chronic pain والألم",
    "أهمية الـ sleep لذوي الإعاقة الحركية",
    "نصائح للتغلب على الـ insomnia والأرق بالكرسي",
    "تأثير الـ blue light والمنبه على الـ REM sleep",
    "ساعات الـ sleep المثالية لمستخدمي الكراسي",
    "ازاي أظبط الـ sleep schedule في الـ weekend؟",
    "علاقة النوم بالـ mental health والتركيز بالنهار",
    "5 نصائح للـ deep sleep والنوم المريح",
    "نصائح لنوم هادئ والتوقف عن الـ snooze"
]
sleep_ans_ar = "النوم الكافي (7 إلى 9 ساعات) ضروري جداً لصحتك الجسدية والنفسية، ويساعدك في تحمل الآلام المزمنة. لتحسين نومك:\n1. ابعد عن الضوء الأزرق: اغلق التلفزيون والموبايل قبل النوم بساعة على الأقل.\n2. اربط السرير بالنوم: لو واجهت صعوبة في النوم، قم من السرير وافعل شيئاً هادئاً حتى تشعر بالنعاس.\n3. تجنب زر الغفوة (Snooze): استيقظ فور رنين المنبه لتجنب تقطيع مرحلة النوم العميق (REM).\n4. الالتزام بالمواعيد: حافظ على موعد نوم واستيقاظ ثابت حتى في عطلة نهاية الأسبوع."
sleep_ans_en = "Quality sleep (7-9 hours) is vital for physical/mental health and helps manage chronic pain. To improve your sleep:\n1. Limit Blue Light: Avoid screens (phones, TV, computers) for at least one hour before bed.\n2. Associate Bed with Sleep: If you can't fall asleep, get out of bed and do a quiet activity until you feel tired.\n3. Avoid Snooze: Get up as soon as your alarm rings to prevent disrupting your deep REM sleep.\n4. Maintain Consistency: Keep the same sleep and wake times even on weekends. Take short naps to catch up instead."

# 8. Home Retrofitting
home_ar = [
    "ازاي أجهز البيت عشان يبقى مناسب للكرسي المتحرك؟",
    "تجهيز الحمام والمطبخ لذوي الاحتياجات الخاصة بالمنزل",
    "ايه هي التعديلات المنزلية المناسبة للكرسي الكهربائي؟",
    "هل فيه دعم مالي أو تأمين لتجهيز المنزل للكرسي؟",
    "نصائح لتوسيع الأبواب وتسهيل حركة الكرسي بالبيت",
    "ازاي أعمل حمام آمن ومناسب لمستخدم الكرسي المتحرك؟",
    "ظبط ارتفاع المطبخ والرخامة لمستخدم الكرسي المتحرك",
    "مواصفات الرامب أو المنحدر المناسب لمدخل البيت",
    "استخدام السمارت هوم والتحكم الصوتي لتسهيل الحركة بالمنزل",
    "برنامج EASE ودعم الـ HDB لتجهيز البيت بالكامل",
    "تعديل غرفة النوم والسرير لتسهيل الانتقال للكرسي",
    "كيفية حماية وتأمين تعديلات المنزل عبر شركات التأمين",
    "شروط تركيب مقابض الحمام وبلاط مانع للانزلاق",
    "نصائح التعديل المنزلي لكبار السن ومستخدمي الكراسي",
    "تجهيز مسارات واضحة وعريضة للكرسي داخل الشقة"
]
home_en = [
    "How do I make my home accessible for a wheelchair?",
    "What are the best home modifications for disabled people?",
    "How to retrofit bathroom and kitchen for wheelchair users?",
    "Is there financial aid or insurance covering home retrofitting?",
    "How wide should doorways and walkways be for a wheelchair?",
    "Tips for installing grab bars and walk-in showers.",
    "What is the recommended height for wheelchair-accessible countertops?",
    "How can smart home technology assist disabled residents?",
    "Explain the EASE program and HDB subsidies in Singapore.",
    "What insurance covers home modifications for permanent disability?",
    "How to design an accessible bedroom and adjustable bed?",
    "Pros and cons of installing entryway ramps vs widening doors.",
    "How to prevent falls in the home for elderly wheelchair users?",
    "Guidelines for accessible home design and renovation.",
    "How does HomeCare or SeniorCare insurance protect accessibility upgrades?"
]
home_mixed = [
    "تجهيز البيت للـ wheelchair والكرسي المتحرك",
    "دعم الـ HDB أو برنامج EASE لتجهيز المنزل",
    "تجهيز الحمام وعمل walk-in shower للكرسي",
    "ارتفاع الـ countertop والرخامة في المطبخ لمستخدم الكرسي",
    "استخدام الـ smart home والتحكم الصوتي بالبيت لمساعدتي",
    "هل الـ insurance زي PA Care Plus Enhanced بيغطي تعديل البيت؟",
    "أبعاد الـ doorways والـ walkways المناسبة للكرسي بالمنزل",
    "تركيب الـ grab bars وبلاط مانع للانزلاق بالـ bathroom",
    "تمويل الـ retrofitting وتجهيز المنزل لذوي الاحتياجات",
    "تجهيز الـ bedroom وتعديل السرير للكرسي"
]
home_ans_ar = "تجهيز البيت بيحميك من مخاطر السقوط وبيساعدك تتحرك بحرية واستقلالية. أهم التعديلات:\n1. المداخل والممرات: تركيب رامبات مائلة وتوسيع الأبواب والممرات لـ 1.2 متر على الأقل لتسهيل مرور الكرسي. \n2. الحمام: تركيب مقابض جدارية (Grab Bars)، استخدام بلاط مانع للانزلاق، وعمل كابينة استحمام بدون عتبات (Walk-In Shower).\n3. المطبخ: خفض مستوى الرخامة لـ 86 سم لتناسب الجلوس، واستخدام أرفف سحب داخلية وأجهزة تحكم آمنة.\n4. التكنولوجيا الذكية: الإضاءة التلقائية بالحساسات والتحكم الصوتي بالأجهزة (Google/Alexa).\n* في سنغافورة، يدعم برنامج EASE ووزارة الإسكان (HDB) هذه التعديلات بنسبة تصل لـ 95%، وتأمين مثل PA Care Plus Enhanced يغطي تكاليف تعديل المنزل للإعاقة الحركية."
home_ans_en = "Retrofitting your home enhances safety, independence, and comfort. Key modifications include:\n1. Entryways & Hallways: Install ramps and widen doors/hallways to at least 1.2 meters. Use flat thresholds.\n2. Bathroom: Install walk-in curb-less showers, slip-resistant tiles, grab bars near the toilet/shower, and raised toilet seats.\n3. Kitchen: Lower countertops to around 34 inches (86 cm), use pull-out drawers, lazy susans, and accessible side-opening appliances.\n4. Smart Home: Voice-activated controls (Alexa/Google), automated lighting, and remote health/security monitoring.\n* Subsidies: Programs like HDB EASE in Singapore provide up to 95% subsidies. Insurance policies (e.g., Liberty PA Care Plus Enhanced) also cover home modification costs."

# 9. Paraplegia
para_ar = [
    "ما هو الشلل النصفي السفلي؟",
    "عندي شلل نصفي سفلي وعايز نصايح لحالتي",
    "أعراض وأسباب الشلل النصفي السفلي وعلاجه",
    "كيفية التعافي والتأهيل من الشلل النصفي السفلي",
    "معلومات عن حالة الشلل النصفي السفلي Paraplegia",
    "ما الذي يسبب الشلل النصفي السفلي المفاجئ؟",
    "أعراض إصابة الحبل الشوكي المؤدية للشلل السفلي",
    "دور العلاج الطبيعي والتأهيل للشلل النصفي السفلي",
    "هل يمكن علاج الشلل النصفي السفلي تماماً؟",
    "أنواع الشلل السفلي وتأثيرها على الحركة والتوازن",
    "كيف يؤثر الشلل السفلي على التحكم في المثانة والأمعاء؟",
    "نصائح وقائية لمنع إصابات الحبل الشوكي والشلل السفلي",
    "تشخيص الشلل النصفي السفلي بالرنين المغناطيسي والأشعة المقطعية",
    "التكيف مع الشلل السفلي باستخدام الكراسي المتحركة",
    "تمارين علاج طبيعي لمرضى الشلل النصفي السفلي بالمنزل"
]
para_en = [
    "What is paraplegia?",
    "What are the causes and symptoms of paraplegia?",
    "How to treat and rehabilitate paraplegia?",
    "Tips for managing paraplegia in daily life.",
    "What triggers paraplegia and spinal cord damage?",
    "Is paraplegia temporary or permanent?",
    "How does a spinal cord injury cause lower limb paralysis?",
    "Physical therapy and rehabilitation for paraplegia.",
    "What are the different types of paraplegia?",
    "How is paraplegia diagnosed by doctors?",
    "Can a spinal tumor or infection cause paraplegia?",
    "How to recover balance and mobility after paraplegia?",
    "Lifestyle advice to manage paraplegia and prevent sores.",
    "What support does a paraplegic person need at home?",
    "Rehabilitation timeline for post-injury paraplegia."
]
para_mixed = [
    "معلومات عن الـ Paraplegia وأسبابه",
    "علاج الشلل النصفي السفلي والتأهيل بالكرسي",
    "أعراض الـ Paraplegia وتأثيرها على الـ balance والتوازن",
    "هل إصابة الحبل الشوكي أو الـ spinal cord injury بتسبب شلل سفلي؟",
    "دور الـ physical therapy في تأهيل الشلل النصفي السفلي",
    "أسباب الـ Paraplegia المفاجئ وعلاجه",
    "كيفية تشخيص الشلل النصفي السفلي بالـ MRI والـ CT Scan",
    "أنواع الشلل النصفي السفلي زي الـ spastic paraplegia",
    "التكيف اليومي مع الـ Paraplegia بالكرسي المتحرك",
    "فترة الـ recovery والتعافي من الشلل النصفي السفلي"
]
para_ans_ar = "الشلل النصفي السفلي (Paraplegia) هو فقدان كامل أو جزئي للحركة والإحساس في الجزء السفلي من الجسم (الساقين) نتيجة إصابة في الحبل الشوكي.\n1. الأسباب: إصابات الحبل الشوكي (حوادث السيارات أو السقوط)، أورام العمود الفقري، التهابات الجهاز العصبي، أو عيوب خلقية.\n2. الأعراض: فقدان الحركة والإحساس في الساقين، صعوبة التحكم في المثانة والأمعاء، وآلام عصبية مزمنة.\n3. العلاج والتأهيل: يعتمد بشكل أساسي على العلاج الطبيعي لتقوية الجزء العلوي من الجسم، والعلاج الوظيفي للتكيف اليومي، واستخدام الكراسي المتحركة الذكية مثل Chairpal لتسهيل الاستقلالية والحركة.\n* التعافي يعتمد على شدة الإصابة ونوعها (كاملة أو جزئية)، ويتحسن بشكل ملحوظ مع المتابعة المستمرة والتأهيل المكثف."
para_ans_en = "Paraplegia is a condition causing complete or partial paralysis of the lower half of the body, including both legs, typically resulting from a spinal cord injury:\n1. Causes: Spinal cord trauma (car accidents, falls), spinal tumors, infections, or congenital conditions.\n2. Symptoms: Loss of movement and sensation in the legs, loss of bowel and bladder control, muscle spasms, and neuropathic pain.\n3. Rehabilitation: Physical therapy to strengthen the upper body, occupational therapy for daily adaptation, and assistive technologies (such as Chairpal smart wheelchairs) to maximize mobility and independence.\n* Recovery: Outcomes depend on whether the injury is complete or incomplete, with significant improvement possible through consistent rehabilitation."

# Assemble dataset
new_data = []

# List of tuples: (intent, lang, questions, answer)
data_mappings = [
    # Topic 1
    ("daily_support", "ar", adventurous_ar, adventurous_ans_ar),
    ("daily_support", "en", adventurous_en, adventurous_ans_en),
    ("daily_support", "mixed", adventurous_mixed, adventurous_ans_ar),
    
    # Topic 2
    ("daily_support", "ar", therapies_ar, therapies_ans_ar),
    ("daily_support", "en", therapies_en, therapies_ans_en),
    ("daily_support", "mixed", therapies_mixed, therapies_ans_ar),
    
    # Topic 3
    ("daily_support", "ar", yoga_ar, yoga_ans_ar),
    ("daily_support", "en", yoga_en, yoga_ans_en),
    ("daily_support", "mixed", yoga_mixed, yoga_ans_ar),
    
    # Topic 4
    ("wheelchair_usage", "ar", posture_ar, posture_ans_ar),
    ("wheelchair_usage", "en", posture_en, posture_ans_en),
    ("wheelchair_usage", "mixed", posture_mixed, posture_ans_ar),
    
    # Topic 5
    ("wheelchair_usage", "ar", measurements_ar, measurements_ans_ar),
    ("wheelchair_usage", "en", measurements_en, measurements_ans_en),
    ("wheelchair_usage", "mixed", measurements_mixed, measurements_ans_ar),
    
    # Topic 6
    ("daily_support", "ar", nutrition_ar, nutrition_ans_ar),
    ("daily_support", "en", nutrition_en, nutrition_ans_en),
    ("daily_support", "mixed", nutrition_mixed, nutrition_ans_ar),
    
    # Topic 7
    ("daily_support", "ar", sleep_ar, sleep_ans_ar),
    ("daily_support", "en", sleep_en, sleep_ans_en),
    ("daily_support", "mixed", sleep_mixed, sleep_ans_ar),
    
    # Topic 8
    ("daily_support", "ar", home_ar, home_ans_ar),
    ("daily_support", "en", home_en, home_ans_en),
    ("daily_support", "mixed", home_mixed, home_ans_ar),
    
    # Topic 9
    ("daily_support", "ar", para_ar, para_ans_ar),
    ("daily_support", "en", para_en, para_ans_en),
    ("daily_support", "mixed", para_mixed, para_ans_ar)
]

for intent, lang, questions, answer in data_mappings:
    for q in questions:
        new_data.append({
            "intent": intent,
            "language": lang,
            "question": q,
            "answer": answer
        })

print(f"Adding {len(new_data)} custom Q&A pairs from articles.txt to {DATASET_FILE}...")

# Read existing lines to avoid duplicate entries
existing_questions = set()
if os.path.exists(DATASET_FILE):
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                existing_questions.add(item["question"].strip().lower())

added_count = 0
with open(DATASET_FILE, "a", encoding="utf-8") as f:
    for item in new_data:
        q_clean = item["question"].strip().lower()
        if q_clean not in existing_questions:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            existing_questions.add(q_clean)
            added_count += 1

print(f"Done! Successfully appended {added_count} new entries (skipping duplicates).")
