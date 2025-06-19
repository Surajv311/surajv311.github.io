---
layout: post 
title: Crossing paths with bugs, issues, unknown systems, and more
category: technicalArticles
---

> From my experience working at [Simpl](https://simpl.com/).

In this article, I jot down, different issues & bugs I or my teammates faced in software systems along with fixes we did.
I may miss some of them, but have added as many as my memory serves me right. 
I think a lot of my learnings actually came from solving issues. 

- Issues with data pipeline(s): 
  - Pipeline 1: As seen below, at a high level it's an event parsing batch job pipeline where raw data is parsed and loaded to tables which is later accessed by downstream teams. The pipeline is actually complex and it has its leaky points.  
    - <img src="{{ site.baseurl }}/public/images/events-data-pipeline.jpg" alt="Events data pipeline" class="blog-image">
    - Issue 1: 
    - Issue 2: 
  - Pipeline 2: 
    - <img src="{{ site.baseurl }}/public/images/rds-data-pipeline.png" alt="Rds data pipeline" class="blog-image">
    - Issue 1: 
    - Issue 2:
- Issues with Concourse deployment pipeline(s): 
  - 



----------------
