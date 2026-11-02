"""Supported language catalog and localization metadata for Gnani.ai Prisma & Timbre."""

from __future__ import annotations

from typing import NamedTuple

from sureword.contracts import FieldKey


class LanguageMetadata(NamedTuple):
    code: str
    name: str
    native_name: str
    script: str
    sample_script: str
    clarification_prompts: dict[str, str]


# All 11 Indic languages supported by Gnani Prisma STT & Gnani Timbre TTS
GNANI_LANGUAGES: dict[str, LanguageMetadata] = {
    "hi-IN": LanguageMetadata(
        code="hi-IN",
        name="Hindi",
        native_name="हिन्दी",
        script="Devanagari",
        sample_script="मरीज का नाम कमला देवी है, उम्र 45 साल, गाँव रामपुर, विजिट डेट आज",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "कृपया मरीज़ का पूरा नाम दोबारा बोलिए।",
            FieldKey.AGE.value: "कृपया मरीज़ की सही उम्र दोबारा बोलिए।",
            FieldKey.VILLAGE.value: "कृपया गाँव का नाम दोबारा बोलिए।",
            FieldKey.VISIT_DATE.value: "कृपया विज़िट की सही तारीख दोबारा बोलिए।",
        },
    ),
    "en-IN": LanguageMetadata(
        code="en-IN",
        name="English",
        native_name="English",
        script="Latin",
        sample_script="Patient name Ramesh Kumar, age 52 years, village Sonpur, visit date 15 August 2026",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "Please repeat the person's full name.",
            FieldKey.AGE.value: "Please repeat the person's age in completed years.",
            FieldKey.VILLAGE.value: "Please repeat the village name.",
            FieldKey.VISIT_DATE.value: "Please repeat the visit date.",
        },
    ),
    "mr-IN": LanguageMetadata(
        code="mr-IN",
        name="Marathi",
        native_name="मराठी",
        script="Devanagari",
        sample_script="रुग्णाचे नाव कमला देवी, वय 45 वर्षे, गाव रामपूर, भेट दिनांक आज",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "कृपया रुग्णाचे पूर्ण नाव पुन्हा सांगा.",
            FieldKey.AGE.value: "कृपया रुग्णाचे योग्य वय पुन्हा सांगा.",
            FieldKey.VILLAGE.value: "कृपया गावाचे नाव पुन्हा सांगा.",
            FieldKey.VISIT_DATE.value: "कृपया भेटीची तारीख पुन्हा सांगा.",
        },
    ),
    "bn-IN": LanguageMetadata(
        code="bn-IN",
        name="Bengali",
        native_name="বাংলা",
        script="Bengali",
        sample_script="রোগীর নাম সুনীতা বাই, বয়স 38 বছর, গ্রাম বিলাসপুর, সাক্ষাতের তারিখ আজ",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "অনুগ্রহ করে রোগীর পুরো নাম আবার বলুন।",
            FieldKey.AGE.value: "অনুগ্রহ করে রোগীর সঠিক বয়স আবার বলুন।",
            FieldKey.VILLAGE.value: "অনুগ্রহ করে গ্রামের নাম আবার বলুন।",
            FieldKey.VISIT_DATE.value: "অনুগ্রহ করে সাক্ষাতের তারিখ আবার বলুন।",
        },
    ),
    "gu-IN": LanguageMetadata(
        code="gu-IN",
        name="Gujarati",
        native_name="ગુજરાતી",
        script="Gujarati",
        sample_script="દર્દીનું નામ કમલા દેવી, ઉંમર 45 વર્ષ, ગામ રામપુર, મુલાકાત તારીખ આજે",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "કૃપા કરીને દર્દીનું પૂરું નામ ફરીથી બોલો.",
            FieldKey.AGE.value: "કૃપા કરીને દર્દીની સાચી ઉંમર ફરીથી બોલો.",
            FieldKey.VILLAGE.value: "કૃપા કરીને ગામનું નામ ફરીથી બોલો.",
            FieldKey.VISIT_DATE.value: "કૃપા કરીને મુલાકાતની તારીખ ફરીથી બોલો.",
        },
    ),
    "pa-IN": LanguageMetadata(
        code="pa-IN",
        name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        script="Gurmukhi",
        sample_script="ਮਰੀਜ਼ ਦਾ ਨਾਮ ਰਮੇਸ਼ ਕੁਮਾਰ, ਉਮਰ 52 ਸਾਲ, ਪਿੰਡ ਸੋਨਪੁਰ, ਮੁਲਾਕਾਤ ਤਾਰੀਖ ਅੱਜ",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "ਕਿਰਪਾ ਕਰਕੇ ਮਰੀਜ਼ ਦਾ ਪੂਰਾ ਨਾਮ ਦੁਬਾਰਾ ਬੋਲੋ।",
            FieldKey.AGE.value: "ਕਿਰਪਾ ਕਰਕੇ ਮਰੀਜ਼ ਦੀ ਸਹੀ ਉਮਰ ਦੁਬਾਰਾ ਬੋਲੋ।",
            FieldKey.VILLAGE.value: "ਕਿਰਪਾ ਕਰਕੇ ਪਿੰਡ ਦਾ ਨਾਮ ਦੁਬਾਰਾ ਬੋਲੋ।",
            FieldKey.VISIT_DATE.value: "ਕਿਰਪਾ ਕਰਕੇ ਮੁਲਾਕਾਤ ਦੀ ਤਾਰੀਖ ਦੁਬਾਰਾ ਬੋਲੋ।",
        },
    ),
    "ta-IN": LanguageMetadata(
        code="ta-IN",
        name="Tamil",
        native_name="தமிழ்",
        script="Tamil",
        sample_script="நோயாளி பெயர் கமலா தேவி, வயது 45 ஆண்டுகள், கிராமம் ராம்பூர், வருகை தேதி இன்று",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "தயவுசெய்து நோயாளியின் முழுப் பெயரை மீண்டும் கூறுங்கள்.",
            FieldKey.AGE.value: "தயவுசெய்து நோயாளியின் சரியான வயதை மீண்டும் கூறுங்கள்.",
            FieldKey.VILLAGE.value: "தயவுசெய்து கிராமத்தின் பெயரை மீண்டும் கூறுங்கள்.",
            FieldKey.VISIT_DATE.value: "தயவுசெய்து வருகை தேதியை மீண்டும் கூறுங்கள்.",
        },
    ),
    "te-IN": LanguageMetadata(
        code="te-IN",
        name="Telugu",
        native_name="తెలుగు",
        script="Telugu",
        sample_script="రోగి పేరు సునీతా బాయి, వయస్సు 38 సంవత్సరాలు, గ్రామం బిలాస్పూర్, సందర్శన తేదీ ఈరోజు",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "దయచేసి రోగి పూర్తి పేరును మళ్ళీ చెప్పండి.",
            FieldKey.AGE.value: "దయచేసి రోగి సరైన వయస్సును మళ్ళీ చెప్పండి.",
            FieldKey.VILLAGE.value: "దయచేసి గ్రామం పేరును మళ్ళీ చెప్పండి.",
            FieldKey.VISIT_DATE.value: "దయచేసి సందర్శన తేదీని మళ్ళీ చెప్పండి.",
        },
    ),
    "kn-IN": LanguageMetadata(
        code="kn-IN",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        script="Kannada",
        sample_script="ರೋಗಿಯ ಹೆಸರು ಕಮಲಾ ದೇವಿ, ವಯಸ್ಸು 45 ವರ್ಷ, ಗ್ರಾಮ ರಾಂಪುರ, ಭೇಟಿ ದಿನಾಂಕ ಇಂದು",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "ದಯವಿಟ್ಟು ರೋಗಿಯ ಪೂರ್ಣ ಹೆಸರನ್ನು ಪುನರಾವರ್ತಿಸಿ.",
            FieldKey.AGE.value: "ದಯವಿಟ್ಟು ರೋಗಿಯ ಸರಿಯಾದ ವಯಸ್ಸನ್ನು ಪುನರಾವರ್ತಿಸಿ.",
            FieldKey.VILLAGE.value: "ದಯವಿಟ್ಟು ಗ್ರಾಮದ ಹೆಸರನ್ನು ಪುನರಾವರ್ತಿಸಿ.",
            FieldKey.VISIT_DATE.value: "ದಯವಿಟ್ಟು ಭೇಟಿಯ ದಿನಾಂಕವನ್ನು ಪುನರಾವರ್ತಿಸಿ.",
        },
    ),
    "ml-IN": LanguageMetadata(
        code="ml-IN",
        name="Malayalam",
        native_name="മലയാളം",
        script="Malayalam",
        sample_script="രോഗിയുടെ പേര് രമേഷ് കുമാർ, പ്രായം 52 വർഷം, ഗ്രാമം സോൺപൂർ, സന്ദർശന തീയതി ഇന്ന്",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "ദയവായി രോഗിയുടെ പൂർണ്ണ പേര് വീണ്ടും പറയുക.",
            FieldKey.AGE.value: "ദയവായി രോഗിയുടെ ശരിയായ പ്രായം വീണ്ടും പറയുക.",
            FieldKey.VILLAGE.value: "ദയവായി ഗ്രാമത്തിന്റെ പേര് വീണ്ടും പറയുക.",
            FieldKey.VISIT_DATE.value: "ദയവായി സന്ദർശന തീയതി വീണ്ടും പറയുക.",
        },
    ),
    "or-IN": LanguageMetadata(
        code="or-IN",
        name="Odia",
        native_name="ଓଡ଼ିଆ",
        script="Odia",
        sample_script="ରୋଗୀଙ୍କ ନାମ କମଳା ଦେବୀ, ବୟସ 45 ବର୍ଷ, ଗ୍ରାମ ରାମପୁର, ପରିଦର୍ଶନ ତାରିଖ ଆଜି",
        clarification_prompts={
            FieldKey.PERSON_NAME.value: "ଦୟାକରି ରୋଗୀଙ୍କ ପୂର୍ଣ ନାମ ପୁନର୍ବାର କୁହନ୍ତୁ।",
            FieldKey.AGE.value: "ଦୟାକରି ରୋଗୀଙ୍କ ସଠିକ୍ ବୟସ ପୁନର୍ବାର କୁହନ୍ତୁ।",
            FieldKey.VILLAGE.value: "ଦୟାକରି ଗ୍ରାମର ନାମ ପୁନର୍ବାର କୁହନ୍ତୁ।",
            FieldKey.VISIT_DATE.value: "ଦୟାକରି ପରିଦର୍ଶନ ତାରିଖ ପୁନର୍ବାର କୁହନ୍ତୁ।",
        },
    ),
}

DEFAULT_LANGUAGE_CODE = "hi-IN"


def get_language_metadata(code: str) -> LanguageMetadata:
    """Retrieve metadata for a language code, falling back to default."""
    return GNANI_LANGUAGES.get(code) or GNANI_LANGUAGES[DEFAULT_LANGUAGE_CODE]


def get_clarification_prompt(field_key: str, language_code: str = DEFAULT_LANGUAGE_CODE) -> str:
    """Retrieve localized clarification question for a field and language."""
    meta = get_language_metadata(language_code)
    return meta.clarification_prompts.get(field_key, f"Please clarify {field_key}.")
