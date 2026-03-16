# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game it appeared to work on the surface — a number field, a submit button, and a hint message. But after a few guesses it was clear something was wrong: the hints pointed me in the wrong direction every time, my score in the debug panel never matched the score in the win message, and garbage input I accidentally typed showed up permanently in the guess history.

### Bug 1 — Inverted hints (`check_guess`, app.py line 38)

**Expected:** When my guess is higher than the secret number, the game should tell me to go lower. When my guess is lower, it should tell me to go higher.

**What actually happened:** The hints were completely backwards. When I guessed 80 and the secret was 38, the game said "Go HIGHER!" — pushing me further away from the answer. When I guessed 20 with a secret of 47, it said "Go LOWER!" The `>` and `<` operators in `check_guess` have the correct comparison but are paired with the wrong message strings, so every hint is the opposite of what it should be.

---

### Bug 2 — Score in debug panel never matches the win message (`app.py` lines 114–119 vs. 168–179)

**Expected:** The "Score" shown in the Developer Debug Panel and the "Final score" shown in the win message should display the same number.

**What actually happened:** They were always different. For example, the debug panel showed `Score: 0` but the win message said `Final score: 50`. This happens because of how Streamlit reruns work: the debug panel is rendered at the top of the script before the `if submit:` block runs, so it shows the score from *before* the current guess was processed. The win message is rendered *inside* the `if submit:` block after `update_score` is called, so it shows the updated value. The two numbers are always one guess apart.

---

### Bug 3 — Invalid input is saved to guess history (`app.py` lines 152–153)

**Expected:** When I type non-numeric text like "xyz" and click Submit, the game should show an error and leave the history unchanged — the bad input was never a real guess.

**What actually happened:** The error message appeared correctly ("That is not a number."), but the raw string "xyz" was still appended to `st.session_state.history` before the error was returned. The invalid input is permanently stored as if it were a legitimate guess. The validation logic catches the error for display purposes but the `history.append(raw_guess)` call on line 153 runs unconditionally inside the `if not ok:` branch, which means every rejected input still ends up in the history.

---

## 2. How did you use AI as a teammate?

I used Claude Code (Anthropic) as my primary AI tool throughout this project. I shared `#file:app.py` and `#file:logic_utils.py` as context, described glitches I observed while playing, and asked the AI to explain the logic causing each one and help repair the code.

**Correct AI suggestion — Score mismatch caused by Streamlit's render order:**
I described the glitch where the debug panel showed `Score: 0` but the win message said `Final score: 50`. The AI suggested that the cause was Streamlit's top-to-bottom execution order: the debug panel renders at the top of the script before the `if submit:` block runs, so it always shows the score from *before* the current guess was processed. The win message renders *inside* the `if submit:` block after `update_score` is called, so it shows the updated value. This suggestion was **correct**. I verified it by reading through `app.py` line by line and confirming that `st.write("Score:", st.session_state.score)` on line 55 runs before `st.session_state.score = update_score(...)` on line 95 — exactly as the AI described.

**Incorrect AI suggestion — Moving the info box and debug panel below the submit block:**
To fix the stale "Attempts left" count and debug panel, the AI suggested moving both elements to *after* the `if submit:` block so they would always show post-submit state. This suggestion was **incorrect** (incomplete). After applying it, the info box and debug panel completely disappeared whenever the game ended in a win or loss. The reason: `st.stop()` in the status check block halted rendering before those elements were ever reached. I verified this by running the app, finishing a game, and seeing the info and debug sections vanish. The fix required moving those elements to *before* the status check instead — above the `st.stop()` call — so they always render regardless of game state.

---

## 3. Debugging and testing your fixes

A bug was only considered fixed when two things were true: the relevant pytest test passed, and I manually replayed the scenario in the running Streamlit app and saw the correct behavior. Passing the test alone wasn't enough — the score-mismatch bug shows that unit tests can't catch every rendering-order issue in a UI framework, so manual verification was always the final check.

**pytest — targeting Bug #1 (inverted hints):**
I asked the AI to generate tests that called `check_guess` directly and asserted on the *message* string, not just the outcome. The two key tests were:
- `test_too_high_message_says_go_lower`: calls `check_guess(80, 38)` and asserts `"LOWER"` is in the message.
- `test_too_low_message_says_go_higher`: calls `check_guess(20, 47)` and asserts `"HIGHER"` is in the message.

Before the fix, both tests failed because the messages were swapped. After swapping them in `logic_utils.py`, both passed. Running `pytest -v` showed all 7 tests green, confirming no regressions.

**pytest — targeting Bug #3 (invalid input in history):**
The AI suggested testing `parse_guess` in isolation rather than simulating a full Streamlit submit. `test_invalid_input_returns_not_ok` calls `parse_guess("xyz")` and asserts `ok is False` and `value is None`. This verified that the function correctly rejects bad input and gives the caller no value to append — which is the contract the fixed `app.py` now relies on.

**AI help with tests:**
Yes — the AI pointed out that the original three tests in `test_game_logic.py` were broken before I even fixed anything: they asserted `result == "Too High"` but `check_guess` returns a tuple `("Too High", "📉 Go LOWER!")`. The AI suggested unpacking the tuple with `outcome, _ = check_guess(...)`, which fixed the test structure and made the existing tests runnable.

---

## 4. What did you learn about Streamlit and state?

The secret number kept changing in the original app because `st.session_state.secret = random.randint(low, high)` was called unconditionally at the top of the script. Streamlit reruns the entire Python script from top to bottom every time the user clicks a button or interacts with a widget — so a brand new random number was generated on every single click, including every Submit.

Streamlit "reruns" work like this: imagine your script is a recipe that gets cooked from scratch every time someone touches the stove. All your regular variables get reset to their starting values on each cook. `st.session_state` is like a sticky notepad attached to the fridge — it survives between cooks, so anything written there stays until you explicitly erase it. That is why wrapping the secret in `if "secret" not in st.session_state:` fixed the problem: the `if` check means "only write the notepad if it's blank," so the first run picks a number and every rerun after that leaves it alone.

The exact change that gave the game a stable secret was adding that `if "secret" not in st.session_state:` guard before `st.session_state.secret = random.randint(low, high)`.

---

## 5. Looking ahead: your developer habits

One habit I want to reuse is **testing pure functions in isolation with pytest before ever touching the UI**. In this project, `check_guess` and `parse_guess` were pure functions with no Streamlit dependency, which made them trivially testable. Having those tests catch the inverted-hint bug immediately — without having to click through the app — saved a lot of manual back-and-forth. In future projects I will look for the same separation: keep logic in plain functions, keep UI in the UI layer, and write tests for the logic layer first.

One thing I would do differently is **start a fresh AI chat session for each individual bug**. Because everything happened in one long conversation, the AI sometimes carried stale context from an earlier fix into a later one. For example, after moving the info box to fix the stale display issue, the AI initially missed that `st.stop()` would prevent those elements from rendering during game over — a mistake that might not have happened if the session was focused only on that one problem with no prior context to confuse it.

This project changed the way I think about AI-generated code because it showed me that AI output looks polished and complete even when it contains deliberate or subtle bugs. The original starter code had `check_guess` returning the wrong hint messages and silently corrupting history on invalid input — neither bug was visible without actually running and testing the game. AI code needs the same skeptical review as any other code: read it, run it, test it, and don't assume it works just because it looks reasonable.
