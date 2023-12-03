from dataclasses import dataclass


@dataclass
class Pose:
    x: float
    y: float
    z: float
    theta: float
