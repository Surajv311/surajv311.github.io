---
layout: post 
title: DNS Misconfiguration Issue
category: technicalArticles
---

> From my experience working at [Punch](https://www.punch.trade/). 

Recently, I was discussing the issue with devops which made me brush up concepts related to DNS. In short, one of the pages of main website of Punch had a broken CSS/styling. 
This happened because the DNS record for that page was probably pointing to the wrong Application Load Balancer (staging service or other). 
Devops fixed the Route 53 record to point to the correct ALB, which restored CSS loading and fixed the UI.
Now, my brushup behind this: 
- Understanding DNS: The Internet's Address Book
  - DNS translates human-readable domain names into IP addresses that computers use to connect. When you type `xyz.punch.trade` into your browser, a lookup process begins that walks through a hierarchy of DNS servers.
  - Your browser queries a recursive DNS resolver, typically your ISP's DNS or a public service like Google's 8.8.8.8. 
  - This resolver contacts one of thirteen root DNS servers asking "who manages .trade domains?" The root server responds with addresses of .trade TLD servers. 
  - The resolver then asks these TLD servers "who is authoritative for punch.trade?" and receives Route 53's nameservers as the answer. (Other nameservers ex: Route 53, Cloudflare, Google DNS, Akamai DNS, etc.)
  - Finally, the resolver queries Route 53 directly for xyz.punch.trade and receives an IP address or load balancer DNS name. 
  - The resolver caches this answer based on TTL settings and returns it to your browser. (Good videos around this: [video 1](https://www.youtube.com/watch?v=akwAv_L1XQ4), [video2](https://www.youtube.com/watch?v=csXEbgwH7Vs&t=91s)).
- How Domains Enter the DNS System
  - Before DNS resolution can work, the domain must exist in the global system. 
  - Punch purchased punch.trade through a registrar like GoDaddy, which acts as a middleman to the official .trade registry. 
  - During registration, Punch specified Route 53 nameservers as the authoritative DNS provider.
  - The registrar communicated this to the .trade registry, which updated its global database.
  - This information propagated to TLD servers worldwide, making Route 53 the authoritative source for all punch.trade DNS queries.
- What DNS Records Actually Control
  - DNS operates exclusively at the hostname level. When you create a Route 53 record for xyz.punch.trade, you map that complete hostname to a destination server or load balancer. 
  - Route 53 knows nothing about files, application code, or URL paths. There's no DNS record for xyz.punch.trade/index.html or xyz.punch.trade/assets/main.css.
  - DNS simply answers "what server hosts this domain name?" The server itself handles all file routing and application logic.
- How Websites Load After DNS Resolution
  - Once your browser obtains the IP address from DNS, it establishes a TCP connection to the Application Load Balancer and performs an SSL/TLS handshake for secure connections. 
  - The browser sends an HTTP request, which the ALB forwards to an ECS container running your web application. That container generates and returns the HTML response.
  - As the browser parses the HTML, it discovers additional resources like CSS files, JavaScript, and images. For each resource, the browser makes separate HTTP requests. When it encounters `<link rel="stylesheet" href="https://xyz.punch.trade/assets/career/main-1234.css">`, it performs DNS resolution again for xyz.punch.trade (typically served from cache) and requests that specific file path. 
  - The ALB forwards this request to an ECS container where your application or web server like Nginx uses its internal routing logic to serve the CSS file from the correct directory.
- About the bug
  - The Route 53 record for xyz.punch.trade pointed to the wrong ALB. When browsers loaded the page, they received HTML successfully, possibly from cache or because the initial connection worked. However, when browsers attempted to fetch the CSS file referenced in the HTML, DNS resolution returned the wrong destination. The CSS request either failed completely or reached a server where the file didn't exist.
  - Without CSS, HTML renders as unstyled text. All content appears on the page but without layouts, colors, fonts, or visual formatting. The site looked broken even though the actual content and structure were intact. 
  - Once Devops updated the Route 53 record to point to the correct ALB and DNS caches expired according to TTL settings, CSS requests began reaching the correct server. The stylesheet loaded successfully and the UI displayed properly.
- Insight
  - DNS sits at the network layer, completely separate from your application. Route 53 points browsers to your ALB, which forwards requests to ECS containers running your application code. 
  - That application code came from GitHub through a CI/CD pipeline that builds Docker images and deploys them to ECS (update image in ECR & ECS pulls and runs container from the image). 
  - DNS has no involvement in this deployment process. Its single job is mapping hostnames to server addresses. 
  - When that mapping breaks, resources referenced by absolute URLs fail to load even though the initial page may appear functional.

----------------------------------------
