to run on mac, you need to comment out references to add_defined_function in the foma python package. https://github.com/mhulden/foma/issues/100

STEPS:

brew install foma?
pip install foma
(delete references to add_defined_function)
make (I ran out of ram trying to do this locally, can send the compiled file)
python underive.py > ess_net.tsv


