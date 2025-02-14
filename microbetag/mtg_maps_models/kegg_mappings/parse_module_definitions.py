"""
author: Haris Zafeiropoulos 
package: microbetag
description: Aim of this script is to build all the unique sets of KO terms that can be used to build up each KEGG module (https://www.genome.jp/brite/ko00002)
output: A 2-levels .json file, in the first one, the various steps will be denoted and in the second the multiple alternative combinations of terms 
        will be shown. All the terms of a combination are necessary for the module to be complete
notes: The pathway module is defined by the logical expression of K numbers, and the signature module 
        is defined by the logical expression of K numbers and M numbers.
        A SPACE ( ) or a PLUS (+) sign, representing a connection in the pathway or the molecular complex, is treated as an AND operator 
        and a COMMA (,), used for alternatives, is treated as an OR operator. 
        A MINUS (-) sign designates an optional item in the complex. 
        This script was inspired by 2 functiosn from the following script of microbeAnnotator:
        https://github.com/cruizperez/MicrobeAnnotator/tree/master/microbeannotator/data/01.KEGG_DB/00.KEGG_Data_Scrapper.py
"""
import itertools
import re, sys

structurals = [ "M00144","M00149","M00151","M00152","M00154","M00155","M00153", "M00156","M00158", "M00160" ]

def flatten(lis):
    """
    Takes a nested list and returns its contents in a sequential one
    e.g. [[a,b,c,][d,e,]] --> [a,b,c,d,e]
    """
    import collections.abc
    collections.Iterable = collections.abc.Iterable
    for item in lis:
        if isinstance(item, collections.Iterable) and not isinstance(item, str):
            for x in flatten(item):
                yield x
        else:        
            yield item

def parse_commas_on_pre_and_post_character(string):
    """
    Takes a string and returns independent scenarions separated by commas (,)
    e.g. K02304,(K24866+K03794)
    ['K02304', '(K24866+K03794)']
    """
    new_true_alt = ""
    open_pars = 0
    for cindex, char in enumerate(string):        
        if char ==",":
            if string[ cindex + 1 ] == "(":
                if open_pars == 0:
                    new_true_alt += " "
                else:
                    new_true_alt += char
            elif string[ cindex - 1] == ")" and open_pars < 2: 
                new_true_alt += " "
            elif open_pars == 0:
                new_true_alt += " "
            else:
                new_true_alt += char       
        else:
            new_true_alt += char
            if char == "(":
                open_pars += 1
            elif char == ")":
                open_pars -= 1
    parts = new_true_alt.split()
    return parts

def check_if_all_in_one_par(string):
    """
    Function to tell you whether a string is included in a single parenthesis
    e.g.:  ((K00705,K22451)_(K02438,K01200))
    or not
    e.g.: K00975_(K00703,K13679,K20812)
    """
    indices_object = re.finditer(pattern="\(", string=string)
    starts = [index.start() for index in indices_object]
    indices_object = re.finditer(pattern="\)", string=string)
    ends = [index.start() for index in indices_object]
    pars = sorted(starts + ends)
    if len(ends) == 1:
        if string[starts[0]] == string[0] and string[ends[0]] == string[-1]:
            return True
        else:
            return False
    else:
        for i in range(len(pars)-1):
            if pars[i] in ends:
                for j in reversed(pars[:i]):
                        if j in starts:
                            pars[i] = ""
                            starts.remove(j) 
                            break
        if 0 in starts:
            return True
        else:
            return False

def get_independent_step_alternatives(step_as_a_list):
    """    
    It takes a complete step and returns its unique indipendent pats recursively
    e.g.:
    in the first round for
    ((K13939,(K13940,K01633 K00950) K00796),(K01633 K13941))
    we get the (K01633 K13941)) as an independent way
    while in the second one, we get the K13939     
    """
    new_list = []
    inner = False
    for index, step in enumerate(step_as_a_list):
        if isinstance(step,list):
            inner = True
            for gindex, inner_step in enumerate(step):
                check = check_if_all_in_one_par(inner_step)
                if check:
                    inner_step = inner_step[1:-1]
        else:
            check = check_if_all_in_one_par(step)
            if check:
                step = step[1:-1]
        if inner:
            get_independent_parts = parse_commas_on_pre_and_post_character(inner_step)
        else:
            get_independent_parts = parse_commas_on_pre_and_post_character(step)

        for i in get_independent_parts:
            new_list.append([i])

    if new_list == step_as_a_list:
        return new_list
    else:
        return get_independent_step_alternatives(new_list)

