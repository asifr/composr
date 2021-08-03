import os
import io
import random
import string
import typing as t
import json
from jinja2 import Environment, PackageLoader, select_autoescape, contextfilter
from markdown import Markdown

# Markdown extensions
extensions = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.footnotes",
    "markdown.extensions.tables",
    "markdown.extensions.codehilite",
    "markdown_katex",
]


@contextfilter
def call_macro_by_name(context, macro_name, *args, **kwargs):
    return context.vars[macro_name](*args, **kwargs)


def generate_key(N=6, prefix="co-") -> str:
    return prefix + "".join(
        random.SystemRandom().choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        )
        for _ in range(N)
    )


def fwrite(file_path: str, data: str):
    """Write data to file"""
    with io.open(file_path, "w", encoding="utf8") as f:
        f.write(data)


def fread(file_path):
    """Read data from file"""
    with io.open(file_path, "r", encoding="utf8") as f:
        return f.read()


def mpl_svg(fig) -> str:
    """Return the SVG string of a matplotlib figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure

    Returns
    -------
    str
        Figure SVG
    """
    f = io.BytesIO()
    fig.savefig(f, format="svg", bbox_inches="tight")
    svg = str(f.getvalue().decode("utf-8"))
    svg = "\n".join(svg.split("\n")[3:])
    return svg


def mpl_png(fig) -> str:
    """Return the base64 encoded png string of a matplotlib figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure

    Returns
    -------
    str
        Figure base64 encoding
    """
    import base64

    f = io.BytesIO()
    fig.savefig(f, format="png", bbox_inches="tight")
    f.seek(0)
    b = base64.b64encode(f.getvalue()).decode("utf-8").replace("\n", "")
    return '<img class="mpl-figure-png" align="center" src="data:image/png;base64,%s">' % b


