#!/usr/bin/env python3

import os
import re

import itertools

def TikZ_sidebar_card(card):
    CARD_TEMPLATE = [
    r'''\begin{tikzpicture}
    \pgfmathsetmacro{\cardroundingradius}{4mm}
    \pgfmathsetmacro{\striproundingradius}{3mm}
    \pgfmathsetmacro{\cardwidth}{5.9}
    \pgfmathsetmacro{\cardheight}{9.2}
    \pgfmathsetmacro{\stripwidth}{1.2}
    \pgfmathsetmacro{\strippadding}{0.1}
    \pgfmathsetmacro{\textpadding}{0.3}
    \pgfmathsetmacro{\ruleheight}{0.1}
    \providecommand{\stripfontsize}{\Huge}
    \providecommand{\captionfontsize}{\LARGE}
    \providecommand{\textfontsize}{\large}
    \draw[rounded corners=\cardroundingradius] (0,0) rectangle (\cardwidth,\cardheight);
    \fill[''',
    r''',rounded corners=\striproundingradius] (\strippadding,\strippadding) rectangle (\strippadding+\stripwidth,\cardheight-\strippadding) node[rotate=90,above left,black,font=\stripfontsize] {''',
    r'''};
    \node[text width=(\cardwidth-\strippadding-\stripwidth-2*\textpadding)*1cm,below right,inner sep=0] at (\strippadding+\stripwidth+\textpadding,\cardheight-\textpadding) 
    {   {\captionfontsize ''',
    r'''}\\ 
        {\textfontsize ''',
    # r'''}\\
        # \tikz{\fill (0,0) rectangle (\cardwidth-\strippadding-\stripwidth-2*\textpadding,\ruleheight);}\\
        # {\captionfontsize ''',
    r'''}\\
        \tikz{\fill (0,0) rectangle (\cardwidth-\strippadding-\stripwidth-2*\textpadding,\ruleheight);}\\
        {\textfontsize ''',
    r'''}\\
    };
    \end{tikzpicture}%''',
    ]

    striptext = card['striptext'] + r' \rotatebox[origin=c]{-90}{' + card['symbol'] + r'}'
    CARD_DATA = [card['stripcolor'], striptext, card['caption'], card['description'], card['quote']]
    # CARD_DATA = [card['stripcolor'], striptext, card['caption'], card['description'], card['bottomcaption'], card['quote']]
    CARD_TEX = itertools.chain(*itertools.zip_longest(CARD_TEMPLATE, CARD_DATA, fillvalue=''))
    # for v in CARD_TEX:
        # print(v)
    # print((CARD_TEX))
    print(''.join(CARD_TEX))

def TikZ_card(card):
    CARD_TEMPLATE = [
    r'''\begin{tikzpicture}
    \pgfmathsetmacro{\cardroundingradius}{5mm}
    \pgfmathsetmacro{\striproundingradius}{3mm}
    % \pgfmathsetmacro{\cardwidth}{5.9}
    % \pgfmathsetmacro{\cardheight}{9.2}
    \pgfmathsetmacro{\cardwidth}{5.7}
    \pgfmathsetmacro{\cardheight}{8.9}
    \pgfmathsetmacro{\stripwidth}{1.2}
    \pgfmathsetmacro{\strippadding}{0.1}
    \pgfmathsetmacro{\textpadding}{0.3}
    \pgfmathsetmacro{\ruleheight}{0.1}
    \providecommand{\stripfontsize}{\Huge}
    \providecommand{\captionfontsize}{\LARGE}
    \providecommand{\textfontsize}{\Large}
    \providecommand{\quotefontsize}{\small}
    \draw[line width=2mm,rounded corners=\cardroundingradius] (0,0) rectangle (\cardwidth,\cardheight);
    \draw[line width=2mm] (0,0) rectangle (\cardwidth,\cardheight);
    \node[text width=(\cardwidth-\strippadding-2*\textpadding)*1cm,below right,inner sep=0] at (\strippadding+\textpadding,\cardheight-\textpadding) 
    { 
    \begin{center} {\fontsize{80pt}{60pt}\selectfont ''',
    r'''}\\\end{center}
\begin{center}
    {\captionfontsize \textsf{\textbf{''',
    r'''}}}\end{center}
        {\textfontsize ''',
    r'''}\\
        \tikz{\fill (0,0) rectangle (\cardwidth-2*\strippadding-2*\textpadding,\ruleheight);}\\
        {\quotefontsize \textit{''',
    r'''}}\\[-2\baselineskip]
    };
    \node[circle,draw,text=black](c) at (.5,\cardheight-.5){''',
    r'''};
    \end{tikzpicture}%''',
    ]

    origin = '?'
    if 'origin' in card:
        origin = card['origin']
    CARD_DATA = [card['symbol'],card['caption'], card['description'], card['quote'], origin]
    # CARD_DATA = [card['stripcolor'], striptext, card['caption'], card['description'], card['bottomcaption'], card['quote']]
    CARD_TEX = itertools.chain(*itertools.zip_longest(CARD_TEMPLATE, CARD_DATA, fillvalue=''))
    # for v in CARD_TEX:
        # print(v)
    # print((CARD_TEX))
    print(''.join(CARD_TEX))

