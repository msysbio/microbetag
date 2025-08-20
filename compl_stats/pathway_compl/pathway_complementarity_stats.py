# %%
import json
import pandas as pd
import pandas as pd
from plotnine import ggplot, aes, geom_histogram, geom_text, labs, scale_x_continuous, theme, element_text
import patchworklib as pw


def count_subsets(lst):
    n = len(lst)
    return (2 ** n) - 1


# %% Load the module definition map
with open("module_definition_map.json") as f:
    defs = json.load(f)  # 491 modules

all_combinations = 0
for module in defs.keys():
    data       = defs[module]["steps"]
    uniq_combo = 1
    for key in data:
        key_combinations = 0
        for sublist in data[key]:
            key_combinations += count_subsets(sublist)
        uniq_combo *= key_combinations
    all_combinations += uniq_combo


log_defs         = defs.copy()
counter          = 0
all_alternatives = 0

for module in defs.keys():

    print(str(counter), "out of", str(len(defs)))
    data = defs[module]["steps"]
    uniq_combo = 1

    for key in data:
        uniq_combo *= len(data[key])

    print(module, uniq_combo)
    log_defs[module]["#-of-alternatives"]  = uniq_combo
    all_alternatives                      += uniq_combo
    counter                               += 1

# %%
df = pd.read_csv("unique_complements.tsv.gz", sep="\t", compression="gzip", header=None)
for index, row in df.iterrows():
    row         = row.to_list()
    module      = "md:" + row[1]
    alternative = row[-1].split(";")
    if "observed-alternatives" not in log_defs[module]:
        log_defs[module]["observed-alternatives"] = [alternative]
    else:
        if alternative not in log_defs[module]["observed-alternatives"]:
            log_defs[module]["observed-alternatives"].append(alternative)

counter3       = 0
data_points    = []
mdls_no_compls = []
for module, data in log_defs.items():
    try:
        data_points.append(len(data["observed-alternatives"]) / data["#-of-alternatives"])
    except Exception:
        # print(module, data.keys())
        counter3 += 1
        mdls_no_compls.append(module)

# NOTE (Haris Zafeiropoulos, 2025-08-20):
# A total of 168 modules have no complemented alternatives (mdls_no_compls).
# So, we only have 323 modules for which we will get stats.


data_points_df = pd.DataFrame(data_points)  # 323 modules
data_points_df.columns = ["ratio"]
# with open("logged_modules.json","w") as f:
#    json.dump(log_defs, f)

# %% # Create alternatives coverage plot

g1 = (
    ggplot(data_points_df, aes(x="ratio"))
    + geom_histogram(binwidth=0.1, alpha=0.7, fill="#28579E")
    + geom_text(
        aes(
            label='..count..'
        ),
        stat     = 'bin',
        binwidth = 0.1,
        va       = 'bottom',
        size     = 16,
        color    = 'black'
    )
    + labs(
        title = "A.      Alternatives coverage",
        x     = "alternatives completed by any donor",  # Fraction of a module's
        y     = "number of modules")

    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22)   # Adjust axis title font size
    )
    # + scale_x_continuous(breaks=range(0, 1), minor_breaks=[])
)


# %%
# Second and third plots
modules         = log_defs.copy()  # added 09.02
new_data_points = []
for module in modules:
    if module not in mdls_no_compls:
        new_data_points.append(modules[module]["#-of-alternatives"])

new_data_points_df         = pd.DataFrame(new_data_points)
new_data_points_df.columns = ["alternatives"]

up_to_10               = new_data_points_df[new_data_points_df["alternatives"] < 11]
higher_than_11         = new_data_points_df[new_data_points_df["alternatives"] > 10]
higher_than_11_to_1000 = higher_than_11[higher_than_11["alternatives"] < 1001]
higher_than_1000       = new_data_points_df[new_data_points_df["alternatives"] > 1000]


# %%
# Create the bar plot
g2 = (
    ggplot(up_to_10, aes(x="alternatives"))
    + geom_histogram(binwidth=1, alpha=0.7, fill="#28579E")
    + geom_text(
        aes(
            label='..count..'
        ),
        stat     = 'bin',
        binwidth = 1,
        va       = 'bottom',
        size     = 16,
        color    = 'black'
    )
    + labs(
        title = "B.      Modules with < 10 alternatives",
        x     = "number of alternatives of a module",
        y     = "number of modules")

    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22)   # Adjust axis title font size
    )
    + scale_x_continuous(breaks=range(1, 11), minor_breaks=[])
)


# %%
min_value, max_value = 10, max(higher_than_11_to_1000["alternatives"])
step_size = 100
g3 = (
    ggplot(higher_than_11_to_1000, aes(x="alternatives"))
    + geom_histogram(binwidth=100, boundary=10, alpha=0.8, fill='#28579E')
    + geom_text(
        aes(
            label='..count..'
        ),
        stat     = 'bin',
        binwidth = 100,
        boundary = 10,
        va       = 'bottom',
        size     = 16,
        color    = 'black'
    )
    + labs(
        title = "C.    Modules with >= 10, <= 1000 alternatives",
        x     = "Number of alternatives of a module",
        y     = "Number of modules")
    + theme(
        plot_title = element_text(size=24, weight="bold", ha='left', x=0),
        axis_text  = element_text(size=22),                # Adjust axis tick labels font size
        axis_title = element_text(size=22)   # Adjust axis title font size
    )
    + scale_x_continuous(
        limits       = (min_value, 1001),
        breaks       = range(min_value, 1001, step_size),
        minor_breaks = []
    )
)
g3 = g3 + theme(figure_size=(14, 6))

# %%
ax1 = pw.load_ggplot(g1)  # + labs(title='A')  this would overwrite the initial plot title
ax2 = pw.load_ggplot(g2)
ax3 = pw.load_ggplot(g3)

# %%
ax123 = (ax1 | ax2) / ax3
ax123.savefig("ax123.png")


# %%  depr

# counter3 = 0
# data_points = []
# mdls_no_compls = []
# for module, data in log_defs.items():
#     try:
#         data_points.append(len(data["observed-alternatives"]) / data["#-of-alternatives"])
#     except:
#         print(module, data.keys())
#         counter3 += 1
#         mdls_no_compls.append(module)

# data_points_df = pd.DataFrame(data_points)
# data_points_df.columns = ["ratio"]

# g1 = (
#     ggplot(data_points_df, aes(x="ratio"))
#     + geom_histogram(binwidth=0.1, alpha=0.7, fill="#28579E")
#     + geom_text(
#         aes(label='..count..'),
#         stat='bin',
#         binwidth=0.1,
#         va='bottom',
#         size=16,
#         color='black'
#     )
#     + labs(
#         title="A. Alternatives coverage",
#         x="Fraction of a module's alternatives completed by any donor",
#         y="Number of modules")

#     + theme(
#         plot_title=element_text(size=18, weight="bold"),
#         axis_text=element_text(size=16),   # Adjust axis tick labels font size
#         axis_title=element_text(size=16)   # Adjust axis title font size
#     )
#     # + scale_x_continuous(breaks=range(0, 1), minor_breaks=[])
# )