def split_to_independent_chunks(string):
    """
    Takes a string and returns indices where you can split it to parts that can be combined
    independently to get the part of the corresponding KEGG module definition 
    e.g. "K00941_(K00788,K21220)"
    [0, 7, 22]
    or 
    "((K03831,K03638)_K03750)"
    [0, 24]
    """
    indices_object = re.finditer(pattern="\(", string=string)
    starts = [index.start() for index in indices_object]
    if len(starts) == 0:
        return []
    indices_object = re.finditer(pattern="\)", string=string)
    ends = [index.start() for index in indices_object]
    pars = sorted(starts + ends)
    ops = 0 
    splits = [0]
    if "(" != string[0]:
        splits.append(starts[0])
    for i in pars: 
        if i in starts:
            ops += 1 
        else: 
            ops -= 1
        if ops == 0:
            splits.append(i+1)
    return splits

def parse(my_string):
    """
    Parses a module's definitions to each main steps
    e.g. 
    md definition: (K02303,K13542) (K03394,K13540) K02229 (K05934,K13540,K13541) K05936 K02228 K05895 K00595 K06042 K02224 K02230+K09882+K09883
    ['(K02303,K13542)', '(K03394,K13540)', 'K02229', '(K05934,K13540,K13541)', 'K05936', 'K02228', 'K05895', 'K00595', 'K06042', 'K02224', 'K02230+K09882+K09883']
    """
    module = []
    parenthesis_count = 0
    for character in my_string:
        if character == "(":
            parenthesis_count += 1
            module.append(character)
        elif character == " ":
            if parenthesis_count == 0:
                module.append(character)
            else:
                module.append("_")
        elif character == ")":
            parenthesis_count -= 1
            module.append(character)
        else:
            module.append(character)
    steps = ''.join(module).split()
    return steps

def parse_regular_module_dictionary(module_components_raw, structural_list):
    """
    Breaks down a module to its steps using the parse() function
    """
    # Parse raw module information
    module_steps_parsed = {}
    for key, values in module_components_raw.items():
        values = values.replace(" --", "")
        values = values.replace("-- ", "")
        
        # or key in bifurcating_list 
        if key in structural_list:
            continue
        else:
            # Run the parse() function 
            steps = parse(values)
            # and return the steps as values in the module_steps_parsed dictionary
            module_steps_parsed[key] = steps

    # Add submodules in cases that a module depends on other modules
    temporal_dictionary = module_steps_parsed.copy()
    for key, values in temporal_dictionary.items():
        for value in values:
            if re.search(r'M[0-9]{5}', value) is not None:
                module_steps_parsed[key].remove(value)
                module_steps_parsed[key] += module_steps_parsed[value]
                break

    return module_steps_parsed

