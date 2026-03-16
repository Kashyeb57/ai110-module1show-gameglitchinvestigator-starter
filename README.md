# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### Game Purpose
This is a number-guessing game built with Streamlit. The player picks a difficulty (Easy, Normal, or Hard), then tries to guess a randomly chosen secret number within a limited number of attempts. After each guess the game gives a hint ("Go Higher" or "Go Lower") and updates a score. The goal is to guess the correct number before running out of attempts.

### Bugs Found

| # | Bug | Where |
|---|-----|-------|
| 1 | Inverted hints — "Too High" said "Go HIGHER!" pushing the player further away | `check_guess` in `app.py` |
| 2 | Score mismatch — debug panel and win message showed different scores | Streamlit render order: debug panel rendered before `update_score` ran |
| 3 | Invalid input saved to history — typing "xyz" stored it in the guess log | `history.append(raw_guess)` ran inside the `if not ok:` branch |
| 4 | New Game broken after win/loss — game stayed permanently stuck | `if new_game:` didn't reset `status`, `score`, or `history` |
| 5 | Info box and debug panel vanished after game over | `st.stop()` halted rendering before those elements were reached |
| 6 | Attempts counter started at 1 instead of 0 | `st.session_state.attempts = 1` on initialization |

### Fixes Applied

- **Refactored** all game logic (`check_guess`, `parse_guess`, `update_score`, `get_range_for_difficulty`) out of `app.py` and into `logic_utils.py`, then imported them back
- **Bug 1** — Swapped the hint message strings in `check_guess` so "Too High" returns "Go LOWER!" and "Too Low" returns "Go HIGHER!"
- **Bug 3** — Removed `history.append(raw_guess)` from the `if not ok:` branch; only valid parsed integers are now appended
- **Bug 4** — Added `st.session_state.status = "playing"`, `st.session_state.score = 0`, and `st.session_state.history = []` to the New Game handler
- **Bug 5** — Moved the info box and debug panel to render *before* the `st.stop()` status check so they always display
- **Bug 6** — Changed attempts initialization from `1` to `0` to match New Game reset behavior

### pytest Results
All 7 tests pass. Run `pytest tests/test_game_logic.py -v` to verify.

## 📸 Demo

![Fixed winning game](Screenshot%202026-03-15%20235334.png)

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
