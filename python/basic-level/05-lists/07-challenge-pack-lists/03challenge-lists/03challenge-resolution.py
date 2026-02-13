dna_sequence = ['GCT', 'AGC', 'AGG', 'TAA', 'ACT', 'CAT', 'TAT', 'CCC', 'ACG', 'GAA', 'ACC', 'GGA']
item_to_find = "CAT"
item_found = False
for item in dna_sequence:
    if item == item_to_find:
        item_found = True

if item_found == True:
    print("Found")
else:
    print("Not Found")