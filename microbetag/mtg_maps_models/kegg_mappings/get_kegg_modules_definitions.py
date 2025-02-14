#!/usr/bin/env python3

"""
This script takes as input the kegg_terms_per_module.tsv file;
that is actually the results of the command:
wget https://rest.kegg.jp/link/ko/md

It makes a list of all the KEGG modules and then retrieves from the KEGG portal 
their definitions, to save them in the module_definitions.tsv file like this:

md:M00006       (K13937,((K00036,K19243);(K01057,K07404)));K00033

The "definition" of a module is a logcail expression of K numbers. 
Comma (,) separated K numbers indicate alternatives. 
Plus signs (+) are used to represent a complex and a minus sign (-) denotes a non-essential component in the complex.
"""

import time, sys
import requests

def write_definition(line, md, iter):
   """
   Write the module_definitions.tsv file 
   """

   if iter > 1: 
      definition = line.strip()
      with open("module_definitions.tsv", "a") as f:
            f.write(md + "_" + str(iter) + "\t" + definition + "\n")

   else:
      definition = line.split("  ")[1:][0][:-1]
      definition = ';'.join(definition.split(" "))
      with open("module_definitions.tsv", "a") as f:
            f.write(md + "\t" + definition + "\n")

   return True

def get_kegg_modules_definitions():

   all_modules_ids     = []
   for line in open("kegg_terms_per_module.tsv", "r"): 
      md_id = line.split("\t")[0]
      if md_id not in all_modules_ids: 
         all_modules_ids.append(md_id)

   counter = 0
   for md in all_modules_ids:

      counter += 1
      
      url       = "http://rest.kegg.jp/get/" + md
      response   = requests.get(url)

      with open("response.txt", "wb") as f:
         f.write(response.content)

      switch      = False
      num_of_defs = 0 

      # print(md, "~~", str(counter), "out of ", str(len(all_modules_ids)))

      for line in open("response.txt", "r"):

         # if "DEFINITION" in line:
         #    switch      = True
         #    num_of_defs = 1
         #    write_definition(line, md, num_of_defs)
         #    continue

         # if "ORTHOLOGY" in line: 
         #    switch = False
         
         # if switch: 
         #    num_of_defs += 1
         #    write_definition(line, md, num_of_defs)

         if "PATHWAY" in line:
            mmap = line.split()[1]
            print(md, "\t", mmap)

      time.sleep(0.5)


if __name__ == "__main__":
   get_kegg_modules_definitions()

