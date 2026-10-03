---
layout: page
title: Articles
description: Technical and non-technical articles by Suraj Verma on computer systems & other topics of interest.
---

<p class="message">
  Includes, blogs I wrote in distant past, present day musings and learnings.
</p>

### Tech learnings... 
<ul>
  {% for post in site.posts %}
    {% if post.category == "technicalArticles" %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a> - <small>{{ post.date | date_to_string }} &middot; {{ post.content | number_of_words | divided_by: 200 | plus: 1 }} min read</small>
      </li>
    {% endif %}
  {% endfor %}
</ul>

### Non-tech learnings... 
<ul>
  {% for post in site.posts %}
    {% if post.category == "nonTechnicalArticles" %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a> - <small>{{ post.date | date_to_string }} &middot; {{ post.content | number_of_words | divided_by: 200 | plus: 1 }} min read</small>
      </li>
    {% endif %}
  {% endfor %}
</ul>

-----------------------------------
