"""Deterministic parsing and normalization for Hindi-English frontline visit forms."""

from __future__ import annotations

import re
import unicodedata
from datetime import date

from sureword.contracts import FieldKey, FieldStatus, FieldValue

# Devanagari digit mapping
DEVANAGARI_DIGITS = {
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
}

# Hindi number words mapping (1 to 100)
HINDI_NUMBER_WORDS: dict[str, int] = {
    "शून्य": 0,
    "एक": 1,
    "दो": 2,
    "तीन": 3,
    "चार": 4,
    "पाँच": 5,
    "पांच": 5,
    "छह": 6,
    "छः": 6,
    "सात": 7,
    "आठ": 8,
    "नौ": 9,
    "दस": 10,
    "ग्यारह": 11,
    "बारह": 12,
    "तेरह": 13,
    "चौदह": 14,
    "पंद्रह": 15,
    "पन्द्रह": 15,
    "सोलह": 16,
    "सत्रह": 17,
    "अठारह": 18,
    "उन्नीस": 19,
    "बीस": 20,
    "इक्कीस": 21,
    "बाईस": 22,
    "तेईस": 23,
    "चौबीस": 24,
    "पच्चीस": 25,
    "छब्बीस": 26,
    "सत्ताईस": 27,
    "अट्ठाईस": 28,
    "उनतीस": 29,
    "तीस": 30,
    "इकतीस": 31,
    "बत्तीस": 32,
    "तैंतीस": 33,
    "चौंतीस": 34,
    "पैंतीस": 35,
    "छत्तीस": 36,
    "सैंतीस": 37,
    "अड़तीस": 38,
    "उनतालीस": 39,
    "चालीस": 40,
    "इकतालीस": 41,
    "बयालीस": 42,
    "तैंतालीस": 43,
    "चवालीस": 44,
    "पैंतालीस": 45,
    "छियालीस": 46,
    "सैंतालीस": 47,
    "अड़तालीस": 48,
    "उनचास": 49,
    "पचास": 50,
    "इक्यावन": 51,
    "बावन": 52,
    "तिरपन": 53,
    "चौवन": 54,
    "बचपन": 55,
    "पचपन": 55,
    "छप्पन": 56,
    "सत्तावन": 57,
    "अट्ठावन": 58,
    "उनसठ": 59,
    "साठ": 60,
    "इकसठ": 61,
    "बासठ": 62,
    "तिरसठ": 63,
    "चौंसठ": 64,
    "पैंसठ": 65,
    "छियासठ": 66,
    "सड़सठ": 67,
    "अड़सठ": 68,
    "उनहत्तर": 69,
    "सत्तर": 70,
    "इकहत्तर": 71,
    "बहत्तर": 72,
    "तिहत्तर": 73,
    "चौहत्तर": 74,
    "पचहत्तर": 75,
    "छिहत्तर": 76,
    "सतहत्तर": 77,
    "अठहत्तर": 78,
    "उन्यासी": 79,
    "अस्सी": 80,
    "इक्यासी": 81,
    "बयासी": 82,
    "तिरासी": 83,
    "चौरासी": 84,
    "पचासी": 85,
    "छियासी": 86,
    "सत्तासी": 87,
    "अठासी": 88,
    "नवासी": 89,
    "नब्बे": 90,
    "इक्यानवे": 91,
    "बानवे": 92,
    "तिरानवे": 93,
    "चौरानवे": 94,
    "पचानवे": 95,
    "छियानवे": 96,
    "सत्तानवे": 97,
    "अट्ठानवे": 98,
    "निन्यानवे": 99,
    "सौ": 100,
}

ENGLISH_NUMBER_WORDS: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
}

