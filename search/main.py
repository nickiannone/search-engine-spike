from __future__ import annotations

from search.exception import SearchException
from search.handler import HandlerFactory
from search.index_handler import IndexHandler
from search.index_node import IndexNode
from search.query_handler import QueryHandler


def main(argv, index):
    handler_factory = HandlerFactory.instantiate()
    handler_factory.register_handler("index", IndexHandler())
    handler_factory.register_handler("query", QueryHandler())

    if len(argv) < 2:
        raise SearchException("MISSING_ARGS")

    # Split the list into a command and following args
    command, command_args = argv[0], argv[1:]

    # Find the handler for the given command
    handler = handler_factory.get_handler(command)

    # Execute the handler
    response = handler.handle(index, command_args)

    # Return the response
    return response


if __name__ == "__main__":
    root_index = IndexNode()
    assert str(main(["index", "1", "soup", "tomato", "cream", "salt"], root_index)) == "index ok 1"
    assert str(main(["index", "2", "cake", "sugar", "eggs", "flour", "sugar", "cocoa", "cream", "butter"], root_index)) == "index ok 2"
    assert str(main(["index", "1", "bread", "butter", "salt"], root_index)) == "index ok 1"
    assert str(main(["index", "3", "soup", "fish", "potato", "salt", "pepper"], root_index)) == "index ok 3"
    assert str(main(["query", "(butter", "|", "potato)", "&", "salt"], root_index)) == "query results 1 3"

