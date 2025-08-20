# %% load libraries
import os
import json
import gzip
import pickle
import numpy as np
import pandas as pd
import patchworklib as pw
import scipy.stats as stats

from copy import deepcopy
from plotnine import ggplot, aes, element_text, labs, theme, geom_bar, geom_histogram

# %% load files
# with gzip.open("seeds_binary_per_patric.pckl.gz", "rb") as f:
with gzip.open("seeds_binary.pckl.gz", "rb") as f:
    all_seeds       = pickle.load(f)
    all_seeds.index = [x.split(".PATRIC")[0] for x in all_seeds.index]

# with gzip.open("non_seeds_binary_per_patric.pckl.gz", "rb") as f:
with gzip.open("non_seeds_binary.pckl.gz", "rb") as f:
    all_nonseeds       = pickle.load(f)
    all_nonseeds.index = [x.split(".PATRIC")[0] for x in all_nonseeds.index]


# %% Get KEGG Module related seeds and non-seeds only
modules_compounds         = pd.read_csv("seedId_keggId_module.tsv", sep="\t", header=0)
modules_compounds.columns = ["modelseed", "kegg", "module"]


def kegg_module_related_intersect(intersect, modelseed_compounds_of_interest):
    """Check if KEGG MODULE related"""
    intersect     = list(intersect)
    tmp_intersect = intersect.copy()
    for compl in tmp_intersect:
        if compl not in modelseed_compounds_of_interest:
            intersect.remove(compl)
    return intersect


modelseed_compounds_of_interest = set(modules_compounds["modelseed"])

relevant_columns_nonseeds = kegg_module_related_intersect(
    all_nonseeds.columns, modelseed_compounds_of_interest
)
self_prod_mets = all_nonseeds[relevant_columns_nonseeds]

relevant_columns_seeds = kegg_module_related_intersect(
    all_seeds.columns, modelseed_compounds_of_interest
)
seeds = all_seeds[relevant_columns_seeds]


"""
733 unique metabolites as seeds
1598 unique metabolites as non-seeds
33755 genomes in total
"""

# %% Arrays
seed_intervals     = seeds.sum()
nonseeds_intervals = self_prod_mets.sum()

# Create custom bins with a separate bin for zero
# Separate the zero values from the rest
zero_values     = seed_intervals[seed_intervals == 0]
non_zero_values = seed_intervals[seed_intervals != 0]


# Get top and lowest seeds
q         = pd.DataFrame(seeds.sum())
q.columns = ["counts"]
print(q["counts"].sort_values())


# %% Distribution of the number of seeds per genome

seeds_num_per_genome = seeds.sum(axis=1)
df_seeds             = pd.DataFrame(seeds_num_per_genome)
df_seeds.columns     = ["number_of_seeds"]

counts, bins  = np.histogram(df_seeds, bins=25)
df_seeds_bins = pd.DataFrame({"bins": bins[:-1], "counts": counts})

p1 = (
    ggplot(df_seeds_bins, aes(x="bins", y="counts"))
    + geom_bar(stat="identity", fill="#28579E", alpha=0.7)
    + labs(
        title = "A.        Seeds per genome",  # Number of
        x     = "number of seeds",
        y     = "number of genomes",
    )
    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),  # x=0.15
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22),                # Adjust axis title font size
    )
)

seeds_per_genomes_plt = deepcopy(p1)

# %% Distribution of the number of non-seeds per genome

nonseeds_num_per_genome = self_prod_mets.sum(axis=1)

df_nonseeds  = pd.DataFrame(nonseeds_num_per_genome, columns=["number_of_nonseeds"])
counts, bins = np.histogram(df_nonseeds, bins=25)

df_nonseeds_bins = pd.DataFrame({"bins": bins[:-1], "counts": counts})

p2 = (
    ggplot(df_nonseeds_bins, aes(x="bins", y="counts"))
    + geom_bar(stat="identity", fill="#28579E", alpha=0.7)
    + labs(
        title = "B.        Non-seeds per genome",  # Number of
        x     = "number of non-seeds",
        y     = "number of genomes",
    )
    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),  # x=0.15
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22),                # Adjust axis title font size
    )
)

nonseeds_per_genomes_plt = deepcopy(p2)
"""
124 min - 442 max
"""

# -----------------------
# %% Seeds ratios
# -----------------------

df_seeds_ratios = pd.DataFrame(seed_intervals / seeds.shape[0], columns=["ratio"])
counts, bins    = np.histogram(df_seeds_ratios, bins=30)

df_seeds_ratios_bins = pd.DataFrame({"bins": bins[:-1], "counts": counts})

# Create the histogram plot
p3 = (
    ggplot(df_seeds_ratios_bins, aes(x="bins", y="counts"))
    + geom_bar(stat="identity", fill="#28579E", alpha=0.7)
    + labs(
        title = "C.      Seeds coverage",  # Distribution of
        x     = "genomes' fraction",  # where \nthe metabolite serves as a seed
        y     = "number of metabolites",
    )
    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),  # x=0.13
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22),                # Adjust axis title font size
        # axis_title_x=element_text(margin={'t': 10})  # add 10pt margin on top
    )
)

seeds_coverage_plt = deepcopy(p3)


# -----------------------
# %% Non-seeds ratios
# -----------------------

df_non_seeds_ratio = pd.DataFrame(
    nonseeds_intervals / self_prod_mets.shape[0], columns=["ratio"]
)
counts, bins = np.histogram(df_non_seeds_ratio, bins=30)

df_non_seeds_ratio_bins = pd.DataFrame({"bins": bins[:-1], "counts": counts})

