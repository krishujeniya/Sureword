/**
 * Sureword — Sovereign Frontline Voice Documentation Engine
 * Production Client Application Logic with 11-Language Support
 */

// Application State
let currentDraftId = null;
let currentVersion = 1;
let currentLanguage = localStorage.getItem("sureword_lang") || "hi-IN";
let mediaRecorder = null;
let audioChunks = [];
let recordTimerInterval = null;
let recordStartTime = 0;
let isClarifyingField = null;
let committedRecordsCache = [];

// Localization Dictionaries for All 11 Supported Indic & Regional Languages
const I18N = {
  "en-IN": {
    context_pill: "Frontline Health",
    tagline: "Bilingual Voice-to-Form Visit Documentation",
    tab_form_text: "Visit Entry",
    tab_registry_text: "Saved Registry",
    step1_title: "Dictate Visit",
    step1_desc: "Speak visit details in your language (Name, Age, Village, Visit Date).",
    presets_label: "Quick Test:",
    record_start: "Start Dictation",
    record_stop: "Stop Dictation",
    rec_live: "LISTENING",
    transcript_title: "Live Transcript",
    step2_title: "Structured Visit Form",
    btn_new_session_text: "New Visit",
    summary_patient_k: "Patient",
    summary_age_k: "Age",
    summary_village_k: "Village",
    summary_date_k: "Visit Date",
    clarify_alert_title: "Clarification Needed",
    btn_hear_prompt: "Hear Prompt",
    btn_speak_field: "Speak Answer",
    btn_save_edit: "Save",
    label_name: "Patient Name",
    label_age: "Age (Years)",
    label_village: "Village",
    label_date: "Visit Date",
    commit_info_incomplete: "Complete all 4 fields to save record.",
    commit_info_ready: "All 4 fields verified. Review carefully and save.",
    commit_info_committed: "Visit record saved.",
    btn_commit: "Save Visit Record",
    committed_heading: "Visit Record Saved",
    record_id_label: "Record ID:",
    registry_title: "Saved Visit Records",
    registry_subtitle: "Locally verified household visit documentation.",
    transcript_empty: "No audio transcribed yet. Click 'Start Dictation' or select a sample above.",
    registry_empty: 'No saved visit records yet. Complete a form to save.',
    status_processing: 'Processing speech with Gnani Prisma STT…',
    status_init: 'Initializing frontline visit session…',
    mic_denied: 'Microphone access denied or unsupported.',
    status_clarify_processing: 'Processing spoken clarification…',
    label_gender: 'Gender',
    label_symptoms: 'Chief Complaints / Symptoms',
    summary_gender_k: 'Gender',
    summary_symptoms_k: 'Symptoms',
    opt_label: '(Optional)'
  },
  "hi-IN": {
    context_pill: "सामुदायिक स्वास्थ्य",
    tagline: "द्विभाषी वॉयस-टू-फॉर्म भेंट दस्तावेज़ीकरण",
    tab_form_text: "भेंट प्रपत्र",
    tab_registry_text: "सहेजे गए रिकॉर्ड",
    step1_title: "भेंट विवरण बोलें",
    step1_desc: "अपनी भाषा में मरीज का विवरण बोलें (नाम, उम्र, गाँव, तारीख)।",
    presets_label: "त्वरित परीक्षण:",
    record_start: "बोलना शुरू करें",
    record_stop: "रिकॉर्डिंग रोकें",
    rec_live: "सुन रहे हैं",
    transcript_title: "वाक् प्रतिलेखन",
    step2_title: "संरचित चिकित्सा प्रपत्र",
    btn_new_session_text: "नई भेंट",
    summary_patient_k: "मरीज",
    summary_age_k: "आयु",
    summary_village_k: "गाँव",
    summary_date_k: "भेंट तारीख",
    clarify_alert_title: "स्पष्टीकरण आवश्यक",
    btn_hear_prompt: "प्रश्न सुनें",
    btn_speak_field: "उत्तर बोलें",
    btn_save_edit: "सहेजें",
    label_name: "मरीज का नाम",
    label_age: "आयु (वर्ष)",
    label_village: "गाँव",
    label_date: "भेंट की तारीख",
    commit_info_incomplete: "रिकॉर्ड सहेजने के लिए सभी 4 फ़ील्ड भरें।",
    commit_info_ready: "सभी 4 फ़ील्ड सत्यापित हैं। सहेजने के लिए तैयार।",
    commit_info_committed: "रिकॉर्ड सहेजा गया।",
    btn_commit: "रिकॉर्ड सहेजें",
    committed_heading: "भेंट रिकॉर्ड सहेजा गया",
    record_id_label: "रिकॉर्ड आईडी:",
    registry_title: "सहेजे गए भेंट रिकॉर्ड",
    registry_subtitle: "सत्यापित घरेलू भेंटों की स्थानीय पंजी।",
    transcript_empty: "अभी तक कोई ऑडियो नहीं सुना। 'बोलना शुरू करें' पर क्लिक करें या ऊपर नमूना चुनें।",
    registry_empty: 'अभी तक कोई रिकॉर्ड नहीं सहेजा गया। फॉर्म भरकर सहेजें।',
    status_processing: 'वाक् प्रसंस्करण चल रहा है…',
    status_init: 'भेंट सत्र प्रारंभ हो रहा है…',
    mic_denied: 'माइक्रोफ़ोन अनुमति अस्वीकृत या असमर्थित।',
    status_clarify_processing: 'स्पष्टीकरण प्रसंस्करण चल रहा है…',
    label_gender: 'मरीज का लिंग',
    label_symptoms: 'मुख्य लक्षण / बीमारी',
    summary_gender_k: 'लिंग',
    summary_symptoms_k: 'लक्षण',
    opt_label: '(वैकल्पिक)'
  },
  "mr-IN": {
    context_pill: "आरोग्य केंद्र",
    tagline: "व्हॉइस-टू-फॉर्म रुग्ण नोंदणी प्रणाली",
    tab_form_text: "रुग्ण नोंदणी",
    tab_registry_text: "नोंदवलेले रेकॉर्ड",
    step1_title: "तपशील बोला",
    step1_desc: "रुग्णाचे नाव, वय, गाव आणि भेटीची तारीख बोला.",
    presets_label: "चाचणी नमुने:",
    record_start: "बोलणे सुरू करा",
    record_stop: "थांबवा",
    rec_live: "ऐकत आहे",
    transcript_title: "प्रतिलेखन",
    step2_title: "वैद्यकीय प्रपत्र",
    btn_new_session_text: "नवीन भेट",
    summary_patient_k: "रुग्ण",
    summary_age_k: "वय",
    summary_village_k: "गाव",
    summary_date_k: "भेट तारीख",
    clarify_alert_title: "स्पष्टीकरण आवश्यक",
    btn_hear_prompt: "प्रश्न ऐका",
    btn_speak_field: "उत्तर बोला",
    btn_save_edit: "जतन करा",
    label_name: "रुग्णाचे नाव",
    label_age: "वय (वर्षे)",
    label_village: "गाव",
    label_date: "भेट तारीख",
    commit_info_incomplete: "नोंद जतन करण्यासाठी सर्व ४ माहिती भरा.",
    commit_info_ready: "सर्व माहिती पडताळली आहे. जतन करा.",
    commit_info_committed: "नोंद जतन झाली.",
    btn_commit: "रेकॉर्ड जतन करा",
    committed_heading: "नोंद जतन झाली",
    record_id_label: "रेकॉर्ड आयडी:",
    registry_title: "नोंदवलेले रेकॉर्ड्स",
    registry_subtitle: "सत्यापित स्थानिक नोंदणी.",
    transcript_empty: "अद्याप ऑडिओ नाही. 'बोलणे सुरू करा' वर क्लिक करा.",
    registry_empty: 'अद्याप कोणतीही नोंद नाही. फॉर्म भरा.',
    status_processing: 'वाक् प्रक्रिया सुरू आहे…',
    status_init: 'भेट सत्र सुरू होत आहे…',
    mic_denied: 'मायक्रोफोन परवानगी नाकारली.',
    status_clarify_processing: 'स्पष्टीकरण प्रक्रिया सुरू आहे…',
    label_gender: 'लिंग',
    label_symptoms: 'प्रमुख लक्षणे / तक्रारी',
    summary_gender_k: 'लिंग',
    summary_symptoms_k: 'लक्षणे',
    opt_label: '(ऐच्छिक)'
  },
  "bn-IN": {
    context_pill: "স্বাস্থ্য কেন্দ্র",
    tagline: "ভয়েস-টু-ফর্ম রোগী নথিভুক্তকরণ",
    tab_form_text: "সাক্ষাৎ এন্ট্রি",
    tab_registry_text: "সংরক্ষিত রেকর্ড",
    step1_title: "বিবরণ বলুন",
    step1_desc: "রোগীর নাম, বয়স, গ্রাম এবং সাক্ষাতের তারিখ বলুন।",
    presets_label: "নমুনা পরীক্ষা:",
    record_start: "বলা শুরু করুন",
    record_stop: "থামুন",
    rec_live: "শুনছি",
    transcript_title: "লাইভ প্রতিলিপি",
    step2_title: "চিকিৎসা ফর্ম",
    btn_new_session_text: "নতুন সাক্ষাৎ",
    summary_patient_k: "রোগী",
    summary_age_k: "বয়স",
    summary_village_k: "গ্রাম",
    summary_date_k: "সাক্ষাতের তারিখ",
    clarify_alert_title: "স্পষ্টীকরণ প্রয়োজন",
    btn_hear_prompt: "প্রশ্ন শুনুন",
    btn_speak_field: "উত্তর বলুন",
    btn_save_edit: "সংরক্ষণ",
    label_name: "রোগীর নাম",
    label_age: "বয়স (বছর)",
    label_village: "গ্রাম",
    label_date: "সাক্ষাতের তারিখ",
    commit_info_incomplete: "সংরক্ষণের জন্য ৪টি তথ্য পূরণ করুন।",
    commit_info_ready: "সকল তথ্য যাচাই করা হয়েছে। সংরক্ষণ করুন।",
    commit_info_committed: "রেকর্ড সংরক্ষিত হয়েছে।",
    btn_commit: "রেকর্ড সংরক্ষণ করুন",
    committed_heading: "রেকর্ড সংরক্ষিত",
    record_id_label: "রেকর্ড আইডি:",
    registry_title: "সংরক্ষিত ভিজিট রেকর্ড",
    registry_subtitle: "স্থানীয়ভাবে যাচাইকৃত নথিভুক্তকরণ।",
    transcript_empty: "এখনও কোনো অডিও নেই। 'বলা শুরু করুন' ক্লিক করুন।",
    registry_empty: 'এখনও কোনো রেকর্ড সংরক্ষিত নেই।',
    status_processing: 'বাক্ প্রক্রিয়াকরণ চলছে…',
    status_init: 'সাক্ষাৎ সেশন শুরু হচ্ছে…',
    mic_denied: 'মাইক্রোফোন অনুমতি প্রত্যাখ্যাত।',
    status_clarify_processing: 'স্পষ্টীকরণ প্রক্রিয়াকরণ…',
    label_gender: 'লিঙ্গ',
    label_symptoms: 'প্রধান উপসর্গ / অভিযোগ',
    summary_gender_k: 'লিঙ্গ',
    summary_symptoms_k: 'উপসর্গ',
    opt_label: '(ঐচ্ছিক)'
  },
  "gu-IN": {
    context_pill: "આરોગ્ય કેન્દ્ર",
    tagline: "વોઇસ-ટુ-ફોર્મ મુલાકાત નોંધણી",
    tab_form_text: "દર્દી નોંધણી",
    tab_registry_text: "સેવ કરેલા રેકોર્ડ",
    step1_title: "વિગત બોલો",
    step1_desc: "દર્દીનું નામ, ઉંમર, ગામ અને મુલાકાતની તારીખ બોલો.",
    presets_label: "નમૂના ચકાસણી:",
    record_start: "બોલવાનું શરૂ કરો",
    record_stop: "બંધ કરો",
    rec_live: "સાંભળી રહ્યા છીએ",
    transcript_title: "ટ્રાન્સક્રિપ્ટ",
    step2_title: "મેડિકલ ફોર્મ",
    btn_new_session_text: "નવી મુલાકાત",
    summary_patient_k: "દર્દી",
    summary_age_k: "ઉંમર",
    summary_village_k: "ગામ",
    summary_date_k: "મુલાકાત તારીખ",
    clarify_alert_title: "સ્પષ્ટીકરણ જરૂરી",
    btn_hear_prompt: "પ્રશ્ન સાંભળો",
    btn_speak_field: "જવાબ બોલો",
    btn_save_edit: "સાચવો",
    label_name: "દર્દીનું નામ",
    label_age: "ઉંમર (વર્ષ)",
    label_village: "ગામ",
    label_date: "મુલાકાત તારીખ",
    commit_info_incomplete: "સેવ કરવા માટે બધી ૪ વિગતો ભરો.",
    commit_info_ready: "બધી વિગતો ચકાસાયેલ છે. સેવ કરો.",
    commit_info_committed: "રેકોર્ડ સાચવવામાં આવ્યો છે.",
    btn_commit: "રેકોર્ડ સેવ કરો",
    committed_heading: "રેકોર્ડ સાચવ્યો",
    record_id_label: "રેકોર્ડ આઈડી:",
    registry_title: "સાચવેલા દર્દી રેકોર્ડ",
    registry_subtitle: "ચકાસાયેલ સ્થાનિક રજિસ્ટ્રી.",
    transcript_empty: "હજુ સુધી કોઈ ઓડિયો નથી. 'બોલવાનું શરૂ કરો' ક્લિક કરો.",
    registry_empty: 'હજુ સુધી કોઈ રેકોર્ડ સાચવ્યો નથી.',
    status_processing: 'વાણી પ્રક્રિયા ચાલુ છે…',
    status_init: 'મુલાકાત સત્ર શરૂ થઈ રહ્યું છે…',
    mic_denied: 'માઇક્રોફોન પરવાનગી નકારાઈ.',
    status_clarify_processing: 'સ્પષ્ટીકરણ પ્રક્રિયા ચાલુ…',
    label_gender: 'જાતિ / લિંગ',
    label_symptoms: 'મુખ્ય લક્ષણો / ફરિયાદો',
    summary_gender_k: 'લિંગ',
    summary_symptoms_k: 'લક્ષણો',
    opt_label: '(વૈકલ્પિક)'
  },
  "pa-IN": {
    context_pill: "ਸਿਹਤ ਕੇਂਦਰ",
    tagline: "ਵਾਇਸ-ਟੂ-ਫਾਰਮ ਮਰੀਜ਼ ਦਸਤਾਵੇਜ਼ੀਕਰਨ",
    tab_form_text: "ਮੁਲਾਕਾਤ ਐਂਟਰੀ",
    tab_registry_text: "ਸੰਭਾਲੇ ਰਿਕਾਰਡ",
    step1_title: "ਵੇਰਵਾ ਬੋਲੋ",
    step1_desc: "ਮਰੀਜ਼ ਦਾ ਨਾਮ, ਉਮਰ, ਪਿੰਡ ਅਤੇ ਮੁਲਾਕਾਤ ਦੀ ਮਿਤੀ ਬੋਲੋ।",
    presets_label: "ਨਮੂਨਾ ਟੈਸਟ:",
    record_start: "ਬੋਲਣਾ ਸ਼ੁਰੂ ਕਰੋ",
    record_stop: "ਰੋਕੋ",
    rec_live: "ਸੁਣ ਰਿਹਾ ਹੈ",
    transcript_title: "ਟ੍ਰਾਂਸਕ੍ਰਿਪਟ",
    step2_title: "ਮੈਡੀਕਲ ਫਾਰਮ",
    btn_new_session_text: "ਨਵੀਂ ਮੁਲਾਕਾਤ",
    summary_patient_k: "ਮਰੀਜ਼",
    summary_age_k: "ਉਮਰ",
    summary_village_k: "ਪਿੰਡ",
    summary_date_k: "ਮੁਲਾਕਾਤ ਮਿਤੀ",
    clarify_alert_title: "ਸਪੱਸ਼ਟੀਕਰਨ ਲੋੜੀਂਦਾ",
    btn_hear_prompt: "ਸਵਾਲ ਸੁਣੋ",
    btn_speak_field: "ਜਵਾਬ ਬੋਲੋ",
    btn_save_edit: "ਸੰਭਾਲੋ",
    label_name: "ਮਰੀਜ਼ ਦਾ ਨਾਮ",
    label_age: "ਉਮਰ (ਸਾਲ)",
    label_village: "ਪਿੰਡ",
    label_date: "ਮੁਲਾਕਾਤ ਮਿਤੀ",
    commit_info_incomplete: "ਸੰਭਾਲਣ ਲਈ ਸਾਰੇ 4 ਖੇਤਰ ਭਰੋ।",
    commit_info_ready: "ਸਾਰੇ ਖੇਤਰ ਤਸਦੀਕ ਹੋ ਗਏ ਹਨ। ਸੰਭਾਲੋ।",
    commit_info_committed: "ਰਿਕਾਰਡ ਸੰਭਾਲਿਆ ਗਿਆ।",
    btn_commit: "ਰਿਕਾਰਡ ਸੰਭਾਲੋ",
    committed_heading: "ਰਿਕਾਰਡ ਸੰਭਾਲਿਆ ਗਿਆ",
    record_id_label: "ਰਿਕਾਰਡ ਆਈਡੀ:",
    registry_title: "ਸੰਭਾਲੇ ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ",
    registry_subtitle: "ਸਥਾਨਕ ਤਸਦੀਕਸ਼ੁਦਾ ਰਜਿਸਟਰੀ।",
    transcript_empty: "ਅਜੇ ਕੋਈ ਆਡੀਓ ਨਹੀਂ। 'ਬੋਲਣਾ ਸ਼ੁਰੂ ਕਰੋ' ਕਲਿੱਕ ਕਰੋ।",
    registry_empty: 'ਅਜੇ ਕੋਈ ਰਿਕਾਰਡ ਸੰਭਾਲਿਆ ਨਹੀਂ ਗਿਆ।',
    status_processing: 'ਬੋਲੀ ਪ੍ਰਕਿਰਿਆ ਚੱਲ ਰਹੀ ਹੈ…',
    status_init: 'ਮੁਲਾਕਾਤ ਸੈਸ਼ਨ ਸ਼ੁਰੂ ਹੋ ਰਿਹਾ ਹੈ…',
    mic_denied: 'ਮਾਈਕ੍ਰੋਫੋਨ ਇਜਾਜ਼ਤ ਨਕਾਰੀ ਗਈ।',
    status_clarify_processing: 'ਸਪੱਸ਼ਟੀਕਰਨ ਪ੍ਰਕਿਰਿਆ…',
    label_gender: 'ਲਿੰਗ',
    label_symptoms: 'ਮੁੱਖ ਲੱਛਣ / ਸ਼ਿਕਾਇਤਾਂ',
    summary_gender_k: 'ਲਿੰਗ',
    summary_symptoms_k: 'ਲੱਛਣ',
    opt_label: '(ਵਿਕਲਪਿਕ)'
  },
  "ta-IN": {
    context_pill: "சுகாதார மையம்",
    tagline: "குரல் வழி படிவ ஆவணமாக்கல்",
    tab_form_text: "வருகை பதிவு",
    tab_registry_text: "சேமிக்கப்பட்ட பதிவேடு",
    step1_title: "விவரம் பேசுக",
    step1_desc: "நோயாளியின் பெயர், வயது, கிராமம், வருகை தேதியை பேசவும்.",
    presets_label: "மாதிரி சோதனை:",
    record_start: "பேசத் தொடங்கு",
    record_stop: "நிறுத்து",
    rec_live: "கேட்கிறது",
    transcript_title: "நேரலை உரை",
    step2_title: "மருத்துவப் படிவம்",
    btn_new_session_text: "புதிய வருகை",
    summary_patient_k: "நோயாளி",
    summary_age_k: "வயது",
    summary_village_k: "கிராமம்",
    summary_date_k: "வருகை தேதி",
    clarify_alert_title: "விளக்கம் தேவை",
    btn_hear_prompt: "கேள்வி கேட்க",
    btn_speak_field: "பதில் பேச",
    btn_save_edit: "சேமி",
    label_name: "நோயாளி பெயர்",
    label_age: "வயது (ஆண்டுகள்)",
    label_village: "கிராமம்",
    label_date: "வருகை தேதி",
    commit_info_incomplete: "சேமிக்க 4 புலங்களையும் நிரப்பவும்.",
    commit_info_ready: "அனைத்து புலங்களும் சரிபார்க்கப்பட்டன.",
    commit_info_committed: "பதிவு சேமிக்கப்பட்டது.",
    btn_commit: "பதிவைச் சேமிக்கவும்",
    committed_heading: "வருகைப் பதிவு சேமிக்கப்பட்டது",
    record_id_label: "பதிவு எண்:",
    registry_title: "சேமிக்கப்பட்ட வருகைப் பதிவுகள்",
    registry_subtitle: "சரிபார்க்கப்பட்ட கள ஆவணங்கள்.",
    transcript_empty: "இதுவரை ஆடியோ இல்லை. 'பேசத் தொடங்கு' கிளிக் செய்யவும்.",
    registry_empty: 'இதுவரை பதிவு எதுவும் சேமிக்கப்படவில்லை.',
    status_processing: 'பேச்சு செயலாக்கம் நடைபெறுகிறது…',
    status_init: 'வருகை அமர்வு தொடங்குகிறது…',
    mic_denied: 'மைக்ரோஃபோன் அனுமதி மறுக்கப்பட்டது.',
    status_clarify_processing: 'விளக்க செயலாக்கம்…',
    label_gender: 'பாலினம்',
    label_symptoms: 'முக்கிய அறிகுறிகள்',
    summary_gender_k: 'பாலினம்',
    summary_symptoms_k: 'அறிகுறிகள்',
    opt_label: '(விருப்பத்தேர்வு)'
  },
  "te-IN": {
    context_pill: "ఆరోగ్య కేంద్రం",
    tagline: "వాయిస్-టు-ఫారం సందర్శన నమోదు",
    tab_form_text: "సందర్శన నమోదు",
    tab_registry_text: "సేవ్ చేసిన రికార్డులు",
    step1_title: "వివరాలు మాట్లాడండి",
    step1_desc: "రోగి పేరు, వయస్సు, గ్రామం మరియు సందర్శన తేదీ చెప్పండి.",
    presets_label: "నమూనా పరీక్ష:",
    record_start: "మాట్లాడటం ప్రారంభించండి",
    record_stop: "ఆపు",
    rec_live: "వింటోంది",
    transcript_title: "లైవ్ ట్రాన్స్క్రిప్ట్",
    step2_title: "వైద్య ఫారము",
    btn_new_session_text: "కొత్త సందర్శన",
    summary_patient_k: "రోగి",
    summary_age_k: "వయస్సు",
    summary_village_k: "గ్రామం",
    summary_date_k: "సందర్శన తేదీ",
    clarify_alert_title: "స్పష్టత అవసరం",
    btn_hear_prompt: "ప్రశ్న వినండి",
    btn_speak_field: "సమాధానం చెప్పండి",
    btn_save_edit: "సేవ్",
    label_name: "రోగి పేరు",
    label_age: "వయస్సు (సంవత్సరాలు)",
    label_village: "గ్రామం",
    label_date: "సందర్శన తేదీ",
    commit_info_incomplete: "సేవ్ చేయడానికి 4 వివరాలను నమోదు చేయండి.",
    commit_info_ready: "అన్ని వివరాలు ధృవీకరించబడ్డాయి. సేవ్ చేయండి.",
    commit_info_committed: "రికార్డు సేవ్ చేయబడింది.",
    btn_commit: "రికార్డును సేవ్ చేయండి",
    committed_heading: "సందర్శన రికార్డు సేవ్ చేయబడింది",
    record_id_label: "రికార్డు ఐడీ:",
    registry_title: "సేవ్ చేయబడిన రికార్డులు",
    registry_subtitle: "ధృవీకరించబడిన రిజిస్ట్రీ.",
    transcript_empty: "ఇంకా ఆడియో లేదు. 'మాట్లాడటం ప్రారంభించండి' క్లిక్ చేయండి.",
    registry_empty: 'ఇంకా రికార్డు సేవ్ చేయబడలేదు.',
    status_processing: 'వాక్ ప్రాసెసింగ్ జరుగుతోంది…',
    status_init: 'సందర్శన సెషన్ ప్రారంభమవుతోంది…',
    mic_denied: 'మైక్రోఫోన్ అనుమతి తిరస్కరించబడింది.',
    status_clarify_processing: 'స్పష్టత ప్రాసెసింగ్…',
    label_gender: 'లింగం',
    label_symptoms: 'ప్రధాన లక్షణాలు',
    summary_gender_k: 'లింగం',
    summary_symptoms_k: 'లక్షణాలు',
    opt_label: '(ఐచ్ఛికం)'
  },
  "kn-IN": {
    context_pill: "ಆರೋಗ್ಯ ಕೇಂದ್ರ",
    tagline: "ಧ್ವನಿ-ಆಧಾರಿತ ಭೇಟಿ ದಾಖಲೀಕರಣ",
    tab_form_text: "ಭೇಟಿ ನಮೂದು",
    tab_registry_text: "ಉಳಿಸಿದ ದಾಖಲೆಗಳು",
    step1_title: "ವಿವರಗಳನ್ನು ಮಾತನಾಡಿ",
    step1_desc: "ರೋಗಿಯ ಹೆಸರು, ವಯಸ್ಸು, ಗ್ರಾಮ ಮತ್ತು ಭೇಟಿಯ ದಿನಾಂಕ ಹೇಳಿ.",
    presets_label: "ಮಾದರಿ ಪರೀಕ್ಷೆ:",
    record_start: "ಮಾತನಾಡಲು ಪ್ರಾರಂಭಿಸಿ",
    record_stop: "ನಿಲ್ಲಿಸಿ",
    rec_live: "ಕೇಳುತ್ತಿದೆ",
    transcript_title: "ಪ್ರತಿಲಿಪಿ",
    step2_title: "ವೈದ್ಯಕೀಯ ನಮೂನೆ",
    btn_new_session_text: "ಹೊಸ ಭೇಟಿ",
    summary_patient_k: "ರೋಗಿ",
    summary_age_k: "ವಯಸ್ಸು",
    summary_village_k: "ಗ್ರಾಮ",
    summary_date_k: "ಭೇಟಿ ದಿನಾಂಕ",
    clarify_alert_title: "ಸ್ಪಷ್ಟೀಕರಣ ಅಗತ್ಯ",
    btn_hear_prompt: "ಪ್ರಶ್ನೆ ಕೇಳಿ",
    btn_speak_field: "ಉತ್ತರ ನೀಡಿ",
    btn_save_edit: "ಉಳಿಸಿ",
    label_name: "ರೋಗಿಯ ಹೆಸರು",
    label_age: "ವಯಸ್ಸು (ವರ್ಷ)",
    label_village: "ಗ್ರಾಮ",
    label_date: "ಭೇಟಿ ದಿನಾಂಕ",
    commit_info_incomplete: "ಉಳಿಸಲು ಎಲ್ಲಾ ೪ ಕ್ಷೇತ್ರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.",
    commit_info_ready: "ಎಲ್ಲಾ ಕ್ಷೇತ್ರಗಳು ಪರಿಶೀಲಿಸಲ್ಪಟ್ಟಿವೆ.",
    commit_info_committed: "ದಾಖಲೆ ಉಳಿಸಲಾಗಿದೆ.",
    btn_commit: "ದಾಖಲೆಯನ್ನು ಉಳಿಸಿ",
    committed_heading: "ದಾಖಲೆ ಉಳಿಸಲಾಗಿದೆ",
    record_id_label: "ದಾಖಲೆ ಐಡಿ:",
    registry_title: "ಉಳಿಸಿದ ಭೇಟಿ ದಾಖಲೆಗಳು",
    registry_subtitle: "ಪರಿಶೀಲಿಸಿದ ದಾಖಲಾತಿ.",
    transcript_empty: "ಇನ್ನೂ ಆಡಿಯೋ ಇಲ್ಲ. 'ಮಾತನಾಡಲು ಪ್ರಾರಂಭಿಸಿ' ಕ್ಲಿಕ್ ಮಾಡಿ.",
    registry_empty: 'ಇನ್ನೂ ದಾಖಲೆ ಉಳಿಸಲಾಗಿಲ್ಲ.',
    status_processing: 'ವಾಕ್ ಸಂಸ್ಕರಣೆ ನಡೆಯುತ್ತಿದೆ…',
    status_init: 'ಭೇಟಿ ಅಧಿವೇಶನ ಪ್ರಾರಂಭವಾಗುತ್ತಿದೆ…',
    mic_denied: 'ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ.',
    status_clarify_processing: 'ಸ್ಪಷ್ಟೀಕರಣ ಸಂಸ್ಕರಣೆ…',
    label_gender: 'ಲಿಂಗ',
    label_symptoms: 'ಮುಖ್ಯ ರೋಗಲಕ್ಷಣಗಳು',
    summary_gender_k: 'ಲಿಂಗ',
    summary_symptoms_k: 'ರೋಗಲಕ್ಷಣಗಳು',
    opt_label: '(ಐಚ್ಛಿಕ)'
  },
  "ml-IN": {
    context_pill: "ആരോഗ്യ കേന്ദ്രം",
    tagline: "വോയ്‌സ്-ടു-ഫോം സന്ദർശന രേഖപ്പെടുത്തൽ",
    tab_form_text: "സന്ദർശന എൻട്രി",
    tab_registry_text: "സൂക്ഷിച്ച രേഖകൾ",
    step1_title: "വിവരങ്ങൾ പറയുക",
    step1_desc: "രോഗിയുടെ പേര്, പ്രായം, ഗ്രാമം, സന്ദർശന തീയതി പറയുക.",
    presets_label: "മാതൃകാ പരിശോധന:",
    record_start: "സംസാരിക്കുക",
    record_stop: "നിർത്തുക",
    rec_live: "കേൾക്കുന്നു",
    transcript_title: "ട്രാൻസ്ക്രിപ്റ്റ്",
    step2_title: "മെഡിക്കൽ ഫോം",
    btn_new_session_text: "പുതിയ സന്ദർശനം",
    summary_patient_k: "രോഗി",
    summary_age_k: "പ്രായം",
    summary_village_k: "ഗ്രാമം",
    summary_date_k: "സന്ദർശന തീയതി",
    clarify_alert_title: "വ്യക്തത ആവശ്യമാണ്",
    btn_hear_prompt: "ചോദ്യം കേൾക്കുക",
    btn_speak_field: "മറുപടി പറയുക",
    btn_save_edit: "സൂക്ഷിക്കുക",
    label_name: "രോഗിയുടെ പേര്",
    label_age: "പ്രായം (വർഷം)",
    label_village: "ഗ്രാമം",
    label_date: "സന്ദർശന തീയതി",
    commit_info_incomplete: "സൂക്ഷിക്കാൻ 4 വിവരങ്ങളും പൂരിപ്പിക്കുക.",
    commit_info_ready: "എല്ലാ വിവരങ്ങളും ശരിയാണെന്ന് സ്ഥിരീകരിച്ചു.",
    commit_info_committed: "രേഖ സൂക്ഷിച്ചു.",
    btn_commit: "രേഖ സൂക്ഷിക്കുക",
    committed_heading: "സന്ദർശന രേഖ സൂക്ഷിച്ചു",
    record_id_label: "റെക്കോർഡ് ഐഡി:",
    registry_title: "സൂക്ഷിച്ച സന്ദർശന രേഖകൾ",
    registry_subtitle: "സ്ഥിരീകരിച്ച രജിസ്ട്രി.",
    transcript_empty: "ഇതുവരെ ഓഡിയോ ഇല്ല. 'സംസാരിക്കുക' ക്ലിക്ക് ചെയ്യുക.",
    registry_empty: 'ഇതുവരെ രേഖ സൂക്ഷിച്ചിട്ടില്ല.',
    status_processing: 'വാക്ക് പ്രോസസ്സിംഗ് നടക്കുന്നു…',
    status_init: 'സന്ദർശന സെഷൻ ആരംഭിക്കുന്നു…',
    mic_denied: 'മൈക്രോഫോൺ അനുമതി നിരസിച്ചു.',
    status_clarify_processing: 'വ്യക്തത പ്രോസസ്സിംഗ്…',
    label_gender: 'ലിംഗം',
    label_symptoms: 'പ്രധാന രോഗലക്ഷണങ്ങൾ',
    summary_gender_k: 'ലിംഗം',
    summary_symptoms_k: 'ലക്ഷണങ്ങൾ',
    opt_label: '(ഓപ്ഷണൽ)'
  },
  "or-IN": {
    context_pill: "ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ର",
    tagline: "ଭଏସ୍-ଟୁ-ଫର୍ମ ଭେଟି ପଞ୍ଜୀକରଣ",
    tab_form_text: "ଭେଟି ଏଣ୍ଟ୍ରି",
    tab_registry_text: "ସଂରକ୍ଷିତ ରେକର୍ଡ",
    step1_title: "ବିବରଣୀ କୁହନ୍ତୁ",
    step1_desc: "ରୋଗୀଙ୍କ ନାମ, ବୟସ, ଗ୍ରାମ ଏବଂ ଭେଟି ତାରିଖ କୁହନ୍ତୁ।",
    presets_label: "ନମୁନା ପରୀକ୍ଷା:",
    record_start: "କୁହିବା ଆରମ୍ଭ କରନ୍ତୁ",
    record_stop: "ବନ୍ଦ କରନ୍ତୁ",
    rec_live: "ଶୁଣୁଛି",
    transcript_title: "ପ୍ରତିଲିପି",
    step2_title: "ଚିକିତ୍ସା ଫର୍ମ",
    btn_new_session_text: "ନୂତନ ଭେଟି",
    summary_patient_k: "ରୋଗୀ",
    summary_age_k: "ବୟସ",
    summary_village_k: "ଗ୍ରାମ",
    summary_date_k: "ଭେଟି ତାରିଖ",
    clarify_alert_title: "ସ୍ପଷ୍ଟୀକରଣ ଆବଶ୍ୟକ",
    btn_hear_prompt: "ପ୍ରଶ୍ନ ଶୁଣନ୍ତୁ",
    btn_speak_field: "ଉତ୍ତର କୁହନ୍ତୁ",
    btn_save_edit: "ସଞ୍ଚୟ କରନ୍ତୁ",
    label_name: "ରୋଗୀଙ୍କ ନାମ",
    label_age: "ବୟସ (ବର୍ଷ)",
    label_village: "ଗ୍ରାମ",
    label_date: "ଭେଟି ତାରିଖ",
    commit_info_incomplete: "ସଞ୍ଚୟ କରିବାକୁ ସମସ୍ତ ୪ ତଥ୍ୟ ପୂରଣ କରନ୍ତୁ।",
    commit_info_ready: "ସମସ୍ତ ତଥ୍ୟ ଯାଞ୍ଚ ହୋଇଛି। ସଞ୍ଚୟ କରନ୍ତୁ।",
    commit_info_committed: "ରେକର୍ଡ ସଞ୍ଚିତ ହେଲା।",
    btn_commit: "ରେକର୍ଡ ସଞ୍ଚୟ କରନ୍ତୁ",
    committed_heading: "ରେକର୍ଡ ସଞ୍ଚିତ ହେଲା",
    record_id_label: "ରେକର୍ଡ ଆଇଡି:",
    registry_title: "ସଂରକ୍ଷିତ ଭେଟି ରେକର୍ଡ",
    registry_subtitle: "ଯାଞ୍ଚ ହୋଇଥିବା ପଞ୍ଜୀ।",
    transcript_empty: "ଏପର୍ଯ୍ୟନ୍ତ କୌଣସି ଅଡିଓ ନାହିଁ। 'କୁହିବା ଆରମ୍ଭ କରନ୍ତୁ' କ୍ଲିକ୍ କରନ୍ତୁ।",
    registry_empty: 'ଏପର୍ଯ୍ୟନ୍ତ କୌଣସି ରେକର୍ଡ ସଞ୍ଚିତ ହୋଇନାହିଁ।',
    status_processing: 'ବାକ୍ ପ୍ରକ୍ରିୟାକରଣ ଚାଲୁଛି…',
    status_init: 'ଭେଟି ସେସନ୍ ଆରମ୍ଭ ହେଉଛି…',
    mic_denied: 'ମାଇକ୍ରୋଫୋନ ଅନୁମତି ପ୍ରତ୍ୟାଖ୍ୟାନ।',
    status_clarify_processing: 'ସ୍ପଷ୍ଟୀକରଣ ପ୍ରକ୍ରିୟାକରଣ…',
    label_gender: 'ଲିଙ୍ଗ',
    label_symptoms: 'ମୁଖ୍ୟ ଲକ୍ଷଣ',
    summary_gender_k: 'ଲିଙ୍ଗ',
    summary_symptoms_k: 'ଲକ୍ଷଣ',
    opt_label: '(ଐଚ୍ଛିକ)'
  }
};

