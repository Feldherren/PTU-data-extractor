# PTU-data-extractor
Python scripts for extracting data from PTU books.

Currently only deals with the Pokedex book, and has issues with certain odd characters showing up at spots. Data is formatted for use with another application of mine; PTU-trainer-generator, also on github. But it's probably easier to convert to whatever format you want than the PDF itself.

####Things it is currently getting wrong (probably some dumb encoding issue, but as of currently I still haven't solved it)

Swi╦Ø should be Swift (Ability: Swift Swim, Move: Swift)

De╦Üant should be Defiant (Ability: Defiant)

Con╦Üdence should be Confidence (Ability: Confidence)

In╦Ültrator should be Infiltrator (Ability: Infiltrator)

Flu╦øy should be Fluffy (Ability: Fluffy Charge)

Justi╦Üed should be Justified (Ability: Justified)

Gi╦Ø should be Gift (Ability: Flower Gift, Natural Gift)

E╦øect should be Effect (Ability: Effect Spore)

Re╦åect should be Reflect (Move: Reflect)

Camou╦åage should be Camouflage (Move: Camouflage)

O╦ø should be Out (Move: Knock Out)

╦£under should be Thunder. (Moves: Thunderbolt, Thunder, Thunder Wave)

╦£ief should be Thief. (Move: Thief)

╦£rash should be Thrash (Move: Thrash)

A╦Øer should be After (Move: A╦Øer You)

Con╦Øned should be Confined; as this shows up in Hoopa's name, this means Hoopa is not correctly identified as a legendary pokemon.

Tornadus, Thundurus and Landorus Therian Forme all show up as ╦£Erian Forme; similar to Confined Hoopa, they aren't correctly identified as legendary pokemon. 

Generally doesn't like lower-case Fs. Or F-sounds, even. Most of the issues seem to contain the ╦ character, though, so they should be easy to find.

Wormadam (Plant Cloak Form) doesn't pick up the 'Plant Cloak Form' part of its name; there's more spacing between the species name and the form than the other two (Sand, Trash), and I haven't yet got it to pick up that section.

####Other notes (1.05 Plus)

Empoleon has 'Omnivore' misspelled as 'Ominvore', and has a period following it, unlike most Diet sections.

Pancham and a few others have 'Human-Like', instead of 'Humanshape' I assume, for an egg-group.

Earlier Pokemon with no gender have 'No Gender' in Gender Ratio. More-recent legendaries have 'Genderless' instead, but I think they're supposed to be the same.

Meloetta Aria/Step 'Form', rather than Forme.

Meloetta Step Forme has the Advanced Ability 'Spining Dance'; should be 'Spinning Dance'.

Rhydon has the evolution to Rhyperior requiring a minimum level 50. Rhyhorn and Rhyperior show the minimum as 45.

Machop has the evolution to Machamp requiring a minimum level 35. Rhyhorn and Rhyperior show the minimum as 40.

Gurdurr is missing a linebreak in evolution section, and seems to claim that it needs a minimum level 250 to evolve to Conkeldurr; this means Gurdurr does not list Conkeldurr as an evolution, whilst Timburr and Conkeldurr do.

Combee and Vespiquen have the gender requirement for evolution to Vespiquen specified after the minimum level. Ralts, Kirlia and Gallade have the gender requirement specified before the minimum level.

Mantyke and Mantine misspell 'with' as 'wiht' in the evolution section, and uses commas to separate information. Also use 'Min.' instead of 'Minimum'