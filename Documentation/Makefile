docgen= rst2pdf
docgenopts= -b1 --fit-literal-mode=shrink --break-side=odd
graphgen= dot
dotsource= $(wildcard *.dot)
images= $(patsubst %.dot, %.svg,$(dotsource))

targets=$(images) odin.hermod.pdf

all : $(targets)

clean:
	rm -f $(targets)

%.pdf : %.rst
	$(docgen) $(docgenopts) $< -o $@

%.svg : %.dot
	$(graphgen) -Tsvg $< -o $@
