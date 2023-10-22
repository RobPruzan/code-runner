import inspect
import json
import os
import sys
from types import FrameType
from typing import Any, List, NamedTuple, TypedDict, Union
from enum import Enum


# whats concatenated:
# @dataclass
# class Node:
#     ID: string
#     value: int


# def algorithm(adjList: Dict[Node, Node], start_node: Node):
#     # your code here
#     pass


class Node(NamedTuple):
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
import inspect
import json
import sys
from types import FrameType
from typing import Any, List, NamedTuple, TypedDict, Union
from enum import Enum


class Tag(Enum):
    Line = "Line"
    Call = "Call"
    Return = "Return"


class Frame(TypedDict):
    line: int
    name: str
    args: dict[str, Any]  # inspect.ArgInfo.asdict() result


class Step(TypedDict):
    tag: Tag  # This is the type of the stringified object
    visualization: Union[List[List[Node]], List[Node]]
    frames: List[Frame]
    line: int


_STEPS: List[Step] = []
_GLOBAL_VISUALIZATION: Union[List[Node], List[List[Node]]] = []


def get_full_trace(current_frame: FrameType) -> List[Frame]:
    if current_frame.f_back is None:
        return []
    partial_frames = get_full_trace(current_frame=current_frame.f_back)
    arg_values = inspect.getargvalues(current_frame)
    # slightly hacky way to ensure locals are serializable
    filtered = {}
    for k, v in arg_values.locals.items():
        try:
            json.dumps(v)
            filtered[k] = v
        except:
            filtered[k] = str(v)
    partial_copied_arg_vales = inspect.ArgInfo(
        args=arg_values.args,
        keywords=arg_values.keywords,
        varargs=arg_values.varargs,
        locals=filtered,
    )
    partial_frames.append(
        Frame(
            line=current_frame.f_lineno,
            name=current_frame.f_code.co_name,
            args=partial_copied_arg_vales._asdict(),
        )
    )
    return partial_frames


def tracing_callback(frame: FrameType, event, arg):
    copied_global_vis = []
    for node in _GLOBAL_VISUALIZATION:
        if isinstance(node[0], list):
            print("what", node)
            copied_global_vis.append([n._asdict() for n in node])  # type:ignore
        else:
            copied_global_vis.append(node._asdict())

    full_trace = get_full_trace(frame)
    current_frame = full_trace[-1]
    locals = current_frame["args"].get("locals", {})
    if locals.get("_cls") == "<class '__main__.Node'>":
        # don't trace node accesses (registers as lambda since it's a namedtuple)
        return tracing_callback
    if event == "call":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Call,
            visualization=copied_global_vis,
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    elif event == "line":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Line,
            visualization=copied_global_vis,
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    elif event == "return":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Return,
            visualization=copied_global_vis,
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    return tracing_callback


adjacencyList = json.loads(os.getenv("ADJACENCY_LIST", "[]"))
adjacencyList = [Node(ID=node[0], value=node[1]) for node, neighbors in adjacencyList]

start_node = Node(
    ID=json.loads(os.getenv("START_NODE", "")),
    value=json.loads(os.getenv("START_NODE_VALUE", "")),
)

sys.settrace(tracing_callback)
algorithm(adjacencyList, start_node)  # type:ignore
sys.settrace(None)
print("{parse_var}")  # type:ignore

serializable_STEPS = []
for idx, step in enumerate(_STEPS):
    serializable_STEPS.append(
        {
            **_STEPS[idx],
            "tag": step.get("tag").value,
        }
    )
print(json.dumps(serializable_STEPS))
