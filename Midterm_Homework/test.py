import os
from personal_collections.dna_contamination import DNAContamination


def test(s, k, l):
    """It reads DNA strings from the dataset target_batcha.fasta and return the indices of the k contaminants in the
    dataset with larger degree of contamination in s, assuming l as contamination threshold"""
    DNA = DNAContamination(s, l)

    with open(os.path.dirname(os.path.abspath(__file__)) + "/target_batch.fasta", "r") as f:
        lines = f.readlines()

    flag = True
    n_cont = 0
    for line in lines:
        if flag:
            n_cont = int(line[1:-1])
            flag = False
        else:
            flag = True
            DNA.addContaminant([n_cont, line[:-1]])

    contaminants = DNA.getContaminants(k)
    contaminants.sort()

    return str(contaminants)[1:-1]
