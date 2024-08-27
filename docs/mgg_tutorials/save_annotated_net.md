---
title: Save annotated network
layout: default
parent: Cytoscape tutorials
nav_order: 5
description: "tutorial on how to save your current work"
---

It is rather common for Cytoscape users to save the whole session they are working with as a `.cys` file by simply clicking on `File > Save Session As...` and giving a name to their session. 

{: .warning}
Due to a buG in the current MGG implementation, if you save your `microbetag`-annotated network as a session, then you most probably will not be able to parse the seed and pathway complementarities **once you re-open** the session. 

We already work on fixing the bug so we support this really handy Cytoscape feature. 

Until then, one can save a `microbetag`-annotated network as described here, in order to have all the MGG features once they re-open it:

- Click on `File > Export >Network to File..`
- From the list of File Formats, select the `CX JSON (*.cx)` one
- Give a name to your `microbetag`-annotated network and press `OK`.

**Remember** that in this way, you only save the specific network and not all the networks you may have opened in your session! 

{: .note}
You can always save your session normally, export the `microbetag`-annotated network as described above and when you want to open your session as it used to be, then you first load the session and from there you import the `.cx` file you exported. This will be *equivalent* with saving the whole original session.

Now you can re-open the `microbetag`-annotated network as descrobed [here](../tutorials/load.md#load-already-microbetag-annotated-networks). 



