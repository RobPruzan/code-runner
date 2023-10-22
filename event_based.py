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


class Node(NamedTuple):
    ID: str
    value: int


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


def test(z):
    a = 2
    b = 3
    _GLOBAL_VISUALIZATION.append(Node(value=2, ID="sup"))
    c = 2 + 3
    d = a + b + c
    return d + 42


sys.settrace(tracing_callback)
result = test(69)
sys.settrace(None)


serializable_STEPS = []
for idx, step in enumerate(_STEPS):
    huh = {
        **_STEPS[idx],
        "tag": step.get("tag").value,
    }

    serializable_STEPS.append(huh)

# print(serializable_STEPS)
for i in json.loads(json.dumps(serializable_STEPS)):
    print(i)
# print(json.dumps(serializable_STEPS))
