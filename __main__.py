"""Main function for the recipe package"""
import argparse
import os
import rconverter
import rparser


CONVERTERS = {
    "md": rconverter.MarkdownConverter,
    "html": rconverter.HTMLConverter,
    "tex": rconverter.LaTeXConverter,
}


def main(conv=rconverter.HTMLConverter):
    """Converts the recipes in the 'recipes' folder in this directory"""
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
    RECIPES = []
    for dirname, folders, files in os.walk(os.path.join(CURR_DIR, "recipes")):
        for f in files:
            RECIPES.append(os.path.join(CURR_DIR, dirname, f))
    for recipe in RECIPES:
        conversion = rparser.RecipeReader(recipe)
        convert = conv(conversion.recipe_info)
        convert.save_output()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--converter", default="html",
                        help="Output type {%s}" % "|".join(CONVERTERS.keys()))
    args = parser.parse_args()
    if args.converter in CONVERTERS:
        main(conv=CONVERTERS[args.converter])
    else:
        print("Invalid converter type '{0}'; must be in {{{1}}}".format(
            args.converter, "|".join(CONVERTERS.keys())
        ))
