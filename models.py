import random as rnd
import pyglet
import operator

def randomizer():
    return rnd.randint(0, 255)

class Creature(object):
    def __init__(self, red, green, blue, energy):
        '''
        Constructor
        '''
        self.gene_a = red
        self.gene_b = green
        self.gene_c = blue

        self.energy = energy

        self.color = (self.gene_a, self.gene_b, self.gene_c)

class OpenWorld:
    '''
    Derived from GameOfLife, this class provides an Open World for creatures.
    '''

    def __init__(self, window_width, window_height, cell_size, percent_fill):
        '''
        Constructor
        '''
        self.grid_width = int(window_width / cell_size)
        self.grid_height = int(window_height / cell_size)
        self.cell_size = cell_size
        self.cells = []
        self.percent_fill = percent_fill
        self.generate_cells()

    def generate_cells(self):
        '''
        Fills the Open World with creatures
        '''
        for row in range(0, self.grid_height):
            self.cells.append([])
            for col in range(0, self.grid_width):
                if rnd.random() < self.percent_fill:
                    new_creature = Creature(randomizer(), randomizer(), randomizer(), randomizer())
                    self.cells[row].append(new_creature)
                else:
                    self.cells[row].append(None)

    def run_rules(self):
        for i in range(0, 400):
            row = rnd.randint(0, self.grid_height - 1)
            col = rnd.randint(0, self.grid_width  -1)
            if not self.cells[row][col]:
                continue

            really = [
                self.real(row, col, row - 1, col),
                self.real(row, col, row - 1, col + 1),
                self.real(row, col, row, col + 1),
                self.real(row, col, row + 1, col + 1),
                self.real(row, col, row + 1, col),
                self.real(row, col, row + 1, col - 1),
                self.real(row, col, row, col - 1),
                self.real(row, col, row - 1, col - 1)]
            seen = [
                self.like(row, col, row - 1, col),
                self.like(row, col, row - 1, col + 1),
                self.like(row, col, row, col + 1),
                self.like(row, col, row + 1, col + 1),
                self.like(row, col, row + 1, col),
                self.like(row, col, row + 1, col - 1),
                self.like(row, col, row, col - 1),
                self.like(row, col, row - 1, col - 1)]
            food = [
                self.unlike(row, col, row - 1, col),
                self.unlike(row, col, row - 1, col + 1),
                self.unlike(row, col, row, col + 1),
                self.unlike(row, col, row + 1, col + 1),
                self.unlike(row, col, row + 1, col),
                self.unlike(row, col, row + 1, col - 1),
                self.unlike(row, col, row, col - 1),
                self.unlike(row, col, row - 1, col - 1)]
            family = [
                self.same(row, col, row - 1, col),
                self.same(row, col, row - 1, col + 1),
                self.same(row, col, row, col + 1),
                self.same(row, col, row + 1, col + 1),
                self.same(row, col, row + 1, col),
                self.same(row, col, row + 1, col - 1),
                self.same(row, col, row, col - 1),
                self.same(row, col, row - 1, col - 1)]
            cell_sum = sum(seen)
            food = [x*y for x,y in zip(food, seen)]
            food_sum = sum(food)
            family = [x*y for x,y in zip(family, seen)]
            family_sum = sum(family)

            #if family_sum > 4:
            #    self.cells[row][col].energy += family_sum * 3

            # Decide on Action - Environment vs Energy Level
            action = ''
            if self.cells[row][col].energy < 0:
                action = 'DIE'
            elif self.cells[row][col].energy < 100 and food_sum > 0:
                action = 'EAT'
            elif self.cells[row][col].energy > 240 and sum(really) < 8:
                action = 'DIVIDE'
            elif cell_sum < 8:
                action = 'MOVE'
            else:
                action = 'STALL'

            if action == 'DIVIDE':
                new_row, new_col = self.find_target(row, col, really, True)
                dEnergy = rnd.randint(0, int(self.cells[row][col].energy/2))
                self.cells[new_row][new_col] = self.cells[row][col]
                self.cells[new_row][new_col].energy = dEnergy
                self.mutate_cell(new_row, new_col)
                self.cells[row][col].energy -= dEnergy


            if action == 'MOVE':
                new_row, new_col = self.find_target(row, col, seen, True)
                if self.cells[new_row][new_col]:
                    #print('Bummms: ' + str(row) + ', ' + str(col) + ' into ' + str(new_row) + ', ' + str(new_col))
                    dEnergy = int(self.cells[row][col].energy / 2)
                    self.cells[row][col].energy = dEnergy
                    self.cells[new_row][new_col].energy += dEnergy
                    if self.cells[new_row][new_col].energy > 255:
                        self.cells[new_row][new_col].energy = 255
                    #print(str(row)+'>'+str(new_row) + ' - ' + str(col) + '>' + str(new_col))
                else:
                    # print('Run from ' + str(row) + ', ' + str(col) + ' to ' + str(new_row) + ', ' + str(new_col))
                    dEnergy = rnd.randint(0, 20)
                    self.cells[row][col].energy += dEnergy
                    if self.cells[row][col].energy > 255:
                        self.cells[row][col].energy = 255
                    self.cells[new_row][new_col] = self.cells[row][col]
                    self.cells[row][col] = None

            if action == 'EAT':
                new_row, new_col = self.find_target(row, col, food, False)
                if self.cells[new_row][new_col]:
                    self.cells[row][col].energy += self.cells[new_row][new_col].energy
                    self.cells[new_row][new_col] = None
                    #print('Bon Appetit: ' + str(food) + '; Energy: ' + str(self.cells[row][col].energy))

            if action == 'STALL':
                dEnergy = self.cells[row][col].energy - rnd.randint(0, 20)
                self.cells[row][col].energy = dEnergy
                if self.cells[row][col].energy < 0:
                    self.cells[row][col] = None
                    #print('RIP: ' + str(row) + ', ' + str(col) + '; Energy: 0')
                #else:
                    #print('Now way: ' + str(row) + ', ' + str(col) + '; Energy: ' + str(self.cells[row][col].energy))

            if action == 'DIE':
                #print('RIP: ' + str(row) + ', ' + str(col) + '; Energy:' + str(self.cells[row][col].energy))
                self.cells[row][col] = None

    def find_target(self, row, col, neighborhood, empty):
        ret_row, ret_col = row, col
        if empty:
            find = 0 # or 1
            selected_occurence = rnd.randint(1, 8 - sum(neighborhood))
        else:
            find = 1 # or 1
            selected_occurence = rnd.randint(1, sum(neighborhood))
        found = -1
        for i in range(selected_occurence):
            found = neighborhood.index(find, found + 1)
        if found > -1 and neighborhood[found] == find:
            if found == 0:
                ret_row, ret_col = row - 1, col
            elif found == 1:
                ret_row, ret_col = row - 1, col + 1
            elif found == 2:
                ret_row, ret_col = row, col + 1
            elif found == 3:
                ret_row, ret_col = row + 1, col + 1
            elif found == 4:
                ret_row, ret_col = row + 1, col
            elif found == 5:
                ret_row, ret_col = row + 1, col - 1
            elif found == 6:
                ret_row, ret_col = row, col - 1
            elif found == 7:
                ret_row, ret_col = row - 1, col - 1

            if ret_row == -1:
                ret_row = self.grid_width - 1
            if ret_row >= self.grid_width:
                ret_row = 0
            if ret_col == -1:
                ret_col = self.grid_height - 1
            if ret_col >= self.grid_height:
                ret_col = 0

        return ret_row, ret_col

    def mutate_cell(self, mut_row, mut_col):
        mutate = False
        drift = 5
        if rnd.randint(0, 1000) == 0:
            mutate = True
        if mutate:
            # Randomly Select Gene (a, b, c) and Direction (+/-)
            select_mutation = rnd.randint(0, 5)
            if select_mutation == 0:
                self.cells[mut_row][mut_col].gene_a += drift
                if self.cells[mut_row][mut_col].gene_a > 255:
                    self.cells[mut_row][mut_col].gene_a = self.cells[mut_row][mut_col].gene_a - 255
            if select_mutation == 1:
                self.cells[mut_row][mut_col].gene_a -= drift
                if self.cells[mut_row][mut_col].gene_a < 0:
                    self.cells[mut_row][mut_col].gene_a = self.cells[mut_row][mut_col].gene_a + 256
            if select_mutation == 2:
                self.cells[mut_row][mut_col].gene_b += drift
                if self.cells[mut_row][mut_col].gene_b > 255:
                    self.cells[mut_row][mut_col].gene_b = self.cells[mut_row][mut_col].gene_b - 255
            if select_mutation == 3:
                self.cells[mut_row][mut_col].gene_b -= drift
                if self.cells[mut_row][mut_col].gene_b < 0:
                    self.cells[mut_row][mut_col].gene_b = self.cells[mut_row][mut_col].gene_b + 256
            if select_mutation == 4:
                self.cells[mut_row][mut_col].gene_c += drift
                if self.cells[mut_row][mut_col].gene_c > 255:
                    self.cells[mut_row][mut_col].gene_c = self.cells[mut_row][mut_col].gene_c - 255
            if select_mutation == 5:
                self.cells[mut_row][mut_col].gene_c -= drift
                if self.cells[mut_row][mut_col].gene_c < 0:
                    self.cells[mut_row][mut_col].gene_c = self.cells[mut_row][mut_col].gene_c + 256

    def verify_cell(self, ver_row, ver_col):
        '''
        Returns row,col across the panel if necessary.
        '''
        if ver_row == -1:
            ver_row = self.grid_width - 1
        if ver_row >= self.grid_width:
            ver_row = 0
        if ver_col == -1:
            ver_col = self.grid_height - 1
        if ver_col >= self.grid_height:
            ver_col = 0

        return ver_row, ver_col

    def gene_similar(self, gene_x, gene_y):
        '''
        Returns True or False. True, the value gene_x is less than 10 from
        gene_y away. Genes are circular from 0 to 255. Returning True is a
        probability which dependes on gene difference and decreases with
        distance. Max distance is 128.
        '''
        if abs(gene_x - gene_y) <= 128:
            distance = abs(gene_x - gene_y)
        else:
            distance = 255 - abs(gene_x - gene_y)

        probability = rnd.randint(0, 128)
        if distance < probability:
            return True
        else:
            return False

    def same(self, row, col, test_row, test_col):
        test_row, test_col = self.verify_cell(test_row, test_col)
        if self.cells[test_row][test_col]:
            if self.cells[test_row][test_col].gene_a == self.cells[row][col].gene_a:
                if self.cells[test_row][test_col].gene_b == self.cells[row][col].gene_b:
                    if self.cells[test_row][test_col].gene_c == self.cells[row][col].gene_c:
                        return 1
        return 0

    def like(self, row, col, test_row, test_col):
        test_row, test_col = self.verify_cell(test_row, test_col)
        if self.cells[test_row][test_col]:
            if self.gene_similar(
                                self.cells[test_row][test_col].gene_a,
                                self.cells[row][col].gene_a
                                ):
                return 1
        return 0

    def real(self, row, col, test_row, test_col):
        test_row, test_col = self.verify_cell(test_row, test_col)
        if self.cells[test_row][test_col]:
            return 1
        return 0

    def unlike(self, row, col, test_row, test_col):
        test_row, test_col = self.verify_cell(test_row, test_col)
        if self.cells[test_row][test_col]:
            if not self.gene_similar(
                                        self.cells[test_row][test_col].gene_a,
                                        self.cells[row][col].gene_a
                                    ):
                return 1
        return 0

    def draw_points(self):
        for row in range(0, self.grid_height):
            for col in range(0, self.grid_width):
                red, green, blue = 0, 0, 0
                if self.cells[row][col]:
                    red, green, blue = self.cells[row][col].color
                pyglet.graphics.draw(4, pyglet.gl.GL_POINTS,
                    ('v2i', (
                        row * self.cell_size, col * self.cell_size,
                        row * self.cell_size+1, col * self.cell_size,
                        row * self.cell_size+1, col * self.cell_size+1,
                        row * self.cell_size, col * self.cell_size+1)),
                    ('c3B', (red, green, blue,
                        red, green, blue,
                        red, green, blue,
                        red, green, blue))
                )

    def draw_squares(self):
        '''
        Draws a square for each creature. Color depends on the genes where gene
        a defines red, gene b green and gene c blue of RGB color. Energy is used
        to control itensity.
        '''
        for row in range(0, self.grid_height):
            for col in range(0, self.grid_width):
                square_coords = (
                                row * self.cell_size,
                                col * self.cell_size,
                                row * self.cell_size,
                                col * self.cell_size + self.cell_size,
                                row * self.cell_size + self.cell_size,
                                col * self.cell_size,
                                row * self.cell_size + self.cell_size,
                                col * self.cell_size + self.cell_size
                            )
                square_colors = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                if self.cells[row][col]:
                    if self.cells[row][col].energy > 0:
                        cell_energy = 255 #+ int(self.cells[row][col].energy/2)
                        red, green, blue = self.cells[row][col].color
                        square_colors = (
                                        int(red*cell_energy/255/10),
                                        int(green*cell_energy/255/10),
                                        int(blue*cell_energy/255/10),
                                        int(red*cell_energy/255/2),
                                        int(green*cell_energy/255/2),
                                        int(blue*cell_energy/255/2),
                                        int(red*cell_energy/255/5),
                                        int(green*cell_energy/255/5),
                                        int(blue*cell_energy/255/5),
                                        int(red*cell_energy/255),
                                        int(green*cell_energy/255),
                                        int(blue*cell_energy/255)
                                    )
                pyglet.graphics.draw_indexed(
                                4, pyglet.gl.GL_TRIANGLES,
                                [0, 1, 2, 1, 2, 3],
                                ('v2i', square_coords),
                                ('c3B', square_colors)
                            )
