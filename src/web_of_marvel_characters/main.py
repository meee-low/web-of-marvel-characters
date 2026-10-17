from collections.abc import Sequence

from .association import AssociationMeasure
from .examples import Examples
from .pipeline import run_pipeline
from .utils.ComicSeries import ComicSeries


def make_graph_from_zero(
    series_to_scrape: Sequence[ComicSeries],
    path: str = "results",
    title: str = "",
    scrape_from_wiki: bool = True,
    association_measure: AssociationMeasure | None = None,
) -> None:
    """Backward-compatible wrapper around the graph-building pipeline."""
    run_pipeline(
        series_to_scrape,
        output_root=path,
        title=title,
        scrape_from_wiki=scrape_from_wiki,
        association_measure=association_measure,
    )


def main() -> None:
    examples = Examples()
    make_graph_from_zero(
        examples.krakoa_era,
        title="Krakoa Era",
        scrape_from_wiki=False,
    )


if __name__ == "__main__":
    main()