MONTH_MAP: dict[str, int] = {
    # January
    "january": 1,
    "jan": 1,
    "जनवरी": 1,
    "जानेवारी": 1,
    "জানুয়ারি": 1,
    "જાન્યુઆરી": 1,
    "ਜਨਵਰੀ": 1,
    "ஜனவரி": 1,
    "జనవరి": 1,
    "ಜನವರಿ": 1,
    "ജനുവരി": 1,
    "ଜାନୁଆରୀ": 1,
    # February
    "february": 2,
    "feb": 2,
    "फरवरी": 2,
    "फेब्रुवारी": 2,
    "ফেব্রুয়ারি": 2,
    "ફેબ્રુઆરી": 2,
    "ਫਰਵਰੀ": 2,
    "பிப்ரவரி": 2,
    "ఫిబ్రవరి": 2,
    "ಫೆಬ್ರವರಿ": 2,
    "ഫെബ്രുവരി": 2,
    "ଫେବୃଆରୀ": 2,
    # March
    "march": 3,
    "mar": 3,
    "मार्च": 3,
    "মার্চ": 3,
    "માર્ચ": 3,
    "ਮਾਰਚ": 3,
    "மார்ச்": 3,
    "మార్చి": 3,
    "ಮಾರ್ಚ್": 3,
    "മാർച്ച്": 3,
    "ମାର୍ଚ୍ଚ": 3,
    # April
    "april": 4,
    "apr": 4,
    "अप्रैल": 4,
    "एप्रिल": 4,
    "এপ্রিল": 4,
    "એપ્રિલ": 4,
    "ਅਪ੍ਰੈਲ": 4,
    "ஏப்ரல்": 4,
    "ఏప్రిల్": 4,
    "ಏಪ್ರಿಲ್": 4,
    "ഏപ്രിൽ": 4,
    "ଏପ୍ରିଲ": 4,
    # May
    "may": 5,
    "मई": 5,
    "मे": 5,
    "মে": 5,
    "મે": 5,
    "ਮਈ": 5,
    "மே": 5,
    "మే": 5,
    "ಮೇ": 5,
    "മേയ്": 5,
    "ମେ": 5,
    # June
    "june": 6,
    "jun": 6,
    "जून": 6,
    "জুন": 6,
    "જૂન": 6,
    "ਜੂਨ": 6,
    "ஜூன்": 6,
    "జూన్": 6,
    "ಜೂನ್": 6,
    "ജൂൺ": 6,
    "ଜୁନ୍": 6,
    # July
    "july": 7,
    "jul": 7,
    "जुलाई": 7,
    "जुलै": 7,
    "জুলাই": 7,
    "જુલાઈ": 7,
    "ਜੁਲਾਈ": 7,
    "ஜூலை": 7,
    "జూలై": 7,
    "ಜುಲೈ": 7,
    "ജൂലൈ": 7,
    "ଜୁଲାଇ": 7,
    # August
    "august": 8,
    "aug": 8,
    "अगस्त": 8,
    "ऑगस्ट": 8,
    "আগস্ট": 8,
    "ઓગસ્ટ": 8,
    "ਅਗਸਤ": 8,
    "ஆகஸ்ட்": 8,
    "ఆగస్టు": 8,
    "ಆಗಸ್ಟ್": 8,
    "ആഗസ്റ്റ്": 8,
    "ଅଗଷ୍ଟ": 8,
    # September
    "september": 9,
    "sep": 9,
    "sept": 9,
    "सितंबर": 9,
    "सितम्बर": 9,
    "सप्टेंबर": 9,
    "সেপ্টেম্বর": 9,
    "સપ્ટેમ્બર": 9,
    "ਸਤੰਬਰ": 9,
    "செப்டம்பர்": 9,
    "సెప్టెంబర్": 9,
    "ಸೆಪ್ಟೆಂಬರ್": 9,
    "സെപ്റ്റംബർ": 9,
    "ସେପ୍ଟେମ୍ବର": 9,
    # October
    "october": 10,
    "oct": 10,
    "अक्टूबर": 10,
    "अक्तूबर": 10,
    "ऑक्टोबर": 10,
    "অক্টোবর": 10,
    "ઓક્ટોબર": 10,
    "ਅਕਤੂਬਰ": 10,
    "அக்டோபர்": 10,
    "అక్టోబర్": 10,
    "ಅಕ್ಟೋಬರ್": 10,
    "ഒക്ടോബർ": 10,
    "ଅକ୍ଟୋବର": 10,
    # November
    "november": 11,
    "nov": 11,
    "नवंबर": 11,
    "नवम्बर": 11,
    "नोव्हेंबर": 11,
    "নভেম্বর": 11,
    "નવેમ્બર": 11,
    "ਨਵੰਬਰ": 11,
    "நவம்பர்": 11,
    "నవంబర్": 11,
    "ನವೆಂಬರ್": 11,
    "നവംബർ": 11,
    "ନଭେମ୍ବର": 11,
    # December
    "december": 12,
    "dec": 12,
    "दिसंबर": 12,
    "दिसम्बर": 12,
    "डिसेंबर": 12,
    "ডিসেম্বর": 12,
    "ડિસેમ્બર": 12,
    "ਦਸੰਬਰ": 12,
    "டிசம்பர்": 12,
    "డిసెంబర్": 12,
    "ಡಿಸೆಂಬರ್": 12,
    "ഡിസംബർ": 12,
    "ଡିସେମ୍ବର": 12,
}

