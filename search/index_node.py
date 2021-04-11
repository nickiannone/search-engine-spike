from __future__ import annotations

import json

from search.exception import SearchQueryException, SearchIndexException


class IndexNode:
    """
    Index node for our search indexing system.
    We're using a single character per branch every time, to ensure that we don't have to do any rebalancing and
    shuffling to optimize index creation. This will also mean we have slightly less optimal search than a properly
    balanced index, but I'm not building ElasticSearch in 3 hours!
    """

    def __init__(self,
                 char: chr = None,
                 doc_ids: list[int] = None,
                 parent: IndexNode = None):
        self.doc_ids = doc_ids if doc_ids is not None else list[int]()
        self.char = char
        self.children = dict[IndexNode]()
        self.parent = parent
        if parent is not None:
            parent._add_child(self)

    def __str__(self):
        return json.dumps(self.json())

    def __del__(self):
        self.children = None
        self.parent = None

    def _add_child(self, child: IndexNode):
        if child is not None and child.parent is not None:
            child.parent._remove_child(self)
        self.children[child.char] = child
        child.parent = self
        return child

    def _remove_child(self, child: IndexNode):
        if child and child.char in self.children and self.children[child.char] == child:
            self.children.pop(child.char)
            child.parent = None
        return child

    def json(self):
        payload = {
            'char': self.char,
            'doc_ids': self.doc_ids
        }
        if len(self.children) > 0:
            children = dict[IndexNode]()
            for char in self.children:
                children[char] = self.children[char].json()
            payload['children'] = children
        return payload

    @staticmethod
    def parse(raw: dict, parent: IndexNode = None):
        try:
            parsed_node = IndexNode(doc_ids=raw['doc_ids'],
                                    char=raw['char'],
                                    parent=parent)
            if 'children' in raw:
                raw_children = raw['children']
                for token in raw_children:
                    IndexNode.parse(raw_children[token], parsed_node)
            return parsed_node
        except Exception as ex:
            raise SearchIndexException("SEARCH_PARSE_FAILED") from ex

    def get_doc_ids_containing_token(self, token: str, full_token: str = None) -> list:
        """
        Retrieves all doc_ids containing the given token.
        :param token: The current token
        :param full_token: The token from the original call of this method.
        :return: The set of doc_ids containing the given token
        :raises: SearchQueryException if we weren't able to find the token in the index!
        """
        if len(token) == 0:
            return self.doc_ids
        if full_token is None:
            full_token = token
        first, rest = token[0], token[1:]
        if first in self.children and self.children[first] is not None:
            return self.children[first].get_doc_ids_containing_token(rest, full_token)
        raise SearchQueryException(f"SEARCH_QUERY_TOKEN_NOT_FOUND({full_token})")

    def recursive_add_token_for_doc_id(self, doc_id: int, token: str, full_token: str = None) -> IndexNode:
        """
        Adds the specified doc_id at the given index for the token, creating a node if necessary.
        :param doc_id: The document ID
        :param token: The token to add.
        :param full_token: Used for recursively searching the node tree.
        :return: The node for the given token.
        """
        if len(token) == 0:
            # This node matches the last token, so add the doc ID here.
            if doc_id not in self.doc_ids:
                self.doc_ids.append(doc_id)
            return self
        if full_token is None:
            full_token = token
        first, rest = token[0], token[1:]
        if first in self.children and self.children[first] is not None:
            # Drop down to the existing node for this character, and add there
            child_node = self.children[first]
            return child_node.recursive_add_token_for_doc_id(doc_id, rest, full_token)
        else:
            # Add a new node for the next
            new_node = IndexNode(char=first,
                                 parent=self)
            return new_node.recursive_add_token_for_doc_id(doc_id, rest, full_token)

    def recursive_remove_doc_id(self, doc_id):
        if doc_id in self.doc_ids:
            self.doc_ids.remove(doc_id)
        char_set = self.children.keys()
        delete_list = []
        for char in char_set:
            child_node = self.children[char]
            child_node.recursive_remove_doc_id(doc_id)
            if len(child_node.doc_ids) == 0 and len(child_node.children) == 0:
                # Mark this child node for deletion!
                delete_list.append(child_node)
        # Now go through and delete them all!
        for node in delete_list:
            del node

    def add_doc(self, doc_id: int, tokens: list[str]):
        """
        Public method to add a document.
        :param doc_id: The document ID
        :param tokens: The list of string tokens.
        :return: None
        """
        # Remove the doc id and all of its existing tokens, if any!
        self.recursive_remove_doc_id(doc_id)
        # Add each token individually!
        for token in tokens:
            self.recursive_add_token_for_doc_id(doc_id, token)


if __name__ == "__main__":
    # Quick test!
    root = IndexNode()

    root.add_doc(1, ["soup", "tomato", "cream", "salt"])
    assert root.get_doc_ids_containing_token("soup") == [1]
    assert root.get_doc_ids_containing_token("tomato") == [1]
    assert root.get_doc_ids_containing_token("cream") == [1]
    assert root.get_doc_ids_containing_token("salt") == [1]

    root.add_doc(2, ["cake", "sugar", "eggs", "flour", "sugar", "cocoa", "cream", "butter"])
    assert root.get_doc_ids_containing_token("cake") == [2]
    assert root.get_doc_ids_containing_token("sugar") == [2]
    assert root.get_doc_ids_containing_token("eggs") == [2]
    assert root.get_doc_ids_containing_token("flour") == [2]
    assert root.get_doc_ids_containing_token("cocoa") == [2]
    assert root.get_doc_ids_containing_token("cream") == [1, 2]
    assert root.get_doc_ids_containing_token("butter") == [2]

    root.add_doc(1, ["bread", "butter", "salt"])
    assert root.get_doc_ids_containing_token("soup") == []
    assert root.get_doc_ids_containing_token("tomato") == []
    assert root.get_doc_ids_containing_token("cream") == [2]
    assert root.get_doc_ids_containing_token("salt") == [1]
    assert root.get_doc_ids_containing_token("cake") == [2]
    assert root.get_doc_ids_containing_token("sugar") == [2]
    assert root.get_doc_ids_containing_token("eggs") == [2]
    assert root.get_doc_ids_containing_token("flour") == [2]
    assert root.get_doc_ids_containing_token("cocoa") == [2]
    assert root.get_doc_ids_containing_token("cream") == [2]
    assert root.get_doc_ids_containing_token("butter") == [2, 1]

    root.add_doc(3, ["soup", "fish", "potato", "salt", "pepper"])
    assert root.get_doc_ids_containing_token("soup") == [3]
    assert root.get_doc_ids_containing_token("tomato") == []
    assert root.get_doc_ids_containing_token("cream") == [2]
    assert root.get_doc_ids_containing_token("salt") == [1, 3]
    assert root.get_doc_ids_containing_token("cake") == [2]
    assert root.get_doc_ids_containing_token("sugar") == [2]
    assert root.get_doc_ids_containing_token("eggs") == [2]
    assert root.get_doc_ids_containing_token("flour") == [2]
    assert root.get_doc_ids_containing_token("cocoa") == [2]
    assert root.get_doc_ids_containing_token("cream") == [2]
    assert root.get_doc_ids_containing_token("butter") == [2, 1]
    assert root.get_doc_ids_containing_token("fish") == [3]
    assert root.get_doc_ids_containing_token("pepper") == [3]
