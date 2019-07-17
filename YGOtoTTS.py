import json
import requests
import os
import urllib.request


def get_card_image(card_id, filename, extension = ".jpg"):
    response = requests.get("https://db.ygoprodeck.com/api/v5/cardinfo.php?name={}".format(card_id))
    card_info = json.loads(response.text)
    image_url = card_info[0]['card_images'][0]['image_url']

    urllib.request.urlretrieve(image_url, "{}{}".format(filename, extension))


# Change this to where your decks are
decks_path = "C:/Users/Jansen/Documents/Yu-Gi-Oh/Decks"

os.chdir(decks_path)

for deck_path in os.listdir():
    os.chdir(decks_path + deck_path)

    skip = False
    ydk_filename = ""

    for file in os.listdir():
        if file.endswith(".ydk"):
            ydk_filename = file
        if file.endswith(".jpg") or file.endswith(".png"):
            skip = True
            break

    if ydk_filename == "":
        skip = True

    if skip:
        continue

    with open(ydk_filename, "r") as deck_file:
        card_index = 0

        for line in deck_file:
            stripped = line.rstrip()
            if stripped.isnumeric():
                get_card_image(stripped, card_index)

                card_index += 1