# search-engine-spike
A search engine, as part of a practical programming assessment.

## Overview

This repository includes the tools needed to build, test, and use the search engine tool created as part of this system.

## Execution

To execute this Python program:

* (Windows) run.bat
* (Unix/Mac) run.sh

When the program starts, it tries to load index.json from the directory
in which the program is launched, for faster evaluation. If this fails,
the program loads a blank index, which can then be added and queried.

There are four special commands:

* load - Loads index.json from the current directory, if possible; otherwise, resets the loaded index.
* save - Saves the current index to index.json in the current directory, if possible.
* clear - Clears the current index, removes all indexed documents
* exit - Quits the program

## Requirements

* This search engine contains a set of documents, each with unique ID and a list of tokens.
* The search engine responds to queries by finding documents which contain certain tokens and returning their IDs.
* The program should accept a sequence of commands from standard input and respond on standard output.
* Commands are terminated by newlines.
* There are two types of commands: index and query. These are described below.
* Any language may be used. (I'm choosing Python)
* Standard and open-source libraries and online materials/books may be used.
* Try to make the implementation reasonably fast, for a fairly large number of documents (est. 10k documents).
* Query speed is more important than indexing speed!

# Commands

## 1. The index command

```
index doc-id token1 ... tokenN
```

The index command adds a document to the index.

* The doc-id is an integer. 
* Tokens are arbitrary alphanumeric strings.
* A document can contain an arbitrary number of tokens greater than zero.
* The same token may occur more than once in a document. 
* If the doc-id in an index command is the same as in a previously seen index command, the previously stored document should be completely replaced (i.e., only the tokens from the latest command should be associated with the doc-id).

### Examples:

```
index 1 soup tomato cream salt
index 2 cake sugar eggs flour sugar cocoa cream butter
index 1 bread butter salt
index 3 soup fish potato salt pepper
```

When the program successfully processes an index command, it should output:

```
index ok <doc-id>
```

If the program sees an invalid index command (e.g, a token contains a non-alphanumeric character, or a doc-id is not an integer) it should report an error to standard output and continue processing commands. The error output should have the following form:

```
index error <error-message>
```

## 2. The query command

```
query <expression>
```

* The <expression> is an arbitrary expression composed of alphanumeric tokens and the special symbols &, |, (, and ).
* The simplest expression is a single token, and the result of executing this query is a list of the IDs of the documents that contain the token.
* More complex expressions can be built by using the operations of set conjunction (denoted by &) and disjunction (denoted by |).
* The & and | operation have equal precedence and are commutative and associative.
* Parentheses have the standard meaning.
* Parentheses are mandatory: `a | b | c` is not valid, `(a | b) | c` must be used (this is to make parsing queries simpler).

Logically, to execute the query the program looks at every document previously specified by the index command, checks if the document matches the query, and outputs the doc-id if it does. However this is suboptimal and much more efficient implementations exist.

Upon reading the query command, the program should execute the query and produce the following output:

```
query results <doc-id1> <doc-id2> ...
```

The doc-ids of the matching documents can be output in arbitrary order. If there is an error, the output should be:

```
query error <error-message>
```

### Examples:

```
query butter -> query results 2 1
query sugar -> query results 2
query soup -> query results 3
query (butter | potato) & salt -> query results 1 3
```