VILLAGE_MAP: dict[str, str] = {
    "rampur": "Rampur",
    "रामपुर": "Rampur",
    "रामपूर": "Rampur",
    "રામપુર": "Rampur",
    "রামপুর": "Rampur",
    "ਰਾਮਪੁਰ": "Rampur",
    "ராம்பூர்": "Rampur",
    "రాంపూర్": "Rampur",
    "ರಾಂಪುರ": "Rampur",
    "രാംപൂർ": "Rampur",
    "ରାମପୁର": "Rampur",
    "bilaspur": "Bilaspur",
    "बिलासपुर": "Bilaspur",
    "बिलासपूर": "Bilaspur",
    "બિલાસપુર": "Bilaspur",
    "বিলাসপুর": "Bilaspur",
    "ਬਿਲਾਸਪੁਰ": "Bilaspur",
    "பிலாஸ்பூர்": "Bilaspur",
    "బిలాస్పూర్": "Bilaspur",
    "ಬಿಲಾಸ್ಪುರ": "Bilaspur",
    "ബിലാസ്പൂർ": "Bilaspur",
    "ବିଲାସପୁର": "Bilaspur",
    "sonpur": "Sonpur",
    "सोनपुर": "Sonpur",
    "सोनपूर": "Sonpur",
    "સોનપુર": "Sonpur",
    "সোনপুর": "Sonpur",
    "ਸੋਨਪੁਰ": "Sonpur",
    "சோன்பூர்": "Sonpur",
    "సోన్పూర్": "Sonpur",
    "ಸೋನಪುರ": "Sonpur",
    "സോൺപൂർ": "Sonpur",
    "ସୋନପୁର": "Sonpur",
    "kalyanpur": "Kalyanpur",
    "कल्याणपुर": "Kalyanpur",
    "कल्याणपूर": "Kalyanpur",
    "chandpur": "Chandpur",
    "चांदपुर": "Chandpur",
    "चाँदपुर": "Chandpur",
    "shivpur": "Shivpur",
    "शिवपुर": "Shivpur",
    "govindpur": "Govindpur",
    "गोविंदपुर": "Govindpur",
    "गोविन्दपुर": "Govindpur",
    "madhopur": "Madhopur",
    "माधोपुर": "Madhopur",
    "sultanpur": "Sultanpur",
    "सुल्तानपुर": "Sultanpur",
    "fatehpur": "Fatehpur",
    "फतेहपुर": "Fatehpur",
    "bikrampur": "Bikrampur",
    "विक्रमपुर": "Bikrampur",
    "haripur": "Haripur",
    "हरिपुर": "Haripur",
    "mohanpur": "Mohanpur",
    "मोहनपुर": "Mohanpur",
    "gopalpur": "Gopalpur",
    "गोपालपुर": "Gopalpur",
    "anandpur": "Anandpur",
    "आनंदपुर": "Anandpur",
}

