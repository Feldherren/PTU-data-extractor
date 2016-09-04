# PTU-data-extractor
Python scripts for extracting data from PTU books.

Currently only deals with the Pokedex book, and has issues with certain odd characters showing up at spots. Data is formatted for use with another application of mine; PTU-trainer-generator, also on github. But it's probably easier to convert to whatever format you want than the PDF itself.

####Things it is currently getting wrong (probably due to encoding weirdness)

Swi╦Ø should be Swift

De╦Üant should be Defiant

####Other notes (1.05 Plus)

Empoleon has 'Omnivore' misspelled as 'Ominvore', and has a period following it, unlike most Diet sections.

Pancham and a few others have 'Human-Like', instead of 'Humanshape' I assume, for an egg-group.

Earlier Pokemon with no gender have 'No Gender' in Gender Ratio. More-recent legendaries have 'Genderless' instead, but I think they're supposed to be the same.

Meloetta has the Advanced Ability 'Spining Dance'; should be 'Spinning Dance'.