// Preset Dictations Across All 11 Supported Gnani Languages
const PRESET_SCRIPTS = {
  "hi-IN": {
    kamla: "मरीज का नाम कमला देवी है, उम्र 45 साल, गाँव रामपुर, विजिट डेट 30 अक्टूबर 2026",
    sunita: "पेशेंट नेम सुनीता बाई, एज अडतीस साल, गांव बिलासपुर, विजिट डेट आज",
    ramesh: "मरीज का नाम रमेश कुमार, उम्र 52 वर्ष, गाँव सोनपुर, विजिट डेट 15 अगस्त 2026"
  },
  "en-IN": {
    kamla: "Patient name Kamla Devi, age 45 years, village Rampur, visit date 30 October 2026",
    sunita: "Patient name Sunita Bai, age 38 years, village Bilaspur, visit date today",
    ramesh: "Patient name Ramesh Kumar, age 52 years, village Sonpur, visit date 15 August 2026"
  },
  "mr-IN": {
    kamla: "रुग्णाचे नाव कमला देवी, वय 45 वर्षे, गाव रामपूर, भेट दिनांक 30 ऑक्टोबर 2026",
    sunita: "रुग्णाचे नाव सुनीता बाई, वय 38 वर्षे, गाव बिलासपूर, भेट दिनांक आज",
    ramesh: "रुग्णाचे नाव रमेश कुमार, वय 52 वर्षे, गाव सोनपूर, भेट दिनांक 15 ऑगस्ट 2026"
  },
  "bn-IN": {
    kamla: "রোগীর নাম কমলা দেবী, বয়স 45 বছর, গ্রাম রামপুর, সাক্ষাতের তারিখ 30 অক্টোবর 2026",
    sunita: "রোগীর নাম সুনীতা বাই, বয়স 38 বছর, গ্রাম বিলাসপুর, সাক্ষাতের তারিখ আজ",
    ramesh: "রোগীর নাম রমেশ কুমার, বয়স 52 বছর, গ্রাম সোনপুর, সাক্ষাতের তারিখ 15 আগস্ট 2026"
  },
  "gu-IN": {
    kamla: "દર્દીનું નામ કમલા દેવી, ઉંમર 45 વર્ષ, ગામ રામપુર, મુલાકાત તારીખ 30 ઓક્ટોબર 2026",
    sunita: "દર્દીનું નામ સુનીતા બાઈ, ઉંમર 38 વર્ષ, ગામ બિલાસપુર, મુલાકાત તારીખ આજે",
    ramesh: "દર્દીનું નામ રમેશ કુમાર, ઉંમર 52 વર્ષ, ગામ સોનપુર, મુલાકાત તારીખ 15 ઓગસ્ટ 2026"
  },
  "pa-IN": {
    kamla: "ਮਰੀਜ਼ ਦਾ ਨਾਮ ਕਮਲਾ ਦੇਵੀ, ਉਮਰ 45 ਸਾਲ, ਪਿੰਡ ਰਾਮਪੁਰ, ਮੁਲਾਕਾਤ ਤਾਰੀਖ 30 ਅਕਤੂਬਰ 2026",
    sunita: "ਮਰੀਜ਼ ਦਾ ਨਾਮ ਸੁਨੀਤਾ ਬਾਈ, ਉਮਰ 38 ਸਾਲ, ਪਿੰਡ ਬਿਲਾਸਪੁਰ, ਮੁਲਾਕਾਤ ਤਾਰੀਖ ਅੱਜ",
    ramesh: "ਮਰੀਜ਼ ਦਾ ਨਾਮ ਰਮੇਸ਼ ਕੁਮਾਰ, ਉਮਰ 52 ਸਾਲ, ਪਿੰਡ ਸੋਨਪੁਰ, ਮੁਲਾਕਾਤ ਤਾਰੀਖ 15 ਅਗਸਤ 2026"
  },
  "ta-IN": {
    kamla: "நோயாளி பெயர் கமலா தேவி, வயது 45 ஆண்டுகள், கிராமம் ராம்பூர், வருகை தேதி 30 அக்டோபர் 2026",
    sunita: "நோயாளி பெயர் சுனிதா பாய், வயது 38 ஆண்டுகள், கிராமம் பிலாஸ்பூர், வருகை தேதி இன்று",
    ramesh: "நோயாளி பெயர் ரமேஷ் குமார், வயது 52 ஆண்டுகள், கிராமம் சோன்பூர், வருகை தேதி 15 ஆகஸ்ட் 2026"
  },
  "te-IN": {
    kamla: "రోగి పేరు కమలా దేవి, వయస్సు 45 సంవత్సరాలు, గ్రామం రాంపూర్, సందర్శన తేదీ 30 అక్టోబర్ 2026",
    sunita: "రోగి పేరు సునీతా బాయి, వయస్సు 38 సంవత్సరాలు, గ్రామం బిలాస్పూర్, సందర్శన తేదీ ఈరోజు",
    ramesh: "రోగి పేరు రమేష్ కుమార్, వయస్సు 52 సంవత్సరాలు, గ్రామం సోన్పూర్, సందర్శన తేదీ 15 ఆగస్టు 2026"
  },
  "kn-IN": {
    kamla: "ರೋಗಿಯ ಹೆಸರು ಕಮಲಾ ದೇವಿ, ವಯಸ್ಸು 45 ವರ್ಷ, ಗ್ರಾಮ ರಾಂಪುರ, ಭೇಟಿ ದಿನಾಂಕ 30 ಅಕ್ಟೋಬರ್ 2026",
    sunita: "ರೋಗಿಯ ಹೆಸರು ಸುನೀತಾ ಬಾಯಿ, ವಯಸ್ಸು 38 ವರ್ಷ, ಗ್ರಾಮ ಬಿಲಾಸ್ಪುರ, ಭೇಟಿ ದಿನಾಂಕ ಇಂದು",
    ramesh: "ರೋಗಿಯ ಹೆಸರು ರಮೇಶ್ ಕುಮಾರ್, ವಯಸ್ಸು 52 ವರ್ಷ, ಗ್ರಾಮ ಸೋನಪುರ, ಭೇಟಿ ದಿನಾಂಕ 15 ಆಗಸ್ಟ್ 2026"
  },
  "ml-IN": {
    kamla: "രോഗിയുടെ പേര് കമലാ ദേവി, പ്രായം 45 വർഷം, ഗ്രാമം രാംപൂർ, സന്ദർശന തീയതി 30 ഒക്ടോബർ 2026",
    sunita: "രോഗിയുടെ പേര് സുനിത ഭായ്, പ്രായം 38 വർഷം, ഗ്രാമം ബിലാസ്പൂർ, സന്ദർശന തീയതി ഇന്ന്",
    ramesh: "രോഗിയുടെ പേര് രമേഷ് കുമാർ, പ്രായം 52 വർഷം, ഗ്രാമം സോൺപൂർ, സന്ദർശന തീയതി 15 ഓഗസ്റ്റ് 2026"
  },
  "or-IN": {
    kamla: "ରୋଗୀଙ୍କ ନାମ କମଳା ଦେବୀ, ବୟସ 45 ବର୍ଷ, ଗ୍ରାମ ରାମପୁର, ପରିଦର୍ଶନ ତାରିଖ 30 ଅକ୍ଟୋବର 2026",
    sunita: "ରୋଗୀଙ୍କ ନାମ ସୁନୀତା ବାଇ, ବୟସ 38 ବର୍ଷ, ଗ୍ରାମ ବିଲାସପୁର, ପରିଦର୍ଶନ ତାରିଖ ଆଜି",
    ramesh: "ରୋଗୀଙ୍କ ନାମ ରମେଶ କୁମାର, ବୟସ 52 ବର୍ଷ, ଗ୍ରାମ ସୋନପୁର, ପରିଦର୍ଶନ ତାରିଖ 15 ଅଗଷ୍ଟ 2026"
  }
};

