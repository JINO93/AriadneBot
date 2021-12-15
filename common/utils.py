import json
import os


def load_config(path):
    path = f"{os.getcwd()}/{path}"
    if not os.path.exists(path):
        print(f"load_config failed,path:{path} no exist.")
        return None
    with open(path, "r", encoding='utf-8') as f:
        return json.loads(f.read())


def save_config(path, content):
    with open(path, "w") as f:
        json.dump(content, f)
