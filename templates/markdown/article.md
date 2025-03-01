# {{ title }}

{{ summary }}

## Tags
{% for tag in tags %}
- {{ tag.name }} ({{ "%.2f"|format(tag.score) }})
{% endfor %}

## Links
{% for link in links %}
- [Link]({{ link }})
{% endfor %}

## Comments
{% for comment in comment_summaries %}
- {{ comment }}
{% endfor %}

---
*Article indexed at: {{ indexed_at }}*
