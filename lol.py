import inspect
from dataclasses import dataclass
from types import FrameType
from typing import Any, Dict, List, Deque
from collections import deque


@dataclass
class GlobalFrames:
    visualization: List[Any]
    frames: "FramesCase"


@dataclass
class FramesCase:
    stale: List["Frame"]
    live: List["Frame"]


_GLOBAL_FRAMES = GlobalFrames(frames=FramesCase(stale=[], live=[]), visualization=[])
_GLOBAL_FRAME_STEPS = []


@dataclass
class Frame:
    line: int
    local_vars: Dict[str, Any]
    name: str


def get_filtered_frame(frame) -> Frame:
    filtered = {}

    for k, v in frame.f_locals.items():
        if k == "args":
            # exclude the first item since that will be "self" in the method
            filtered[k] = v[1:]
            continue
        if k != "current_frame" and k != "frames" and k != "global_frames" and k != "f":
            filtered[k] = v
    return Frame(
        local_vars=filtered,
        line=frame.f_lineno,
        name=frame.f_code.co_name,
    )


def get_most_recent_frames(current_frame: FrameType, frames: GlobalFrames):
    if current_frame.f_back is None:
        return
    get_most_recent_frames(current_frame=current_frame.f_back, frames=frames)
    frame = get_filtered_frame(current_frame)
    if frame.name != "_handler":
        frames.frames.live.append(frame)


def stack_tracker(global_frames: GlobalFrames):
    def true_decorator(f):
        def _handler(*args, **kwargs):
            current_frame = inspect.stack()[0][0]

            get_most_recent_frames(current_frame=current_frame, frames=global_frames)
            frame = get_filtered_frame(current_frame)
            global_frames.frames.stale.append(frame)

            _GLOBAL_FRAME_STEPS.append
            # .append(
            #     {
            #         "visualization": [*global_frames["visualization"]],
            #         "frames": [*global_frames["frames"]],
            #     }
            # )
            # clear the collected live stack
            # clear live and stale because both still need to be maintained
            # live just updates references local
            global_frames.frames.live.clear()
            global_frames.frames.stale.clear()
            return f(*args, **kwargs)

        return _handler

    return true_decorator


class ListWithStackVis(list):
    @stack_tracker(_GLOBAL_FRAMES)
    def append(self, item):
        super().append(item)
        _GLOBAL_FRAMES["visualization"].append(item)

    @stack_tracker(_GLOBAL_FRAMES)
    def extend(self, iterable):
        super().extend(iterable)
        _GLOBAL_FRAMES["visualization"].extend(iterable)

    @stack_tracker(_GLOBAL_FRAMES)
    def insert(self, index, item):
        super().insert(index, item)
        _GLOBAL_FRAMES["visualization"].insert(index, item)

    @stack_tracker(_GLOBAL_FRAMES)
    def remove(self, item):
        super().remove(item)
        _GLOBAL_FRAMES["visualization"].remove(item)

    @stack_tracker(_GLOBAL_FRAMES)
    def pop(self, index=-1):
        _GLOBAL_FRAMES["visualization"].pop(index)

        return super().pop(index)

    @stack_tracker(_GLOBAL_FRAMES)
    def clear(self):
        super().clear()
        _GLOBAL_FRAMES["visualization"].clear()

    @stack_tracker(_GLOBAL_FRAMES)
    def __delitem__(self, index):
        super().__delitem__(index)
        _GLOBAL_FRAMES["visualization"].__delitem__(index)

    @stack_tracker(_GLOBAL_FRAMES)
    def __setitem__(self, index, item):
        super().__setitem__(index, item)
        _GLOBAL_FRAMES["visualization"].__setitem__(index, item)

    @stack_tracker(_GLOBAL_FRAMES)
    def __iadd__(self, other):
        _GLOBAL_FRAMES["visualization"].__iadd__(other)

        return super().__iadd__(other)

    @stack_tracker(_GLOBAL_FRAMES)
    def __imul__(self, other):
        _GLOBAL_FRAMES["visualization"].__imul__(other)

        return super().__imul__(other)

    @stack_tracker(_GLOBAL_FRAMES)
    def reverse(self):
        super().reverse()
        _GLOBAL_FRAMES["visualization"].reverse()

    @stack_tracker(_GLOBAL_FRAMES)
    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        _GLOBAL_FRAMES["visualization"].sort(*args, **kwargs)


lst = ListWithStackVis()


@stack_tracker(_GLOBAL_FRAMES)
def mut():
    print("2", _GLOBAL_FRAME_STEPS)
    lst.append(1)
    print("3", _GLOBAL_FRAME_STEPS)


@stack_tracker(_GLOBAL_FRAMES)
def test():
    copy = lst
    print("1", _GLOBAL_FRAME_STEPS)
    mut()


# def run():
#     test()


test()
print(end="\n\nend\n")
print(_GLOBAL_FRAME_STEPS)
for i in _GLOBAL_FRAME_STEPS:
    print(i, end="\n\n")
