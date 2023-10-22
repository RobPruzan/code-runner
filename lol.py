import inspect
from dataclasses import dataclass
import sys
from types import FrameType
from typing import Any, Dict, List, Deque
from collections import deque
from functools import wraps


@dataclass
class GlobalFrames:
    visualization: List[Any]
    frames: List["Frame"]


_GLOBAL_FRAMES = GlobalFrames(frames=[], visualization=[])
_GLOBAL_FRAME_STEPS: List[GlobalFrames] = []


def trace_func(frame, event, arg):
    if event == "call":
        print("Entering", frame.f_code.co_name)
        print("Arguments:", inspect.getargvalues(frame))
    elif event == "line":
        print("Executing line in", frame.f_code.co_name)
        print("Local variables:", frame.f_locals)
    elif event == "return":
        print("Exiting", frame.f_code.co_name)
        print("Return value:", arg)
    return trace_func


@dataclass
class Frame:
    line: int
    local_vars: List[Dict[Any, Any]]
    name: str


def get_most_recent_frames(current_frame: FrameType, frames: GlobalFrames):
    if current_frame.f_back is None:
        return
    get_most_recent_frames(current_frame=current_frame.f_back, frames=frames)
    # print(current_frame.f_code.co_name, current_frame.f_locals)
    filtered = {}
    for k, v in current_frame.f_locals.items():
        if k == "args":
            # exclude the first item since that will be "self" in the method
            filtered[k] = v[1:]
            continue
        if k != "current_frame" and k != "frames" and k != "global_frames" and k != "f":
            filtered[k] = v
    if current_frame.f_code.co_name != "_handler":
        frames.frames.append(
            Frame(
                local_vars=[{k: str(v)} for k, v in filtered.items()],
                line=current_frame.f_lineno,
                name=current_frame.f_code.co_name,
            )
        )


def stack_tracker(global_frames: GlobalFrames):
    def true_decorator(f):
        def _handler(*args, **kwargs):
            sys.settrace(trace_func)
            result = f(*args, **kwargs)
            sys.settrace(None)
            print("\n\n\n")
            return result

            # current_frame = inspect.stack()[0][0]

            # get_most_recent_frames(current_frame=current_frame, frames=global_frames)

            # _GLOBAL_FRAME_STEPS.append(
            #     GlobalFrames(
            #         visualization=[*global_frames.visualization],
            #         frames=[*global_frames.frames],
            #     )
            # )
            # # clear the collected live stack
            # global_frames.frames.clear()
            # return f(*args, **kwargs)

        return _handler

    return true_decorator


class ListWithStackVis(list):
    @stack_tracker(_GLOBAL_FRAMES)
    def append(self, item):
        super().append(item)
        _GLOBAL_FRAMES.visualization.append(item)

    @stack_tracker(_GLOBAL_FRAMES)
    def extend(self, iterable):
        super().extend(iterable)
        _GLOBAL_FRAMES.visualization.extend(iterable)

    @stack_tracker(_GLOBAL_FRAMES)
    def insert(self, index, item):
        super().insert(index, item)
        _GLOBAL_FRAMES.visualization.insert(index, item)

    @stack_tracker(_GLOBAL_FRAMES)
    def remove(self, item):
        super().remove(item)
        _GLOBAL_FRAMES.visualization.remove(item)

    @stack_tracker(_GLOBAL_FRAMES)
    def pop(self, index=-1):
        _GLOBAL_FRAMES.visualization.pop(index)

        return super().pop(index)

    @stack_tracker(_GLOBAL_FRAMES)
    def clear(self):
        super().clear()
        _GLOBAL_FRAMES.visualization.clear()

    @stack_tracker(_GLOBAL_FRAMES)
    def __delitem__(self, index):
        super().__delitem__(index)
        _GLOBAL_FRAMES.visualization.__delitem__(index)

    @stack_tracker(_GLOBAL_FRAMES)
    def __setitem__(self, index, item):
        super().__setitem__(index, item)
        _GLOBAL_FRAMES.visualization.__setitem__(index, item)

    @stack_tracker(_GLOBAL_FRAMES)
    def __iadd__(self, other):
        _GLOBAL_FRAMES.visualization.__iadd__(other)

        return super().__iadd__(other)

    @stack_tracker(_GLOBAL_FRAMES)
    def __imul__(self, other):
        _GLOBAL_FRAMES.visualization.__imul__(other)

        return super().__imul__(other)

    @stack_tracker(_GLOBAL_FRAMES)
    def reverse(self):
        super().reverse()
        _GLOBAL_FRAMES.visualization.reverse()

    @stack_tracker(_GLOBAL_FRAMES)
    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        _GLOBAL_FRAMES.visualization.sort(*args, **kwargs)


lst = ListWithStackVis()


# @stack_tracker(_GLOBAL_FRAMES)
def mut():
    print(locals())
    lst.append(1)
    a = lst
    last()


# @stack_tracker(_GLOBAL_FRAMES)
def last():
    c = 3
    lst.append(2)
    b = lst
    print(locals())
    # it wont register previous's locals until we call another reigstered frame so we can traverse the stack
    done()


# @stack_tracker(_GLOBAL_FRAMES)
def done():
    return


@stack_tracker(_GLOBAL_FRAMES)
def test():
    print(locals())
    copy = lst
    # print(copy)
    # print("1", _GLOBAL_FRAME_STEPS)
    mut()


# def run():
#     test()


test()

for i in _GLOBAL_FRAME_STEPS:
    print(i, end="\n\n")
