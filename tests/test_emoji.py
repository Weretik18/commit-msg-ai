from commit_msg_ai.emoji import prepend_emoji


def test_prepends_feat_emoji():
    assert prepend_emoji("feat: add login").startswith("✨")

def test_prepends_with_scope():
    assert prepend_emoji("fix(auth): null check").startswith("🐛")

def test_idempotent_when_already_has_emoji():
    msg = "✨ feat: add login"
    assert prepend_emoji(msg) == msg

def test_unknown_type_unchanged():
    msg = "xxx: nothing"
    assert prepend_emoji(msg) == msg

def test_preserves_body():
    out = prepend_emoji("feat: short\n\nlong body here")
    assert out.startswith("✨ feat:")
    assert "long body here" in out
