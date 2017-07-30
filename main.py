'''
Creatures
Cellular Automata. A program to simulate natural selection.
by Karl-Heinz Muller, MuuuhMedia

A world full with creatures is created. On each turn the direct environment of a
creature is analyzed by comparing a specific gene or multiple genes with
creatures surrounding it.

The type of neighbors and the energy level of the creature itself define the
possible actions it can take. A creature can either move, divide, eat a neighbor
or to stay at the place. Each action may increase or decrease the its energy.
'''
import pyglet
from models import OpenWorld

DRAW_POINTS = False
CELL_SIZE = 15
WORLD_SIZE = CELL_SIZE * 40
PERCENT_FILL = 0.2

class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(WORLD_SIZE, WORLD_SIZE)
        self.world = OpenWorld(
                                self.get_size()[0],
                                self.get_size()[1],
                                CELL_SIZE,
                                PERCENT_FILL
                            )
        pyglet.clock.schedule_interval(self.update, 1.0/24.0)

    def on_draw(self):
        if DRAW_POINTS:
            self.world.draw_points()
        else:
            self.world.draw_squares()

    def update(self, dt):
        self.world.run_rules()

if __name__ == '__main__':
    window = Window()
    window.set_caption('An Open World for Creatures by MuuuhMedia')
    pyglet.app.run()
