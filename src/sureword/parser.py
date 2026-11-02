"""Deterministic parsing and normalization for Hindi-English frontline visit forms."""

from __future__ import annotations

import re
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
    "january": 1,
    "jan": 1,
    "जनवरी": 1,
    "february": 2,
    "feb": 2,
    "फरवरी": 2,
    "march": 3,
    "mar": 3,
    "मार्च": 3,
    "april": 4,
    "apr": 4,
    "अप्रैल": 4,
    "may": 5,
    "मई": 5,
    "june": 6,
    "jun": 6,
    "जून": 6,
    "july": 7,
    "jul": 7,
    "जुलाई": 7,
    "august": 8,
    "aug": 8,
    "अगस्त": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "सितंबर": 9,
    "सितम्बर": 9,
    "october": 10,
    "oct": 10,
    "अक्टूबर": 10,
    "अक्तूबर": 10,
    "november": 11,
    "nov": 11,
    "नवंबर": 11,
    "नवम्बर": 11,
    "december": 12,
    "dec": 12,
    "दिसंबर": 12,
    "दिसम्बर": 12,
}

VILLAGE_MAP: dict[str, str] = {
    "rampur": "Rampur",
    "रामपुर": "Rampur",
    "bilaspur": "Bilaspur",
    "बिलासपुर": "Bilaspur",
    "sonpur": "Sonpur",
    "सोनपुर": "Sonpur",
    "kalyanpur": "Kalyanpur",
    "कल्याणपुर": "Kalyanpur",
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
    "सुनीता बाई": "Sunita Bai",
    "रमेश कुमार": "Ramesh Kumar",
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


def convert_devanagari_digits(text: str) -> str:
    """Convert Devanagari numerals to ASCII digits."""
    return "".join(DEVANAGARI_DIGITS.get(ch, ch) for ch in text)


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

    # Patterns matching age mentions
    # e.g., "उम्र 42 साल", "age 35", "45 years", "उम्र बयालीस वर्ष", "30 saal", "age is 28"
    patterns = [
        r"(?:उम्र|आयु|age|patient\s+age)(?:\s+(?:is|है|था))?\s*[:\-]?\s*([०-९\w\s\-]+?)(?:\s*(?:साल|वर्ष|years|year|saal|bars)|\b)",
        r"(\d+|[०-९]+|[a-zA-Z\u0900-\u097F]+)\s*(?:साल|वर्ष|years|year|saal|bars)(?:\s*(?:की|का|old))?",
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

    # Relative dates
    if re.search(r"\b(आज|today)\b", text, re.IGNORECASE):
        return FieldValue(
            key=FieldKey.VISIT_DATE.value,
            raw_span="आज/today",
            canonical_value=ref.isoformat(),
            status=FieldStatus.PROPOSED,
        )

    if re.search(r"\b(कल|yesterday)\b", text, re.IGNORECASE):
        from datetime import timedelta

        y_date = ref - timedelta(days=1)
        return FieldValue(
            key=FieldKey.VISIT_DATE.value,
            raw_span="कल/yesterday",
            canonical_value=y_date.isoformat(),
            status=FieldStatus.PROPOSED,
        )

    # ISO format YYYY-MM-DD
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

    # DD-MM-YYYY format
    dmy_match = re.search(r"\b(0?[1-9]|[12]\d|3[01])[\-/](0?[1-9]|1[0-2])[\-/(202\d)]\b", text)
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

    # Worded dates: e.g. "30 October 2026", "15 अगस्त 2026", "28 oct"
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

    # Explicit village marker: e.g., "गाँव रामपुर", "village Rampur", "स्थान सोनपुर"
    pat_marker = r"(?:गाँव|गांव|ग्राम|village|place|location)\s*[:\-]?\s*([A-Za-z\u0900-\u097F]+)"
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

    # Marker patterns: "नाम कमला देवी है", "patient name Sunita Bai", "name is Ramesh Kumar"
    markers = [
        r"(?:मरीज\s+का\s+नाम|मरीज़\s+का\s+नाम|नाम|name\s+is|patient\s+name)\s*[:\-]?\s*([A-Za-z\u0900-\u097F\s]{2,30}?)(?:\s+(?:है|hai|था|उम्र|age|village|गाँव|रहने)|$)",
        r"(?:shrimati|smt|shri|mr|mrs|sushri|श्रीमती|श्री)\s+([A-Za-z\u0900-\u097F\s]{2,25})",
    ]

    for pat in markers:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw_name = m.group(1).strip()
            # Clean up trailing words
            raw_name = re.sub(
                r"\b(है|hai|ji|जी|ka|की|ke|के)\b", "", raw_name, flags=re.IGNORECASE
            ).strip()
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
