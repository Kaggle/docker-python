"""%tensorboard line magic that patches TensorBoard's implementation to make use of Jupyter 
TensorBoard server extention providing built-in proxying.

Use:
    %load_ext tensorboard.notebook
    %tensorboard --logdir /logs
"""

import argparse
import uuid

from IPython.display import display, HTML, Javascript

def _tensorboard_magic(line):
    """Line magic function."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--logdir', default='/kaggle/working')
    args = parser.parse_args(line.split())
    
    iframe_id = 'tensorboard-' + str(uuid.uuid4())
        
    html = """
<script>
    const req = {
        method: 'POST',
        contentType: 'application/json',
        body: JSON.stringify({ 'logdir': '%s' }),
        headers: { 'Content-Type': 'application/json' }
    };

    const baseUrl = Jupyter.notebook.base_url;

    fetch(baseUrl + 'api/tensorboard', req)
        .then(res => res.json())
        .then(res => document.getElementById('%s').src = baseUrl + 'tensorboard/' + res.name);
</script>

<iframe id="%s" style="width: 100%%; height: 620px" frameBorder="0"></iframe>
""" % (args.logdir, iframe_id, iframe_id)
    
    display(HTML(html))
    
def load_ipython_extension(ipython):
    """IPython extention entry point."""
    ipython.register_magic_function(
        _tensorboard_magic,
        magic_kind='line',
        magic_name='tensorboard',
    )