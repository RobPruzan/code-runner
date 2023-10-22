import inspect
import json
import os
import sys
from types import FrameType
from typing import Any, List, TypedDict, Union
from enum import Enum


# whats concatenated:
# @dataclass
# class Node:
#     ID: string
#     value: int


# def algorithm(adjList: Dict[Node, Node], start_node: Node):
#     # your code here
#     pass


class Node(TypedDict):
    ID: str
    value: int


_node = lambda node: Node(ID=node.split(",")[0], value=int(node.split(",")[1]))


adjacencyList = {
    _node(node): [Node(n, v) for n, v in neighbors]  # type:ignore
    for node, neighbors in json.loads(os.getenv("ADJACENCY_LIST", "[]")).items()
}
has_start_node = (
    True
    if bool(os.getenv("START_NODE")) and bool(os.getenv("START_NODE_VALUE"))
    else False
)
start_node = (
    Node(
        ID=json.loads(os.getenv("START_NODE")),  # type:ignore
        value=json.loads(os.getenv("START_NODE_VALUE")),  # type:ignore
    )
    if has_start_node
    else "NO-START-NODE-SELECTED"
)


# def stack(f):
#     def handler(*args, **kwargs):
#         stack = traceback.