// Localized Chip Labels for Fast Visual Orientation
const CHIP_LABELS = {
  "en-IN": { kamla: "Kamla Devi (45y)", sunita: "Sunita Bai (38y)", ramesh: "Ramesh Kumar (52y)" },
  "hi-IN": { kamla: "कमला देवी (45 वर्ष)", sunita: "सुनीता बाई (38 वर्ष)", ramesh: "रमेश कुमार (52 वर्ष)" },
  "mr-IN": { kamla: "कमला देवी (45 वर्ष)", sunita: "सुनीता बाई (38 वर्ष)", ramesh: "रमेश कुमार (52 वर्ष)" },
  "bn-IN": { kamla: "কমলা দেবী (45 বছর)", sunita: "সুনীতা বাই (38 বছর)", ramesh: "রমেশ কুমার (52 বছর)" },
  "gu-IN": { kamla: "કમલા દેવી (45 વર્ષ)", sunita: "સુનીતા બાઈ (38 વર્ષ)", ramesh: "રમેશ કુમાર (52 વર્ષ)" },
  "pa-IN": { kamla: "ਕਮਲਾ ਦੇਵੀ (45 ਸਾਲ)", sunita: "ਸੁਨੀਤਾ ਬਾਈ (38 ਸਾਲ)", ramesh: "ਰਮੇਸ਼ ਕੁਮਾਰ (52 ਸਾਲ)" },
  "ta-IN": { kamla: "கமலா தேவி (45)", sunita: "சுனிதா பாய் (38)", ramesh: "ரமேஷ் குமார் (52)" },
  "te-IN": { kamla: "కమలా దేవి (45)", sunita: "సునీతా బాయి (38)", ramesh: "రమేష్ కుమార్ (52)" },
  "kn-IN": { kamla: "ಕಮಲಾ ದೇವಿ (45)", sunita: "ಸುನೀತಾ ಬಾಯಿ (38)", ramesh: "ರಮೇಶ್ ಕುಮಾರ್ (52)" },
  "ml-IN": { kamla: "കമലാ ദേവി (45)", sunita: "സുനിത ഭായ് (38)", ramesh: "രമേഷ് കുമാർ (52)" },
  "or-IN": { kamla: "କମଳା ଦେବୀ (45)", sunita: "ସୁନୀତା ବାଇ (38)", ramesh: "ରମେଶ କୁମାର (52)" }
};

