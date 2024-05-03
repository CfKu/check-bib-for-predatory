# check-bib-for-predatory
Double-check your bibliography (BibTeX, bib) for predatory publishers and journals

## Why?
In order to ensure that no articles from predatory journals or publishers are cited, the tool compares the well-known predatory journals and publishers with your bibliography (BibTeX file). The titles in your bib file are compared with the well-known titles of the predatory journals based on [cosine similarity score](https://en.wikipedia.org/wiki/Cosine_similarity). 

## Getting Started

### Dependencies

* [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)

### Requirements

* Install 'predatory' environment from [environment.yml](environment.yml)
```bash
# Install 'predatory' environment from environment.yml 
$ conda env create -n predatory -f environment.yml
```

### Minimal example
```bash
# Activate 'predatory' environment
$ conda activate predatory
$ python check-bib.py bib-file-to-be-checked.bib
[...]

# Refresh the local predatory journal cache before checking (! local cache will be overwritten)
$ python check-bib.py bib-file-to-be-checked.bib --refresh
[...]
```
![screenshot_check_bib](https://user-images.githubusercontent.com/8809455/63655910-274aae80-c78e-11e9-8b41-68097bee08dd.png)

## Sources for predatory journals and publishers used

* https://beallslist.net/
* https://beallslist.net/standalone-journals/

Possible enhancements:
* CSV files in https://github.com/stop-predatory-journals/stop-predatory-journals.github.io/tree/master/_data (instead of crawling)

Feel free to extend it.

## Disclaimer

The used sources might not be complete. So in case you use this tool, make sure to use an up to date predatory journal repository.

## License
This project is licensed under the terms of the MIT license - see the [LICENSE](LICENSE) file for details.
