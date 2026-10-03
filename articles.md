---
layout: page
title: Articles
description: Technical and non-technical articles by Suraj Verma on backend & data systems, plus history, politics, mythology and other topics of interest.
---

<p class="message">
  Includes, blogs I wrote in distant past, present day musings and learnings.
</p>

### Tech learnings... 
<ul>
  {% for post in site.posts %}
    {% if post.category == "technicalArticles" %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a> - <small>{{ post.date | date_to_string }}</small>
      </li>
    {% endif %}
  {% endfor %}
</ul>

### Non-tech learnings... 
<ul>
  {% for post in site.posts %}
    {% if post.category == "nonTechnicalArticles" %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a> - <small>{{ post.date | date_to_string }}</small>
      </li>
    {% endif %}
  {% endfor %}
</ul>

-----------------------------------
