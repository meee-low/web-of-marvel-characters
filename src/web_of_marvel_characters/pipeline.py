from pathlib import Path
from collections.abc import Sequence

import pandas as pd

from .association import AssociationMeasure, calculate_associations
from .utils import parse_issues, prepare_edges, process_appearances, scrape, visualization
from .utils.ComicSeries import ComicSeries


def run_pipeline(
    series_to_scrape: Sequence[ComicSeries],
    *,
    output_root: Path | str = "results",
    title: str = "",
    scrape_from_wiki: bool = True,
    association_measure: AssociationMeasure | None = None,
) -> None:
    """Build appearance data, a character network, and an HTML visualization.

    ``association_measure`` receives the weighted appearance DataFrame from
    ``build_weights_df``. That DataFrame contains one character per row, the
    character name in its first column, and one numeric issue column per
    remaining column. The callable must return a square character-by-character
    DataFrame with matching row and column labels. When omitted, the existing
    Pearson association is used.
    """
    if not series_to_scrape:
        raise ValueError("At least one comic series is required")

    if not title:
        first_series = series_to_scrape[0]
        title = f"{first_series.title} Vol {first_series.volume}"

    output_root = Path(output_root)
    project_dir = output_root / title
    data_dir = project_dir / "data"
    output_dir = project_dir / "output"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    appearances_path = data_dir / "table_of_appearances.csv"
    if scrape_from_wiki:
        issue_list = scrape.build_full_list_of_issues(list(series_to_scrape))
        print("Scraping...")
        appearances = parse_issues.build_full_table(issue_list, path=str(appearances_path))
        appearances.to_csv(appearances_path, index=False)
    else:
        appearances = pd.read_csv(appearances_path)

    print("Counting appearances...")
    character_stats = process_appearances.count_types_of_appearances(appearances)
    character_stats.to_csv(data_dir / "character_stats.csv", index=False)

    print("Dropping characters with too few appearances...")
    appearances = process_appearances.filter_less_frequent_characters(
        appearances,
        character_stats,
        min_number_of_appearances=2,
        top_n_characters=200,
        character_percentile=0.5,
    )

    print("Calculating correlations...")
    weights = prepare_edges.build_weights_df(appearances)
    if association_measure is None:
        associations = calculate_associations(weights)
    else:
        associations = calculate_associations(weights, association_measure)

    print("Listing edges...")
    edge_list = prepare_edges.build_edge_list(associations)
    edge_list.to_csv(data_dir / "edge_list.csv", index=False)

    print("Filtering edges...")
    edges_to_graph = prepare_edges.filter_edges(edge_list, 0.5, 0.2, 3)
    edges_to_graph.to_csv(data_dir / "edges_filtered.csv", index=False)

    graph = visualization.make_nx_graph(edges_to_graph)
    print("Partitioning graph into communities...")
    visualization.set_graph_attributes(graph, character_stats)

    print("Building graph visualization...")
    visualization.show_graph(graph, save_path=output_dir, title=title)