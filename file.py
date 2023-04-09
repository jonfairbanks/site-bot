import json


def save_json(data, filename):
    try:
        filename = f"{filename}.json"
        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=2)
            print(f"** {filename} saved! **")
            return
    except Exception as e:
        print(f"Failed to save JSON: {e}")
