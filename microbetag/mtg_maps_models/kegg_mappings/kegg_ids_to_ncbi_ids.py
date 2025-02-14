#!/usr/bin/env python

import requests, time
import re, json


kegg_file = open("br08610.keg", "r")
lines = kegg_file.readlines()

r = re.compile(r'ABacteria')
for i in range(len(lines)):

   if r.search(lines[i]):
      starting_point = i
      break

kegg_file = open("br08610.keg", "r")
counter = 0
ncbi_id_to_kegg_ids = {}
check = False
line  = ''


for line in kegg_file:
   if counter < starting_point:
      counter += 1

   else:

      if "TAX:" in line:
         level   = line[0]
         ncbi_id = line.split("TAX:")[1][:-2]
         check   = True
         ncbi_id_to_kegg_ids[ncbi_id] = []
         continue

      try:

         if check and level <= line[0]:

            kegg_id = line.split()[1]
            if kegg_id != ncbi_id:
               ncbi_id_to_kegg_ids[ncbi_id].append(kegg_id)
            level   = line[0]

         else:
            check = False

      except:
         continue

out_file = open("out_file.json", "w")
json.dump(ncbi_id_to_kegg_ids, out_file, indent = 6)


output_file = open("NCBI_IDS2KEGG_IDS", "a")

for ncbi_id, kegg_ids, in ncbi_id_to_kegg_ids.items():

   if len(kegg_ids) == 1:

      print(ncbi_id, kegg_ids)

      output_file.write(ncbi_id + "\t" + kegg_ids[0] + "\n")
      continue

   else:

      for kegg_id in kegg_ids:

         r = requests.get("https://www.genome.jp/kegg-bin/show_organism?org=" + kegg_id)
         try:
            SEMI = r.text.split("TAX:")[1]
            semi = SEMI.split(">")[1]
            tax_id = semi.split("<")[0]

            output_file.write(tax_id + "\t" + kegg_id +  "\n")
            time.sleep(0.35)
         except:
            print(kegg_id)

