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
    # Current dir is images
    card_index = 0

    for deck in decklist_dict["decks"]:
        # Current dir is images
        os.mkdir(deck["name"])
        os.chdir(deck["name"])

        for card in deck["cards"]:
            get_card_image(card, "{}".format(card_index), extension=extension)
            card_index += 1

        os.chdir("..")


def make_deck_image():
    # Current dir is the deck images folder

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

    return deck_image


def make_decklist_dict(ydk_filename, decklist_name):
    print("Getting info for {}...".format(decklist_name))

    deck_list = []

    with open(ydk_filename, "r") as ydk_file:
        deck_name = ""
        card_list = []

        for line in ydk_file:
            stripped = line.rstrip()

            if "created by" in stripped:
                continue

            if not stripped.isnumeric():
                # Stripped must be a separate deck (main, extra, side, etc)

                if len(card_list) != 0:
                    deck_dict = {
                        "name": deck_name,
                        "cards": card_list
                    }

                    deck_list.append(deck_dict)

                deck_name = stripped[1:]
                card_list = []

            else:
                # Stripped must be a card id
                card_list.append(get_card_info(stripped))

    decklist_dict = {
        "name": decklist_name,
        "decks": deck_list
    }

    print("Done!")

    return decklist_dict


def get_imgur_link(img_path):
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


# TERMINOLOGY:
#   A "card" is in a "deck"
#   A "deck" is in a "decklist"
# Currently, there can be up to 3 decks in a decklist:
#   main,
#   extra, and
#   side.

# Is the absolute path of the program/.py file
# decklists_path = os.path.dirname(os.path.realpath(__file__))
decklists_path = "C:/Users/Jansen/Documents/Yu-Gi-Oh/Decks"

os.chdir(decklists_path)

for decklist_name in os.listdir():
    decklist_path = os.path.join(decklists_path, decklist_name)
    os.chdir(decklist_path)

    dir_list = os.listdir()
    dir_exts_list = [os.path.splitext(filename)[1] for filename in dir_list]

    for file in dir_list:
        if file.endswith(".ydk"):
            decklist_dict = make_decklist_dict(file, decklist_name)

            if "images" not in dir_list:
                os.mkdir("images")
                os.chdir("images")
                get_decklist_images(decklist_dict)

            else:
                os.chdir("images")

            if "deck_image_urls.txt" not in dir_list:
                # Current dir is still images

                # Basically just checks if theres a "main.png" if there's a main deck,
                #   "side.png" if there's a side deck, etc.
                png_imgs = ["{}.png".format(deck_name) for deck_name in [deck["name"] for deck in decklist_dict["decks"]]]
                if png_imgs not in os.listdir():
                    # then create them
                    for deck in decklist_dict["decks"]:
                        os.chdir(deck["name"])
                        deck_image = make_deck_image()
                        os.chdir("..")
                        deck_image.save("{}.png".format(deck["name"]))

                with open("deck_image_urls.txt", "w") as deck_image_urls:
                    for img in png_imgs:
                        deck_image_urls.writelines(get_imgur_link(img))


            os.chdir(decklist_path)

# back_img_url = "http://cloud-3.steamusercontent.com/ugc/925921299334738938/83EE3D4F457FE0CD9251F7318E9FE6CAC92D6FF9/"
