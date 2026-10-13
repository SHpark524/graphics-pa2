import pyglet
from pyglet import gl
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Mat4, Vec3
from pyglet.window import key, mouse
from camera import TrackballCamera

from geometry import CubeMesh
from scene import build_scene


VERTEX_SHADER = """#version 330 core
in vec3 position;
in float shade;
out float face_shade;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main() {
    face_shade = shade;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER = """#version 330 core
in float face_shade;
out vec4 final_color;
uniform vec3 color;
void main() {
    final_color = vec4(color * face_shade, 1.0);
}
"""

class CornellWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(
            width=1100, height=720,
            config=gl.Config(major_version=3, minor_version=3,
                             depth_size=24, double_buffer=True))
        self.set_vsync(True)
        self.program = ShaderProgram(
            Shader(VERTEX_SHADER, "vertex"), Shader(FRAGMENT_SHADER, "fragment"))
        self.meshes = {
            "cube": CubeMesh(self.program),
        }
        self.parts = build_scene()
        self.camera = TrackballCamera()
        self.view_matrix = self.camera.view_matrix()
        self.on_resize(self.width, self.height)
        gl.glClearColor(0.12, 0.13, 0.16, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.projection_matrix = Mat4.perspective_projection(
            width / max(height, 1), 0.1, 120.0, 52.0)

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self.program:
            self.program["view"] = self.view_matrix
            self.program["projection"] = self.projection_matrix
            for part in self.parts:
                self.program["model"] = part.model()
                self.program["color"] = part.color
                self.meshes["cube"].draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            if modifiers & key.MOD_SHIFT:
                self.camera.move(dx, dy)
            elif modifiers & key.MOD_CTRL:
                self.camera.zoom(dy)
            else:
                self.camera.rotate(x, y, dx, dy, self.width, self.height)

            self.view_matrix = self.camera.view_matrix()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R:
            self.camera = TrackballCamera()
            self.view_matrix = self.camera.view_matrix()



def main():
    window = CornellWindow()
    refresh_rate = window.screen.get_mode().rate or 60
    draw_rate = min(144, max(60, 2 * refresh_rate))

    def tick(dt):
        window.draw(dt)

    pyglet.clock.schedule_interval(tick, 1.0 / draw_rate)
    pyglet.app.run(interval=None)


if __name__ == "__main__":
    main()
