.PHONY: all downloadess
all: fsts/ess-2.8/l2s.fomabin analyses/ess.tsv
fsts/ess-2.8/l2s.fomabin: fsts/ess-2.8/ess.foma
	cd fsts/ess-2.8/; make -f Makefile l2s.fomabin

analyses/ess.tsv:
	cat fsts/ess-2.8/tests/**/*.tsv > $@
	
fsts/ess-2.8/ess.foma:
	@mkdir -p fsts/
	@cd fsts/; \
	wget https://github.com/SaintLawrenceIslandYupik/finite_state_morphology/archive/refs/tags/2.8.zip; \
	unzip 2.8.zip; mv finite_state_morphology-2.8 ess-2.8; rm 2.8.zip



