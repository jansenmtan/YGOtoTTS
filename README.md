# YGOtoTTS

A tool to automate importing Yu-Gi-Oh decks to Tabletop Simulator

This is done by using YGOPRODeck (.ydk) files found at <https://ygoprodeck.com> and using the API at <https://db.ygoprodeck.com>.


## Setup

Get the program at the release page.

Your directory should look like this:

```
general yu-gi-oh folder
|
├── sub folder
|   └── your favorite deck.ydk
|
├── other sub folder
|   └── meta deck.ydk
|
├── YGOtoTTS program
|
└── ...
```

## Usage

Run the program. The finished deck.png file (found in each subfolder) can be imported into TTS.


## Building

All I did was use pyinstaller on YGOtoTTS.py