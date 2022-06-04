#!/usr/bin/env python3
# Copyright (C) 2022 Thomas Schmid
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from errno import EL2HLT
from numpy import angle
from sympy import E1
from boxes import *


class ParachuteCompartment(Boxes):
    """Round box made from layers with twist on top"""

    description = """Glue together - all outside rings to the bottom, all inside rings to the top."""
    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)

        self.argparser.add_argument(
            "--diameter",  action="store", type=float, default=77.,
            help="Inner Diameter of the pet bottel in mm")
        self.argparser.add_argument(
            "--wall_thickness",  action="store", type=float, default=1.5,
            help="Wall thickness of the pet bottel in mm")
        self.argparser.add_argument(
            "--height",  action="store", type=float, default=81,
            help="Height of the parachute compartment")
        self.argparser.add_argument(
            "--timer_side_distance", action="store", type=float, default=11.5, help="Distance from face of tommy timer to side of the bottle")
        self.argparser.add_argument(
            "--timer_width", action="store", type=float, default=15.5, help="Width of tommy timer")
        self.argparser.add_argument(
            "--timer_height", action="store", type=float, default=29, help="Width of tommy timer")
        self.argparser.add_argument(
            "--timer_depth", action="store", type=float, default=12.5, help="Width of tommy timer")
        self.buildArgParser("outside")
        self.addSettingsArgs(edges.FingerJointSettings)

    def side_plate_2_finger_holes(self):
        self.fingerHolesAt(-self.compartment_width / 2 - self.thickness *
                           1.5, -self.side_plate_2_width/2, self.side_plate_2_width, angle=90)
        self.fingerHolesAt(self.compartment_width / 2 + self.thickness *
                           1.5, -self.side_plate_2_width/2, self.side_plate_2_width, angle=90)

    def bottom_plate_finger_holes(self):
        self.fingerHolesAt(-self.compartment_width/2, 0,
                           self.compartment_width, angle=0)
        self.fingerHolesAt(-self.compartment_width / 2 - self.thickness /
                           2, -self.side_plate_width/2, self.side_plate_width, angle=90)
        self.fingerHolesAt(self.compartment_width / 2 + self.thickness /
                           2, -self.side_plate_width/2, self.side_plate_width, angle=90)
        self.side_plate_2_finger_holes()

    def top_plate_finger_holes(self):
        with self.saved_context():
            self.fingerHolesAt(-self.lt/2, 0, self.lt, angle=0)
            self.side_plate_2_finger_holes()

        angles = [-90, 90, 90, -90]
        x = self.compartment_width / 2 + 0.5 * self.thickness
        y = self.side_plate_width / 2
        pos = [(x, y), (x, -y), (-x, -y), (-x, y)]

        for i, p in enumerate(pos):
            with self.saved_context():
                self.moveTo(p[0], p[1])
                self.fingerHolesAt(
                    0, 0, self.side_plate_2_top_finger_length, angles[i])

        self.rectangularHole(self.compartment_width/2 + self.thickness - self.timer_depth,
                             0, self.timer_depth, self.timer_width, center_x=False, center_y=True)
        self.rectangularHole(-(self.compartment_width/2 + self.thickness), 0,
                             self.timer_depth, self.timer_width, center_x=False, center_y=True)

    def finger_holes(self, inner=False, outer=False):
        d = self.diameter

        self.fingerHolesAt(0, 0, 30)

        with self.saved_context():
            self.hole(0, 0, d=d/4)

    def draw_edges(self, edges, length: list, angles: list, callback=None):
        for i, l in enumerate(length):
            self.cc(callback, i, y=edges[i].startwidth() + self.burn)
            e1 = edges[i]
            e2 = edges[i + 1]

            edges[i](l)
            self.edgeCorner(e1, e2, angles[i])

    def side_plate_2_cutout(self):
        # draw clock wise to work with burn correction
        self.moveTo(self.side_plate_2_width/2 - 4, self.inner_height - 20)
        straight_edge = 8
        long_endge = 18
        radius = 0
        polyline = [long_endge, (-90, radius),
                    straight_edge, (-90, radius)] * 2
        self.moveTo(self.burn, radius, 90)
        self.polyline(*polyline)
        self.moveTo(0, 0, 270)
        self.moveTo(0, -radius)
        self.moveTo(-self.burn)

    def side_plate_cutout(self):
        self.fingerHolesAt(self.side_plate_width/2, 0, self.ls, 90)

    def side_plate(self, move=None, label=None, callback=None):
        x = 2 * (self.compartment_width / 2) / self.diameter
        width = self.diameter/2 * 2 * (math.sqrt(1-x**2))
        height = self.inner_height

        edges = "fefeeefe"
        angles = [90, 90, 90, -90, -90, 90, 90, 90]
        l1 = (width - self.timer_width)/2
        self.side_plate_2_top_finger_length = l1
        l2 = self.timer_height - self.thickness
        length = [width, self.inner_height, l1, l2,
                  self.timer_width, l2, l1, self.inner_height]
        edges = [self.edges.get(e, e) for e in edges]
        edges = edges + edges

        overallwidth = width + edges[1].margin() + edges[7].margin()
        overallheight = height + edges[0].margin() + max(edges[2].margin(), edges[6].margin())

        if self.move(overallwidth, overallheight, move, before=True):
            return


        self.moveTo(edges[-1].spacing())
        self.moveTo(0, edges[0].margin())
        self.draw_edges(edges, length, angles, callback)

        self.move(overallwidth, overallheight, move, label=label)

    def centerPlate(self, x, y,
                    move=None,
                    label=""):
        edges = "ffeefeef"

        ls1 = self.inner_height - self.timer_height + self.thickness
        ld = self.timer_depth - self.thickness
        ls2 = self.timer_height - self.thickness
        lt = self.lt

        edges = [self.edges.get(e, e) for e in edges]
        edges += edges
        length = [
            self.compartment_width,
            ls1,
            ld,
            ls2,
            lt,
            ls2,
            ld,
            ls1
        ]

        angles = [
            90, 90, -90, 90, 90, -90, 90, 90
        ]
        overallwidth = self.compartment_width + edges[1].margin() + edges[7].margin()
        overallheight = y + edges[4].spacing() + edges[0].spacing()

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(0, edges[0].margin())
        self.moveTo(edges[0].spacing())
        self.draw_edges(edges, length, angles)
        self.move(overallwidth, overallheight, move, label=label)

    def circ_y(self, diameter, x):
        p = 2 * x / diameter
        return diameter/2 * 2 * (math.sqrt(1-p**2))

    def render(self):
        self.compartment_width = self.diameter - \
            (self.timer_side_distance + self.thickness)*2
        self.side_plate_width = self.circ_y(
            self.diameter, self.compartment_width / 2)
        self.side_plate_2_width = self.circ_y(
            self.diameter, (self.compartment_width) / 2 + self.thickness)
        width = self.timer_width + 2 * self.thickness
        self.lt = self.compartment_width - 2 * \
            (self.timer_depth - self.thickness)
        self.inner_height = self.height - 2 * self.thickness
        self.ls = self.inner_height - (self.timer_height - self.thickness)

        if self.side_plate_2_width > width:
            self.side_plate_2_width = width

        self.rectangularWall(width, self.inner_height, "fefe", callback=[
                             self.side_plate_2_cutout], move="right")
        self.rectangularWall(width, self.inner_height, "fefe", callback=[
                             self.side_plate_2_cutout], move="right")
        self.side_plate(move="right", callback=[self.side_plate_cutout])
        self.side_plate(move="right", callback=[self.side_plate_cutout])
        self.parts.disc(
            self.diameter, callback=lambda: self.bottom_plate_finger_holes(), move="right")
        self.parts.disc(
            self.diameter, callback=lambda: self.top_plate_finger_holes(), move="right")
        self.centerPlate(self.compartment_width, self.height, move="right")