const FIELD_KEYS = ["person_name", "age", "gender", "village", "symptoms", "visit_date"];
const REQUIRED_FIELD_KEYS = ["person_name", "age", "village", "visit_date"];

// DOM References
const providerBadge = document.getElementById("provider-badge");
const langSelect = document.getElementById("lang-select");
const recordBtn = document.getElementById("record-btn");
const recordText = document.getElementById("record-text");
const recordingTimer = document.getElementById("recording-timer");
const recordingStateIndicator = document.getElementById("recording-state-indicator");
const statusMessage = document.getElementById("status-message");
const transcriptContent = document.getElementById("transcript-content");
const newDraftBtn = document.getElementById("new-draft-btn");
const clarificationBanner = document.getElementById("clarification-banner");
const clarifyFieldTitle = document.getElementById("clarify-field-title");
const clarifyPromptText = document.getElementById("clarify-prompt-text");
const playTtsBtn = document.getElementById("play-tts-btn");
const clarifyMicBtn = document.getElementById("clarify-mic-btn");
const clarifyManualInput = document.getElementById("clarify-manual-input");
const clarifySaveBtn = document.getElementById("clarify-save-btn");
const commitBtn = document.getElementById("commit-btn");
const commitValidationInfo = document.getElementById("commit-validation-info");
const committedResult = document.getElementById("committed-result");
const savedRecordId = document.getElementById("saved-record-id");
const savedJson = document.getElementById("saved-json");
const ttsAudioPlayer = document.getElementById("tts-audio-player");

