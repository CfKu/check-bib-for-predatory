# check-bib-for-predatory
check-predatory - Double-check your bibliography (BibTeX, bib) for predatory publishers and journals

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

## License
This project is licensed under the Beerware License - see the [LICENSE](LICENSE) file for details.
