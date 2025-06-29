---
layout: post
title: Tech Cost optimizations
category: technicalArticles
---

> From my experience working at [Simpl](https://simpl.com/).

When it comes to saving costs around systems, if looked deeply, we'll find many avenues to save cost. As a part of work, learned lots of things around this working on it myself and listening to how other teams saved cost.
It's not exhaustive list, but have tried adding as many as I recall. 
- Tools which we use, check for usage vs cost optimizations, if not used with full potential, discard. Building in-house tools. 
- Shutting down un-utilized services or APIs. 
- Scaling down over-provisioned infra. Moving from reserved to spot infra, changing to graviton processors, etc. 
- User coms cleanup and optimize. 
- Optimizing data queries like reducing scanning, adding index, changing workflow frequencies, etc., - deprecating unnecessary tables.
- Optimizing workflows - places where we publish/send full data -> Change it to delta. 
- Save storage space in S3, write files in zip format?, object versioning remove??, unnecessary files delete, add a retention policy in bucket, explored AWS Glacier cold storage for older data, etc. 
- Underused ALBs shutdown or merge, i.e having commone ALB for multiple services, staging/production infra ecosystem cleanup. 
- Removing unnecessary logs publishing to Opensearch and other places. 
- Cleaning up dynamo tables, adding TTL, etc. 
- Unnecessary Cloudwatch alarms removed. AWS Cloudtrail optimize. Metrics being captured reduced. 
- Cloudfront costs save, use optimized images, cache data rather than fetching from Cloudfront everytime, etc.

And, slow can be sometimes good to save cost. 

--------------------------------------------------
