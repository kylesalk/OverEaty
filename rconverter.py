"""
Uses the dictionary from ``parser.RecipeReader`` to format recipe files
"""
import os
from abc import ABC, abstractmethod

DEFAULT_OUTPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                               "converted")


class Converter(ABC):
    """Base converter class; do not instatiate directly

    Parameters
    ----------
    rdict : dict
        Recipe dictionary
    """
    recipe_text = ""

    def __init__(self, rdict):
        self.rdict = rdict

    @staticmethod
    @abstractmethod
    def _make_header(text, level):
        """Creates a header string in the specified language
        
        Parameters
        ----------
        text : str
        level : int
        
        Returns
        -------
        str
        """

    @staticmethod
    @abstractmethod
    def _make_line(text):
        """Add a line of text in the specified language
        
        Parameters
        ----------
        text : str
        
        Returns
        -------
        str
        """

    @staticmethod
    @abstractmethod
    def _make_ol(litems):
        """Creates an ordered list in the specific language

        Parameters
        ----------
        litems : list(str)
        
        Returns
        -------
        str
        """
    
    @staticmethod
    @abstractmethod
    def _make_ul(litems):
        """Creates an un-ordered list in the specified language
        
        Parameters
        ----------
        litems : list(str)
        
        Returns
        -------
        str
        """

    def format(self, rdict=None, initial=""):
        """Returns the formatted dictionary as a string"""
        if rdict is None:
            rdict = self.rdict

        self.recipe_text = initial
        self.recipe_text += self._make_header(
            rdict.get("title", "Recipe Title"), level=1
        )
        self.recipe_text += self._make_line(rdict.get("time", "Time: N/A"))
        
        self.recipe_text += self._make_ul(rdict.get("ingredients", []))
        self.recipe_text += "\n"
        
        for stage, steps in rdict.get("stages", {}).items():
            self.recipe_text += self._make_header(stage, level=2)
            self.recipe_text += self._make_ol(steps)
            self.recipe_text += "\n"
        
        comments = rdict.get("comments", [])
        if comments:
            self.recipe_text += self._make_header("Comments", level=2)
            self.recipe_text += self._make_ul(comments)

        return self.recipe_text

    def save_output(self, ext, rdict=None, fname=None,
                    fpath=DEFAULT_OUTPATH):
        """Saves the formatted object to a file location"""
        print("saving...", fpath)
        if rdict is None:
            rdict = self.rdict
        if fname is None:
            fname = rdict["title"]
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        with open(os.path.join(fpath, fname + ext), "w") as f:
            f.write(self.recipe_text)


class LaTeXConverter(Converter):
    """Converts a recipe dict to LaTeX output"""
    initial = "\\documentclass{article}\n\\usepackage[english]{babel}\n\\" \
               + "usepackage[utf8]{inputenc}\n\\begin{document}\n"

    def __init__(self, rdict):
        Converter.__init__(self, rdict)
        self.header_format = {  # '*' ensures it isn't numbered
            1: "\\section*{{{0}}}",
            2: "\\subsection*{{{0}}}",
            3: "\\subsubsection*{{{0}}}",
            4: "\\paragraph*{{{0}}}",
            5: "\\subparagraph*{{{0}}}",
        }
        self.format()

    def _make_header(self, title, level=1):
        """Makes a header line"""
        if level in self.header_format:
            return self.header_format[level].format(title) + "\n"
        return title + "\n"

    @staticmethod
    def _make_line(text):
        """Makes a text line"""
        return text + "\n"

    @staticmethod
    def _make_ol(litems):
        """Makes an ordered LaTeX list string (numbers 1 - len(list))"""
        text = "\\begin{enumerate}\n"
        for i in litems:
            text += "\\item " + i + "\n"
        return text + "\\end{enumerate}\n"

    @staticmethod
    def _make_ul(litems):
        """Makes an un-ordered LaTeX list string"""
        text = "\\begin{itemize}\n"
        for i in litems:
            text += "\item " + i + "\n"
        return text + "\\end{itemize}\n"

    def format(self, rdict=None, initial=None):
        if initial is None:
            initial = self.initial
        Converter.format(self, rdict=rdict, initial=initial)
        self.recipe_text += "\\end{document}"

    def save_output(self, rdict=None, fname=None,
                    fpath=os.path.join(DEFAULT_OUTPATH, "latex")):
        """Super call to normal save with '.md' extension"""
        extension = ".tex"
        Converter.save_output(self, extension, rdict=rdict, fname=fname,
                              fpath=fpath)


class MarkdownConverter(Converter):
    """Converts a recipe dict to Markdown output"""
    def __init__(self, rdict):
        Converter.__init__(self, rdict)
        self.format()

    @staticmethod
    def _make_header(title, level=1):
        """Makes a header line"""
        return "#" * level + " " + title + "\n\n"

    @staticmethod
    def _make_line(text):
        """Makes a text line"""
        return text + "\n\n"

    @staticmethod
    def _make_ol(litems):
        """Makes an ordered list Markdown string (numbers 1 - len(list))"""
        text = ""
        for i, j in enumerate(litems):
            text += "{0}. {1}\n".format(i + 1, j)
        return text

    @staticmethod
    def _make_ul(litems):
        """Makes an un-ordered list Markdown string"""
        text = ""
        for i in litems:
            text += "* " + i + "\n"
        return text

    def save_output(self, rdict=None, fname=None,
                    fpath=os.path.join(DEFAULT_OUTPATH, "markdown")):
        """Super call to normal save with '.md' extension"""
        extension = ".md"
        Converter.save_output(self, extension, rdict=rdict, fname=fname,
                              fpath=fpath)
        

class HTMLConverter(Converter):
    """Converts a recipe dict to HTML output"""
    def __init__(self, rdict):
        Converter.__init__(self, rdict)
        self.format()

    @staticmethod
    def _make_header(title, level=1):
        return "<h{0}>{1}</h{0}>\n".format(level, title)

    @staticmethod
    def _make_line(text):
        return "<p>" + text + "</p>\n"

    @staticmethod
    def _make_ol(litems):
        """Creates an unordered list"""
        text = "<ol>\n"
        for i in litems:
            text += "<li>{0}</li>\n".format(i)
        return text + "</ol>\n"

    @staticmethod
    def _make_ul(litems):
        """Creates an unordered list"""
        text = "<ul>\n"
        for i in litems:
            text += "<li>" + i + "</li>\n"
        return text + "</ul>\n"

    def save_output(self, rdict=None, fname=None,
                    fpath=os.path.join(DEFAULT_OUTPATH, "html")):
        """Super call to normal save with '.html' extension"""
        extension = ".html"
        Converter.save_output(self, extension, rdict=rdict, fname=fname,
                              fpath=fpath)
