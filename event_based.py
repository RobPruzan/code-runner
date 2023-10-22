import inspect
from dataclasses import dataclass, asdict
import json
import sys
from types import FrameType
from typing import Any, Dict, List, Deque, Union
from collections import deque
from functools import wraps
from enum import Enum


class Tag(Enum):
    Line = "Line"
    Call = "Call"
    Return = "Return"


@dataclass
class Frame:
    line: int
    name: str
    args: inspect.ArgInfo


@dataclass(
    eq=True,
    frozen=True,
)
class Node:
    ID: str
    value: int


@dataclass
class Step:
    tag: Tag  # This is the type of the stringified object
    visualization: str  # Union[List[List[Node]], List[Node]]
    frames: List[Frame]
    line: int


# class ListWithStackVis(list):
#     def append(self, item: Union[Node, List[Node]]):
#         super().append(item)

#     def extend(self, iterable):
#         super().extend(iterable)

#     def insert(self, index, item: Union[Node, List[Node]]):
#         super().insert(index, item)

#     def remove(self, item: Union[Node, List[Node]]):
#         super().remove(item)

#     def pop(self, index=-1):
#         return super().pop(index)

#     def clear(self):
#         super().clear()

#     def __delitem__(self, index):
#         super().__delitem__(index)

#     def __setitem__(self, index, item: Union[Node, List[Node]]):
#         super().__setitem__(index, item)

#     def __iadd__(self, other):
#         return super().__iadd__(other)

#     def __imul__(self, other):
#         return super().__imul__(other)

#     def reverse(self):
#         super().reverse()

#     def sort(self, *args, **kwargs):
#         super().sort(*args, **kwargs)


_STEPS: List[Step] = []
_GLOBAL_VISUALIZATION: Union[List[Node], List[List[Node]]] = []


class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        return asdict(obj)


def get_full_trace(current_frame: FrameType):
    if current_frame.f_back is None:
        return []
    partial_frames = get_full_trace(current_frame=current_frame.f_back)
    filtered = {}
    for k, v in current_frame.f_locals.items():
        if k == "args":
            # exclude the first item since that will be "self" in the method
            filtered[k] = v[1:]
            continue
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
            args=partial_copied_arg_vales,
        )
    )
    return partial_frames


def tracing_callback(frame: FrameType, event, arg):
    if event == "call":
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Call,
            visualization=json.dumps(_GLOBAL_VISUALIZATION, cls=ExtendedEncoder),
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    elif event == "line":
        # print("Executing line in", frame.f_code.co_name)
        # print("Local variables:", frame.f_locals)
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Line,
            visualization=json.dumps(_GLOBAL_VISUALIZATION, cls=ExtendedEncoder),
            line=frame.f_lineno,
        )
        _STEPS.append(new_step)
    elif event == "return":
        # print("Exiting", frame.f_code.co_name)
        # print("Return value:", arg)
        new_step = Step(
            frames=get_full_trace(frame),
            tag=Tag.Return,
            visualization=json.dumps(_GLOBAL_VISUALIZATION, cls=ExtendedEncoder),
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


for step in _STEPS:
    print(step, end="\n\n")