NAME_MAP: dict[str, str] = {
    "कमला देवी": "Kamla Devi",
    "কমলা দেবী": "Kamla Devi",
    "કમલા દેવી": "Kamla Devi",
    "ਕਮਲਾ ਦੇਵੀ": "Kamla Devi",
    "கமலா தேவி": "Kamla Devi",
    "కమలా దేవి": "Kamla Devi",
    "ಕಮಲಾ ದೇವಿ": "Kamla Devi",
    "കമലാ ദേവി": "Kamla Devi",
    "କମଳା ଦେବୀ": "Kamla Devi",
    "kamla devi": "Kamla Devi",
    "सुनीता बाई": "Sunita Bai",
    "সুনীতা বাই": "Sunita Bai",
    "સુનીતા બાઈ": "Sunita Bai",
    "સુનિતા બાઈ": "Sunita Bai",
    "ਸੁਨੀਤਾ ਬਾਈ": "Sunita Bai",
    "சுனிதா பாய்": "Sunita Bai",
    "సునీతా బాయి": "Sunita Bai",
    "ಸುನೀತಾ ಬಾಯಿ": "Sunita Bai",
    "സുനിത ഭായ്": "Sunita Bai",
    "സുനിതാ ഭായ്": "Sunita Bai",
    "ସୁନୀତା ବାଇ": "Sunita Bai",
    "sunita bai": "Sunita Bai",
    "रमेश कुमार": "Ramesh Kumar",
    "রমেশ কুমার": "Ramesh Kumar",
    "રમેશ કુમાર": "Ramesh Kumar",
    "ਰਮੇਸ਼ ਕੁਮਾਰ": "Ramesh Kumar",
    "ரமேஷ் குமார்": "Ramesh Kumar",
    "రమేష్ కుమార్": "Ramesh Kumar",
    "ರಮೇಶ್ ಕುಮಾರ್": "Ramesh Kumar",
    "രമേഷ് കുമാർ": "Ramesh Kumar",
    "ରମେଶ କୁମାର": "Ramesh Kumar",
    "ramesh kumar": "Ramesh Kumar",
    "पूजा पटेल": "Pooja Patel",
    "मोहन लाल": "Mohan Lal",
    "आशा देवी": "Asha Devi",
    "राधा देवी": "Radha Devi",
    "सुरेश": "Suresh",
    "गीता देवी": "Geeta Devi",
    "दिनेश कुमार": "Dinesh Kumar",
    "रेखा देवी": "Rekha Devi",
    "विजय": "Vijay",
    "सीमा बाई": "Seema Bai",
    "अनिल": "Anil",
    "मीना देवी": "Meena Devi",
    "राजेश": "Rajesh",
}


def convert_indic_digits(text: str) -> str:
    """Convert any Indic script numeral (Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Telugu, Kannada, Malayalam) to ASCII digits."""
    result: list[str] = []
    for ch in text:
        if ch in DEVANAGARI_DIGITS:
            result.append(DEVANAGARI_DIGITS[ch])
        elif ch.isdigit() and unicodedata.category(ch) == "Nd":
            result.append(str(unicodedata.digit(ch)))
        else:
            result.append(ch)
    return "".join(result)


# Alias for backward compatibility
convert_devanagari_digits = convert_indic_digits


def normalize_number(text: str) -> int | None:
    """Convert number string, Devanagari digits, or Hindi/English words to an integer."""
    text_clean = convert_devanagari_digits(text.strip().lower())

    if text_clean.isdigit():
        return int(text_clean)

    # Check Hindi number words
    if text_clean in HINDI_NUMBER_WORDS:
        return HINDI_NUMBER_WORDS[text_clean]

    # Check English number words (e.g., "forty two", "twenty five")
    words = text_clean.replace("-", " ").split()
    if len(words) == 1 and words[0] in ENGLISH_NUMBER_WORDS:
        return ENGLISH_NUMBER_WORDS[words[0]]
    elif len(words) == 2 and words[0] in ENGLISH_NUMBER_WORDS and words[1] in ENGLISH_NUMBER_WORDS:
        tens = ENGLISH_NUMBER_WORDS[words[0]]
        ones = ENGLISH_NUMBER_WORDS[words[1]]
        if tens in {20, 30, 40, 50, 60, 70, 80, 90} and 0 <= ones <= 9:
            return tens + ones

    return None


