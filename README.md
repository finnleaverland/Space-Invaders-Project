# Space Invaders

A Space Invaders-style arcade shooter written in Python for my A-level Computer Science
project. The game itself is built with [pygame-ce](https://pyga.me/), and it sits behind a
tkinter account system with registration, logins, password resets and a high-score
leaderboard.

<!-- Add a screenshot: save one as docs/screenshot.png and it will show here. -->
![Gameplay screenshot](docs/screenshot.png)

## Features

- **Arcade gameplay:** waves of aliens that sway and shoot back, five lives, and endless
  waves with a bonus for every wave cleared
- **Mystery alien:** a special enemy crossing the top of the screen that gives a random
  reward: an extra life or 100, 150 or 200 points
- **Player accounts:** register, log in, delete an account, and reset a forgotten password
  by answering a security question
- **Secure password storage:** passwords and security answers are stored as salted
  PBKDF2-HMAC-SHA256 hashes (`hashlib`), never as plain text
- **Leaderboard:** shows the top five players by highest score
- **Algorithms written by hand:** insertion sort keeps accounts in username order, a
  recursive binary search finds accounts, and a bubble sort ranks the leaderboard
- **Tests:** a pytest suite covering the account system

## Getting started

You need Python 3 with tkinter. Tested with Python 3.13 and pygame-ce 2.5 on Windows.
tkinter comes with the python.org installers. On Linux you may need to install it separately
(for example `sudo apt install python3-tk`).

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python -m venv .venv
```

Activate the virtual environment (`.venv\Scripts\activate` on Windows,
`source .venv/bin/activate` on macOS/Linux), then install the dependencies and start the game:

```bash
pip install -r requirements.txt
python main.py
```

> pygame-ce replaces the original `pygame` package. If `pygame` is already installed in the
> same environment, uninstall it first (`pip uninstall pygame`).

Register an account to get started. Accounts and scores are saved in `Clientfile.txt` in the
project folder, which is created the first time you run the game.

## Controls

| Key | Action |
| --- | --- |
| Left / Right arrow | Move the ship |
| Space | Shoot (hold it down to keep firing) |
| Space (after game over) | Return to the menu |
| Esc | Stop playing and return to the menu |

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Project structure

```text
main.py                  Starts the game at the login screen
space_invaders/
    accounts.py          Client and ClientList: accounts, hashing, sorting, searching, saving
    login_screen.py      tkinter login, registration, password reset and account deletion
    menu_screen.py       tkinter menu, how to play and leaderboard
    game.py              The pygame game
assets/
    images/              Sprites and background
    sounds/              Sound effects
tests/
    test_accounts.py     pytest tests for the account system
```

## How passwords are stored

Each password and security answer is hashed with PBKDF2-HMAC-SHA256 using 600,000 iterations
and its own random 16-byte salt, and stored as `pbkdf2_sha256$iterations$salt$hash`. Security
answers are lower-cased and trimmed before hashing, so they aren't case-sensitive. A forgotten
password can't be recovered, only reset. Account files from earlier versions of the game,
which stored plain text, are upgraded to hashes automatically the first time they load.

## Credits

- Sprites (spaceship, bullets and aliens) and sound effects come from the
  [Coding With Russ Space Invaders tutorial](https://github.com/russs123/Space_Invaders).
<!-- TODO: add the source of background.png, mysteryalien.png, explosion1.png and explosion2.png -->

The images and sounds belong to their creators and are **not** covered by this project's
license.

## License

The code is released under the MIT License. See [LICENSE](LICENSE).
