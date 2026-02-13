# instructions
DNA is made of the following four pieces:
``````
Adenine (A)
Cytosine (C)
Guanine (G)
Thymine (T)
A DNA sequence is made of three-letter combinations of these pieces, such as 'ACG', TCA', and 'CGT'.

Let's use a Python list to find a specific three-letter combination, starting with the following:

dna_sequence = ['GCT', 'AGC', 'AGG', 'TAA', 'ACT', 'CAT', 'TAT', 'CCC', 'ACG', 'GAA', 'ACC', 'GGA']
Next, define two variables:

item_to_find string that is set as a three-letter combination of your choice, with no spaces (e.g. 'TGA' or 'CAT').
item_found boolean, initialized to False.
Loop through each item in the dna_sequence list. Inside, use an if statement to test if a given item is equal to the item_to_find. If so, set item_found to True.

Outside the loop, use an if/else statement to check if item_found is True:

If so, print something like "Item Found!"
Else, print something like "Item not found."