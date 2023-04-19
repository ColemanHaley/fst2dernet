This repository contains code for generating derivational networks from finite-state morphological transducers, as well as generated networks for Greenlandic and SLI Yupik. More details can be found here: https://docs.google.com/presentation/d/17oQFyjVaC0xToOZ5lk6-cIt_3f28PhNkhW3KZgGsRto/edit?usp=sharing

The networks in [Universal Derivations](https://ufal.mff.cuni.cz/universal-derivations) format are in the `networks/` directory.

To run on mac, you need to comment out references to add_defined_function in the foma python package. https://github.com/mhulden/foma/issues/100

STEPS:

brew install foma?
pip install foma
(delete references to add_defined_function)
make 
python underive.py > ess_net.tsv


