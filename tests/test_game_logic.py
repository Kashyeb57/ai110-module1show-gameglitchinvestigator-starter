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


# --- Challenge 1: Advanced edge-case tests ---

def test_parse_guess_decimal_truncates_to_int():
    """A decimal like '3.7' should be accepted and truncated to 3, not rejected."""
    ok, value, err = parse_guess("3.7")
    assert ok is True
    assert value == 3
    assert err is None


def test_parse_guess_negative_number_is_accepted():
    """'-5' is a valid integer parse — range validation is the game's job, not parse_guess."""
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5


def test_parse_guess_very_large_number():
    """Extremely large numbers should parse without crashing."""
    ok, value, err = parse_guess("999999999")
    assert ok is True
    assert value == 999999999


def test_parse_guess_whitespace_only_rejected():
    """A string of spaces contains no number and must be rejected."""
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert value is None


def test_check_guess_boundary_exact_match_at_one():
    """Boundary value: guess == secret == 1 must return Win."""
    outcome, _ = check_guess(1, 1)
    assert outcome == "Win"


def test_check_guess_negative_guess_is_too_low():
    """A negative guess against a positive secret must be Too Low."""
    outcome, _ = check_guess(-1, 50)
    assert outcome == "Too Low"


def test_check_guess_zero_against_positive_secret():
    """Guessing 0 when secret is any positive number must be Too Low."""
    outcome, _ = check_guess(0, 1)
    assert outcome == "Too Low"
