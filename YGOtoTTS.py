import os
import requests
import urllib.request
from PIL import Image


def ceil_div(a, b):
    return -(-a // b)


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


def make_deck_image():
    # We are in the card_images folder

    list_dir = os.listdir()
    deck_size = len(list_dir)

    (card_width, card_height) = Image.open(list_dir[0]).size
    (deck_width, deck_height) = (min(deck_size, 10), ceil_div(deck_size, 10))
    (deck_image_width, deck_image_height) = (deck_width * card_width, deck_height * card_height)

    deck_image = Image.new('RGB', (deck_image_width, deck_image_height))
    (x_pos, y_pos) = (0, 0)
    card_index = 0

    for card in list_dir:
        card_image = Image.open(card)
        deck_image.paste(im=card_image, box=(x_pos, y_pos))

        card_index += 1
        x_pos = (card_index % deck_width) * card_width
        y_pos = (card_index // deck_width) * card_height

    os.chdir("..")
    deck_image.save("deck.png")


os.chdir(".")

# Is the absolute path of the program/.py file
decks_path = os.path.dirname(os.path.realpath(__file__))

for deck_path in os.listdir():
    os.chdir(decks_path + deck_path)

    for file in os.listdir():
        if file.endswith(".ydk"):
            if "card_images" not in os.listdir():
                get_deck_images(file)
                os.chdir("..")

            if "deck.png" not in os.listdir():
                os.chdir("card_images")
                make_deck_image()
