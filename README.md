# web-of-marvel-characters
A database of Marvel characters + some visualizations tools.
 
Data scraped from https://marvel.fandom.com/wiki/

Inpired by [Thu Vu's similar project](https://github.com/thu-vu92/the_witcher_network) and videos on The Witcher. 

<hr>

### X-Men Characters during the Claremont years:
![Graph of X-Men Characters during the Claremont years](results/Claremont%20X-Comics/output/screenshot.png)

Link to the interactive graph: [link](https://meee-low.github.io/web-of-marvel-characters/results/Claremont%20X-Comics/output/X-Men_2022-07-26-23-10-49_n200-e890)


## Packages used:
- numpy
- pandas
- bs4
- requests
- networkx
- python-louvain
- pyvis

## Instructions:
1. Clone the repo
2. Use Python 3.13 or newer and install the project environment with `uv sync`.
3. Run `uv run web-of-marvel-characters`, changing the parameters in `main()` when needed.

To work with the X-Men showcase notebook, open `showcase - x-men.ipynb` in VS Code and select the `.venv` Python environment, or start Jupyter with `uv run jupyter lab`.