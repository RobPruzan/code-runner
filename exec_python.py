import os, json

from dataclasses import dataclass, asdict
from typing import List, Dict

# whats concatenated:
# @dataclass
# class Node:
#     ID: string
#     value: int


# def algorithm(adjList: Dict[Node, Node], start_node: Node):
#     # your code here
#     pass

# def apply_dict(step):
#     if (type(step) == list):
#         if len(step) > 0 and type(step[0]) == list:
#             return [s.as]


@dataclass(
    eq=True,
    frozen=True,
)
class Node:
    ID: str
    value: int

    # def __json__(self):
    #     dct = {"ID": self.ID, "value": self.value}
    #     return json.dumps(dct)


class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        # if hasattr(obj, 'dictify'):
        #     return obj.dictify()
        # return super
        return asdict(obj)


_node = lambda node: Node(ID=node.split(",")[0], value=int(node.split(",")[1]))


adjacencyList = {
    _node(node): [Node(n, v) for n, v in neighbors]
    for node, neighbors in json.loads(os.getenv("ADJACENCY_LIST", "[]")).items()
}
has_start_node = (
    True
    if bool(os.getenv("START_NODE")) and bool(os.getenv("START_NODE_VALUE"))
    else False
)
start_node = (
    Node(
        ID=json.loads(os.getenv("START_NODE")),
        value=json.loads(os.getenv("START_NODE_VALUE")),
    )
    if has_start_node
    else "NO-START-NODE-SELECTED"
)


# def is_bst(adj_list, node, min_value=float('-inf'), max_value=float('inf')):
#     if node is None:
#         return True
#     if not min_value <= node.value <= max_value:
#         return False

#     children = adj_list.get(node.id, [])
#     if len(children) > 2:
#         return False

#     if len(children) == 1:
#         return is_bst(adj_list, children[0], min_value, node.value) or is_bst(adj_list, children[0], node.value, max_value)
#     elif len(children) == 2:
#         return is_bst(adj_list, children[0], min_value, node.value) and is_bst(adj_list, children[1], node.value, max_value)
#     return True


