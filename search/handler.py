from abc import ABCMeta, abstractmethod

from search.exception import SearchException
from search.index_node import IndexNode


class Response(metaclass=ABCMeta):
    @abstractmethod
    def __str__(self):
        pass


class IndexResponse(Response):
    def __init__(self, doc_id: int):
        self.doc_id = doc_id

    def __str__(self):
        return f"index ok {self.doc_id}"


class FailureResponse(Response):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"index error {self.message}"


class QueryResponse(Response):
    def __init__(self, doc_ids: list[int]):
        self.doc_ids = doc_ids

    def __str__(self):
        doc_id_str = ' '.join([str(doc_id) for doc_id in self.doc_ids])
        return f"query results {doc_id_str}"


class Handler(metaclass=ABCMeta):
    @abstractmethod
    def handle(self, index_root: IndexNode, args: list[str]) -> Response:
        pass


class HandlerFactory:
    _instance = None

    def __init__(self):
        self.handlers = dict()

    @staticmethod
    def instantiate():
        if not HandlerFactory._instance:
            HandlerFactory._instance = HandlerFactory()
        return HandlerFactory._instance

    def register_handler(self, command: str, handler: Handler):
        self.handlers[command] = handler

    def get_handler(self, command: str) -> Handler:
        try:
            return self.handlers[command]
        except IndexError as error:
            raise SearchException(f"COMMAND_NOT_FOUND({command})")