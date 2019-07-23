# Copyright (C) 2019 Jansen Tan
#
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

# TODO: Have decks less than 2 cards appear as a "Card" object.
#   (Shouldn't happen often)
import os
import requests
import urllib.request
from PIL import Image
import json
from base64 import b64encode
import sys


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

    list_dir = [os.path.splitext(path)[0] for path in os.listdir(".")]
    list_dir.sort(key=int)
    deck_size = len(list_dir)

    (card_width, card_height) = Image.open("{}.jpg".format(list_dir[0])).size
    (deck_width, deck_height) = (min(deck_size, 10), min(ceil_div(deck_size, 10), 7))
    (deck_image_width, deck_image_height) = (deck_width * card_width, deck_height * card_height)

    deck_image = Image.new('RGB', (deck_image_width, deck_image_height))
    card_index = 0

    for card in list_dir:
        x_pos = (card_index % deck_width) * card_width
        y_pos = (card_index // deck_width) * card_height

        card_image = Image.open("{}.jpg".format(card))
        deck_image.paste(im=card_image, box=(x_pos, y_pos))

        card_index += 1

    return deck_image


def make_decklist_dict(ydk_filename, decklist_name):
    print("Getting info for {}...".format(decklist_name))

    decklist = []

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

                    decklist.append(deck_dict)

                deck_name = stripped[1:]
                card_list = []

            else:
                # Stripped must be a card id
                card_list.append(get_card_info(stripped))

    decklist_dict = {
        "name": decklist_name,
        "decks": decklist
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
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": "Client-ID {}".format(client_id)}

    response = requests.post(
        url,
        data={
            "image": b64encode(open(img_path, "rb").read()),
            "type": "base64"
        },
        headers=headers
    )

    img_url = ""

    if response:
        img_url = "{}\n".format(response.json()["data"]["link"])
    else:
        # I don't know how to properly handle errors
        print(response.json()["data"]["error"])

    del response

    # If there's an error, just sit and cry
    return img_url


def make_tts_object(decklist_dict, img_urls):
    transform_base = {
        "posX": 0.0,
        "posY": 0.0,
        "posZ": -6.50,
        "rotX": 0.0,
        "rotY": 0.0,
        "rotZ": 0.0,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "scaleZ": 1.0
    }

    decks = []
    for deck_idx, deck in enumerate(decklist_dict["decks"]):
        deck_size = len(deck["cards"])
        deck_id = deck_idx + 1
        deck_ids = [100*deck_id + card_idx for card_idx in range(deck_size)]
        cards = [{
            "Name": "Card",
            "Transform": transform_base,
            "Nickname": card["name"],
            "Description": card["desc"],
            "CardID": deck_ids[card_idx]
        } for card_idx, card in enumerate(deck["cards"])]

        decks.append({
            "Name": "DeckCustom",
            "Transform": transform_base,
            "Nickname": "{} {} Deck".format(decklist_dict["name"], deck["name"].capitalize()),
            "DeckIDs": deck_ids,
            "CustomDeck": {
                str(deck_id): {
                    "FaceURL": img_urls[deck_idx],
                    # Image of the back of card found in another mod:
                    "BackURL": "http://cloud-3.steamusercontent.com/ugc/925921299334738938/83EE3D4F457FE0CD9251F7318E9FE6CAC92D6FF9/",
                    "NumWidth": min(deck_size, 10),
                    "NumHeight": min(ceil_div(deck_size, 10), 7),
                }
            },
            "ContainedObjects": cards
        })

    decklist_tts_obj = {
        "Name": "Bag",
        "Transform": transform_base,
        "Nickname": decklist_dict["name"],
        "ContainedObjects": decks
    }

    tts_object = {
        "ObjectStates": [decklist_tts_obj]
    }

    return tts_object


# TERMINOLOGY:
#   A "card" is in a "deck"
#   A "deck" is in a "decklist"
# Currently, there can be up to 3 decks in a decklist:
#   main,
#   extra, and
#   side.

# Is the absolute path of the program/.py file
decklists_path = os.path.dirname(os.path.realpath(__file__))

saved_objects_path = ""
if sys.platform == "win32":
    saved_objects_path = os.path.expanduser("~/Documents/My Games/Tabletop Simulator/Saves/Saved Objects")
else:
    err_msg = "This platform is not supported. Please create an issue at https://github.com/jansenmtan/YGOtoTTS/issues.\n"
    print(err_msg)
    input("Press enter to continue.")
    raise Exception(err_msg)

os.chdir(decklists_path)

# could implement an asynchronous process to only have to iterate through
#   the deck info once, but I am ignorant
decklists = [folder for folder in os.listdir(".") if os.path.isdir(folder)]
for decklist_name in decklists:
    decklist_path = os.path.join(decklists_path, decklist_name)
    os.chdir(decklist_path)

    dir_list = os.listdir(".")
    dir_exts_list = [os.path.splitext(filename)[1] for filename in dir_list]

    for file in dir_list:
        if file.endswith(".ydk"):
            decklist_info_name = "decklist_info.json"
            if decklist_info_name not in dir_list:
                decklist_dict = make_decklist_dict(file, decklist_name)
                with open(decklist_info_name, "w") as decklist_info:
                    json.dump(decklist_dict, decklist_info, indent="  ")

            else:
                with open(decklist_info_name, "r") as decklist_info:
                    decklist_dict = json.load(decklist_info)

            if "images" not in dir_list:
                os.mkdir("images")
                os.chdir("images")
                get_decklist_images(decklist_dict)

            else:
                os.chdir("images")

            if "deck_image_urls.txt" not in os.listdir("."):
                # Current dir is still images

                deck_image_ext = ".jpg"

                # Basically just checks if theres a "main.*" if there's a main deck,
                #   "side.*" if there's a side deck, etc.
                deck_names = [deck["name"] for deck in decklist_dict["decks"]]
                if deck_names != [os.path.splitext(filename)[0] for filename in os.listdir(".")]:
                    # then create them
                    for deck in decklist_dict["decks"]:
                        os.chdir(deck["name"])
                        deck_image = make_deck_image()
                        os.chdir("..")
                        deck_image.save("{}.png".format(deck["name"]))
                        deck_image.save("{}_compressed{}".format(deck["name"], deck_image_ext), quality=65, optimize=True)

                os.chdir(os.path.join(decklist_path, "images"))

                deck_image_paths = ["{}_compressed{}".format(deck["name"], deck_image_ext) for deck in decklist_dict["decks"]]
                with open("deck_image_urls.txt", "w") as image_url_file:
                    for img in deck_image_paths:
                        image_url_file.writelines(get_imgur_link(img))

            os.chdir(saved_objects_path)

            tts_obj_path = "{}.json".format(decklist_name)
            if tts_obj_path not in os.listdir("."):
                with open(os.path.join(decklist_path, "images/deck_image_urls.txt"), "r") as image_url_file:
                    deck_image_urls = image_url_file.read().split("\n")

                tts_object = make_tts_object(decklist_dict, deck_image_urls)
                with open(tts_obj_path, "w") as tts_json:
                    json.dump(tts_object, tts_json, indent="  ")

            os.chdir(decklist_path)
