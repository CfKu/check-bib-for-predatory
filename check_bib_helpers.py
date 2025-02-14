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

# =============================================================================
# IMPORT
# =============================================================================
import platform
import colorama
import re
import urllib.parse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


# =============================================================================
# CONST
# =============================================================================
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    colorama.init()


# =============================================================================
# DEFINITION
# =============================================================================
def print_title(app_title, app_author, filler, terminal_size):
    title = " "
    title += colorama.Style.BRIGHT + app_title + colorama.Style.RESET_ALL
    title += " by "
    title += colorama.Style.BRIGHT + app_author + colorama.Style.RESET_ALL
    title += " " + 3*filler
    print(title.rjust(terminal_size, filler) + colorama.Style.RESET_ALL)
    print()


def print_colored_status(text, status_color_id=0):
    # status to color store
    COLORS = (colorama.Fore.RED + colorama.Style.BRIGHT,
              colorama.Fore.GREEN + colorama.Style.BRIGHT,
              colorama.Fore.YELLOW + colorama.Style.BRIGHT)

    # print colored status
    if status_color_id < len(COLORS):
        if status_color_id == 0:
            print(COLORS[status_color_id] + ">>> " +
                  text + colorama.Style.RESET_ALL)
        else:
            print(COLORS[status_color_id] + ">>> " +
                  colorama.Style.RESET_ALL + text)
    else:
        print(text)


def get_cache_csv(url):
    return r"predatory_cache_{}.csv".format(urllib.parse.quote(url, safe=""))

def highlight_similarity(hl_words, sentence):
    re_from = r"(" + r"|".join(hl_words.replace(r"(", r"\(").
                               replace(r")", r"\)").split(" ")) + r")"
    re_to = colorama.Fore.LIGHTCYAN_EX + r"\1" + colorama.Style.RESET_ALL
    return re.sub(re_from, re_to, sentence)


def get_jaccard_sim_score(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


def get_vectors(*strs):
    text = [t for t in strs]
    vectorizer = CountVectorizer()
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()


def get_cosine_sim_score(*strs):
    vectors = [t for t in get_vectors(*strs)]
    return cosine_similarity(vectors)


def score_color(score, thresholds):
    thr0, thr1, thr2 = thresholds
    if thr0 <= score < thr1:
        return colorama.Fore.YELLOW
    elif thr1 <= score < thr2:
        return colorama.Fore.LIGHTRED_EX + \
            colorama.Style.BRIGHT
    else:
        return colorama.Back.RED + colorama.Fore.BLACK


def print_report(report, thresholds):
    for bib_key, bib_matches in report.items():
        # report bib_key
        print("Similarites found in '{}{}{}':".format(
            colorama.Back.WHITE + colorama.Fore.BLACK,
            bib_key,
            colorama.Style.RESET_ALL
        ))
        for bib_field, (bib_entry, pj_matches) in bib_matches.items():
            # report bib_field
            print("   {} : {}{}{}".format(
                bib_field.rjust(15, " "),
                colorama.Fore.WHITE + colorama.Style.BRIGHT,
                bib_entry,
                colorama.Style.RESET_ALL
            ))
            # print match
            for similarity_score, pj_name, pj_url in \
                    sorted(pj_matches, reverse=True):
                print("   {}{}{:.2f}{} | {} >> URL:{}".format(
                    " " * (15 - 4),
                    score_color(similarity_score, thresholds),
                    similarity_score,
                    colorama.Style.RESET_ALL,
                    highlight_similarity(
                        bib_entry, pj_name.ljust(100, " ")),
                    pj_url
                ))
