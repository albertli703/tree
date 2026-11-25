import os
import re
import json
import sys


def natural_key(text):
    return [
        int(c) if c.isdigit() else c.lower()
        for c in re.split(r'(\d+)', text)
    ]


def long_path(path):
    path = os.path.abspath(path)

    if os.name == "nt":
        if not path.startswith("\\\\?\\"):
            path = "\\\\?\\" + path

    return path


def scan_folder(path):

    node = {
        "name": os.path.basename(path) or path,
        "type": "folder",
        "children": []
    }

    total_files = 0
    total_folders = 0
    total_size = 0

    try:
        entries = list(os.scandir(long_path(path)))
    except Exception:
        node["error"] = True
        return node

    dirs = []
    files = []

    for e in entries:

        try:
            if e.is_dir(follow_symlinks=False):
                dirs.append(e)
            else:
                files.append(e)
        except:
            pass

    dirs.sort(key=lambda x: natural_key(x.name))
    files.sort(key=lambda x: natural_key(x.name))

    for d in dirs:

        child = scan_folder(d.path)

        node["children"].append(child)

        total_files += child.get("files",0)
        total_folders += child.get("folders",0) + 1
        total_size += child.get("size",0)

    for f in files:

        try:

            stat = f.stat()

            node["children"].append({
                "type":"file",
                "name":f.name,
                "size":stat.st_size,
                "modified":int(stat.st_mtime)
            })

            total_files += 1
            total_size += stat.st_size

        except:
            pass

    node["files"] = total_files
    node["folders"] = total_folders
    node["size"] = total_size

    return node


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print('python tree_to_json.py "folder"')
        sys.exit()

    root = sys.argv[1]

    print("Scanning...")
    root_node = scan_folder(root)

    with open(
        "tree_data.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            root_node,
            f,
            ensure_ascii=False
        )

    print("Done.")
    print("Output: tree_data.json")
