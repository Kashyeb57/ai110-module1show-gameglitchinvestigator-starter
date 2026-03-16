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

I used Claude Code (Anthropic) as my primary AI tool throughout this project. I shared the full `app.py` file as context and described specific glitches I observed while playing, then asked the AI to explain the underlying logic causing each one.

**Correct suggestion — Score mismatch explained by Streamlit's execution order:**
I described the glitch where the debug panel showed `Score: 0` while the win message showed `Final score: 50`, and asked the AI to explain the logic. The AI correctly identified that both pieces of UI read the same `st.session_state.score` variable, but the debug panel (lines 114–119) renders *before* the `if submit:` block runs, while the win message renders *inside* it after `update_score` is called. So the debug panel always shows the score from the previous guess, not the current one. I verified this by tracing through the script top-to-bottom myself and confirming the render order matched exactly what the AI described.

**Misleading suggestion — My initial assumption about two separate score variables:**
Before asking the AI, I assumed the mismatch meant there were two *different* score variables that were out of sync — one for the debug panel and one for the win message. This framing was wrong. The AI clarified that it was the same variable (`st.session_state.score`) being read at two different points in a single top-to-bottom rerun, not two separate variables. My initial assumption would have sent me looking for a non-existent second variable, so the AI's correction saved time and redirected me to the real cause.

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

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
