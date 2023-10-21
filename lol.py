import inspect
from dataclasses import dataclass
from types import FrameType
from typing import Any, Dict, List, Deque
from collections import deque


_GLOBAL_FRAMES = []
_GLOBAL_FRAME_STEPS = []


@dataclass
class Frame:
    line: str
    local_vars: Dict[str, Any]


def get_most_recent_frames(current_frame: FrameType, frames: List[Frame]):
    if current_frame.f_back is None:
        return
    get_most_recent_frames(current_frame=current_frame.f_back, frames=frames)
    frames.append(Frame(local_vars=current_frame.f_locals, line=current_frame.f_lineno))


def stack_tracker(global_frames: List[Frame]):
    def true_decorator(f):
        def handler(*args, **kwargs):
            current_frame = inspect.stack()[0][0]
            global_frames.clear()
            get_most_recent_frames(current_frame=current_frame, frames=global_frames)
            return f(*args, **kwargs)

        return handler

    return true_decorator


class ListWithStackVis(list):
    @stack_tracker(_GLOBAL_FRAMES)
    def append(self, item):
        super().append(item)
        _GLOBAL_FRAMES.append(item)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def extend(self, iterable):
        super().extend(iterable)
        _GLOBAL_FRAMES.extend(iterable)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def insert(self, index, item):
        super().insert(index, item)
        _GLOBAL_FRAMES.insert(index, item)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def remove(self, item):
        super().remove(item)
        _GLOBAL_FRAMES.remove(item)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def pop(self, index=-1):
        _GLOBAL_FRAMES.pop(index)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])
        return super().pop(index)

    @stack_tracker(_GLOBAL_FRAMES)
    def clear(self):
        super().clear()
        _GLOBAL_FRAMES.clear()
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def __delitem__(self, index):
        super().__delitem__(index)
        _GLOBAL_FRAMES.__delitem__(index)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def __setitem__(self, index, item):
        super().__setitem__(index, item)
        _GLOBAL_FRAMES.__setitem__(index, item)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def __iadd__(self, other):
        _GLOBAL_FRAMES.__iadd__(other)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])
        return super().__iadd__(other)

    @stack_tracker(_GLOBAL_FRAMES)
    def __imul__(self, other):
        _GLOBAL_FRAMES.__imul__(other)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])
        return super().__imul__(other)

    @stack_tracker(_GLOBAL_FRAMES)
    def reverse(self):
        super().reverse()
        _GLOBAL_FRAMES.reverse()
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])

    @stack_tracker(_GLOBAL_FRAMES)
    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        _GLOBAL_FRAMES.sort(*args, **kwargs)
        _GLOBAL_FRAME_STEPS.append([*_GLOBAL_FRAMES])