def buildTeX(cards):
    TEX_HEADER = r'''
    % latexmk -pdflatex='lualatex' -pdf FontExhibition.tex
    \documentclass[parskip,landscape,letter]{scrartcl}
    \usepackage{fontspec}
    \usepackage[margin=10mm,left=30mm]{geometry}
    \usepackage{tikz}
    \usetikzlibrary{matrix,backgrounds}
    \usepackage{pifont}
    \usepackage{graphicx}
    \usepackage{chessfss}
    \usepackage{setspace}
    \usepackage{stackengine,scalerel}
    %\providecommand{\move}{\stackengine{0pt}{\u2194}{\u2195}{O}{c}{F}{F}{L}}
    \begin{document}
    \setmainfont[Extension={.ttf},ItalicFont={DejaVuSerif-Italic}]{FreeSerif}
    '''

    TEX_FOOTER = r'''
    \end{document}
    '''
    print(TEX_HEADER)
    for i, card in enumerate(cards):
        # TikZ_sidebar_card(card)
        TikZ_card(card)
        if i%4==3:
            print(r'\\[-\lineskip]')
    print(TEX_FOOTER)

def Magic_TikZ_card(card):
    CARD_TEMPLATE = [
    r'''\begin{tikzpicture}
    \pgfmathsetmacro{\cardroundingradius}{5mm}
    \pgfmathsetmacro{\striproundingradius}{3mm}
    % \pgfmathsetmacro{\cardwidth}{5.9}
    % \pgfmathsetmacro{\cardheight}{9.2}
    \pgfmathsetmacro{\cardwidth}{6.1}  % Magic cards are 63x88mm
    \pgfmathsetmacro{\cardheight}{8.6}
    \pgfmathsetmacro{\stripwidth}{1.2}
    \pgfmathsetmacro{\strippadding}{0.1}
    \pgfmathsetmacro{\textpadding}{0.3}
    \pgfmathsetmacro{\ruleheight}{0.1}
    \providecommand{\stripfontsize}{\Huge}
    \providecommand{\captionfontsize}{\LARGE}
    \providecommand{\textfontsize}{\Large}
    \providecommand{\quotefontsize}{\small}
    \draw[line width=2mm,rounded corners=\cardroundingradius] (0,0) rectangle (\cardwidth,\cardheight);
    \draw[line width=2mm] (0,0) rectangle (\cardwidth,\cardheight);
    \node[text width=(\cardwidth-\strippadding-2*\textpadding)*1cm,below right,inner sep=0] at (\strippadding+\textpadding,\cardheight-\textpadding) 
    { 
    \begin{center} {\fontsize{80pt}{60pt}\selectfont ''',
    r'''}\\\end{center}
\begin{center}
    {\captionfontsize \textsf{\textbf{''',
    r'''}}}\end{center}
        {\textfontsize ''',
    r'''}
        \tikz{\fill (0,0) rectangle (\cardwidth-2*\strippadding-2*\textpadding,\ruleheight);}\\
        {\quotefontsize \textit{''',
    r'''}}\\[-2\baselineskip]
    };
    \node[circle,draw,text=black](c) at (.5,\cardheight-.5){''',
    r'''};
    \node[circle,draw,text=black](c) at (\cardwidth-.5,\cardheight-.5){''',
    r'''};
    \end{tikzpicture}%''',
    ]

    origin = '?'
    genre = '?'
    if 'origin' in card:
        origin = card['origin']
    if 'genre' in card:
        genre = card['genre']
    if 'graphic' in card:
        card['quote'] = card['graphic']
    CARD_DATA = [card['symbol'],card['caption'], card['description'], card['quote'], origin, genre]
    # CARD_DATA = [card['stripcolor'], striptext, card['caption'], card['description'], card['bottomcaption'], card['quote']]
    CARD_TEX = itertools.chain(*itertools.zip_longest(CARD_TEMPLATE, CARD_DATA, fillvalue=''))
    # for v in CARD_TEX:
        # print(v)
    # print((CARD_TEX))
    print(''.join(CARD_TEX))

def buildMagicTeX(cards):
    TEX_HEADER = r'''
    % latexmk -pdflatex='lualatex' -pdf FontExhibition.tex
    \documentclass[parskip,landscape,letter]{scrartcl}
    \usepackage{fontspec}
    \usepackage[margin=10mm,left=20mm]{geometry}
    \usepackage{tikz}
    \usetikzlibrary{matrix,backgrounds}
    \usepackage{pifont}
    \usepackage{graphicx}
    \usepackage{chessfss}
    \usepackage{setspace}
    \usepackage{enumitem}
    \usepackage{amssymb}
    \usepackage{graphicx,calc}
    \graphicspath{{./graphics/}}
    \input{symbols.tex}

    \begin{document}
    \setmainfont[Extension={.ttf},ItalicFont={DejaVuSerif-Italic}]{FreeSerif}
    '''

    TEX_FOOTER = r'''
    \end{document}
    '''
    print(TEX_HEADER)
    for i, card in enumerate(cards):
        # TikZ_sidebar_card(card)
        Magic_TikZ_card(card)
        print(r'\hspace{1pt}%')
        if i%4==3:
            print(r'\\[-.5\lineskip]')
    print(TEX_FOOTER)

if __name__ == '__main__':
    import json

    cardfile = 'Frictionless.json'
    # with open('cards.json', 'w') as outfile:
        # json.dump(cards, outfile, indent=2, sort_keys=True)
    with open(cardfile, 'r') as infile:
        json_dict = json.load(infile)
    cards = json_dict['text_cards']
    gcards = json_dict['graphic_cards']
    buildMagicTeX(cards)
    # buildTeX(cards)
    # buildTeX(gcards)
