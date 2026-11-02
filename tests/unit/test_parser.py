"""Unit tests for deterministic Hindi-English field parsing and normalization."""

from datetime import date

from sureword.contracts import FieldKey, FieldStatus
from sureword.parser import (
    convert_devanagari_digits,
    normalize_number,
    parse_age,
    parse_date,
    parse_person_name,
    parse_village,
    parse_visit_form,
)


def test_devanagari_conversion() -> None:
    assert convert_devanagari_digits("४२") == "42"
    assert convert_devanagari_digits("२०२६-१०-३०") == "2026-10-30"


def test_normalize_number() -> None:
    assert normalize_number("42") == 42
    assert normalize_number("४२") == 42
    assert normalize_number("पैंतालीस") == 45
    assert normalize_number("तीस") == 30
    assert normalize_number("forty two") == 42
    assert normalize_number("twenty five") == 25
    assert normalize_number("ten") == 10
    assert normalize_number("invalid_word") is None


def test_parse_age_valid() -> None:
    # Digits + साल
    res = parse_age("उम्र 42 साल है")
    assert res.canonical_value == "42"
    assert res.status == FieldStatus.PROPOSED

    # Hindi number words
    res_hi = parse_age("मरीज की उम्र पैंतालीस वर्ष है")
    assert res_hi.canonical_value == "45"
    assert res_hi.status == FieldStatus.PROPOSED

    # English expression
    res_en = parse_age("patient age is 28 years")
    assert res_en.canonical_value == "28"
    assert res_en.status == FieldStatus.PROPOSED


def test_parse_age_physiological_bounds() -> None:
    # Age 150 out of bounds -> NEEDS_REPEAT
    res = parse_age("उम्र 150 साल")
    assert res.status == FieldStatus.NEEDS_REPEAT
    assert "out of valid physiological range" in res.reasons[0]


def test_parse_age_conflicting_mentions() -> None:
    # Multiple different ages mentioned
    res = parse_age("उम्र 35 साल नहीं 40 साल है")
    assert res.status == FieldStatus.NEEDS_REPEAT
    assert "Conflicting age mentions" in res.reasons[0]


def test_parse_date_formats() -> None:
    ref_d = date(2026, 10, 31)

    # Relative "आज"
    res_today = parse_date("आज की तारीख", reference_date=ref_d)
    assert res_today.canonical_value == "2026-10-31"
    assert res_today.status == FieldStatus.PROPOSED

    # Relative "कल"
    res_yesterday = parse_date("कल विजिट हुआ था", reference_date=ref_d)
    assert res_yesterday.canonical_value == "2026-10-30"
    assert res_yesterday.status == FieldStatus.PROPOSED

    # ISO format
    res_iso = parse_date("विजिट डेट 2026-10-28")
    assert res_iso.canonical_value == "2026-10-28"

    # Hindi month name
    res_hi = parse_date("15 अगस्त 2026")
    assert res_hi.canonical_value == "2026-08-15"

    # Rejection of invalid calendar date (e.g. Feb 30)
    res_invalid = parse_date("30 फरवरी 2026")
    assert res_invalid.status == FieldStatus.NEEDS_REPEAT
    assert "Invalid date" in res_invalid.reasons[0]


def test_parse_village() -> None:
    # Known village
    res = parse_village("गाँव रामपुर में विजिट हुई")
    assert res.canonical_value == "Rampur"
    assert res.status == FieldStatus.PROPOSED

    # Village via marker
    res_marker = parse_village("स्थान सोनपुर")
    assert res_marker.canonical_value == "Sonpur"
    assert res_marker.status == FieldStatus.PROPOSED


def test_parse_person_name() -> None:
    res = parse_person_name("मरीज का नाम कमला देवी है उम्र 45 साल")
    assert res.canonical_value == "Kamla Devi"
    assert res.status == FieldStatus.PROPOSED

    res_en = parse_person_name("patient name Ramesh Kumar age 52")
    assert res_en.canonical_value == "Ramesh Kumar"
    assert res_en.status == FieldStatus.PROPOSED


def test_parse_visit_form_full() -> None:
    transcript = "मरीज का नाम कमला देवी है, उम्र पैंतालीस साल, गाँव रामपुर, विजिट डेट 30 अक्टूबर 2026"
    fields = parse_visit_form(transcript)

    assert fields[FieldKey.PERSON_NAME.value].canonical_value == "Kamla Devi"
    assert fields[FieldKey.AGE.value].canonical_value == "45"
    assert fields[FieldKey.VILLAGE.value].canonical_value == "Rampur"
    assert fields[FieldKey.VISIT_DATE.value].canonical_value == "2026-10-30"


def test_parse_age_single_word_fallback() -> None:
    res = parse_age("42")
    assert res.canonical_value == "42"
    assert res.status == FieldStatus.PROPOSED


def test_parse_date_dmy_and_invalid_branches() -> None:
    # DD-MM-YYYY slash
    res_slash = parse_date("विजिट डेट 15/10/2026")
    assert res_slash.canonical_value == "2026-10-15"
    assert res_slash.status == FieldStatus.PROPOSED

    # DD-MM-YYYY dash
    res_dash = parse_date("विजिट 25-12-2026")
    assert res_dash.canonical_value == "2026-12-25"

    # Invalid ISO date (Feb 31)
    res_inv_iso = parse_date("विजिट डेट 2026-02-31")
    assert res_inv_iso.status == FieldStatus.NEEDS_REPEAT

    # Invalid DMY date (Feb 31)
    res_inv_dmy = parse_date("विजिट डेट 31/02/2026")
    assert res_inv_dmy.status == FieldStatus.NEEDS_REPEAT


def test_parse_village_clarification_and_stopwords() -> None:
    # Single-word clarification fallback with known and unknown village
    res = parse_village("Rampur")
    assert res.canonical_value == "Rampur"
    assert res.status == FieldStatus.PROPOSED

    res_single_ood = parse_village("Hoshiarpur")
    assert res_single_ood.canonical_value == "Hoshiarpur"
    assert res_single_ood.status == FieldStatus.PROPOSED

    # Village via marker for out-of-dictionary name
    res_marker_ood = parse_village("place Hoshiarpur")
    assert res_marker_ood.canonical_value == "Hoshiarpur"
    assert "Out-of-dictionary" in res_marker_ood.reasons[0]

    # Stopword filtered
    res_stop = parse_village("गाँव में")
    assert res_stop.status == FieldStatus.MISSING


def test_parse_person_name_clarification_and_honorifics() -> None:
    # Single/two word clarification fallback
    res_clarify = parse_person_name("Kamla Devi")
    assert res_clarify.canonical_value == "Kamla Devi"
    assert res_clarify.status == FieldStatus.PROPOSED

    # Honorific marker
    res_hon = parse_person_name("smt Rekha Devi age 29")
    assert res_hon.canonical_value == "Rekha Devi"

    # Missing name when only numbers/gibberish
    res_none = parse_person_name("12345 67890")
    assert res_none.status == FieldStatus.MISSING