def parse_age(transcript: str) -> FieldValue:
    """Extract and validate age in completed years (1-120)."""
    text = convert_devanagari_digits(transcript)

    # Patterns matching age mentions across Indic languages & English
    # e.g., "उम्र 42 साल", "age 35", "वय 45 वर्षे", "வயது 45 ஆண்டுகள்", "వయస్సు 38", "বয়স 38 বছর"
    patterns = [
        r"(?:उम्र|आयु|वय|বয়স|ઉંમર|ਉਮਰ|வயது|వయస్సు|ವಯಸ್ಸು|പ്രായം|ବୟସ|age|patient\s+age)(?:\s+(?:is|है|था|आहे|ആണ്|ஆகும்))?\s*[:\-]?\s*([\d\w\s\-]+?)(?:\s*(?:साल|वर्ष|वर्षे|বছর|વર્ષ|ਸਾਲ|ஆண்டு|வருடம்|సంవత్సరాలు|ವರ್ಷ|വർഷം|ବର୍ଷ|years|year|saal|bars)|\b)",
        r"(\d+|[a-zA-Z\u0900-\u0D7F]+)\s*(?:साल|वर्ष|वर्षे|বছর|વર્ષ|ਸਾਲ|ஆண்டு|வருடம்|సంవత్సరాలు|ವರ್ಷ|വർഷം|ବର୍ଷ|years|year|saal|bars)(?:\s*(?:की|का|old))?",
    ]

    candidates: list[tuple[int, str]] = []

    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            raw_matched = match.group(1).strip()
            val = normalize_number(raw_matched)
            if val is not None:
                candidates.append((val, match.group(0).strip()))

    if not candidates:
        # Fallback: look for isolated numbers if the utterance is short (like clarification turn "42")
        words = text.strip().split()
        if len(words) <= 3:
            for w in words:
                v = normalize_number(w)
                if v is not None and 1 <= v <= 120:
                    return FieldValue(
                        key=FieldKey.AGE.value,
                        raw_span=w,
                        canonical_value=str(v),
                        status=FieldStatus.PROPOSED,
                    )
        return FieldValue(
            key=FieldKey.AGE.value,
            status=FieldStatus.MISSING,
            reasons=["Age not mentioned or could not be parsed"],
        )

    # Check for conflicting candidates
    distinct_vals = {c[0] for c in candidates}
    if len(distinct_vals) > 1:
        return FieldValue(
            key=FieldKey.AGE.value,
            raw_span=candidates[-1][1],
            canonical_value=str(candidates[-1][0]),
            status=FieldStatus.NEEDS_REPEAT,
            reasons=[f"Conflicting age mentions found: {sorted(list(distinct_vals))}"],
        )

    final_val, raw_span = candidates[-1]
    if not (1 <= final_val <= 120):
        return FieldValue(
            key=FieldKey.AGE.value,
            raw_span=raw_span,
            canonical_value=str(final_val),
            status=FieldStatus.NEEDS_REPEAT,
            reasons=[f"Age {final_val} out of valid physiological range (1-120)"],
        )

    return FieldValue(
        key=FieldKey.AGE.value,
        raw_span=raw_span,
        canonical_value=str(final_val),
        status=FieldStatus.PROPOSED,
    )


