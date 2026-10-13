from dataclasses import dataclass

from pyglet.math import Mat4, Vec3

BOX_WIDTH = 25.0
BOX_HEIGHT = 20.0
BOX_DEPTH = 15.0

WALL_THICKNESS = 0.2
LIGHT_SIZE = 1.0

WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
EARBUD_WHITE = (240 / 255, 240 / 255, 238 / 255)
CASE_SEAM = (0.36, 0.36, 0.38)
YELLOW = (1.0, 0.85, 0.05)


@dataclass
class Part:
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    color: tuple[float, float, float]
    mesh: str = "cube"

    def model(self) -> Mat4:
        translation = Mat4.from_translation(Vec3(*self.center))
        scaling = Mat4.from_scale(Vec3(*self.size))
        return translation @ scaling


def build_scene() -> list[Part]:
    w = BOX_WIDTH
    h = BOX_HEIGHT
    d = BOX_DEPTH
    t = WALL_THICKNESS
    l = LIGHT_SIZE

    return [
        # Floor
        Part(
            center=(0, -t / 2, d / 2),
            size=(w, t, d),
            color=WHITE,
        ),
        # Back wall
        Part(
            center=(0, h / 2, d + t / 2),
            size=(w, h, t),
            color=WHITE,
        ),
        # Left wall
        Part(
            center=(-w / 2 - t / 2, h / 2, d / 2),
            size=(t, h, d),
            color=GREEN,
        ),
        # Right wall
        Part(
            center=(w / 2 + t / 2, h / 2, d / 2),
            size=(t, h, d),
            color=RED,
        ),
        # Ceiling (front)
        Part(
            center=(0, h + t / 2, (d - l) / 4),
            size=(w, t, (d - l) / 2),
            color=WHITE,
        ),
        # Ceiling (back)
        Part(
            center=(0, h + t / 2, (3 * d + l) / 4),
            size=(w, t, (d - l) / 2),
            color=WHITE,
        ),
        # Ceiling (left)
        Part(
            center=(-(w + l) / 4, h + t / 2, d / 2),
            size=((w - l) / 2, t, l),
            color=WHITE,
        ),
        # Ceiling (right)
        Part(
            center=((w + l) / 4, h + t / 2, d / 2),
            size=((w - l) / 2, t, l),
            color=WHITE,
        ),
        # Earbuds case
        Part(
            center=(4.20, 2.78 / 2, 9.57),
            size=(5.0, 2.78, 5.02),
            color=EARBUD_WHITE,
            mesh="rounded_box",
        ),
        Part(
            center=(4.20, 2.78 / 2, 9.57),
            size=(5.0, 2.78, 5.02),
            color=CASE_SEAM,
            mesh="rounded_box_seam",
        ),
        # Glue-stick cap
        Part(
            center=(-4.16, 3.0 / 2, 4.47),
            size=(3.0, 3.0, 3.0),
            color=YELLOW,
            mesh="cylinder",
        ),
    ]
