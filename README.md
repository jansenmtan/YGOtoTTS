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
you can insert your own direct image links at this file: `images/deck_image_urls.txt`

If you don't trust the executable, you can build it yourself from the source code.

## Building

I used PyInstaller to build an executable.

If you don't have Python, [get it here](https://www.python.org/).

There are build scripts in the root directory. 
If you're on Windows, run `build.bat`. 
If you're on macOS or Linux, run `build.sh`.

The executable will be at the folder `dist/`

If you plan on distributing your binary, you should format it like so:
```
[name]-[platform]
```
where the platform is specified here: https://docs.python.org/3.7/library/sys.html#sys.platform