import json

x = {
    "Rectangles": [
        {"name": "Zeit", "xstart": 27, "ystart": 30, "xend": 50, "yend": 50},
        {"name": "Drittel", "xstart": 27, "ystart": 30, "xend": 50, "yend": 50},
    ]
}

json_object = json.dumps(x, indent=4)
with open("Rectangles.json", "w") as outfile:
    outfile.write(json_object)
