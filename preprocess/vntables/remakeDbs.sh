rm -rf vntables
sort wn_to_vn.txt | uniq | cut -f1,2 | python3 quotecols.py > wn_to_vn_derby.tsv
sort vn_to_vn.txt | uniq | cut -f1,2 | python3 quotecols.py > vn_to_vn_derby.tsv
ij import-derby.sql
