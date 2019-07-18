# TODO: Implement making a TTS saved object .json file

import os
import requests
import urllib.request
from PIL import Image
import json


def ceil_div(a, b):
    return -(-a // b)


def get_card_info(card_id):
    response = requests.get("https://db.ygoprodeck.com/api/v5/cardinfo.php?name={}".format(card_id))
    card_info = response.json()
    del response

    # There's only one item in this list
    return card_info[0]


def get_card_image(card_info, filename, extension=".jpg"):
    image_url = card_info['card_images'][0]['image_url']

    urllib.request.urlretrieve(image_url, "{}{}".format(filename, extension))


def get_decklist_images(decklist_dict, extension=".jpg"):
    # Current dir is card_images
    card_index = 0

    for deck in decklist_dict["decks"]:
        # Current dir is card_images
        os.mkdir(deck["name"])
        os.chdir(deck["name"])

        for card in deck["cards"]:
            get_card_image(card, "{}".format(card_index), extension=extension)
            card_index += 1

        os.chdir("..")


def make_deck_image(deck_name):
    # Current dir the deck images folder

    filename = "{}.png".format(deck_name)

    list_dir = os.listdir()
    deck_size = len(list_dir)

    (card_width, card_height) = Image.open(list_dir[0]).size
    (deck_width, deck_height) = (min(deck_size, 10), min(ceil_div(deck_size, 10), 7))
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

    os.chdir("../..")
    deck_image.save(filename)


def make_decklist_dict(ydk_filename, decklist_name):
    decklist_list = []

    with open(ydk_filename, "r") as ydk_file:
        deck_name = ""
        deck_list = []

        for line in ydk_file:
            stripped = line.rstrip()

            if "created by" in stripped:
                continue

            if not stripped.isnumeric():
                # Stripped must be a separate deck (main, extra, side, etc)

                if len(deck_list) != 0:
                    deck_dict = {
                        "name": deck_name,
                        "cards": deck_list
                    }

                    decklist_list.append(deck_dict)

                deck_name = stripped[1:]
                deck_list = []

            else:
                # Stripped must be a card id
                deck_list.append(get_card_info(stripped))

    decklist_dict = {
        "name": decklist_name,
        "decks": decklist_list
    }

    return decklist_dict


def upload_to_imgur(img_path):
    """
    Uploads image from disk to imgur anonymously and returns link to image
    :param img_path: Path to image on disk
    :return: img_url - Link to image
    """
    client_id = "8b9d897b9a78e50"
    url = "http://api.imgur.com/3/upload.json"
    headers = {"Authorization": "Client-ID {}".format(client_id)}

    response = requests.post(
        url,
        headers=headers,
        data={
            "image": img_path,
            "type": file,
        }
    )

    img_url = ""

    if response:
        img_url = response.json()["data"]["link"]
    else:
        # I don't know how to properly handle errors
        print("Error trying to upload {}".format(img_path))
        print("Code {}".format(response.status_code))

    del response

    # If there's an error, just sit and cry
    return img_url


# Is the absolute path of the program/.py file
decklists_path = os.path.dirname(os.path.realpath(__file__))

os.chdir(decklists_path)

for decklist_name in os.listdir():
    decklist_path = os.path.join(decklists_path, decklist_name)
    os.chdir(decklist_path)

    list_dir = os.listdir()
    list_dir_exts = [os.path.splitext(filename)[1] for filename in list_dir]

    for file in list_dir:
        if file.endswith(".ydk"):
            decklist_dict = make_decklist_dict(file, decklist_name)

            if "card_images" not in list_dir:
                os.mkdir("card_images")
                os.chdir("card_images")

                get_decklist_images(decklist_dict)

            if ".png" not in list_dir_exts:
                # Current dir is still card_images
                for deck in decklist_dict["decks"]:
                    os.chdir(deck["name"])
                    make_deck_image(deck["name"])

            os.chdir(decklist_path)

