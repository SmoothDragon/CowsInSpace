import numpy as np
import drawsvg as draw
import collections

def complex2eisen(v):
    return 3**.5*v.imag/2, v.real-.5*v.imag

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
    cut = 'black'
    mark = 'green'
    d = draw.Drawing(2000, 1000, origin=(-100,-100))

    # Write edges in eisenstein coordinates 1,w = (1,0) and (-1,3**.5)/2
    n = 9
    edges = calc_edges(n)
    # add_grid(d, edges, mark)
    perimeter, interior = calc_perimeter(edges)
    # add_grid(d, perimeter, cut, stroke_width=5)
    add_grid(d, extend(perimeter), cut, stroke_width=5)
    add_grid(d, extend(interior), mark, stroke_width=3)
    addCenters(d, n)
    d.save_svg('TriangleBoard.svg')