// Patient Encounter Summary DOM Elements (OpenMRS Inspired)
const summaryPatientV = document.getElementById("summary-patient-v");
const summaryAgeV = document.getElementById("summary-age-v");
const summaryVillageV = document.getElementById("summary-village-v");
const summaryDateV = document.getElementById("summary-date-v");
const summaryGenderV = document.getElementById("summary-gender-v");
const summarySymptomsV = document.getElementById("summary-symptoms-v");

// Navigation Tabs & Views
const tabFormBtn = document.getElementById("tab-form-btn");
const tabRegistryBtn = document.getElementById("tab-registry-btn");
const viewForm = document.getElementById("view-form");
const viewRegistry = document.getElementById("view-registry");
const registryCountPill = document.getElementById("registry-count-pill");
const registryTableBody = document.getElementById("registry-table-body");
const refreshRegistryBtn = document.getElementById("refresh-registry-btn");
const exportCsvBtn = document.getElementById("export-csv-btn");
const exportJsonBtn = document.getElementById("export-json-btn");

// App Initialization
window.addEventListener("DOMContentLoaded", async () => {
  await checkHealth();
  await loadCommittedRecords();

  if (langSelect) {
    langSelect.value = currentLanguage;
  }
  setLanguage(currentLanguage);

  const urlParams = new URLSearchParams(window.location.search);
  const existingDraftId = urlParams.get("draft_id");
  if (existingDraftId) {
    await loadExistingDraft(existingDraftId);
  } else {
    await initNewDraft();
  }

  setupEventListeners();
  setupKeyboardShortcuts();
});