def parse_date(transcript: str, reference_date: date | None = None) -> FieldValue:
    """Extract and validate visit date in ISO format YYYY-MM-DD."""
    ref = reference_date or date.today()
    text = convert_devanagari_digits(transcript)

    # 1. ISO format YYYY-MM-DD (checked before relative to avoid substrings)
    iso_match = re.search(r"\b(202\d)[\-/](0?[1-9]|1[0-2])[\-/](0?[1-9]|[12]\d|3[01])\b", text)
    if iso_match:
        y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        try:
            parsed_d = date(y, m, d)
            return FieldValue(
                key=FieldKey.VISIT_DATE.value,
                raw_span=iso_match.group(0),
                canonical_value=parsed_d.isoformat(),
                status=FieldStatus.PROPOSED,
            )
        except ValueError:
            return FieldValue(
                key=FieldKey.VISIT_DATE.value,
                raw_span=iso_match.group(0),
                canonical_value=None,
                status=FieldStatus.NEEDS_REPEAT,
                reasons=[f"Invalid calendar date {iso_match.group(0)}"],
            )

    # 2. DD-MM-YYYY format
    dmy_match = re.search(r"\b(0?[1-9]|[12]\d|3[01])[\-/](0?[1-9]|1[0-2])(?:[\-/](202\d))?\b", text)
    if dmy_match:
        d_str, m_str, y_str = dmy_match.group(1), dmy_match.group(2), dmy_match.group(3)
        y = int(y_str) if y_str else ref.year
        try:
            parsed_d = date(y, int(m_str), int(d_str))
            return FieldValue(
                key=FieldKey.VISIT_DATE.value,
                raw_span=dmy_match.group(0),
                canonical_value=parsed_d.isoformat(),
                status=FieldStatus.PROPOSED,
            )
        except ValueError:
            return FieldValue(
                key=FieldKey.VISIT_DATE.value,
                raw_span=dmy_match.group(0),
                canonical_value=None,
                status=FieldStatus.NEEDS_REPEAT,
                reasons=[f"Invalid calendar date {dmy_match.group(0)}"],
            )

    # 3. Worded dates: e.g. "30 October 2026", "15 अगस्त 2026", "28 oct"
    for m_word, m_num in MONTH_MAP.items():
        pat = rf"(\d{{1,2}})\s+{m_word}(?:\s+(\d{{4}}))?"
        m_word_match = re.search(pat, text, re.IGNORECASE)
        if m_word_match:
            day = int(m_word_match.group(1))
            year = int(m_word_match.group(2)) if m_word_match.group(2) else ref.year
            try:
                parsed_d = date(year, m_num, day)
                return FieldValue(
                    key=FieldKey.VISIT_DATE.value,
                    raw_span=m_word_match.group(0),
                    canonical_value=parsed_d.isoformat(),
                    status=FieldStatus.PROPOSED,
                )
            except ValueError:
                return FieldValue(
                    key=FieldKey.VISIT_DATE.value,
                    raw_span=m_word_match.group(0),
                    canonical_value=None,
                    status=FieldStatus.NEEDS_REPEAT,
                    reasons=[f"Invalid date: day {day} for month {m_word}"],
                )

    # 4. Relative dates (boundary safe across Indic scripts & English)
    if re.search(
        r"(?<![\u0900-\u0D7F\w])(आज|आज|आज|আজ|આજે|ਅੱਜ|இன்று|ఈరోజు|ಇಂದು|ഇന്ന്|ଆଜି|today)(?![\u0900-\u0D7F\w])",
        text,
        re.IGNORECASE,
    ):
        return FieldValue(
            key=FieldKey.VISIT_DATE.value,
            raw_span="today",
            canonical_value=ref.isoformat(),
            status=FieldStatus.PROPOSED,
        )

    if re.search(
        r"(?<![\u0900-\u0D7F\w])(कल|काल|গতকাল|ગઈકાલે|ਕੱਲ੍ਹ|நேற்று|నిన్న|ನಿನ್ನೆ|ഇന്നലെ|ଗତକାଲି|yesterday)(?![\u0900-\u0D7F\w])",
        text,
        re.IGNORECASE,
    ):
        from datetime import timedelta

        y_date = ref - timedelta(days=1)
        return FieldValue(
            key=FieldKey.VISIT_DATE.value,
            raw_span="yesterday",
            canonical_value=y_date.isoformat(),
            status=FieldStatus.PROPOSED,
        )

    return FieldValue(
        key=FieldKey.VISIT_DATE.value,
        status=FieldStatus.MISSING,
        reasons=["Visit date not found or not in recognizable format"],
    )


def parse_village(transcript: str) -> FieldValue:
    """Extract village name matching known directory or explicit context."""
    text = transcript.strip()

    # Search known villages
    for v_key, canonical in VILLAGE_MAP.items():
        pat = rf"\b{re.escape(v_key)}\b"
        if re.search(pat, text, re.IGNORECASE):
            return FieldValue(
                key=FieldKey.VILLAGE.value,
                raw_span=v_key,
                canonical_value=canonical,
                status=FieldStatus.PROPOSED,
            )

    # Explicit village marker across Indian languages
    pat_marker = r"(?:गाँव|गांव|ग्राम|गाव|গ্রাম|ગામ|ਪਿੰਡ|கிராமம்|గ్రామం|ಗ್ರಾಮ|ഗ്രാമം|ଗ୍ରାମ|village|place|location)\s*[:\-]?\s*([A-Za-z\u0900-\u0D7F]+)"
    m = re.search(pat_marker, text, re.IGNORECASE)
    if m:
        v_name = m.group(1).strip()
        # Filter out common stop words
        if v_name.lower() not in {"is", "mein", "में", "ka", "का", "visit", "date"}:
            canonical = VILLAGE_MAP.get(v_name.lower(), v_name.title())
            return FieldValue(
                key=FieldKey.VILLAGE.value,
                raw_span=m.group(0),
                canonical_value=canonical,
                status=FieldStatus.PROPOSED,
                reasons=["Out-of-dictionary village name extracted via marker"]
                if canonical == v_name.title()
                else [],
            )

    # Single-word clarification fallback
    words = text.split()
    if len(words) == 1 and len(words[0]) >= 3:
        w = words[0].strip(",.")
        canonical = VILLAGE_MAP.get(w.lower(), w.title())
        return FieldValue(
            key=FieldKey.VILLAGE.value,
            raw_span=w,
            canonical_value=canonical,
            status=FieldStatus.PROPOSED,
        )

    return FieldValue(
        key=FieldKey.VILLAGE.value,
        status=FieldStatus.MISSING,
        reasons=["Village name not found"],
    )


