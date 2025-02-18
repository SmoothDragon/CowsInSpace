import numpy as np
import solid2 as sd
import drawsvg as draw
import collections

def complex2eisen(v):
    return v.real+.5*v.imag, 3**.5*v.imag/2

def calc_edges(n):
    vertices = np.array([0, 1,2+1j, 2+2j, 1+2j, 1j])
    hexagon = np.array(list(zip(vertices, np.roll(vertices, -1))))
    edges = np.vstack([hexagon + ii*(1+2j) for ii in range(n)])
    for jj in range(1,n):
        edges = np.vstack([edges, np.vstack([hexagon +(2+1j)*jj + ii*(1+2j) for ii in range(n-jj)])])
    # edges = np.vstack([edges + ii*(1-1j) for ii in range(n)])
    # edges = np.vstack([edges + ii*(1+2j) for ii in range(n+1)])
    return edges

def calc_perimeter(edges):
    edges = [sorted(((xy[0].real, xy[0].imag), (xy[1].real, xy[1].imag))) for xy in edges]
    edges = [tuple(xy) for xy in edges]
    counts = collections.Counter(edges)
    perimeter = np.array([[xy[0][0]+1j*xy[0][1], xy[1][0]+1j*xy[1][1]] for xy in counts if counts[xy]==1])
    interior = np.array([[xy[0][0]+1j*xy[0][1], xy[1][0]+1j*xy[1][1]] for xy in counts if counts[xy]==2])
    return perimeter, interior

def add_grid(d, edges, color='black', stroke_width=2):
    # edges = 10*3.78*edges
    edges = 15*3.78*edges
    for edge in edges:
        d.append(draw.Line(*complex2eisen(edge[0]),*complex2eisen(edge[1]), stroke=color, stroke_width=stroke_width, fill='none'))

def addCenters(d,n):
    centers = np.array([1+1j + jj*(1-1j) + (jj+ii)*(1+2j)  for jj in range(n) for ii in range(n-jj)])
    # centers = np.hstack([centers + ii*(1+2j) for ii in range(n+1)])
    # centers = 10*3.78*centers
    centers = np.hstack([centers, 9*(1+2j) +centers, 28+27j-centers])
    centers = 15*3.78*centers
    for center in centers:
        d.append(draw.Circle(*complex2eisen(center),10, stroke=cut, stroke_width=2, fill='red'))

def extend(edges):
    result = np.vstack([edges, 9*(1+2j) +edges, 28+27j-edges])
    return result

if __name__ == '__main__':
    fn = 64
    d = 26  # 26mm is close to the max print size of the MK3S and two triangles can fit diagonally for laser cutting from a square foot acrylic sheet
    # 26mm is close to the max print size of the MK3S and two triangles can fit
    # diagonally for laser cutting from a square foot acrylic sheet.
    d = 26
    n = 9
    pos = []
    neg = []
    large = sd.linear_extrude(4)(sd.circle(d=d))
    small = sd.translate([0,0,-1])(sd.linear_extrude(6)(sd.circle(d=d/4)))
    outer = sd.linear_extrude(4)(sd.rotate(0)(sd.intersection()(sd.square(d),sd.circle(d=2*d)-sd.circle(d=d))))
    outer = sd.intersection()(outer,sd.rotate(-30)(outer))
    outer = sd.rotate(60)(outer)
    outer = sd.translate([d*.5, -d*.5*3**.5])(outer)
    outer = sd.union()(*[sd.translate([ii*d,0])(outer) for ii in range(n-1)])
    # outer = sd.translate(complex2eisen((2.75+2.75j)*(-d)))(outer)
    outer = sd.translate((-d*.5*8, -d*4*3**-.5))(outer)
    outer = sd.union()(*[sd.rotate(ii*120)(outer) for ii in range(3)])
    outer = sd.translate((d*.5*8, d*4*3**-.5))(outer)
    for x in range(n):
        for y in range(n-x):
            pos.append(sd.translate(complex2eisen((x+1j*y)*d))(large))
    for x in range(n-1):
        for y in range(n-1-x):
            neg.append(sd.translate(complex2eisen((x+1j*y+1/3+1j/3)*d))(small))
    for x in range(n-2):
        for y in range(n-2-x):
            neg.append(sd.translate(complex2eisen((x+1j*y+2/3+2j/3)*d))(small))
    result = sd.union()(*pos)
    # result += sd.linear_extrude(4)(sd.polygon([(0,0), ((n-1)*d,0), complex2eisen((1j)*(n-1)*d)]))
    result += outer
    result -= sd.union()(*neg)
    result = sd.scale([1,1,.5])(result)
    final = sd.scad_render(result, file_header=f'$fn={fn};')
    print(final)