// Localization Engine
function setLanguage(lang) {
  currentLanguage = lang;
  try {
    localStorage.setItem("sureword_lang", lang);
  } catch (e) {}

  if (langSelect && langSelect.value !== lang) {
    langSelect.value = lang;
  }

  const strings = I18N[lang] || I18N["hi-IN"] || I18N["en-IN"];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (strings && strings[key]) {
      el.textContent = strings[key];
    }
  });

  const chips = document.querySelectorAll(".preset-chip");
  if (CHIP_LABELS[lang]) {
    chips.forEach((chip) => {
      const presetKey = chip.getAttribute("data-preset");
      if (CHIP_LABELS[lang][presetKey]) {
        chip.textContent = CHIP_LABELS[lang][presetKey];
      }
    });
  }

  // Update empty state transcript if not yet transcribed
  if (transcriptContent && (!currentDraftId || transcriptContent.hasAttribute("data-i18n"))) {
    transcriptContent.textContent = strings.transcript_empty || transcriptContent.textContent;
  }

  document.documentElement.lang = lang;
}

// System Health Check
async function checkHealth() {
  try {
    const res = await fetch("/healthz");
    const data = await res.json();
    if (data.gnani_configured) {
      providerBadge.textContent = "● Live Speech Online";
      providerBadge.className = "badge badge-live";
    } else {
      providerBadge.textContent = "● Speech Engine Ready";
      providerBadge.className = "badge badge-fixture";
    }
  } catch (err) {
    providerBadge.textContent = "○ Offline Mode";
    providerBadge.className = "badge badge-warning";
  }
}

// Draft Session Lifecycle
async function initNewDraft() {
  const initDict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  showStatus(initDict.status_init || "Initializing frontline visit session...", "info");
  try {
    const res = await fetch("/api/drafts", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `language=${encodeURIComponent(currentLanguage)}`
    });
    const data = await res.json();
    currentDraftId = data.draft_id;
    currentVersion = data.version;
    updateStateUI(data.state, currentVersion);
    resetFormUI();
    hideStatus();
  } catch (err) {
    showStatus("Failed to initialize draft session: " + err.message, "error");
  }
}

