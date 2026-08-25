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
            if not any(keyword in searchable for keyword in self.research_keywords):
                raise DropItem(
                    f"Not relevant to RESEARCH_KEYWORDS: {item.get('id', 'unknown')}"
                )

        return item
