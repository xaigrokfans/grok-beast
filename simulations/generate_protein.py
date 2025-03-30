from Bio.Seq import Seq
import random
amino_acids = "ACDEFGHIKLMNPQRSTVWY"
sequence = ''.join(random.choice(amino_acids) for _ in range(100))
with open("simulations/protein_100.fasta", "w") as f:
    f.write(">T1030 Grok-beast 2.0 Protein Folding Test (100 residues)\n")
    f.write(f"{sequence[:60]}\n{sequence[60:]}\n")
