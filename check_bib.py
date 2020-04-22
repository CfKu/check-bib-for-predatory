#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © by Christof Küstner
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE"
# wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.
# Christof Küstner
# ----------------------------------------------------------------------------

"""
@author: CfK
"""

# Prepare for Python3 (if called in Python2)
from __future__ import (
    absolute_import, division, print_function, unicode_literals)


# =============================================================================
# IMPORT
# =============================================================================
import argparse
import requests
import re
import csv
import html
import lxml
import lxml.html
import unicodedata
import os
from tqdm import tqdm
from pybtex.database.input import bibtex
import colorama

# LOCAL IMPORT
from check_bib_helpers import print_title, print_colored_status, \
    print_report, get_cache_csv, get_cosine_sim_score

# =============================================================================
# CONSTANTS USER
# =============================================================================
SIMILARITY_THRESHOLDS = (0.7, 0.75, 0.8)
PREDATORY_SOURCES = {
    # {URL: (LXML-ETREE-ELEMENTS, ELEMENT-REGEX, [BIB-FIELDS,]}
    r"https://predatoryjournals.com/journals/":
        (
            r"//li[not(@id) and not(@class)]",
            r"./a/@href",
            ["journal", "journaltitle", "booktitle"]
        ),
    r"https://predatoryjournals.com/hijacked/":
        (
            r"//td[not(@id) and not(@class)]",
            r"./a/@href",
            ["journal", "journaltitle", "booktitle"]
        ),
    r"https://predatoryjournals.com/publishers/":
        (
            r"//li[not(@id) and not(@class)]",
            r"./a/@href",
            ["publisher"]
        ),  
    r"https://beallslist.net/":
        (
            r"//li[not(@id) and not(@class)]",
            r"./a/@href",
            ["publisher"]
        ),
    r"https://beallslist.net/standalone-journals/":
        (
            r"//li[not(@id) and not(@class)]",
            r"./a/@href",
            ["journal", "journaltitle", "booktitle"]
        ),
}
# =============================================================================
# CONSTANTS APP
# =============================================================================
RE_LATEX_COMMANDS_STRIP = re.compile(r"\\[^\s]*{(.*?)}")
RE_HTML_COMMANDS_STRIP = re.compile(r"<[^>]+>")


# =============================================================================
# DEFINITION
# =============================================================================
def crawl_predatory_sources():
    print_colored_status(
        "Crawl and cache predatory journals and publishers from given URLs", 1)
    for source_url, (source_pj_element, source_pj_url, _) in PREDATORY_SOURCES.items():
        cache_csv_filename = get_cache_csv(source_url)
        with open(cache_csv_filename, mode="w") as cache_file:
            # prepare cache CSV
            cache_writer = csv.writer(
                cache_file, delimiter=",", quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            # get html code of source url
            r = requests.get(source_url)
            if r.status_code == 200:  # succeeded
                pj_counter = 0
                tqdm_desc = "  + '{}'".format(source_url)
                # crawl predatory journals names, urls, and short names
                html_tree = lxml.html.fromstring(r.content)
                pj_elements = html_tree.xpath(source_pj_element)
                for pj_element in tqdm(pj_elements, desc=tqdm_desc, unit=""):
                    # element_text = lxml.etree.tostring(
                    #    element).decode().strip()
                    pj_urls = pj_element.xpath(source_pj_url)
                    if pj_urls and pj_urls[0].startswith("http"):
                        pj_name = unicodedata.normalize(
                            "NFKD", pj_element.text_content())
                        pj_url = pj_urls[0]
                        cache_row = [pj_name, pj_url]
                        # add pj to csv
                        pj_counter += 1
                        cache_writer.writerow(cache_row)

                print("  => Crawled {} journals/"
                      "publishers.".format(pj_counter))
    print()


def check_bibliography(bib_file):
    print_colored_status(
        "Read predatory journals and publishers from local CSV cache", 1)
    # 1: create index of predatory journals / publishers
    idx_pj = {}
    for source_url, (_, _, compare_fields) in PREDATORY_SOURCES.items():
        cache_csv_filename = get_cache_csv(source_url)

        with open(cache_csv_filename, mode="r") as cache_file:
            cache_reader = csv.reader(cache_file,
                                      delimiter=",", quotechar='"')
            # create indexes including compare_fields (names)
            # to be double-checked
            for row in cache_reader:
                pj_name, pj_url = row
                idx_pj[pj_name.lower()] = [pj_name, pj_url, compare_fields]
    print("   > Added {} unique predatory journals/publishers "
          "to index.".format(len(idx_pj)))
    print()

    print_colored_status("Compare predatory index with bib-file entries", 1)
    # 2: compare index items with bib file
    parser = bibtex.Parser()
    bib = parser.parse_file(bib_file)
    # iterate over every bib item in bib_file
    report = {}
    for bib_key in tqdm(bib.entries.keys(), unit="keys",
                        desc="Double-check bib keys"):
        # get all filed names of bib_key entry
        bib_fields = bib.entries[bib_key].fields.keys()
        # compare required fields with predatory journals/publishers in index
        for _, (pj_name, pj_url, compare_fields) in idx_pj.items():
            for bib_field in bib_fields:
                # check if field needs to be double-checked
                if bib_field.lower() not in compare_fields:
                    continue

                # get value/content of field to be double-checked
                bib_entry = bib.entries[bib_key].fields[bib_field]
                # strip latex special characters
                bib_entry = RE_LATEX_COMMANDS_STRIP.sub(r"\1", bib_entry)
                bib_entry = bib_entry.replace(r"\&", r"&")

                # compute score
                similarity_score = get_cosine_sim_score(
                    bib_entry.lower(), pj_name.lower())[0][1]

                # add to report if score is over smallest given threshold
                thr0 = SIMILARITY_THRESHOLDS[0]
                if (thr0 <= similarity_score):
                    # prepare report dict (if required)
                    if bib_key not in report:
                        report[bib_key] = {}
                    if bib_field not in report[bib_key]:
                        report[bib_key][bib_field] = (bib_entry, [])
                    # add new match
                    report[bib_key][bib_field][1].append([
                        similarity_score,
                        pj_name,
                        pj_url
                    ])

    # print report
    print()
    print_colored_status("Report", 1)
    print_report(report, SIMILARITY_THRESHOLDS)


def main():
    # ---------------------------------------------------------- PRE PROCESSING
    # define cli options
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("bib_file", type=argparse.FileType("r"),
                            help=("BibTeX file to be double-checked"))
    cli_parser.add_argument("--refresh", action="store_true", default=False,
                            help=("Refresh the local predatory CSV cache"))
    # parse cli options
    cli_args = cli_parser.parse_args()

    # -------------------------------------------------------------- PROCESSING
    print_title("Double-check bibliography (BibTeX, bib) for predatory "
                "publishers and journals", "CfK", "~", 120)
    print()

    # crawl given sources (if required)
    if cli_args.refresh:
        crawl_predatory_sources()
    # check bibliography
    check_bibliography(cli_args.bib_file)


if __name__ == '__main__':
    main()
