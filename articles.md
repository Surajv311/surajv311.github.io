---
layout: page
title: Articles
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

[//]: # (### Super-old learnings... )

[//]: # (<ul>)

[//]: # (  {% for post in site.posts %})

[//]: # (    {% if post.category == "oldArticles" %})

[//]: # (      <li>)

[//]: # (        <a href="{{ post.url }}">{{ post.title }}</a> - <small>{{ post.date | date_to_string }}</small>)

[//]: # (      </li>)

[//]: # (    {% endif %})

[//]: # (  {% endfor %})

[//]: # (</ul>)

-----------------------------------
