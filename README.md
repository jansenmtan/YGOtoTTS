# YGOtoTTS

A tool to automate importing Yu-Gi-Oh decks to Tabletop Simulator

This is done by using YGOPRODeck (.ydk) files found at <https://ygoprodeck.com> and using the API at <https://db.ygoprodeck.com>.


## Setup

Get the program at the release page.

Your directory should look like this:

```
general yu-gi-oh folder
|
├── Name of some deck
|   └── some file.ydk
|
├── Name of other deck
|   └── other file.ydk
|
├── YGOtoTTS program
|
└── ...
```

## Usage

Run the program. The deck is ready to spawn in-game in Tabletop Simulator.

If the images are taking too long to upload (program stuck on `Uploading images to remote host...`),
you can insert your own image links at this file: `images/deck_image_urls.txt`

If you don't trust the executable, you can build it yourself from the source code.

## Building

I used PyInstaller to build an executable.

If you don't have Python, [get it here](https://www.python.org/).

See the [PyInstaller quickstart](https://www.pyinstaller.org).

I recommend using the flag `-F`. For example,
```
python -m pyinstaller -F YGOtoTTS.py
```