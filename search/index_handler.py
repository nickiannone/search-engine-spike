from search.handler import Handler, Response, FailureResponse, IndexResponse
from search.index_node import IndexNode


class IndexHandler(Handler):
    def handle(self, root: IndexNode, args: list[str]) -> Response:
        """
        Handles an index request from the given args list, using the given root node.
        :param root: The root node for the tree.
        :param args: The list of arguments to process.
        :return: A Response which can be serialized.
        """
        if len(args) < 2:
            return FailureResponse(f"SEARCH_INDEX_TOO_FEW_ARGS({args})")

        # Parse the doc ID
        try:
            doc_id = int(args[0])
        except ValueError as e:
            return FailureResponse(f"SEARCH_INDEX_INVALID_DOC_ID({args[0]})")

        # Split off the rest of the tokens
        tokens = args[1:]

        try:
            # Add the document, and return the appropriate response.
            root.add_doc(doc_id, tokens)
            return IndexResponse(doc_id)
        except Exception as ex:
            return FailureResponse(str(ex))

