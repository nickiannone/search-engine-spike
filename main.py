#!/usr/bin/python3

# Press the green button in the gutter to run the script.
import json

from search.exception import SearchIndexException
from search.index_node import IndexNode
from search.main import main

if __name__ == '__main__':
    # Load the JSON file, if it exists
    try:
        with open("./index.json", "r") as in_file:
            index = IndexNode.parse(json.loads(in_file.read()))
            print("Loaded index.json successfully")
    except SearchIndexException as ex:
        # We weren't able to load the file, so just create a new index
        print("WARNING - Unable to load index file! Defaulting to empty index...")
        index = IndexNode()

    done = False
    while not done:
        cmd = input("> ")
        if cmd == "save":
            # Save the JSON file
            with open("./index.json", "w") as out_file:
                out_file.write(json.dumps(index.json()))
            print("JSON file saved")
        elif cmd == "load":
            # Reload the JSON file
            try:
                with open("./index.json", "r") as in_file:
                    index = IndexNode.parse(json.loads(in_file.read()))
                    print("Loaded index.json successfully")
            except SearchIndexException as ex:
                # We weren't able to load the file, so just create a new index
                print("WARNING - Unable to load index file! Defaulting to empty index...")
                index = IndexNode()
        elif cmd == "exit":
            # Exit
            print("Bye!")
            done = True
        elif cmd.startswith("clear"):
            index = IndexNode()
            print("Index cleared")
        else:
            args = cmd.split(' ')
            print(main(args, index))

