import os
import requests
import urllib.request


def get_card_image(card_id, filename, extension=".jpg"):
    response = requests.get("https://db.ygoprodeck.com/api/v5/cardinfo.php?name={}".format(card_id))
    card_info = response.json()
    del response

    image_url = card_info[0]['card_images'][0]['image_url']

    urllib.request.urlretrieve(image_url, "{}{}".format(filename, extension))


def get_deck_images(ydk_filename):
    with open(ydk_filename, "r") as deck_file:
        os.mkdir("card_images")
        os.chdir("card_images")

        card_index = 0

        for line in deck_file:
            stripped = line.rstrip()
            if stripped.isnumeric():
                get_card_image(stripped, card_index)

                card_index += 1


os.chdir(".")

for deck_path in os.listdir():
    os.chdir(deck_path)

    # Check if card images already exist
    if "card_images" in os.listdir():
        continue

    for file in os.listdir():
        if file.endswith(".ydk"):
            get_deck_images(file)
