{# 
Jinja template to inject notebook cell metadata to enhance generated HTML output
All cell metadata starting with '_kg_' will be included with its value ({key}-{value}) 
as a class in the cell's DIV container
#}
    
{% extends 'full.tpl'%}
{% block any_cell %}
    <div class="{% for k in cell['metadata'] if k.startswith("_kg_") %}{{k}}-{{cell['metadata'][k] | lower}} {% endfor %}">
        {{ super() }}
    </div>
{% endblock any_cell %}