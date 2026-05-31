from commit_msg_ai.providers.base import resolve_language


def test_code_ru_becomes_russian():
    assert resolve_language("ru") == "Russian"

def test_code_en_becomes_english():
    assert resolve_language("en") == "English"

def test_unknown_code_passthrough():
    assert resolve_language("xyz") == "Xyz"

def test_full_name_passthrough():
    assert resolve_language("Russian") == "Russian"

def test_empty_defaults_to_english():
    assert resolve_language("") == "English"
    assert resolve_language(None) == "English"