async function loadExistingDraft(draftId) {
  showStatus(`Loading visit draft ${draftId}...`, "info");
  try {
    const res = await fetch(`/api/drafts/${draftId}`);
    if (res.ok) {
      const data = await res.json();
      currentDraftId = data.draft_id;
      currentVersion = data.version;
      renderDraft(data);
      hideStatus();
    } else {
      await initNewDraft();
    }
  } catch (err) {
    await initNewDraft();
  }
}

function updateEncounterSummary(fields) {
  if (!fields) return;
  if (summaryPatientV) summaryPatientV.textContent = fields.person_name?.canonical_value || "—";
  if (summaryAgeV) summaryAgeV.textContent = fields.age?.canonical_value ? `${fields.age.canonical_value}y` : "—";
  if (summaryGenderV) summaryGenderV.textContent = fields.gender?.canonical_value || "—";
  if (summaryVillageV) summaryVillageV.textContent = fields.village?.canonical_value || "—";
  if (summarySymptomsV) summarySymptomsV.textContent = fields.symptoms?.canonical_value || "—";
  if (summaryDateV) summaryDateV.textContent = fields.visit_date?.canonical_value || "—";
}

function resetFormUI() {
  committedResult.classList.add("hidden");
  clarificationBanner.classList.add("hidden");
  if (recordingStateIndicator) recordingStateIndicator.classList.add("hidden");
  const transDict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  transcriptContent.textContent = transDict.transcript_empty || "No audio transcribed yet. Click 'Start Dictation' or select a sample above.";

  updateEncounterSummary({ person_name: {}, age: {}, gender: {}, village: {}, symptoms: {}, visit_date: {} });

  FIELD_KEYS.forEach((key) => {
    const input = document.getElementById(`field-${key}`);
    const tag = document.getElementById(`tag-${key}`);
    const reasons = document.getElementById(`reasons-${key}`);
    if (input) {
      input.value = "";
      input.setAttribute("aria-invalid", "false");
    }
    if (tag) {
      tag.textContent = "Missing";
      tag.className = "status-tag tag-missing";
    }
    if (reasons) reasons.innerHTML = "";
  });

  const dict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  commitBtn.disabled = true;
  commitValidationInfo.textContent = dict.commit_info_incomplete;
}

function updateStateUI(state, version) {
  // Clinical state handling
}

function renderDraft(draft) {
  currentDraftId = draft.draft_id;
  currentVersion = draft.version;
  updateStateUI(draft.state, currentVersion);
  updateEncounterSummary(draft.fields);

  let allValid = true;

  FIELD_KEYS.forEach((key) => {
    const f = draft.fields[key];
    const input = document.getElementById(`field-${key}`);
    const tag = document.getElementById(`tag-${key}`);
    const reasonsDiv = document.getElementById(`reasons-${key}`);

    if (f) {
      if (input && f.canonical_value) {
        input.value = f.canonical_value;
      }
      if (tag) {
        tag.textContent = formatStatus(f.status);
        tag.className = `status-tag tag-${f.status}`;
      }
      if (reasonsDiv) {
        reasonsDiv.innerHTML = f.reasons.length ? f.reasons.join("<br>") : "";
      }
      if (input) {
        input.setAttribute("aria-invalid", (f.status === "needs_repeat" || (f.status === "missing" && !f.canonical_value)) ? "true" : "false");
      }

      if (f.status === "missing" || f.status === "needs_repeat" || !f.canonical_value) {
        if (REQUIRED_FIELD_KEYS.includes(key)) {
          allValid = false;
        }
      }
    } else {
      if (REQUIRED_FIELD_KEYS.includes(key)) {
        allValid = false;
      }
    }
  });

  const dict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];

  // Handle Clarification Banner (Policy P)
  if (draft.state === "NEEDS_CLARIFICATION" && draft.active_prompt) {
    clarificationBanner.classList.remove("hidden");
    isClarifyingField = draft.active_prompt.target_field;
    clarifyFieldTitle.textContent = `${dict.clarify_alert_title}: ${formatFieldName(isClarifyingField)}`;
    clarifyPromptText.textContent = draft.active_prompt.prompt_text;
    if (clarifyManualInput) {
      clarifyManualInput.value = "";
    }
    if (clarifyMicBtn) {
      clarifyMicBtn.focus();
    }
  } else {
    clarificationBanner.classList.add("hidden");
    isClarifyingField = null;
  }

  // Handle Commit button & validation feedback
  if (draft.state === "READY_FOR_REVIEW" && allValid) {
    commitBtn.disabled = false;
    commitValidationInfo.textContent = dict.commit_info_ready;
  } else if (draft.state === "COMMITTED") {
    commitBtn.disabled = true;
    commitValidationInfo.textContent = dict.commit_info_committed;
  } else {
    commitBtn.disabled = true;
    commitValidationInfo.textContent = dict.commit_info_incomplete;
  }
}

function formatStatus(status) {
  switch (status) {
    case "missing": return "Missing";
    case "proposed": return "Proposed";
    case "needs_repeat": return "Needs Repeat";
    case "user_confirmed": return "Confirmed ✓";
    case "manually_edited": return "Edited ✎";
    default: return status;
  }
}

function formatFieldName(key) {
  const dict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  switch (key) {
    case "person_name": return dict.label_name || "Patient Name";
    case "age": return dict.label_age || "Age";
    case "gender": return dict.label_gender || "Gender";
    case "village": return dict.label_village || "Village";
    case "symptoms": return dict.label_symptoms || "Symptoms";
    case "visit_date": return dict.label_date || "Visit Date";
    default: return key;
  }
}

function showStatus(msg, type = "info") {
  statusMessage.textContent = msg;
  statusMessage.className = `status-box status-${type}`;
  statusMessage.classList.remove("hidden");
}

function hideStatus() {
  statusMessage.classList.add("hidden");
}

// Audio Recording & Normalization
async function toggleRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const dict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      clearInterval(recordTimerInterval);
      if (recordingStateIndicator) recordingStateIndicator.classList.add("hidden");
      recordBtn.classList.remove("btn-recording");
      recordText.textContent = dict.record_start;

      stream.getTracks().forEach((track) => track.stop());

      if (isClarifyingField) {
        await submitClarificationAudio(isClarifyingField, audioBlob);
      } else {
        await submitFullAudio(audioBlob);
      }
    };

    const dict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
    mediaRecorder.start();
    recordStartTime = Date.now();
    recordBtn.classList.add("btn-recording");
    recordText.textContent = dict.record_stop;
    if (recordingStateIndicator) recordingStateIndicator.classList.remove("hidden");

    recordTimerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
      const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
      const ss = String(elapsed % 60).padStart(2, "0");
      if (recordingTimer) recordingTimer.textContent = `${mm}:${ss} / 00:20`;

      if (elapsed >= 20) {
        stopRecording();
      }
    }, 500);

  } catch (err) {
    const micDict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
    showStatus((micDict.mic_denied || "Microphone access denied or unsupported.") + " (" + err.message + ")", "error");
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
}

async function startClarificationRecording(fieldKey) {
  if (!fieldKey) return;
  showStatus(`Recording spoken clarification for ${formatFieldName(fieldKey)}...`, "info");
  await startRecording();
}

// API Submission Pipelines
async function submitFullAudio(blobOrFile) {
  const procDict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  showStatus(procDict.status_processing || "Processing speech with Gnani Prisma STT...", "info");
  const formData = new FormData();
  formData.append("expected_version", currentVersion);
  formData.append("audio_file", blobOrFile, "recording.webm");

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/audio`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Server error");
    }

    const data = await res.json();
    transcriptContent.textContent = data.transcript.text;

    renderDraft(data.draft);
    hideStatus();

    if (data.draft.state === "NEEDS_CLARIFICATION") {
      playSpokenClarification();
    }
  } catch (err) {
    showStatus("Audio processing failed: " + err.message, "error");
  }
}

// Preset Chip Pipeline: Allows Immediate Frictionless Testing
async function runPresetScript(presetKey) {
  const langPresets = PRESET_SCRIPTS[currentLanguage] || PRESET_SCRIPTS["hi-IN"] || PRESET_SCRIPTS["en-IN"];
  const script = langPresets[presetKey] || PRESET_SCRIPTS["hi-IN"][presetKey];
  if (!script) return;

  showStatus(`Processing sample dictation: "${script.substring(0, 35)}..."`, "info");
  const formData = new FormData();
  formData.append("expected_version", currentVersion);
  formData.append("simulated_transcript", script);

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/audio`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Preset processing error");
    }

    const data = await res.json();
    transcriptContent.textContent = data.transcript.text;

    renderDraft(data.draft);
    hideStatus();

    if (data.draft.state === "NEEDS_CLARIFICATION") {
      playSpokenClarification();
    }
  } catch (err) {
    showStatus("Preset run failed: " + err.message, "error");
  }
}