def create_final_regular_dictionary(module_steps_parsed):
    """
    This function returns all the possible combinations of KOs to have a complete KEGG module
    """
    final_regular_dict = {}

    # Parse module steps and export them into a text file
    for module, steps in module_steps_parsed.items():

        final_regular_dict[module] = {}
        step_number = 0 

        # Deal with one step at a time
        for step in steps:

            temp_string = step
            step_number += 1
            
            # Check for "-" terms
            if "-(" in temp_string:
                temp_string = re.sub("-\(.*?\)", "", temp_string, count=0, flags=0)
            if "-" in temp_string:
                temp_string = re.sub(r'-K[0-9]{5}', '', temp_string)
            if len(temp_string) == 0:
                continue

            # Get major independent alternatives to have the step             
            indep_alts = get_independent_step_alternatives([temp_string])   

            # [REMEMBER!] An alternative is completely independent from the others
            tmp_alts = indep_alts.copy()

            # Parse each of the independent alternatives found to get the various combinations of KO terms in each 
            for index, alt in enumerate(indep_alts):

                if "(" not in alt[0] :
                    alt = re.split(r"\+|\_", alt[0]) 
                    tmp_alts[index] = [alt]

                else:

                    # In the tmp_alt we keep the semi-steps that will have to be combined to build the alternative (parts)
                    tmp_alt = []
                    split_indices = split_to_independent_chunks(alt[0])
                    parts = [alt[0][i:j] for i,j in zip(split_indices, split_indices[1:]+[None])]
                    parts = [x for x in parts if x]

                    # Make sure that jumps in an alternative are taken distinct steps in case they're out of an inner_part (see M00083)
                    new_parts = []
                    for ppindex, part in enumerate(parts):
                        ops = 0 ; new_part = ""
                        for cchar in part: 
                            if cchar == "(":
                                ops += 1 ; new_part += cchar
                            elif cchar == ")":
                                ops -= 1 ; new_part += cchar
                            elif cchar =="_":
                                if ops == 0:
                                    new_part += " "
                                else:
                                    new_part += cchar
                            else:
                                new_part += cchar
                        new_part = new_part.split() ; new_parts += new_part
                    parts = new_parts

                    # [IMPORTANT STEP!] Parse each part of the alternative to get the various combinations that can build the alterinative
                    for k in range(len(parts)):
                        inner_indices = split_to_independent_chunks(parts[k])
                        inner_parts = [parts[k][i:j] for i,j in zip(inner_indices, inner_indices[1:]+[None])]
                        inner_parts = [x for x in inner_parts if x]

                        # Run again the independency step for each inner part 
                        if len(inner_parts) > 0: 


                            inner_parts = get_independent_step_alternatives(inner_parts)
                            inner_parts = [j for j in inner_parts if j!=["_"]]

                            # Each entry of this list is an alternative for a part of the step
                            ready_to_go = []
                            for inner_part_index in range(len(inner_parts)):

                                coord = split_to_independent_chunks(inner_parts[inner_part_index][0])

                                if len(coord) == 0:
                                    ready_to_go.append(inner_parts[inner_part_index][0].split("+"))

                                # [ ATTENTION! ] Up to now, 2023.05, this is only the case for M00022
                                # Thus, we only deal with this for now so please always check for this warning message in case a new module goes throug this case
                                else:

                                    last_parts = [inner_parts[inner_part_index][0][i:j] for i,j in zip(coord, coord[1:]+[None])]
                                    last_parts = [x for x in last_parts if x] 
                                    last_parts = [ re.split(r"\+|,|_", x) for x in last_parts ] 
                                    for x,y in enumerate(last_parts):
                                        for z in range(len(y)):
                                            last_parts[x][z] = last_parts[x][z].replace("(","").replace(")","")
                                    for x,y in enumerate(last_parts):
                                            last_parts[x] = [k for k in last_parts[x] if k]

                                    for comb in list(itertools.product(*last_parts)):
                                        ready_to_go.append(list(comb))


                            tmp_alt.append(ready_to_go)

                        else:
                            # All KOs included in this part needs to be used so a nested list with a single entry will be kept, e.g. [['K01041', 'K00252']] 
                            inner_parts = parts[k].split("_") 
                            inner_parts = [ inner_parts[j] for j in range(len(inner_parts)) if inner_parts[j]]
                            inner_parts = [ inner_parts[u].split("+") for u in range(len(inner_parts)) ]
                            inner_parts = [list(flatten(inner_parts))] ; inner_parts = [[x for x in inner_parts[0] if x]]
                            tmp_alt.append(inner_parts)

                        # [ATTENTION!] WE NEED SOMETHING FROM ALL LISTS INCLUDED IN THIS NESTED LIST
                        tmp_alts[index] = tmp_alt

            # Get all the combinations from each of the independent alternatives 
            all_alternatives = []
            for calt in tmp_alts:
                if len(calt)>1:
                    combos = list(itertools.product(*calt))
                    combos = [list(flatten(combos[i])) for i in range(len(combos))]
                    all_alternatives += combos

                else:
                    all_alternatives += calt

            # Assign the list with all the combinations for a step to the module:step:combinations dictionary
            final_regular_dict[module][step_number] = all_alternatives

    return final_regular_dict

# -----   Run modules parsing -----------

modules = open("module_definitions.tsv", "r")
module_components_raw = {}
# Build dictionary with module ids as keys and the initial definition as value
for line in modules:
   # Remove the "md:" prefix from the id and the new line from the definition
   md, definition = line.split("\t")[0][3:], line.split("\t")[1][:-1]
   # Replace ";" character with a space; this denotes a next layer of the module
   definition = definition.replace(";", " ")
   module_components_raw[md] = definition

# Get a dictionary with the major steps of each module, 
# e.g.: for module md:M00022 with the definition: 
# (K01626,K03856,K13853);(((K01735,K13829);((K03785,K03786);K00014,K13832)),K13830);((K00891,K13829);(K00800,K24018),K13830);K01736
# we get the following 4 major steps
# ['(K01626,K03856,K13853)', '(((K01735,K13829)_((K03785,K03786)_K00014,K13832)),K13830)', '((K00891,K13829)_(K00800,K24018),K13830)', 'K01736']
module_steps_parsed = parse_regular_module_dictionary(module_components_raw, structurals)

# Get alla the combos to get each and every step of a module
P = create_final_regular_dictionary(module_steps_parsed)

# Build the final dictionary to be used for the pathway complementarity step ( input for the pathway_complementarity.py )
q = {}
for md, steps in P.items():
    module = "md:" + md
    for step_numb, altertnatives in steps.items(): 
        new_step = {}
        for alt_index, alternative in enumerate(altertnatives):

            # Remove alts that include empty terms ("") as they're false combinations 
            if (any(len(ele) == 0 for ele in alternative)):
                altertnatives.remove(altertnatives[alt_index])

            # Split terms with jumps "_" still included  
            if (any("_" in ele for ele in alternative)):
                new_alt = [ ele.split("_") for ele in alternative ]
                altertnatives[alt_index] = list(flatten(new_alt))
    q[module] = {}
    q[module]["id"] = md
    q[module]["definition"] = module_components_raw[md]
    q[module]["#-of-steps"] = len(steps)    
    q[module]["steps"] = steps
    q[module]["unique-KOs"] = list(set(list(flatten(q[module]["steps"].values()))))

import json
with open('module_definition_map.json', 'w') as fp:
    json.dump(q, fp, indent=4)
