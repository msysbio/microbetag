"""
microbetag is working as a set of workflows that consists of tools
This script runs FlashWeave to get a co-occurrence network based on 
an OTU or ASV table (mandatory) and a metadata table (optional)

Essential parameters:
     n_obs_min - don't compute associations between variables having less reliable samples 
                 (i.e. non-zero if heterogeneous=true) than this number.
                  -1: automatically choose a threshold.

     track_rejections - store for each discarded edge, which variable set lead to its exclusion (can be memory intense for large networks)

     transposed - if true, rows of data are variables and columns are samples

"""


"""
DEPRECATED
"""

# [TODO] Make flashweave running with 2 workers ( -p 2 ); change ARGS accordingly

# import flashweave
using FlashWeave # this has some pre-compilation delay the first time it's called, subsequent imports are fast

FLASHWEAVE_OUTPUT_DIR = ARGS[1]
data_path = ARGS[2]
sensitive = parse(Bool, ARGS[3])
heterogeneous = parse(Bool, ARGS[4])
metadata = parse(Bool, ARGS[5])


println("HELLO FRIEND FROM FLASHWEAVE SCRIPT", flush=true)

if metadata

   meta_data_path     = ARGS[6]
   netw_results = learn_network(
                                 data_path,
                                 meta_data_path,
                                 sensitive = sensitive,
                                 heterogeneous = heterogeneous,
                                 transposed = true,
                                 n_obs_min = 3
                              )

else
   
   netw_results = learn_network(
                                 data_path,
                                 n_obs_min = 5,
                                 sensitive = sensitive,
                                 heterogeneous = heterogeneous,
                                 max_k = 1,
                                 transposed = true,
                              )

end

G = graph(netw_results) # weighted graph object representing interactions + weights, 
                        # to be used with the JuliaGraphs ecosystem (https://github.com/JuliaGraphs)

save_network(FLASHWEAVE_OUTPUT_DIR * "/network_output.edgelist", netw_results)
save_network(FLASHWEAVE_OUTPUT_DIR * "/network_detailed_output.edgelist", netw_results, detailed = true)

