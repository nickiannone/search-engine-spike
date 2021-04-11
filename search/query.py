from __future__ import annotations

from search.exception import SearchQueryException
from search.index_node import IndexNode


class QueryToken:
    def __init__(self, token: str):
        self.token = token
        self.left_child = None
        self.right_child = None
        if token in ['&', '|']:
            self.token_type = 'BINOP'
        elif token == '(':
            self.token_type = 'LPAREN'
        elif token == ')':
            self.token_type = 'RPAREN'
        elif token.isalnum():
            self.token_type = 'LITERAL'
        else:
            raise SearchQueryException(f"SEARCH_QUERY_TOKEN_INVALID({token})")

    def __str__(self):
        if self.token_type == 'LPAREN':
            return "("
        if self.token_type == 'RPAREN':
            return ")"
        return f"{self.token}"

    def get_token(self) -> str:
        return self.token

    def get_token_type(self) -> str:
        return self.token_type

    def get_left_child(self):
        return self.left_child

    def get_right_child(self):
        return self.right_child

    def evaluate(self, tree: IndexNode) -> list[int]:
        if self.token_type == 'LITERAL':
            return tree.get_doc_ids_containing_token(self.token)
        if self.token_type == 'BINOP':
            if self.left_child is None:
                raise SearchQueryException(f"SEARCH_QUERY_BINOP_INVALID_LVALUE({self})")
            if self.right_child is None:
                raise SearchQueryException(f"SEARCH_QUERY_BINOP_INVALID_RVALUE({self})")
            lvalue = self.left_child.evaluate(tree)
            rvalue = self.right_child.evaluate(tree)
            if self.token == '|':
                return list(set(lvalue) | set(rvalue))
            if self.token == '&':
                return list(set(lvalue) & set(rvalue))
        raise SearchQueryException(f"SEARCH_QUERY_EVALUATE_FAILED({self})")

    @staticmethod
    def parse(args: list[str]) -> QueryToken:
        # Tokenize
        tokens = []
        for chunk in args:
            for token in QueryToken.tokenize(chunk):
                tokens.append(token)

        # Build an AST query
        return QueryToken.build_tree(tokens)

    @staticmethod
    def tokenize(chunk) -> list[QueryToken]:
        tokens = []
        curr_literal = ""
        for char in chunk:
            if char in ["(", ")", "|", "&"]:
                if len(curr_literal) > 0:
                    tokens.append(QueryToken(curr_literal))
                    curr_literal = ""
                tokens.append(QueryToken(char))
            elif char.isalnum():
                curr_literal += char
            else:
                raise SearchQueryException(f"SEARCH_QUERY_INVALID_CHUNK({chunk})")
        # If we hit the end of the chunk and still have some accumulated literal values:
        if len(curr_literal) > 0:
            tokens.append(QueryToken(curr_literal))
        return tokens

    @staticmethod
    def build_tree(tokens: list[QueryToken]):
        paren_levels = [[]]
        for token in tokens:
            if token.token_type == 'LPAREN':
                # Jump down to the next level of parentheses
                paren_levels.append(list[QueryToken]())
            elif token.token_type == 'BINOP' or token.token_type == 'LITERAL':
                # Add to the current row
                paren_levels[len(paren_levels) - 1].append(token)
            elif token.token_type == 'RPAREN':
                # End the current row and move it up
                if len(paren_levels) == 0:
                    raise SearchQueryException("SEARCH_QUERY_UNEXPECTED_RPAREN")
                # Get the clause composed of all the tokens we wrote into the current paren level
                clause = paren_levels.pop()
                if len(clause) == 0:
                    # Handle empty parentheses
                    continue
                if len(clause) == 1:
                    # Handle a single-token clause
                    if clause[0].token_type == 'LITERAL' or clause[0].token_type == 'BINOP':
                        # Move up as-is
                        paren_levels[len(paren_levels) - 1].append(clause[0])
                        continue
                if len(clause) != 3:
                    # Handle too many/few tokens inside parentheses (error!)
                    raise SearchQueryException(f"SEARCH_QUERY_INVALID_CLAUSE({clause})")
                if clause[1].token_type != "BINOP":
                    # Handle missing binary operation
                    raise SearchQueryException(f"SEARCH_QUERY_MISSING_OPERATION({clause})")
                if clause[0].token_type != "LITERAL" and clause[0].node_type != "BINOP":
                    # Handle invalid lvalue
                    raise SearchQueryException(f"SEARCH_QUERY_LVALUE_INVALID({clause})")
                if clause[2].token_type != "LITERAL" and clause[2].node_type != "BINOP":
                    # Handle invalid rvalue
                    raise SearchQueryException(f"SEARCH_QUERY_RVALUE_INVALID({clause})")
                # We have a valid binary operation, let's add it to the tree
                op = clause[1]
                op.left_child = clause[0]
                op.right_child = clause[2]
                paren_levels[len(paren_levels) - 1].append(op)

        if len(paren_levels) > 1:
            # If we still have
            raise SearchQueryException("SEARCH_QUERY_UNCLOSED_PAREN")

        # Now that we've gotten everything to [ a OP b ] or [ a ], we can make the final tree.
        final_clause = paren_levels[0]
        if len(final_clause) == 1:
            # For [ a ], just return a.
            return final_clause[0]
        if len(final_clause) == 3:
            # For [ a OP b ], return OP(a, b).
            op = final_clause[1]
            op.left_child = final_clause[0]
            op.right_child = final_clause[2]
            return op
        # Everything else throws an error.
        raise SearchQueryException("SEARCH_QUERY_UNKNOWN_ERROR")


if __name__ == "__main__":
    root = QueryToken.parse(["(A", "&", "B)", "|", "C"])
    assert root.token == "|"
    assert root.left_child is not None
    assert root.right_child is not None

    assert root.left_child.token == "&"
    assert root.left_child.left_child is not None
    assert root.left_child.right_child is not None

    assert root.left_child.left_child.token == "A"
    assert root.left_child.left_child.left_child is None
    assert root.left_child.left_child.right_child is None

    assert root.left_child.right_child.token == "B"
    assert root.left_child.right_child.left_child is None
    assert root.left_child.right_child.right_child is None

    assert root.right_child.token == "C"
    assert root.right_child.left_child is None
    assert root.right_child.right_child is None