def parse_person_name(transcript: str) -> FieldValue:
    """Extract fictional person name."""
    text = transcript.strip()

    # Check direct name map
    for raw_hi, canonical in NAME_MAP.items():
        if raw_hi in text:
            return FieldValue(
                key=FieldKey.PERSON_NAME.value,
                raw_span=raw_hi,
                canonical_value=canonical,
                status=FieldStatus.PROPOSED,
            )

    # Marker patterns across Indian languages
    markers = [
        r"(?:मरीज\s+का\s+नाम|मरीज़\s+का\s+नाम|नाव|নাম|નામ|ਨਾਮ|பெயர்|పేరు|ಹೆಸರು|പേര്|ନାମ|name\s+is|patient\s+name|नाम)\s*[:\-]?\s*([A-Za-z\u0900-\u0D7F\s]{2,35}?)(?:[,;]|\s+(?:है|hai|था|is|उम्र|वय|বয়স|ઉંમર|ਉਮਰ|வயது|వయస్సు|ವಯಸ್ಸು|പ്രായം|ବୟସ|age|village|गाँव|गाव|ગામ|গ্রাম|கிராமம்|గ్రామం|ಗ್ರಾಮ|ഗ്രാമം|ଗ୍ରାମ|ਪਿੰਡ|\d)|$)",
        r"(?:shrimati|smt|shri|mr|mrs|sushri|श्रीमती|श्री)\s+([A-Za-z\u0900-\u0D7F\s]{2,25}?)(?:[,;]|\s+(?:है|hai|था|is|उम्र|वय|বয়স|ઉંમર|ਉਮਰ|வயது|వయస్సు|ವಯಸ್ಸು|പ്രായം|ବୟସ|age|village|गाँव|गाव|\d)|$)",
    ]

    for pat in markers:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw_name = m.group(1).strip(" ,;:-")
            # Clean up trailing words
            raw_name = re.sub(
                r"\b(है|hai|ji|जी|ka|की|ke|के|age|उम्र)\b", "", raw_name, flags=re.IGNORECASE
            ).strip(" ,;:-")
            if len(raw_name) >= 2 and not raw_name.isdigit():
                canonical = NAME_MAP.get(raw_name, raw_name.title())
                return FieldValue(
                    key=FieldKey.PERSON_NAME.value,
                    raw_span=raw_name,
                    canonical_value=canonical,
                    status=FieldStatus.PROPOSED,
                )

    # Clarification turn fallback (e.g. user just said "Kamla Devi")
    words = text.split()
    if 1 <= len(words) <= 3 and all(w.isalpha() for w in words):
        lower_joined = " ".join(words).lower()
        if lower_joined not in {"yes", "no", "haan", "nahin", "today", "yesterday", "aaj", "kal"}:
            canonical = NAME_MAP.get(text, text.title())
            return FieldValue(
                key=FieldKey.PERSON_NAME.value,
                raw_span=text,
                canonical_value=canonical,
                status=FieldStatus.PROPOSED,
            )

    return FieldValue(
        key=FieldKey.PERSON_NAME.value,
        status=FieldStatus.MISSING,
        reasons=["Person name not found in transcript"],
    )


def parse_visit_form(transcript: str, reference_date: date | None = None) -> dict[str, FieldValue]:
    """Parse all four core fields deterministically from transcript."""
    return {
        FieldKey.PERSON_NAME.value: parse_person_name(transcript),
        FieldKey.AGE.value: parse_age(transcript),
        FieldKey.VILLAGE.value: parse_village(transcript),
        FieldKey.VISIT_DATE.value: parse_date(transcript, reference_date),
    }
