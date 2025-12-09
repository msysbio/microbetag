modelseedpy 0.4.2 requiries cobra >= 0.28;
yet dnngioir requireis cobra <= 0.23


ModelSEEDpy is now under development in a fork repo: 
https://github.com/freiburgermsu/ModelSEEDpy.git

Yet, its `main` branch still results in several errors when running MSBuilder.

-----------------     ModelSEEDpy==0.4.2

BIG CONFLICT !! 

modelseedpy 0.2.2 is the only that actually works so far, though it requires `scikit-learn == 0.24.2`,
so the knn_ACNP_RAST_filter.pickle would be loaded fine

Yet, 0.24.2 is only supported for Python >=3.6, <3.10 !!! 

`scikit-learn == 0.24.2`  Not working on Python 3.10
`scikit-learn==1.2.0`


depends on `scikit-learn==0.23.2`

https://github.com/univieCUBE/phenotrex/blob/master/requirements/prod.txt

`phenotrex[fasta]`    # ==0.6.0     phenonotrex is installed through setup_environmnet.sh 


Based on which ModelSEEDpy version you are about to use, it requires a specific scikit-learn version. 

For example, in `>= 1.2.0` version lock for pickle ML models

We now install ModelSEEDpy on the setup_environment.sh since latest version in not on PiPY, but only on a fork.
