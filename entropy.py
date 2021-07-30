from manim import *
from pprint import pprint
import random as rd
import math as m
import colorsys as clr

def gen_random_directed_path(pos, initial_angle, velocity, num_steps, max_angle_diff, final_height):
    points = [ list(pos) ]
    theta = initial_angle
    height_diff = final_height / num_steps
    for k in range(num_steps):
        last_point = points[-1]
        rand_theta = rd.uniform(-1, 1) * max_angle_diff
        theta += rand_theta
        new_point = [
            np.cos(theta) * velocity + last_point[0],
            np.sin(theta) * velocity + last_point[1],
            height_diff + last_point[2]
        ]
        points.append(new_point)
    points.append(points[-1])
    return Non_Manim_Path(np.asarray(points))

def gen_random_path_to_point(pos, initial_angle, velocity, num_steps, max_angle_diff, final_height):
    points = [ list(pos) ]
    theta = initial_angle
    height_diff = final_height / num_steps
    for k in range(num_steps):
        last_point = points[-1]
        rand_theta = rd.uniform(-1, 1) * max_angle_diff
        theta += rand_theta
        new_point = [
            np.cos(theta) * velocity + last_point[0],
            np.sin(theta) * velocity + last_point[1],
            height_diff + last_point[2]
        ]
        points.append(new_point)
    points = points[::-1]
    points.append(points[-1])
    return Non_Manim_Path(np.asarray(points))

def gen_random_directed_path_to_y_half_plane(pos, initial_angle, velocity, num_steps, max_angle_diff, axis_sign):
    points = [ list(pos) ]
    theta = initial_angle
    for k in range(num_steps):
        last_point = points[-1]
        rand_theta = rd.uniform(-1, 1) * max_angle_diff
        theta += rand_theta
        y_effect = 0
        if m.fabs(np.sign(last_point[1]) - np.sign(axis_sign)) > 0.1:
            y_effect = 2.0 * axis_sign - last_point[1]
            y_effect = y_effect / np.sqrt(m.fabs(y_effect))
        else:
            y_effect = axis_sign * (rd.uniform(0, 1) + 0.25 / (last_point[1] ** 4 + 1.0) - 3.0 / 32.0 * last_point[1] ** 2)
        new_point = [
            np.cos(theta) * velocity + last_point[0],
            (np.sin(theta) + y_effect) * velocity + last_point[1],
            last_point[2]
        ]
        points.append(new_point)
    points.append(points[-1])
    return Non_Manim_Path(np.asarray(points))

class Non_Manim_Path:
    def __init__(
        self,
        path : np.ndarray
    ):
        self.path = path

    def point_from_proportion(self, t):
        cur_index = m.modf(t * (len(self.path) - 2))
        frac = cur_index[0]
        index = int(cur_index[1])
        points = self.path[index:index + 2]
        point = [
            a * (1.0 - frac) + b * frac
            for a, b in zip(*points)
        ]
        return point

def color_interpolation(start, stop, t):
    _start = [ k / 255.0 for k in start ]
    _stop = [ k / 255.0 for k in stop ]
    _start = clr.rgb_to_hls(*_start)
    _stop = clr.rgb_to_hls(*_stop)
    interp = None
    #if m.fabs(_stop[0] - _start[0]) > 0.5:
    #    if _start[0] < _stop[0]:
    #        _stop[0] -= 1
    #    else:
    #        _start[0] += 1
    interp = [ m.modf(a * (1.0 - t) + b * t)[0] for a, b in zip(_start, _stop) ]
    return '#%02x%02x%02x' % tuple( int(255 * k) for k in clr.hls_to_rgb(*interp) )

