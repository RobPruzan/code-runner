import inspect
import json
import sys
from types import FrameType
from typing import Any, List, TypedDict, Union
from enum import Enum


class Tag(Enum):
    Line = "Line"
    Call = "Call"
    Return = "Return"


class Frame(TypedDict):
    line: int
    name: str
    args: dict[str, Any]  # inspect.ArgInfo.asdict() result


class Node(TypedDict):
    ID: str
    value: int


class Step(TypedDict):
    tag: Tag  # This is the type of the stringified object
    visualization: Union[List[List[Node]], List[Node]]
    frames: List[Frame]
    line: int


_STEPS: List[Step] = []
_GLOBAL_VISUALIZATION: Union[List[Node], List[List[Node]]] = []


def get_full_trace(current_frame: FrameType):
    if current_frame.f_back is None:
        return []
    partial_frames = get_full_trace(current_frame=current_frame.f_back)
    filtered = {}
    for k, v in current_frame.f_locals.items():
        # if k == "args":
        #     # exclude the first item since that will be "self" in the method
        #     filtered[k] = v[1:]
        #     continue
        if k != "current_frame" and k != "frames" and k != "global_frames" and k != "f":
            filtered[k] = v
    arg_values = inspect.getargvalues(current_frame)

    partial_copied_arg_vales = inspect.ArgInfo(
        args=arg_values.args,
        keywords=arg_values.keywords,
        varargs=arg_values.varargs,
        locals={**arg_values.locals},
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
    if event == "call":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Call,
            visualization=[*_GLOBAL_VISUALIZATION],
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    elif event == "line":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Line,
            visualization=[*_GLOBAL_VISUALIZATION],
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    elif event == "return":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Return,
            visualization=[*_GLOBAL_VISUALIZATION],
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
    serializable_STEPS.append({**_STEPS[idx], "tag": step.get("tag").value})


print(json.dumps(serializable_STEPS))
