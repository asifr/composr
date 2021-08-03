# Composr - Static report generator

Compose HTML and PDF documents using any Python object inclduing strings, lists, dicts, modules, functions, code comments, docstrings, Pandas DataFrames, Matplotlib figures, and Plotly graphs. Use composr to knit the output of your python programs into a single self-contained document.

## Install

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```bash
pip install git+https://github.com/asifr/composr.git --upgrade
```

## In a nutshell

```python
from composr import Composr
com = Composr()
# set the page title
com.add_title("Composr - Static report generator")
# add a markdown file
com.add_markdown_file("./README.md")
# save
com.save_html("./documentation.html")
```

## Use cases

- Reproducible data science reports with figures, code, and prose
- Create documentation without leaving Python
- Generate static sites

## Features

- Automatic table and figure numbering
- Latex math inside Markdown (using [Katex](https://katex.org/))
- Code highlighting inside markdown
- Source code of python objects with code highlighting
- Customizable themes with [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/templates/) templates
- Save as HTML or PDF (saving PDF requires [pdfkit](https://pypi.org/project/pdfkit/) and [wkhtmltopdf](https://wkhtmltopdf.org/))

## API

- Pandas DataFrame to table: `com.add_dataframe(df, caption, max_rows=1000)`
- Paginated DataFrames: `com.add_tabulator(df, caption, rows_per_page=20, max_rows=1000, height=300)`
- Matplotlib figure to embedded SVG: `com.add_svg(fig, caption)`
- Matplotlib figure to embedded PNG: `com.add_png(fig, caption)`
- Plotly figures embedded in HTML: `com.add_plotly(fig, caption, width=800, height=600)`
- Embed markdown files: `com.add_markdown_file(filename)`
- Markdown-formatted text: `com.add_markdown(text)`
- Plain text: `com.add_text(text)`
- Source code: `com.add_sourcecode(obj, lang="python", hidden=False)`
- Markdown-formatted docstrings: `com.add_markdown_docstring(obj)`
- Plain docstrings: `com.add_docstring(obj)`
- Comments: `com.add_comments(obj)`
- JSON viewer: `com.add_json(dict)`
- [Details disclosure](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details): `com.add_details(text, title)`
- Tip aside: `com.add_tip_aside(text, title)`
- Important aside: `com.add_important_aside(text, title)`
- Add custom css: `com.add_css_file(filename)`, `com.add_custom_css_file(filename)`, `com.add_codehilite_css_file(filename)`
