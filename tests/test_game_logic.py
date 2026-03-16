from logic_utils import check_guess, parse_guess


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Bug #1 fix: inverted hints ---

def test_too_high_message_says_go_lower():
    """When guess > secret the player needs to go lower, not higher."""
    _, message = check_guess(80, 38)
    assert "LOWER" in message, f"Expected LOWER in hint, got: {message}"


def test_too_low_message_says_go_higher():
    """When guess < secret the player needs to go higher, not lower."""
    _, message = check_guess(20, 47)
    assert "HIGHER" in message, f"Expected HIGHER in hint, got: {message}"


# --- Bug #3 fix: invalid input must not appear in history ---

def test_invalid_input_returns_not_ok():
    """Non-numeric input must return ok=False so the caller never appends it to history."""
    ok, value, err = parse_guess("xyz")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_empty_input_returns_not_ok():
    """Empty string must also be rejected cleanly."""
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
