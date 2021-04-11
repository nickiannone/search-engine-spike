from search.exception import SearchQueryException
from search.handler import Handler, Response, FailureResponse, QueryResponse
from search.index_node import IndexNode
from search.query import QueryToken


class QueryHandler(Handler):
    def handle(self, root: IndexNode, args: list[str]) -> Response:
        if len(args) < 1:
            return FailureResponse(f"SEARCH_QUERY_TOO_FEW_ARGS({args})")

        try:
            # Parse the args list into a query
            query = QueryToken.parse(args)

            # Apply the query tree to the index and give out our responses
            results = query.evaluate(root)

            # Return the response.
            return QueryResponse(results)

        except SearchQueryException as ex:
            return FailureResponse(str(ex))
