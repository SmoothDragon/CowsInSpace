.PHONY: main clean FORCE

TEXTMP=.textmp
GRAPHICS= $(wildcard graphics/*.pdf)

main: Frictionless.pdf Frictionless.png

Frictionless.tex: Frictionless.tex.py Frictionless.json symbols.tex $(GRAPHICS)

%.tex: %.tex.py
	python3 $< > $@

%.pdf: %.tex
	mkdir -p $(TEXTMP)
	latexmk -auxdir=$(TEXTMP) -outdir=$(TEXTMP) -pdflatex='lualatex -halt-on-error -file-line-error -interaction=errorstopmode' -pdf $<
	mv $(TEXTMP)/$@ .

%.png:	%.pdf
	pdftoppm -singlefile -png $< $*

clean:
	latexmk -pdf -C
