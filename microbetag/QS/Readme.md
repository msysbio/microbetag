# QS Function Annotation

## Step 0: Build Quorum Sensing Database

Script: build_QSdb.sh

Required file(s): **m02024_genes.txt** in the same directory.

Purpose: This script downloads the KEGG Orthology HMM database, extracts HMMs related to KEGG pathway m02024 (quorum sensing), builds an HMMsearch database, and keeps only the final outputs in the current directory.

Command: `bash /path/to/build_QSdb.sh`

Output(s): 
`m02024_genes.hmm`
`m02024_genes.hmm.h3f`
`m02024_genes.hmm.h3i`
`m02024_genes.hmm.h3m`
`m02024_genes.hmm.h3p`

## Step 1: Annotate QS functions against QSdb in users' genomes

Script: QS_annotation.sh

Required file(s): 5 related HMM database files generated in Step 0, Users' genomes in protein sequences (.faa).

Purpose: Command for using QS database to annotate quorum sensing functions in users' genome.

Command: `bash /path/to/QS_annotation.sh`

Output(s): HMM result tabular files.

## Step 2: Annotate genomes with QS sending and receiving pathways based on HMMsearch results

Script: HMMres_to_QS.py

Required file(s): **map02024_parse_dict.json** and HMM result tabular files generated in Step 1.

Command and help:

```
python annotate_qs_pathways.py -h
usage: annotate_qs_pathways.py [-h] [--evalue EVALUE] [--output OUTPUT]
                               input_dir qs_json

Annotate genomes with QS sending and receiving pathways based on HMMsearch
results.

positional arguments:
  input_dir        Directory containing HMMsearch .tbl result files
  qs_json          Path to QS pathway definition JSON file
                   (map02024_parse_dict.json)

optional arguments:
  -h, --help       show this help message and exit
  --evalue EVALUE  E-value threshold for KO filtering (default: 1e-5)
  --output OUTPUT  Output CSV file path (default: qs_summary.csv)
```

Result preview:

```
Genome,Sending Pathway,Receiving Pathway
GCF_900111605.1,3/6/7/8/9/10/11/12/13/14/15/17/18/19/20/22/25/27/28/29/30/34,2/3/4/5/6/7/8/9/10/11/12/13/14/15/17/18/20/21/22/23/24/25/26/27/28/29/30/31/32/34/36/37/38/39/40/41
GCA_001883705.1,3/4/5/7/8/9/10/11/12/13/14/15/17/18/19/20/21/22/23/24/25/26/27/28/29/30/31/34,1/2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27/28/29/30/31/32/34/36/37/39/40/41
GCF_014643695.1,1/9/10/11/12/13/14/15/16/27/28/34,4/5/7/8/9/10/11/12/13/14/15/17/18/19/20/21/22/23/24/25/26/27/28/29/30/31/34/37/39/40/41
```

## Step 3: Generate sender–receiver–pathway table from QS summary file

Script: Sender_Receiver_tab.py

Required file(s): **qs_summary.csv** generated in Step 2.

Command and help:

```
python decide_pair.py -h
usage: decide_pair.py [-h] -i INPUT -o OUTPUT [--force-parallel]
                      [--no-parallel] [--threshold THRESHOLD]

Generate sender–receiver–pathway table from QS summary file.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input CSV: qs_sending_receiving_summary.csv
  -o OUTPUT, --output OUTPUT
                        Output CSV: sender_receiver_pathway_table.csv
  --force-parallel      Force use of parallel processing
  --no-parallel         Disable parallel processing
  --threshold THRESHOLD
                        Genome count threshold to enable parallel mode
```

Result preview:

```
Sender,Receiver,Pathways
GCF_900111605.1,GCF_900111605.1,3/6/7/8/9/10/11/12/13/14/15/17/18/20/22/25/27/28/29/30/34
GCF_900111605.1,GCA_001883705.1,3/6/7/8/9/10/11/12/13/14/15/17/18/19/20/22/25/27/28/29/30/34
GCF_900111605.1,GCF_014643695.1,7/8/9/10/11/12/13/14/15/17/18/19/20/22/25/27/28/29/30/34
GCF_900111605.1,GCA_017542125.1,3/7/8/9/10/11/12/13/14/15/17/18/20/22/25/27/28/29/30/34
GCF_900111605.1,GCF_018881715.1,6/7/8/9/10/11/12/13/15/17/18/20/22/25/27/28/29/30/34
GCF_900111605.1,GCA_006226495.1,3/6/7/8/9/10/11/12/13/14/15/17/18/19/20/22/25/27/28/29/30/34
```