# TODO: Have decks less than 2 cards appear as a "Card" object.
#   (Shouldn't happen often)
import os
import requests
import urllib.request
from PIL import Image
import json
from base64 import b64encode


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

    list_dir = os.listdir(".")
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
    decks = []
    for deck_idx, deck in enumerate(decklist_dict["decks"]):
        deck_id = deck_idx + 1
        deck_ids = [100*deck_id + card_idx for card_idx in range(len(deck["cards"]))]
        cards = [{
            "Name": "Card",
            "Transform": {
                "posX": 0.0,
                "posY": 0.0,
                "posZ": -6.50,
                "rotX": 0.0,
                "rotY": 0.0,
                "rotZ": 0.0,
                "scaleX": 1.0,
                "scaleY": 1.0,
                "scaleZ": 1.0
            },
            "Nickname": card["name"],
            "Description": card["desc"],
            "CardID": deck_ids[card_idx]
        } for card_idx, card in enumerate(deck["cards"])]

        decks.append({
            "Name": "DeckCustom",
            "Transform": {
                "posX": 0.0,
                "posY": 0.0,
                "posZ": -6.50,
                "rotX": 0.0,
                "rotY": 0.0,
                "rotZ": 0.0,
                "scaleX": 1.0,
                "scaleY": 1.0,
                "scaleZ": 1.0
            },
            "Nickname": "{} {} Deck".format(decklist_dict["name"], deck["name"].capitalize()),
            "DeckIDs": deck_ids,
            "CustomDeck": {
                str(deck_id): {
                    "FaceURL": img_urls[deck_idx],
                    # Image of the back of card found in another mod:
                    "BackURL": "http://cloud-3.steamusercontent.com/ugc/925921299334738938/83EE3D4F457FE0CD9251F7318E9FE6CAC92D6FF9/"
                }
            },
            "ContainedObjects": cards
        })

    decklist_tts_obj = {
        "Name": "Bag",
        "Transform": {
            "posX": 0.0,
            "posY": 0.0,
            "posZ": -6.50,
            "rotX": 0.0,
            "rotY": 0.0,
            "rotZ": 0.0,
            "scaleX": 1.0,
            "scaleY": 1.0,
            "scaleZ": 1.0
        },
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

os.chdir(decklists_path)

# could implement an asynchronous process to only have to iterate through
#   the deck info once, but I am ignorant
decklists = [folder for folder in os.listdir() if os.path.isdir(folder)]
for decklist_name in decklists:
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

                os.chdir(decklist_path)

                with open("deck_image_urls.txt", "w") as image_url_file:
                    for img in png_imgs:
                        img_path = os.path.join("images", img)
                        image_url_file.writelines(get_imgur_link(img_path))

            os.chdir(decklist_path)

            tts_obj_path = "{}.json".format(decklist_name)
            if tts_obj_path not in dir_list:
                with open("deck_image_urls.txt", "r") as image_url_file:
                    deck_image_urls = image_url_file.read().split("\n")

                with open(tts_obj_path, "w") as tts_json:
                    json.dump(make_tts_object(decklist_dict, deck_image_urls), tts_json, indent="  ")

            os.chdir(decklist_path)

