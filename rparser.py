"""
The class RecipeReader parses a recipe file (plain text) with the form:

    title: ...
    time: ...
    ingredient: ...
    .
    .
    stage: ...
    step: ...
    .
    .
    comment: ...
    .
    .

All steps after a "stage" are added to a list of steps for that stage.

When parsed, a dictionary is created:
    {
        "title": str,
        "time": str,
        "ingredients": list(str),
        "stages": {
            str: list(str)
        },
        "comments": list(str),
    }
"""
import json
import os


class ParserException(Exception):
    """Exception for the parser

    Parameters
    ----------
    message : str
        Exception message
    """
    def __init__(self, message):
        self.message = message
        super(ParserException, self).__init__(message)


class RecipeReader:
    """Reads a recipe file and extracts information

    Parameters
    ----------
    filepath : str
        Absolute path to the recipe file
    read_now : bool
        If the file should be parsed immediately (default=True)
    """
    def __init__(self, filepath, read_now=True):
        self.filepath = filepath
        self.recipe_info = {
            "title": "",
            "time": "N/A",
            "ingredients": [],
            "stages": {},
            "comments": [],
        }

        if read_now:
            self.parse()

    def _parse_comment(self, string):
        comment = string.split("comment:")[1].strip()
        if comment not in self.recipe_info["comments"]:
            self.recipe_info["comments"].append(comment)

    def _parse_ingredient(self, string):
        ingredient = string.split("ingredient:")[1].strip()
        if ingredient not in self.recipe_info["ingredients"]:
            self.recipe_info["ingredients"].append(ingredient)

    def _parse_stage(self, string):
        stage = string.split("stage:")[1].strip()
        if stage not in self.recipe_info["stages"].keys():
            self.recipe_info["stages"][stage] = []
        return stage

    def _parse_step(self, string, stage):
        if stage not in self.recipe_info["stages"].keys():
            return

        step = string.split("step:")[1].strip()
        if step not in self.recipe_info["stages"][stage]:
            self.recipe_info["stages"][stage].append(step)

    def _parse_time(self, string):
        self.recipe_info["time"] = string.split("time:")[1].strip()

    def _parse_title(self, string):
        self.recipe_info["title"] = string.split("title:")[1].strip()

    def parse(self, filepath=None):
        """Reads a file. If left as None, the method will parse `self.filepath`

        Parameters
        ----------
        filepath : str
            Abs. path to file to read (default=None)
        """
        if filepath is None:
            filepath = self.filepath

        if not os.path.exists(filepath):
            raise ParserException("File ({0}) was not found!".format(filepath))

        with open(filepath) as r_f:
            lines = r_f.readlines()
            curr_stage = ""
            for line in lines:
                if line.startswith("title:"):
                    self._parse_title(line)
                elif line.startswith("time:"):
                    self._parse_time(line)
                elif line.startswith("ingredient:"):
                    self._parse_ingredient(line)
                elif line.startswith("stage:"):
                    curr_stage = self._parse_stage(line)
                elif line.startswith("step:"):
                    self._parse_step(line, curr_stage)
                elif line.startswith("comment:"):
                    self._parse_comment(line)

    def output_json(self, loc, append=False):
        """Outputs the recipe as JSON to a file location

        Parameters
        ----------
        loc : str
            File location (absolute path)
        append : bool
            Append recipe to existing file
        """
        to_dump = json.dumps(self.recipe_info)
        mode = "a" if append else "w"
        with open(loc, mode) as fout:
            json.dump(to_dump, fout)


def main():
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
    RECIPES = []
    for dirname, folders, files in os.walk(os.path.join(CURR_DIR, "recipes")):
        for f in files:
            RECIPES.append(os.path.join(CURR_DIR, dirname, f))
    for recipe in RECIPES:
        RecipeReader(recipe)

if __name__ == "__main__":
    main()
