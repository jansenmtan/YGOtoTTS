# YGOtoTTS

A tool to automate importing Yu-Gi-Oh decks to Tabletop Simulator

This is done by using YGOPRODeck (.ydk) files found at <https://ygoprodeck.com>

Your directory should look like this:

```
general yu-gi-oh folder
|__ sub folder
|   |__ your favorite deck.ydk
|__ other sub folder
|   |__ meta deck.ydk
|__ ...
```

In YGOtoTTS.py: Change `decks_path` to where your decks are located. 

On Windows, change "\\" to "/" in the deck path.
For example, change `C:\Users\Jansen\Documents\Yu-Gi-Oh\Decks` to `C:/Users/Jansen/Documents/Yu-Gi-Oh/Decks`
