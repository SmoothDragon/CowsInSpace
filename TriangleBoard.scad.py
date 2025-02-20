import numpy as np
import solid2 as sd
import drawsvg as draw
import collections

def complex2eisen(v):
    return v.real+.5*v.imag, 3**.5*v.imag/2

def pin_holes(n, d, d_pin):
    pin_hole = sd.circle(d=d_pin)
    neg = []
    for x in range(n-1):
        for y in range(n-1-x):
            neg.append(sd.translate(complex2eisen((x+1j*y+1/3+1j/3)*d))(pin_hole))
    for x in range(n+1):
        for y in range(n+1-x):
            neg.append(sd.translate(complex2eisen((x+1j*y-1/3-1j/3)*d))(pin_hole))
    return neg

def pin_bumps(n, d, d_pin):
    pin_hole = sd.circle(d=d_pin)
    pin_bump = sd.translate([6*d_pin, 0])(sd.circle(3*d_pin))
    pin_bump = sd.union()(*[sd.rotate(120*ii)(pin_bump) for ii in range(3)])
    neg = []
    for x in range(n-1):
        for y in range(n-1-x):
            neg.append(sd.translate(complex2eisen((x+1j*y+1/3+1j/3)*d))(pin_bump))
    for x in range(n+1):
        for y in range(n+1-x):
            neg.append(sd.translate(complex2eisen((x+1j*y-1/3-1j/3)*d))(pin_bump))
    return sd.union()(*neg)

def line_grooves(n, d, w_groove):
    line = sd.square([3*n*d, 4*w_groove], center=True)
    lines = sd.union()(*[sd.translate([0,3**.5/2*d*ii])(line) for ii in range(-n-1,n+2)])
    lines = sd.union()(*[sd.rotate(120*ii)(lines) for ii in range(3)])
    # lines = sd.offset(r=-w_groove)(lines)
    line2 = sd.square([3*n*d, 3*w_groove], center=True)
    lines2 = sd.union()(*[sd.translate([0,3**.5/2*d*ii])(line2) for ii in range(-n-1,n+2)])
    lines2 = sd.union()(*[sd.rotate(120*ii)(lines2) for ii in range(3)])
    result = lines - lines2
    # result = lines
    # if False:  # Circles
        # result = sd.translate((-d*.5*8, -d*4*3**-.5))(result)
        # result = sd.intersection()(result, sd.union()(*[sd.circle(r=1.6*ii)-sd.circle(r=1.6*ii-0.8) for ii in range(90)]))
        # result = sd.translate((d*.5*8, d*4*3**-.5))(result)
    return result

def board(n,d, hex_holes=True):
    large = (sd.circle(d=d))
    pos = []
    for x in range(n):
        for y in range(n-x):
            pos.append(sd.translate(complex2eisen((x+1j*y)*d))(large))
    result = sd.union()(*pos)
    result += (sd.polygon([(0,0), ((n-1)*d,0), complex2eisen((1j)*(n-1)*d)]))
    if hex_holes:
        pos = []
        for x in range(n):
            for y in range(n-x):
                pos.append(sd.translate(complex2eisen((x+1j*y)*d))(sd.rotate(30)(sd.circle(d=d/3, _fn=6))))
        result -= sd.union()(*pos)
    return result

def outer_edge(n,d):
    outer = (sd.rotate(0)(sd.intersection()(sd.square(d),sd.circle(d=2*d)-sd.circle(d=d))))
    outer = sd.intersection()(outer,sd.rotate(-30)(outer))
    outer = sd.rotate(60)(outer)
    outer = sd.intersection()(sd.rotate(45)(sd.square([1.5*d,1.5*d], center=True)), outer)
    outer = sd.translate([d*.5, -d*.5*3**.5])(outer)
    outer = sd.union()(*[sd.translate([ii*d,0])(outer) for ii in range(n-1)])
    # outer = sd.translate(complex2eisen((2.75+2.75j)*(-d)))(outer)
    outer = sd.translate((-d*.5*8, -d*4*3**-.5))(outer)
    outer = sd.union()(*[sd.rotate(ii*120)(outer) for ii in range(3)])
    outer = sd.translate((d*.5*8, d*4*3**-.5))(outer)
    return outer

if __name__ == '__main__':
    fn = 64  # edges around a circle
    # 26mm is close to the max print size of the MK3S and two triangles can fit
    # diagonally for laser cutting from a square foot acrylic sheet.
    d = 26
    d_pin = 2.5  # Pin hole diameter chosen so that two walls of thickness will be achieved
    n = 9
    h = 3  # height of board piece. Acrylic is typically 3mm
    pos = []
    result = board(n,d)
    result += outer_edge(n,d)
    # result -= sd.union()(*pin_holes(n, d, d_pin))
    # connect = sd.intersection()(result, pin_bumps(n, d, d_pin))
    final = sd.linear_extrude(2.6)(result)
    # result += sd.linear_extrude(4)(connect)
    final += sd.translate([0,0,2.6])(sd.linear_extrude(.4)(result-line_grooves(n,d,2)))
    # final += sd.translate([0,0,2.6])(sd.linear_extrude(.4)(result & line_grooves(n,d,2)))
    # final = line_grooves(n,d,2)
    final = sd.scad_render(final, file_header=f'$fn={fn};')
    print(final)