class Entropy_Disorder(Scene):
    def construct(self):
        atoms_pos = [ (x, y + 0.5, 0) for x in range(-10, 11) for y in range(-5, 5) ]
        atoms = [ Circle(radius = 0.2, color="#B87333", fill_opacity=1) for k in range(len(atoms_pos)) ]
        for circle in atoms:
            circle.set_fill(BLACK)
        atom_paths = [
            gen_random_path_to_point(
                atoms_pos[k],
                rd.random() * np.pi * 2.0,
                0.002,
                1000,
                0.08,
                rd.uniform(-10, 10)
            )
            for k in range(len(atoms))
        ]
        for atom, pos in zip(atoms, atom_paths):
            atom.move_to(pos.point_from_proportion(0))
            self.add(atom)
        self.play(*[MoveAlongPath(atoms[k], atom_paths[k], run_time = 2.0) for k in range(len(atoms))], run_time=2.5, rate_func=linear)
        color_tracker = ValueTracker(0)
        atom_paths = [
            gen_random_directed_path(
                atoms_pos[k],
                rd.random() * np.pi * 2.0,
                0.0003,
                2000,
                0.8,
                rd.uniform(-10, 10)
            )
            for k in range(len(atoms))
        ]
        self.play(*[MoveAlongPath(atoms[k], atom_paths[k]) for k in range(len(atoms))], run_time=2.5, rate_func=linear)
        random_atoms = list(range(len(atoms)))
        rd.shuffle(random_atoms)
        oil_atoms = [ atoms[k] for k in random_atoms[:len(atoms) // 2] ]
        oil_atoms_pos = [ atom_paths[k].point_from_proportion(1.0) for k in random_atoms[:len(atoms) // 2] ]
        water_atoms = [ atoms[k] for k in random_atoms[len(atoms) // 2:] ]
        water_atoms_pos = [ atom_paths[k].point_from_proportion(1.0) for k in random_atoms[len(atoms) // 2:] ]
        for atom in oil_atoms:
            atom.add_updater(
                lambda o: o.set_stroke(
                    color_interpolation(
                        [184, 115, 51],
                        [219, 207, 92],
                        color_tracker.get_value()
                    )
                )
            )
        for atom in water_atoms:
            atom.add_updater(
                lambda o: o.set_stroke(
                    color_interpolation(
                        [184, 115, 51],
                        [135, 206, 235],
                        color_tracker.get_value()
                    )
                )
            )
        oil_atom_paths = [
            gen_random_directed_path_to_y_half_plane(
                oil_atoms_pos[k],
                rd.random() * np.pi * 2.0,
                0.002,
                2500,
                0.08,
                1.0
            )
            for k in range(len(oil_atoms))
        ]
        water_atom_paths = [
            gen_random_directed_path_to_y_half_plane(
                water_atoms_pos[k],
                rd.random() * np.pi * 2.0,
                0.002,
                2500,
                0.08,
                -1.0
            )
            for k in range(len(water_atoms))
        ]
        self.play(
            color_tracker.animate.set_value(1),
            run_time = 0.5,
            rate_func=linear
        )
        self.play(
            *[MoveAlongPath(oil_atoms[k], oil_atom_paths[k]) for k in
                range(len(oil_atoms))
            ],
            *[MoveAlongPath(water_atoms[k], water_atom_paths[k]) for k in
                range(len(water_atoms))
            ],
            run_time = 4,
            rate_func=linear
        )

class Title_Card(Scene):
    def construct(self):
        ft = MarkupText(f'Entropy is <span fgcolor="{RED}">NOT disorder</span>.', font="Noto Sans")
        self.add(ft)
        self.wait(2.0)

def nice_step(x, a, width):
    if x < (a - width / 2.0):
        return 0
    elif x > (a + width / 2.0):
        return 1
    else:
        return (x - (a - width / 2.0)) / width

def copper_to_silver(o, t):
    o.set_stroke(
        color_interpolation(
            [200, 131, 67],
            [192, 192, 192],
            nice_step(t, 0.5, 0.2)
        )
    )
    o.set_fill(
        color_interpolation(
            [200, 131, 67],
            [192, 192, 192],
            nice_step(t, 0.5, 0.2)
        )
    )

def silver_to_copper(o, t):
    o.set_stroke(
        color_interpolation(
            [192, 192, 192],
            [200, 131, 67],
            nice_step(t, 0.5, 0.2)
        )
    )
    o.set_fill(
        color_interpolation(
            [192, 192, 192],
            [200, 131, 67],
            nice_step(t, 0.5, 0.2)
        )
    )

class Low_Entropy_State(Scene):
    def construct(self):
        box = RoundedRectangle(width=7.8, height=7.8, color="#DC143C")
        box.move_to([3.125, 0, 0])
        self.add(box)
        coins_pos = [ (0.75 * x - 1, 0.75 * y - 2.0 + 0.125, 0) for x in range(1, 11) for y in range(-2, 8) ]
        coins = [ Circle(radius = 0.25, color="#C88343", fill_opacity=1, stroke_width=5) for k in range(len(coins_pos)) ]
        for circle in coins:
            circle.set_fill("#C88343")
        for coin, pos in zip(coins, coins_pos):
            coin.move_to(pos)
            self.add(coin)
        self.wait(3.0)
        random_coins = list(range(len(coins)))
        rd.shuffle(random_coins)
        silver_coins = set(random_coins[:len(random_coins) // 2])
        copper_coins = set(random_coins[len(random_coins) // 2:])
        flips = []
        for i in silver_coins:
            coins[i].add_updater(lambda o : copper_to_silver(o, coin_flip_tracker.get_value()))
            flips.append(Rotate(coins[i], axis = RIGHT))
        coin_flip_tracker = ValueTracker(0)
        new_notes = Tex(r"""
\begin{tabular}{rrr}
    \hline
    Heads & Tails & $\Omega$ \\
    \hline
    100 & 0 & 1 \\
    99 &  1 & 100 \\
    98 &  2 & 4950 \\
    95 &  5 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(95 + 1) - m.lgamma( 5 + 1)) / m.log(10))) + r"""}$ \\
    90 & 10 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(90 + 1) - m.lgamma(10 + 1)) / m.log(10))) + r"""}$ \\
    80 & 20 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(80 + 1) - m.lgamma(20 + 1)) / m.log(10))) + r"""}$ \\
    70 & 30 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(70 + 1) - m.lgamma(30 + 1)) / m.log(10))) + r"""}$ \\
    60 & 40 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(60 + 1) - m.lgamma(40 + 1)) / m.log(10))) + r"""}$ \\
    50 & 50 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(50 + 1) - m.lgamma(50 + 1)) / m.log(10))) + r"""}$ \\
    40 & 60 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(40 + 1) - m.lgamma(60 + 1)) / m.log(10))) + r"""}$ \\
    30 & 70 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(30 + 1) - m.lgamma(70 + 1)) / m.log(10))) + r"""}$ \\
    20 & 80 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(20 + 1) - m.lgamma(80 + 1)) / m.log(10))) + r"""}$ \\
    10 & 90 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma(10 + 1) - m.lgamma(90 + 1)) / m.log(10))) + r"""}$ \\
     5 & 95 & $~10^{""" + str(m.floor((m.lgamma(100 + 1) - m.lgamma( 5 + 1) - m.lgamma(95 + 1)) / m.log(10))) + r"""}$ \\
     2 & 98 & 4950 \\
     1 & 99 & 100 \\
    0 & 100 & 1 \\
    \hline
\end{tabular}
        """).scale(0.70).shift(LEFT * 4.0)
        self.play(*flips, coin_flip_tracker.animate.set_value(1.0), Create(new_notes), rate_func=linear, run_time=0.25)
        self.wait(0.5)
        prev_silver_coins = silver_coins
        prev_copper_coins = copper_coins
        for i in range(20):
            self.remove(*coins)
            coins = []
            j = 0
            while j < len(prev_silver_coins):
                if len(coins) in prev_silver_coins:
                    coins.append(
                        Circle(radius = 0.25, color="#C0C0C0", fill_opacity=1,
                        stroke_width=5)
                    )
                    coins[-1].set_fill("#C0C0C0")
                    j += 1
                else:
                    coins.append(
                        Circle(radius = 0.25, color="#C88343", fill_opacity=1,
                        stroke_width=5)
                    )
                    coins[-1].set_fill("#C88343")
            for j in range(len(coins), 100):
                coins.append(
                    Circle(radius = 0.25, color="#C88343", fill_opacity=1,
                    stroke_width=5)
                )
                coins[-1].set_fill("#C88343")
            for k in range(len(coins)):
                coins[k].move_to(coins_pos[k])
                self.add(coins[k])
            coin_flip_tracker.set_value(0.0)
            rd.shuffle(random_coins)
            silver_coins = set(random_coins[:len(random_coins) // 2])
            copper_coins = set(random_coins[len(random_coins) // 2:])
            silver_coins_to_flip = silver_coins.difference(prev_silver_coins)
            copper_coins_to_flip = copper_coins.difference(prev_copper_coins)
            coins_to_flip = silver_coins_to_flip.union(copper_coins_to_flip)
            flips = [ Rotate(coins[j], axis = RIGHT) for j in coins_to_flip ]
            for j in silver_coins_to_flip:
                coins[j].add_updater(lambda o : copper_to_silver(o, coin_flip_tracker.get_value()))
            for j in copper_coins_to_flip:
                coins[j].add_updater(lambda o : silver_to_copper(o, coin_flip_tracker.get_value()))
            self.play(*flips, coin_flip_tracker.animate.set_value(1.0), rate_func=linear, run_time=0.25)
            self.wait(0.5)
            prev_silver_coins = silver_coins
            prev_copper_coins = copper_coins

class Entropy_Measures_Probability(Scene):
    def construct(self):
        box = RoundedRectangle(width=7.8, height=7.8, color="#DC143C")
        box.move_to([3.125, 0, 0])
        self.add(box)
        coins_pos = [ (0.75 * x - 1, 0.75 * y - 2.0 + 0.125, 0) for x in range(1, 11) for y in range(-2, 8) ]
        coins = [ Circle(radius = 0.25, color="#C88343", fill_opacity=1, stroke_width=5) for k in range(len(coins_pos)) ]
        for circle in coins:
            circle.set_fill("#C88343")
        for coin, pos in zip(coins, coins_pos):
            coin.move_to(pos)
            self.add(coin)
        entropy_tex = Tex(r"""$S =$""").shift(LEFT * 4.5 + UP * 2)
        entropy_units_tex = Tex(r"""$k_B$""")
        entropy = DecimalNumber(0)
        entropy.next_to(entropy_tex, RIGHT)
        silver_coins = {}
        copper_coins = set(range(0, 100))
        entropy.add_updater(lambda d: d.set_value(m.lgamma(100.0 + 1.0) - m.lgamma(len(silver_coins) + 1) - m.lgamma(len(copper_coins) + 1)))
        num_heads_tex = Tex(r"""\# Heads =""").shift(LEFT * 4.5 + UP * 1)
        num_heads = DecimalNumber(
            len(silver_coins),
            num_decimal_places=0
        )
        num_heads.next_to(num_heads_tex, RIGHT)
        entropy_units_tex.next_to(num_heads, RIGHT)
        num_heads.add_updater(lambda d: d.set_value(len(silver_coins)))
        self.play(
            Create(entropy_tex),
            Create(entropy),
            Create(num_heads_tex),
            Create(num_heads)
        )
        random_coins = list(range(len(coins)))
        rd.shuffle(random_coins)
        silver_coins = set(random_coins[:(len(random_coins) // 20)])
        copper_coins = set(random_coins[(len(random_coins) // 20):])
        flips = []
        for i in silver_coins:
            coins[i].add_updater(lambda o : copper_to_silver(o, coin_flip_tracker.get_value()))
            flips.append(Rotate(coins[i], axis = RIGHT))
        coin_flip_tracker = ValueTracker(0)
        self.play(*flips, coin_flip_tracker.animate.set_value(1.0), rate_func=linear, run_time=0.25)
        self.wait(0.5)
        prev_silver_coins = silver_coins
        prev_copper_coins = copper_coins
        for i in range(60):
            self.remove(*coins)
            coins = []
            j = 0
            while j < len(prev_silver_coins):
                if len(coins) in prev_silver_coins:
                    coins.append(
                        Circle(radius = 0.25, color="#C0C0C0", fill_opacity=1,
                        stroke_width=5)
                    )
                    coins[-1].set_fill("#C0C0C0")
                    j += 1
                else:
                    coins.append(
                        Circle(radius = 0.25, color="#C88343", fill_opacity=1,
                        stroke_width=5)
                    )
                    coins[-1].set_fill("#C88343")
            for j in range(len(coins), 100):
                coins.append(
                    Circle(radius = 0.25, color="#C88343", fill_opacity=1,
                    stroke_width=5)
                )
                coins[-1].set_fill("#C88343")
            for k in range(len(coins)):
                coins[k].move_to(coins_pos[k])
                self.add(coins[k])
            coin_flip_tracker.set_value(0.0)
            rd.shuffle(random_coins)
            coins_to_flip = set(random_coins[:len(random_coins) // 20])
            flips = [ Rotate(coins[j], axis = RIGHT) for j in coins_to_flip ]
            silver_coins = prev_silver_coins
            copper_coins = prev_copper_coins
            for j in coins_to_flip:
                if j in prev_silver_coins:
                    coins[j].add_updater(lambda o : silver_to_copper(o, coin_flip_tracker.get_value()))
                    copper_coins.add(j)
                    silver_coins.remove(j)
                else:
                    coins[j].add_updater(lambda o : copper_to_silver(o, coin_flip_tracker.get_value()))
                    silver_coins.add(j)
                    copper_coins.remove(j)
            print((len(silver_coins), len(copper_coins), len(silver_coins) + len(copper_coins)))
            self.play(*flips, coin_flip_tracker.animate.set_value(1.0), rate_func=linear, run_time=0.25)
            self.wait(0.25)
            prev_silver_coins = silver_coins
            prev_copper_coins = copper_coins

class Entropy_Definitions(Scene):
    def construct(self):
        definitions = [
            MathTex(r"S = k_B \ln \Omega", substrings_to_isolate="S"),
            MathTex(r"dE = T dS", substrings_to_isolate=[ "S", "T", "dS", "dE" ]),
        ]
        ft = [
            MarkupText(f'The Two', font="Noto Sans"),
            MarkupText(f'Definitions of <span fgcolor="#DC143C">Entropy</span>', font="Noto Sans")
        ]
        ft[0].move_to([0, 2.75, 0])
        ft[1].next_to(ft[0], DOWN)
        definitions[0].move_to([0, 0, 0])
        definitions[1].move_to([0, -1.5, 0])
        for definition in definitions:
            definition.set_color_by_tex("S", "#DC143C")
        box = RoundedRectangle(width=3, height=1.5, color="#DC143C")
        box.move_to([0, 0, 0])
        hline = Line([-10, 1.5, 0], [10, 1.5, 0])
        self.add(*ft, *definitions, hline)
        self.play(Create(box))
        self.wait(3)
        path = Line([0, 0, 0], [0, -1.5, 0])
        self.play(MoveAlongPath(box, path))
        self.wait(3)

class Second_Law(Scene):
    def construct(self):
        ft = [
            MarkupText(f'The Second Law', font="Noto Sans"),
            MarkupText(f'of Thermodynamics', font="Noto Sans")
        ]
        ft[0].move_to([0, 2.75, 0])
        ft[1].next_to(ft[0], DOWN)
        hline = Line([-10, 1.5, 0], [10, 1.5, 0])
        statement = [
            MarkupText(f'<span fgcolor="#DC143C">Entropy</span> tends towards a <span fgcolor="#FF0000">maximum</span>', font="Noto Sans"),
            MarkupText(f'in <span fgcolor="#DD77DD">isolated systems</span>.', font="Noto Sans")
        ]
        statement[0].move_to([0, 0, 0])
        statement[1].next_to(statement[0], DOWN)
        self.add(*ft, hline)
        self.play(Create(statement[0]))
        self.play(Create(statement[1]))
        self.wait(3)

class See_Description_For_More_Info(Scene):
    def construct(self):
        message = [
            MarkupText(f'See the <span fgcolor="#B57EDC">description</span> for', font="Noto Sans"),
            MarkupText(f'an <span fgcolor="#DC143C">in-depth explanation</span>.', font="Noto Sans")
        ]
        for k in message:
            k.scale(1.5)
        message[0].move_to(2 * UP)
        message[1].next_to(message[0], DOWN)
        self.play(Create(message[0]))
        self.play(Create(message[1]))
        self.wait(5)

rd.seed(127)
