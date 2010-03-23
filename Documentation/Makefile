docgen=rst2pdf
docgenopts= -b1 --fit-literal-mode=shrink --break-side=odd
targets=odin.hermod.pdf

all : $(targets)

clean:
	rm -f $(targets)

%.pdf : %.rst
	$(docgen) $(docgenopts) $< -o $@

