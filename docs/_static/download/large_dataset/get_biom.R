# Author: Karoline Faust
# Date: Feb 2025

output.folder="HMPData"
metadata.file="HMPData/1928_20230202-081854.txt"
metadata=read.table(metadata.file,header = TRUE,sep="\t", row.names=1) # row names contain sample identifiers

otu.file="HMPData/study_1928_020725-012149/BIOM/69758/hmp_otu_table.txt"
otus=read.table(otu.file,header = TRUE,sep="\t", row.names = 1, check.names = FALSE) # row names contain taxon identifiers, column names contain sample identifiers, last column contains lineages

my.bodysite="Subgingival_plaque"

bodysite.indices=which(metadata$bodysite==my.bodysite)

# samples are not in the same order
same.order=identical(rownames(metadata), colnames(otus))

otu.columns=c()
for(bodysite.index in bodysite.indices){
  sample.id=rownames(metadata)[bodysite.index]
  found=which(colnames(otus)==sample.id)
  if(length(found)==0){
    print(paste("sample",sample.id,"not found in OTU table"))
  }else{
    # only proceed for samples with non-zero total abundance
    if(sum(otus[,found])>0){
      otu.columns=c(otu.columns,found)
    }else{
      print(paste("Sample",bodysite.index,"has zero abundance across taxa."))
    }
  }
}
# make sure last column with lineages is included
bodysite.table=otus[,c(otu.columns,ncol(otus))]

# remove taxa with zero sum in bodysite table (lineage column skipped)
nonzero.taxa=which(rowSums(bodysite.table[,1:(ncol(bodysite.table)-1)])>0)
bodysite.table=bodysite.table[nonzero.taxa,]

# subgingival plaque: 2057 non-zero taxa, 373 samples (omitting lineage column)
write.csv(bodysite.table, quote = FALSE, file = file.path(output.folder,paste(my.bodysite,".txt",sep="")))

