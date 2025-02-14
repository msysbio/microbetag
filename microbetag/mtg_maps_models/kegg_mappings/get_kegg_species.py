#!/usr/bin/env python3

import os, time 
import requests
import json

kegg_species = open("NCBI_IDS2KEGG_IDS", "r")
cwd          = os.getcwd()

ncbi_prokaryotes_file = open("ncbi_prokaryotes.tsv", "r")
ncbi_prokaryotes = set()
for ncbi_id in ncbi_prokaryotes_file: 
   ncbi_prokaryotes.add(ncbi_id[:-1])

counter = 1 
for line in kegg_species:

   if counter % 100 == 0: 
      print("line in NCBI_IDS2KEGG_IDS file: " + str(counter))
   counter += 1

   species_kos_per_module = {}

   ncbi_id = line.split("\t")[0]
   kegg_id = line.split("\t")[1][:-1]


   mo_url  = "http://rest.kegg.jp/link/module/" + kegg_id
   kos_url = "http://rest.kegg.jp/link/ko/" + kegg_id

   dir_for_ncbi_id = cwd + "/kegg_genomes/" + ncbi_id

   if os.path.isdir(dir_for_ncbi_id) == False:
      os.mkdir(cwd + "/kegg_genomes/" + ncbi_id)

   else: 
      print("~ NCBI Taxonomy Id: ", ncbi_id, " has more than one KEGG genomes. \n")


   kos_file = cwd + "/kegg_genomes/" + ncbi_id + "/" + kegg_id + "_kos"
   if os.path.isfile(kos_file): 
      print("The KEGG genome with id: ", kegg_id, " and NCBI Taxonomy Id: ", ncbi_id, " has already been retrieved\n")
      continue

   r        = requests.get(kos_url, allow_redirects=True)


   open(kos_file, 'wb').write(r.content)

   q        = requests.get(mo_url, allow_redirects=True)
   mos_file = cwd + "/kegg_genomes/" + ncbi_id + "/" + kegg_id + "_mos"
   open(mos_file, 'wb').write(q.content)

   mos_download    = open(mos_file, "r")
   species_modules = {}

   for entry in mos_download:
      
      mo         = "md:" + (entry.split("\t")[1]).split("_")[1][:-1]
      species_ko = entry.split("\t")[0]
      
      if species_ko in species_modules:
         species_modules[species_ko][str(len(species_modules[species_ko]) + 1)] = mo

      else:
         species_modules[species_ko] = {}
         species_modules[species_ko]['1'] = mo


   kos_download = open(kos_file, "r")
   kos_related_to_mos_path = cwd + "/kegg_genomes/" + ncbi_id + "/" + kegg_id + "_kos_related_to_mos.tsv"
   kos_related_to_mos_json = cwd + "/kegg_genomes/" + ncbi_id + "/" + kegg_id + "_kos_related_to_mos.json"
   kos_related_to_mos_file = open(kos_related_to_mos_path, "w")


   for entry in kos_download: 

      species_ko = entry.split("\t")[0]

      if species_ko in species_modules.keys():
      
         for module in species_modules[species_ko]: 

            kegg_module = (species_modules[species_ko][module])
            kegg_ko     = entry.split("\t")[1]

            kos_related_to_mos_file.write(kegg_module + "\t" + kegg_ko)

            if kegg_module not in species_kos_per_module: 

               species_kos_per_module[kegg_module] = {}
               species_kos_per_module[kegg_module]['0'] = kegg_ko[:-1]

            else:

               species_kos_per_module[kegg_module][str(len(species_kos_per_module[kegg_module]))] = kegg_ko[:-1]



   out_file = open(kos_related_to_mos_json, "w")  
   json.dump(species_kos_per_module, out_file, indent = 6)
   out_file.close()

   time.sleep(0.5)


"""
Through the mo_url we get all the species-specific kegg terms that have been linked to a kegg module.
Therefore, the number of entries in this file 
and in the kos_related_to_mos_file that we build has to be the same!
"""
      