# Create the histogram plot
p4 = (
    ggplot(df_non_seeds_ratio_bins, aes(x="bins", y="counts"))
    + geom_bar(stat="identity", fill="#28579E", alpha=0.7)
    + labs(
        title = "D.      Non-seeds coverage",  # Distribution of
        x     = "genomes' fraction",  # where the metabolite serves as a non-seed
        y     = "number of metabolites",
    )
    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),  # x=0.09
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22),                # Adjust axis title font size
    )
)

nonseeds_coverage_plt = deepcopy(p4)


# %% Number of genomes (donors) potentially providing a seed

if not os.path.exists("counts_of_a_genomes_potential_nonseed_hits.json"):

    nonseed_hits_per_genome = {}
    for index, genome in enumerate(self_prod_mets.index):

        # potential donor
        # self_prod_mets.iloc[1,:]   gets a row
        # (self_prod_mets.iloc[1,:][self_prod_mets.iloc[1,:]==1]  gets colums where row is 1
        # gets its column names
        compounds_of_interest = list(
            self_prod_mets.iloc[index, :][self_prod_mets.iloc[index, :] == 1].index
        )

        compounds_of_interest_presnt = [
            x for x in compounds_of_interest if x in seeds.columns
        ]

        # times a metabolite of donor's nonseeds appears as a seed accross the 33K genomes as a seed
        count_ones_specific = seeds[compounds_of_interest_presnt]

        c = count_ones_specific.sum().sum()

        nonseed_hits_per_genome[genome] = c

    data = {
        k: int(v) if isinstance(v, np.integer) else v
        for k, v in nonseed_hits_per_genome.items()
    }

    with open("counts_of_a_genomes_potential_nonseed_hits.json", "w") as f:
        json.dump(data, f)

else:
    with open("counts_of_a_genomes_potential_nonseed_hits.json", "r") as f:
        data = json.load(f)


# %%

df_perce   = pd.DataFrame.from_dict([data])
df_perce_t = df_perce.T

total_potential_hits = seeds.shape[0] * seeds.shape[1]
# or
total_potential_hits = seeds.sum().sum()

df_perc         = df_perce_t / total_potential_hits * 100
df_perc.columns = ["coverage"]

counts, bins = np.histogram(df_perc, bins=30)

df = pd.DataFrame({"bins": bins[:-1], "counts": counts})

q = (
    ggplot(df, aes(x="bins", y="counts"))
    + geom_bar(stat="identity", fill="#28579E", alpha=0.7)
    + labs(
        title = "E.        Non-seeds overlaps across genomes' seeds",  # Per genome
        x     = "percentage of potential total nonseed overlap",
        y     = "number of genomes",
    )
    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),  # x=0.1
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22),                # Adjust axis title font size
    )
)

nonseed_across_seeds_percentage_plt = deepcopy(q)

# %% Build merged image

ax1 = pw.load_ggplot(
    p1
)  # + labs(title='A')  this would overwrite the initial plot title
ax2 = pw.load_ggplot(p2)
ax3 = pw.load_ggplot(p3)
ax4 = pw.load_ggplot(p4)
ax5 = pw.load_ggplot(q)


# %%
# ax123 = (ax1/ax2|ax3/ax4)/ax5
ax123 = (ax1 / ax2 / ax3) | ax4 / ax5
ax123.savefig("seeds_stats.png")


# %%   Figure out what distirbution fits

print(
    """
    The distribution with the lowest AIC/BIC and highest KS test p-value is the best fit.
    If multiple distributions are close, consider biological relevance.
    """
)


# Distributions to fit
distributions = {
    "Normal": stats.norm,
    "Gamma": stats.gamma,
    "Beta": stats.beta,
    "Log-Normal": stats.lognorm,
    "Logistic": stats.logistic,
    "exponential": stats.expon,
}

# Data arrays
arrays = {
    "seeds": df_seeds["number_of_seeds"],
    "seeds ratios": df_seeds_ratios["ratio"],
    "non seeds": df_nonseeds["number_of_nonseeds"],
    "coverage": df_perc["coverage"],
}


def aic_bic(data, dist, params):
    log_likelihood = np.sum(np.log(dist.pdf(data, *params)))
    k, n = len(params), len(data)
    return 2 * k - 2 * log_likelihood, k * np.log(n) - 2 * log_likelihood


def get_fittest_distribution(variable, data):
    print(f"\n\n{variable}")

    fitted_params, ks_results = {}, {}
    max_ks_d, max_ks = "", 0
    for name, dist in distributions.items():
        params = dist.fit(data)
        fitted_params[name] = params
        D, p_value = stats.kstest(data, dist.cdf, args=params)
        ks_results[name] = p_value
        if p_value > max_ks:
            max_ks, max_ks_d = p_value, name

    print(ks_results)
    print("KS Test Results:", ks_results, "\nMax KS:", max_ks_d, max_ks)

    lowest_aic = lowest_bic = 10e9
    lowest_aic_name = lowest_bic_name = ""
    for name, dist in distributions.items():
        params = fitted_params[name]
        aic, bic = aic_bic(data, dist, params)
        if aic < lowest_aic:
            lowest_aic, lowest_aic_name = aic, name
        if bic < lowest_bic:
            lowest_bic, lowest_bic_name = bic, name
        print(name, aic, bic)

    print(
        f"Lower AIC: {lowest_aic_name} {lowest_aic}\nLower BIC: {lowest_bic_name} {lowest_bic}"
    )


for k, v in arrays.items():
    get_fittest_distribution(k, v)
