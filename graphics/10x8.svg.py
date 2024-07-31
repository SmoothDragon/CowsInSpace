#!/usr/bin/env python

import solid as sd
import numpy as np

import tempfile
import subprocess

def scad2svg(obj):
    # tmp = tempfile.NamedTemporaryFile()
    # with open(tmp.name, 'w+') as outfile:
    with tempfile.NamedTemporaryFile(mode='w', dir='.') as tmp:
        tmp.writelines(sd.scad_render(obj))
        tmp.flush()
        command = f'openscad --export-format svg -o - {tmp.name}'
        p = subprocess.run(command, capture_output=True, shell=True, encoding='utf-8')
    return p.stdout

def setSVGproperty(svg, stroke=None, fill=None, stroke_width=None):
    if fill is not None:
        svg = svg.replace('fill="lightgray"', f'fill="{fill}"')
    if stroke is not None:
        svg = svg.replace('stroke="black"', f'stroke="{stroke}"')
    if stroke_width is not None:
        svg = svg.replace('stroke-width="0.5"', f'stroke-width="{stroke_width}"')
    return svg

def joinSCAD_SVG(svg0,svg1):
    result = svg0.split('\n')[:-2]+svg1.split('\n')[4:]
    return '\n'.join(result)


def board(x,y,square=10,rim=.1):
    black = sd.square(square)
    box = black
    for i in range((x+1)//2):
        for j in range(y):
            box += sd.translate([(2*i+(j&1))*square, j*square])(black)
    return box

def backdrop(x,y,square=10):
    box = sd.square([x*square,y*square])
    return box

def backback(x,y,square=10):
    rim = .2
    box = sd.square([(x+2*rim)*square,(y+2*rim)*square])
    box = sd.translate([-rim*square,-rim*square])(box)
    return box

if __name__ == '__main__':
    x,y,square = 8,10,10
    svg_bb = scad2svg(backback(x,y,square))
    svg_bb = setSVGproperty(svg_bb, fill='white')
    svg_back = scad2svg(backdrop(x,y,square))
    svg_back = setSVGproperty(svg_back, fill='white')
    svg_board = scad2svg(board(x,y,square))
    svg_board = setSVGproperty(svg_board, fill='black', stroke_width=0)
    svg_back = joinSCAD_SVG(svg_bb, svg_back)
    total = joinSCAD_SVG(svg_back, svg_board)
    print(total)