class Composr:
    """The composr object loads the templates, macros, extensions, and acts as
    the central object for adding components and saving documents. Once it is
    created it will act as the central repository for components, figure and
    table numbers and much more."""

    def __init__(self, basic: t.Optional[bool] = False):
        self.env = Environment(
            loader=PackageLoader("composr"), autoescape=select_autoescape()
        )
        # call macro in template using the macro name: {{name | macro(params)}}
        self.env.filters["macro"] = call_macro_by_name
        self.mdprocessor = Markdown(
            extensions=extensions,
            extension_configs={
                "markdown_katex": {
                    "insert_fonts_css": True,
                },
            },
        )

        # global parameters for layout.html template
        self.tpl_params: t.Mapping[str, t.Any] = {
            "basic": basic,
            "width": 980
        }
        # collection of components
        self.components_: t.Sequence[t.Mapping[str, t.Any]] = []
        # figure and table numbering
        self.figure_number_: int = 0
        self.table_number_: int = 0

    def add_title(self, text: str):
        """Add a page title"""
        self.tpl_params["title"] = text

    def add_heading(self, text: str):
        """Add a H1 HTML heading"""
        self.append_component("heading", value=text)

    def add_subheading(self, text: str):
        """Add a H2 HTML heading"""
        self.append_component("subheading", value=text)

    def add_markdown(self, text: str):
        """Add markdown formatted text."""
        self.append_component("markdown", value=self.mdprocessor.convert(text))

    def add_markdown_file(self, file_path: str):
        """Add markdown formatted text from a file"""
        assert os.path.isfile(file_path), f"{file_path} does not exist"
        text = fread(file_path)
        self.append_component("markdown", value=self.mdprocessor.convert(text))

    def add_html(self, text: str):
        """Add raw HTML"""
        self.append_component("html", value=text)

    def add_text(self, text: str):
        """Add plain unformatted text"""
        self.append_component("text", value=text)

    def add_dataframe(
        self, df, caption: t.Optional[str] = None, max_rows: t.Optional[int] = 1000
    ):
        """Add a Pandas dataframe as an HTML table"""
        self.table_number_ += 1
        try:
            df = df.iloc[:max_rows]
        except:
            pass
        self.append_component(
            "dataframe",
            value=df.to_html(),
            caption=caption,
            table_number=self.table_number_,
        )

    def add_tabulator(
        self,
        df,
        caption: t.Optional[str] = None,
        rows_per_page: t.Optional[int] = 20,
        max_rows: t.Optional[int] = 1000,
        height: t.Optional[int] = 300,
    ):
        """Add a pandas dataframe as a paginated table"""
        # set the global tabulator variable to load the javascript and css
        self.tpl_params["tabulator"] = True
        self.table_number_ += 1
        self.append_component(
            "tabulator",
            value=df.iloc[:max_rows].to_dict(orient="records"),
            caption=caption,
            table_number=self.table_number_,
            rows_per_page=rows_per_page,
            height=height,
        )

    def add_link(self, text: str, url: str):
        """Add a link"""
        self.append_component("link", value=text, url=url)

    def add_docstring(self, fun: t.Callable):
        """Add the preformatted docstring from a function or module"""
        import inspect

        source = inspect.cleandoc(fun.__doc__)
        value = f"```text\n{source}\n```"
        value = self.mdprocessor.convert(value)
        self.append_component("docstring", value=value, name=fun.__name__)

    def add_markdown_docstring(self, fun: t.Callable):
        """Add the markdown formatted docstring from a function or module"""
        import inspect

        self.append_component(
            "docstring",
            value=self.mdprocessor.convert(inspect.cleandoc(fun.__doc__)),
            name=fun.__name__,
        )

    def add_comments(self, fun: t.Callable):
        """Add the markdown formatted comments from a function or module"""
        import inspect

        text = inspect.getcomments(fun)
        # remove comment token
        text = inspect.cleandoc(
            "\n".join([line.lstrip("#") for line in text.split("\n")])
        )
        self.append_component(
            "docstring", value=self.mdprocessor.convert(text), name=fun.__name__
        )

    def add_details(self, text: str, title: t.Optional[str] = None):
        """Add details and summary"""
        self.append_component("details", value=text, title=title)

    def add_patient(self, df, columns: t.List[str]=[], rows: t.List[str]=[]):
        """Add patient tables"""
        vitals = df.astype(str).to_dict()
        self.append_component("patient", vitals=vitals, columns=columns, rows=rows)

    def add_tip_aside(self, text: str, title: t.Optional[str] = None):
        """Add an markdown formatted tip aside"""
        self.append_component("tip", value=self.mdprocessor.convert(text), title=title)

    def add_important_aside(self, text: str, title: t.Optional[str] = None):
        """Add an markdown formatted important aside"""
        self.append_component("important", value=self.mdprocessor.convert(text), title=title)

    def add_sourcecode(self, fun, lang: t.Optional[str] = "python", hidden=False):
        """Add source code from a function or module"""
        import inspect

        source = inspect.getsource(fun)
        value = self.mdprocessor.convert(f"```{lang}\n{source}\n```")
        self.append_component(
            "sourcecode", value=value, name=fun.__name__, hidden=hidden
        )

    def add_plotly(
        self,
        fig,
        caption: t.Optional[str] = None,
        width: t.Optional[int] = 800,
        height: t.Optional[int] = 600,
    ):
        """Embed a plotly figure"""
        from plotly.io import to_json

        # set the global plotly variable to load the javascript and css
        self.tpl_params["plotly"] = True
        self.figure_number_ += 1
        ps = json.dumps(to_json(fig))
        self.append_component(
            "plotly",
            value=ps,
            width=width,
            height=height,
            caption=caption,
            figure_number=self.figure_number_,
        )

    def add_svg(self, fig, caption: t.Optional[str]=None):
        """Add matplotlib figure as embedded SVG"""
        svg = mpl_svg(fig)
        self.figure_number_ += 1
        self.append_component(
            "svg", value=svg, caption=caption, figure_number=self.figure_number_
        )

    def add_png(self, fig, caption: t.Optional[str]=None):
        """Add matplotlib figure as base64 encoded PNG"""
        png = mpl_png(fig)
        self.figure_number_ += 1
        self.append_component(
            "png", value=png, caption=caption, figure_number=self.figure_number_
        )

    def add_json(self, data):
        """Show a dictionary or sequence in a JSON viewer"""
        self.tpl_params["jquery"] = True
        self.append_component("json", value=json.dumps(data))

    def insert_custom_css_file(self, file_path: str):
        """Add custom css from a file"""
        assert os.path.isfile(file_path), f"{file_path} does not exist"
        css = fread(file_path)
        self.tpl_params["custom_css"] = css

    def replace_default_css_file(self, file_path: str):
        """Replace the default CSS from a file"""
        assert os.path.isfile(file_path), f"{file_path} does not exist"
        css = fread(file_path)
        self.tpl_params["css"] = css

    def replace_codehilite_css_file(self, file_path: str):
        """Replace the default codehilite CSS from a file"""
        assert os.path.isfile(file_path), f"{file_path} does not exist"
        css = fread(file_path)
        self.tpl_params["codehilite_css"] = css

    def append_component(self, type: str, **kwargs):
        """Add a new component"""
        params = {"type": type, "id": generate_key()}
        assert "type" not in kwargs, "type is a reserved component template variable"
        assert "id" not in kwargs, "id is a reserved component template variable"
        params.update(kwargs)
        self.components_.append(params)

    def generate_html(self) -> str:
        """Generate HTML"""
        template = self.env.get_template("layout.html")
        html = template.render(components=self.components_, **self.tpl_params)
        return html

    def save_html(self, file_path: str):
        """Save generated document as HTML file"""
        assert file_path.endswith(".html"), "file_path must have a .html extension"
        assert (
            len(self.components_) > 0
        ), "components list is empty, add components before saving"
        html = self.generate_html()
        print("Creating HTML...")
        fwrite(file_path, html)

    def save_pdf(self, file_path: str):
        """Save generated document as a PDF"""
        assert file_path.endswith(".pdf"), "file_path must have a .pdf extension"
        assert (
            len(self.components_) > 0
        ), "components list is empty, add components before saving"
        import pdfkit

        html = self.generate_html()
        print("Creating PDF...")
        pdfkit.from_string(html, file_path)

    def display_notebook(self):
        """Display generated HTML in a Jupyter notebook"""
        from IPython.core.display import display, HTML

        html = self.generate_html()
        display(HTML(html))