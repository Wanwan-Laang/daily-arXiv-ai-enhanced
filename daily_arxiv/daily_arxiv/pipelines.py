# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import arxiv
import json
import os
import sys
from datetime import datetime, timedelta
from scrapy.exceptions import DropItem


class DailyArxivPipeline:
    def __init__(self):
        self.page_size = 100
        self.client = arxiv.Client(self.page_size)
        raw_keywords = os.environ.get("RESEARCH_KEYWORDS", "")
        self.research_keywords = [
            keyword.strip().lower()
            for keyword in raw_keywords.split(",")
            if keyword.strip()
        ]
        self.strict_research_profile = os.environ.get(
            "RESEARCH_STRICT_PROFILE", "0"
        ).lower() in {"1", "true", "yes"}
        self.specific_topics = [
            "high-entropy carbide",
            "high entropy carbide",
            "refractory high-entropy carbide",
            "titazrnb",
            "carbon vacancy",
            "vacancy ordering",
            "vacancy formation energy",
            "flibe",
            "molten salt",
            "zirconium hydride",
            "zrh2",
            "hydride moderator",
            "hydrogen retention",
            "irradiation damage",
            "radiation damage",
            "displacement cascade",
            "collision cascade",
            "primary knock-on atom",
            "nuclear fuel",
        ]
        self.method_topics = [
            "machine-learning interatomic potential",
            "machine learned interatomic potential",
            "interatomic potential",
            "deepmd",
            "deepmd-kit",
            "mlip",
            "neural network potential",
            "graph neural network",
            "active learning",
            "density functional theory",
            "first-principles",
            "aimd",
            "molecular dynamics",
            "lammps",
        ]
        self.application_topics = [
            "defect energetics",
            "defect evolution",
            "point defect",
            "microstructure",
            "vacancy",
            "irradiation",
            "radiation",
            "ion diffusion",
            "ionic transport",
            "superionic",
            "ceramic",
            "carbide",
            "hydride",
            "nuclear material",
            "nuclear fuel",
        ]

    def process_item(self, item: dict, spider):
        item["pdf"] = f"https://arxiv.org/pdf/{item['id']}"
        item["abs"] = f"https://arxiv.org/abs/{item['id']}"
        search = arxiv.Search(
            id_list=[item["id"]],
        )
        paper = next(self.client.results(search))
        item["authors"] = [a.name for a in paper.authors]
        item["title"] = paper.title
        item["categories"] = paper.categories
        item["comment"] = paper.comment
        item["summary"] = paper.summary

        # Optional local relevance filter.  It is applied after retrieving the
        # title/abstract but before the LLM enhancement step, so unrelated
        # papers do not consume local API time or tokens.
        if self.research_keywords:
            searchable = " ".join([
                item.get("title", ""),
                item.get("summary", ""),
                " ".join(item.get("authors", [])),
            ]).lower()
            if self.strict_research_profile:
                specific_match = any(
                    keyword in searchable for keyword in self.specific_topics
                )
                method_match = any(
                    keyword in searchable for keyword in self.method_topics
                )
                application_match = any(
                    keyword in searchable for keyword in self.application_topics
                )
                relevant = specific_match or (method_match and application_match)
            else:
                relevant = any(keyword in searchable for keyword in self.research_keywords)

            if not relevant:
                raise DropItem(
                    f"Not relevant to RESEARCH_KEYWORDS: {item.get('id', 'unknown')}"
                )

        return item
