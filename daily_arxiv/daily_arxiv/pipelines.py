# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import arxiv
import json
import os
import re
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
        # The material context is deliberately required.  Generic terms such
        # as "vacancy", "radiation", "DFT", or "molecular dynamics" alone
        # are too broad for this user's reading list.
        self.direct_material_topics = [
            "high-entropy carbide",
            "high entropy carbide",
            "refractory high-entropy carbide",
            "titazrnb",
            "titazrnbc",
            "flibe",
            "molten salt",
            "zirconium hydride",
            "zrh2",
            "hydride moderator",
            "hydrogen retention",
            "nuclear fuel",
            "fuel cladding",
        ]
        self.material_context_topics = self.direct_material_topics + [
            "nuclear material",
            "nuclear ceramic",
            "nuclear reactor material",
            "nuclear energy material",
            "nuclear energy materials",
            "ceramic fuel",
            "carbide ceramic",
            "actinide material",
            "uranium carbide",
            "thorium carbide",
        ]
        self.defect_topics = [
            "carbon vacancy",
            "vacancy ordering",
            "vacancy formation energy",
            "defect energetics",
            "defect evolution",
            "point defect",
            "irradiation damage",
            "radiation damage",
            "displacement cascade",
            "collision cascade",
            "primary knock-on atom",
            "ion implantation",
            "radiation-induced",
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
        self.transport_topics = [
            "ion diffusion",
            "ionic transport",
            "superionic transition",
            "hydrogen diffusion",
            "hydrogen transport",
        ]
        self.experimental_topics = [
            "experiment",
            "experimental",
            "synthesis",
            "characterization",
            "microstructure",
            "phase stability",
            "thermal conductivity",
            "mechanical properties",
            "neutron irradiation",
            "ion irradiation",
            "proton irradiation",
            "x-ray diffraction",
            "xrd",
            "transmission electron microscopy",
            "tem",
            "scanning electron microscopy",
            "sem",
        ]
        self.seen_ids = set()

    @staticmethod
    def _normalize(text):
        """Normalize words so matching does not create substring false positives."""
        text = re.sub(r"[^a-z0-9]+", " ", text.lower())
        return f" {text.strip()} "

    @classmethod
    def _has_any(cls, text, topics):
        return any(f" {cls._normalize(topic).strip()} " in text for topic in topics)

    def process_item(self, item: dict, spider):
        paper_id = item["id"]
        if paper_id in self.seen_ids:
            raise DropItem(f"Duplicate arXiv paper across categories: {paper_id}")
        self.seen_ids.add(paper_id)

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
            title_searchable = self._normalize(item.get("title", ""))
            searchable = self._normalize(" ".join([
                item.get("title", ""),
                item.get("summary", ""),
                " ".join(item.get("authors", [])),
            ]))
            if self.strict_research_profile:
                direct_material_in_title = self._has_any(
                    title_searchable, self.direct_material_topics
                )
                material_context_match = self._has_any(
                    searchable, self.material_context_topics
                )
                research_signal_match = (
                    self._has_any(searchable, self.defect_topics)
                    or self._has_any(searchable, self.method_topics)
                    or self._has_any(searchable, self.transport_topics)
                    or self._has_any(searchable, self.experimental_topics)
                )
                relevant = direct_material_in_title or (
                    material_context_match and research_signal_match
                )
            else:
                relevant = any(keyword in searchable for keyword in self.research_keywords)

            if not relevant:
                raise DropItem(
                    f"Not relevant to RESEARCH_KEYWORDS: {item.get('id', 'unknown')}"
                )

        return item
