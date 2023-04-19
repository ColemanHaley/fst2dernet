.PHONY: all downloadess
all: fsts/ess-2.8/l2s.fomabin analyses/ess.tsv
fsts/ess-2.8/l2s.fomabin: fsts/ess-2.8/ess.foma
	cd fsts/ess-2.8/; make -f Makefile l2s.fomabin

analyses/ess.tsv:
	cat fsts/ess-2.8/tests/**/*.tsv > $@

kal_words.txt: fsts/lang-kal/tools/shellscripts/kal-analyse
	wget https://github.com/AlexJonesNLP/KALComp/raw/main/data/kl/mono.kl
	cat mono.kl | fsts/lang-kal/tools/shellscripts/kal-analyse > kal_words.txt
crk_words.txt: fsts/lang-crk/tools/shellscripts/crk-analyse crk.txt
	cat crk.txt | fsts/lang-crk/tools/shellscripts/crk-analyse > crk_words.txt


	
fsts/ess-2.8/ess.foma:
	@mkdir -p fsts/
	@cd fsts/; \
	wget https://github.com/SaintLawrenceIslandYupik/finite_state_morphology/archive/refs/tags/2.8.zip; \
	unzip 2.8.zip; mv finite_state_morphology-2.8 ess-2.8; rm 2.8.zip



