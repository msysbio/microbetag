# Parsing KEGG modules

## Aim



Scripts under this folder aim at retrieving and parsing the KEGG modules. 

Also, they intend to link each genome retrieved and the KEGG terms that have been annotated to them to their corresponding KEGG modules. 



## Structure

The KEGG modules definitions are parsed and devided in steps.
Each step may has alternatives:

- single KOs (e.g., step 1 in `md:M00022`)
- substeps (e.g., one of the alternatives in step 2 in `md:M000022` include `K01735` > `K03785` > `K00014`)

```JSON
"md:M00022": {
    "#-of-steps": 4,
    "steps": [
        [
            "K01626",
            "K03856",
            "K13853"
        ],
        [
            [
                [
                    "K01735",
                    "K03785"
                ],
                "K00014",
                "K13832"
            ],
            [
                [
                    "K01735",
                    "K03786"
                ],
                "K00014",
                "K13832"
            ],
            [
                [
                    "K13829",
                    "K03785"
                ],
                "K00014",
                "K13832"
            ],
            [
                [
                    "K13829",
                    "K03786"
                ],
                "K00014",
                "K13832"
            ],
            "K13830"
        ],
        [
            [
                "K00891",
                "K00800"
            ],
            [
                "K00891",
                "K24018"
            ],
            [
                "K13829",
                "K00800"
            ],
            [
                "K13829",
                "K24018"
            ],
            "K13830"
        ],
        [
            "K01736"
        ]
    ],
    "unique-KOs": [
        "K03786",
        "K01736",
        "K00800",
        "K01735",
        "K13830",
        "K24018",
        "K03785",
        "K03856",
        "K13829",
        "K00014",
        "K13832",
        "K13853",
        "K00891",
        "K01626"
    ]
}
```

rules:

- `;` stands for next   $\rightarrow$ add
- `,` stands for OR     $\rightarrow$ split
- `+` stands for complex
- `-` stands for not needed

we need a `while` for the  `\(([^)]+)\)` regex

parts = re.findall("\((([^\(\)]*)|(\?R))*\)", md23)

def nested_parens(n):
   if n == 0:
      return ['']
   parens = []
   for i in range(n):
      for a in nested_parens(i):
         for b in nested_parens(n - 1 - i):
            parens.append('(' + a + ')' + b)
   return parens

```python
import pyparse
import re

# As others have mentioned, regular expressions are not the way to go for nested constructs.
# https://stackoverflow.com/questions/5454322/python-how-to-match-nested-parentheses-with-regex
# However, this regex implementation is backwards-compatible with the standard ‘re’ module, but offers additional functionality.
# https://pypi.org/project/regex/
# It will work only at a step at a time

result = regex.search(r'''
                        (?<rec> #capturing group rec
                        \( #open parenthesis
                        (?: #non-capturing group
                        [^()]++ #anyting but parenthesis one or more times without backtracking
                        | #or
                        (?&rec) #recursive substitute of group rec
                        )*
                        \) #close parenthesis
                        )
                        ''',md23,flags=regex.VERBOSE
                    )

result.captures('rec')
step_rest = module_definition.split(result.captures('rec')[-1])[1:][0]

# Now focus on what's going on within a step 
# For left to right in the list, we move from pieces to the full step

def parse_base_block(block):

    return 


def combinations_on_a_step(step):
    for block1, block2 in zip(step, step[1:]):
        match_start_index = block2.index(block1)
        match_end_index   = match_start_index + len(block1)
        how_to = block2[match_end_index:][0]
    
        if how_to == ";":
            #that is an add, meaning that in all the previous cases, we need to add the following block
        elif how_to == ","
            #that is an or , meaning perturbations of the previous with the following block

    return 1
        


```