async function submitClarificationAudio(fieldKey, audioBlob) {
  showStatus(`Processing spoken clarification for ${formatFieldName(fieldKey)}...`, "info");
  const formData = new FormData();
  formData.append("target_field", fieldKey);
  formData.append("expected_version", currentVersion);
  formData.append("audio_file", audioBlob, "clarify.webm");

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/clarify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Clarification failed");
    }
    const updatedDraft = await res.json();
    renderDraft(updatedDraft);
    hideStatus();
  } catch (err) {
    showStatus("Clarification failed: " + err.message, "error");
  }
}

async function saveManualClarification() {
  const val = clarifyManualInput.value.trim();
  if (!val || !isClarifyingField) return;
  await saveFieldManualEdit(isClarifyingField, val);
}

async function saveFieldManualEdit(fieldKey, val) {
  if (!val || !val.trim()) return;

  const formData = new FormData();
  formData.append("target_field", fieldKey);
  formData.append("expected_version", currentVersion);
  formData.append("manual_value", val.trim());

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/clarify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Edit failed");
    }
    const updatedDraft = await res.json();
    renderDraft(updatedDraft);
  } catch (err) {
    showStatus("Failed to update field: " + err.message, "error");
  }
}

// Spoken Clarification Synthesis via Gnani Timbre
async function playSpokenClarification() {
  const dict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  try {
    playTtsBtn.disabled = true;
    playTtsBtn.textContent = "🔊 Synthesizing...";

    const res = await fetch(`/api/drafts/${currentDraftId}/speech`, { method: "POST" });
    if (!res.ok) throw new Error("TTS generation failed");

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    ttsAudioPlayer.src = audioUrl;
    ttsAudioPlayer.play();

    playTtsBtn.textContent = "🔊 Playing...";
    ttsAudioPlayer.onended = () => {
      playTtsBtn.disabled = false;
      playTtsBtn.textContent = `🔊 ${dict.btn_hear_prompt}`;
    };
  } catch (err) {
    playTtsBtn.disabled = false;
    playTtsBtn.textContent = `🔊 ${dict.btn_hear_prompt}`;
    showStatus("Could not play spoken prompt: " + err.message, "error");
  }
}

// Idempotent Commit Pipeline
async function commitCurrentDraft() {
  showStatus("Verifying invariants and committing clinical record...", "info");
  const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/commit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        expected_version: currentVersion,
        idempotency_key: idempotencyKey,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Commit failed");
    }

    const data = await res.json();
    renderDraft(data.draft);
    savedRecordId.textContent = data.record_id;
    savedJson.textContent = JSON.stringify(data.draft, null, 2);
    committedResult.classList.remove("hidden");
    hideStatus();

    // Reload Registry Cache
    await loadCommittedRecords();
  } catch (err) {
    showStatus("Commit failed: " + err.message, "error");
  }
}

// Committed Records Registry
async function loadCommittedRecords() {
  try {
    const res = await fetch("/api/records");
    if (!res.ok) return;
    const records = await res.json();
    committedRecordsCache = records;
    registryCountPill.textContent = records.length;
    renderRegistryTable(records);
  } catch (err) {
    // Registry fetch failed; table gracefully shows empty state
  }
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "—";
  const s = String(str);
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function renderRegistryTable(records) {
  const regDict = I18N[currentLanguage] || I18N["hi-IN"] || I18N["en-IN"];
  if (!records || records.length === 0) {
    registryTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="table-empty">${escapeHtml(regDict.registry_empty || "No saved visit records yet. Complete a form to save.")}</td>
      </tr>
    `;
    return;
  }

  registryTableBody.innerHTML = records.map((r) => {
    const snap = r.snapshot || {};
    const fields = snap.fields || {};
    const name = fields.person_name ? fields.person_name.canonical_value : "—";
    const age = fields.age ? fields.age.canonical_value : "—";
    const gender = fields.gender ? fields.gender.canonical_value : "—";
    const village = fields.village ? fields.village.canonical_value : "—";
    const symptoms = fields.symptoms ? fields.symptoms.canonical_value : "—";
    const date = fields.visit_date ? fields.visit_date.canonical_value : "—";
    const timeFormatted = new Date(r.committed_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    return `
      <tr>
        <td><strong class="code-record-id">${escapeHtml(r.record_id)}</strong></td>
        <td>${escapeHtml(name)}</td>
        <td>${escapeHtml(age)}</td>
        <td>${escapeHtml(gender)}</td>
        <td>${escapeHtml(village)}</td>
        <td>${escapeHtml(symptoms)}</td>
        <td>${escapeHtml(date)}</td>
        <td>${escapeHtml(timeFormatted)}</td>
        <td><span class="badge badge-live">Verified ✓</span></td>
      </tr>
    `;
  }).join("");
}

// Export Registry CSV & JSON
function exportRegistryCSV() {
  if (!committedRecordsCache.length) {
    showStatus("No committed records available to export", "error");
    return;
  }

  const headers = ["RecordID", "DraftID", "PatientName", "Age", "Gender", "Village", "Symptoms", "VisitDate", "CommittedAt"];
  const rows = committedRecordsCache.map((r) => {
    const f = r.snapshot.fields || {};
    return [
      r.record_id,
      r.draft_id,
      `"${f.person_name?.canonical_value || ""}"`,
      f.age?.canonical_value || "",
      `"${f.gender?.canonical_value || ""}"`,
      `"${f.village?.canonical_value || ""}"`,
      `"${f.symptoms?.canonical_value || ""}"`,
      f.visit_date?.canonical_value || "",
      r.committed_at
    ].join(",");
  });

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `sureword_committed_records_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportRegistryJSON() {
  if (!committedRecordsCache.length) {
    showStatus("No committed records available to export", "error");
    return;
  }

  const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(committedRecordsCache, null, 2));
  const link = document.createElement("a");
  link.setAttribute("href", jsonStr);
  link.setAttribute("download", `sureword_committed_records_${Date.now()}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Navigation Tabs Switcher
function switchTab(targetView) {
  if (tabFormBtn) {
    tabFormBtn.classList.toggle("active", targetView === "form");
    tabFormBtn.setAttribute("aria-selected", targetView === "form" ? "true" : "false");
  }
  if (tabRegistryBtn) {
    tabRegistryBtn.classList.toggle("active", targetView === "registry");
    tabRegistryBtn.setAttribute("aria-selected", targetView === "registry" ? "true" : "false");
  }

  if (viewForm) {
    viewForm.classList.toggle("active", targetView === "form");
    viewForm.classList.toggle("hidden", targetView !== "form");
  }
  if (viewRegistry) {
    viewRegistry.classList.toggle("active", targetView === "registry");
    viewRegistry.classList.toggle("hidden", targetView !== "registry");
    if (targetView === "registry") {
      loadCommittedRecords();
    }
  }
}

// Event Listeners
function setupEventListeners() {
  if (langSelect) {
    langSelect.addEventListener("change", async (e) => {
      setLanguage(e.target.value);
      await initNewDraft();
    });
  }

  if (tabFormBtn) tabFormBtn.addEventListener("click", () => switchTab("form"));
  if (tabRegistryBtn) tabRegistryBtn.addEventListener("click", () => switchTab("registry"));

  newDraftBtn.addEventListener("click", initNewDraft);
  recordBtn.addEventListener("click", toggleRecording);

  playTtsBtn.addEventListener("click", playSpokenClarification);
  clarifyMicBtn.addEventListener("click", () => startClarificationRecording(isClarifyingField));
  if (clarifySaveBtn) {
    clarifySaveBtn.addEventListener("click", saveManualClarification);
  }

  commitBtn.addEventListener("click", commitCurrentDraft);

  refreshRegistryBtn.addEventListener("click", loadCommittedRecords);
  exportCsvBtn.addEventListener("click", exportRegistryCSV);
  exportJsonBtn.addEventListener("click", exportRegistryJSON);

  const viewInRegistryBtn = document.getElementById("view-in-registry-btn");
  if (viewInRegistryBtn) {
    viewInRegistryBtn.addEventListener("click", () => switchTab("registry"));
  }
  const startNextDraftBtn = document.getElementById("start-next-draft-btn");
  if (startNextDraftBtn) {
    startNextDraftBtn.addEventListener("click", initNewDraft);
  }

  // Preset Chips
  document.querySelectorAll(".preset-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const presetKey = chip.getAttribute("data-preset");
      runPresetScript(presetKey);
    });
  });

  // Pure Voice-to-Form: Manual input editing removed per frontline field design
}

// Accessible Keyboard Shortcuts (frontend-a11y)
function setupKeyboardShortcuts() {
  window.addEventListener("keydown", (e) => {
    // Ctrl+Enter or Cmd+Enter to commit
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      if (!commitBtn.disabled) {
        e.preventDefault();
        commitCurrentDraft();
      }
    }

    // Escape to close clarification or reset active focus
    if (e.key === "Escape") {
      if (!clarificationBanner.classList.contains("hidden")) {
        if (clarifyManualInput) {
          clarifyManualInput.blur();
        } else if (clarifyMicBtn) {
          clarifyMicBtn.blur();
        }
      }
    }
  });
}
