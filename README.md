# Auto Solitaire
This Python application is designed to win every game of [Solitaire](https://play.google.com/store/apps/details?id=com.dna.solitaireapp).

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features
- Interfaces with Samsung Android S23+, which hosts the Solitaire game.
- Uses a game variant that allows unlimited undos and draws from the stock one card at a time.
- Reads game state by taking screen captures using OpenCV and updating an internal data structure.
- Sends inputs to device using Android Debug Bridge.
- Uses a simple set of heuristics to make more efficient moves.

## Installation
1. Clone the repository
```bash
git clone ssh://git@github.com/DeathEel/auto_solitaire.git
cd auto_solitaire
```

2. Create and activate a Python virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Install [Android SDK platform-tools](https://developer.android.com/studio/releases/platform-tools) and [scrcpy](https://github.com/Genymobile/scrcpy) for your local machine
```bash
# If local machine is run on Linux
sudo apt install adb scrcpy
```

## Usage
1. Run the main script
```bash
python main.py
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
