wellcome

<!-- It retrieves the KEGG modules that have been assigned to each of the species found related. 
Based on the **pathway complementarity** concept, pathways found in both taxa of an association are further explored to check whether the processes of each of the two taxa are complementary denoting a  positive interaction. 
Likewise, if the same processes are found to occur in both taxa, a negative interaction will be derived.

On top of that, *microbetag* integrates phenotypic information thanks to resources such as [FAPROTAX](https://github.com/knights-lab/BugBase); 
a series of environmental variables (pH optima, oxygen tolerance etc.) are assembled in each node of the network.
Their comparison in each pair of correlated taxa evaluates their corresponding association further.  -->


<!-- 
To use `MGG` you need to first make sure you have Cytoscape installed on your machine; 
Then, there are two ways to install MGG in Cytoscape: 
Either from through the Cytoscape app store on a browser or from within Cytoscape.
In the first case, you need to **first launching Cytoscape**, and then visit the [MGG Cytoscape Appstore page](https://apps.cytoscape.org/apps/mgg). By clicking the `Install` button `MGG` will be automatically added on your Cytoscape.
Alternatively, to install `MGG` from within Cytoscape, you may click `Apps > App Store > Show App Store`, then search for "microbetag" in the pop-up box and follow this will guide you to the MGG page.
 -->
<!-- 
Once MGG is installed, you are ready to use `microbetag` either on the fly, by providing an OTUs/ASVs (amplicon data) and optionally a network, if you already have one, or locally, if you want to apply the annotations on your own bins/MAGs. In the last case, you will also have to install [Docker](https://www.docker.com) or [Singularity](https://sylabs.io) and pull the `microbetag` image that allows you to do so (see [Additional tutorials](advanced_use/tutorials.md) for more). -->




<!-- 
## Dependencies

To run *microbetag* you need to have [Docker](https://www.docker.com/) on your computing environment. 
As described from IBM, Docker is an open source containerization platform. 
It enables developers to package applications into containers—standardized executable components combining application source code with the operating system libraries and dependencies required to run that code in any environment.

You can install Docker in Linux, MaxOS or Windows systems by following the instructions you will finde [here](https://docs.docker.com/get-docker/).


### Get

Once Docker is available, to get *microbetag* you need to *pull* it from DockerHub. 
To do this, you need to run: 

```bash=
docker push hariszaf/microbetag
```

This way, the latest version of *microbetag* will be pulled. 
You may specify which version of *microbetag* you wish to pull by running instead:

```bash=
docker push hariszaf/microbetag:tagname
```
where `tagname` is the name of the specific version. 

 -->



