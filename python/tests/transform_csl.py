
import json
import pytest
from fatcat_tools import *
from fatcat_client import *

from fixtures import api
from import_crossref import crossref_importer

def test_csl_crossref(crossref_importer):
    with open('tests/files/crossref-works.single.json', 'r') as f:
        # not a single line
        raw = json.loads(f.read())
        r = crossref_importer.parse_record(raw)
    # this work has some null contrib names; these should cause errors
    with pytest.raises(ValueError):
        release_to_csl(r)
    with pytest.raises(ValueError):
        csl = release_to_csl(r)
        citeproc_csl(csl, 'csl-json')
    # set with dummy so we can run other tests
    for c in r.contribs:
        if not c.raw_name:
            c.raw_name = "dummy"
    csl = release_to_csl(r)
    citeproc_csl(csl, 'csl-json')
    citeproc_csl(csl, 'bibtex')
    citeproc_csl(csl, 'harvard1')
    citeproc_csl(csl, 'harvard1', html=True)

def test_csl_pubmed(crossref_importer):
    with open('tests/files/example_releases_pubmed19n0972.json', 'r') as f:
        # multiple single lines
        for line in f:
            r = entity_from_json(line, ReleaseEntity)
            csl = release_to_csl(r)
            citeproc_csl(csl, 'csl-json')
            citeproc_csl(csl, 'bibtex')
            citeproc_csl(csl, 'harvard1')
            citeproc_csl(csl, 'harvard1', html=True)

def test_csl_pubmed_bibtex(crossref_importer):
    with open('tests/files/example_releases_pubmed19n0972.json', 'r') as f:
        r = entity_from_json(f.readline(), ReleaseEntity)
    csl = release_to_csl(r)
    print(citeproc_csl(csl, 'bibtex'))
    # XXX: what's with the '`' in volume?
    assert citeproc_csl(csl, 'bibtex').strip() == """
@article{mędrela-kuder_szymura_2018, 
  title={Selected anti-health behaviours among women with osteoporosis}, 
  volume={69`}, 
  ISSN={0035-7715}, 
  DOI={10.32394/rpzh.2018.0046}, 
  abstractNote={In the prevention of osteoporosis and its treatment, it is important to prevent bone loss by reducing the occurrence of factors determining human health, which reduce the risk of osteoporosis, such as health behaviors.}, 
  number={4}, 
  journal={Roczniki Panstwowego Zakladu Higieny}, 
  author={Mędrela-Kuder and Szymura}, 
  year={2018}}
    """.strip()
    assert citeproc_csl(csl, 'harvard1', html=True).strip() == """
    Mędrela-Kuder &amp; Szymura, 2018. Selected anti-health behaviours among women with osteoporosis. <i>Roczniki Panstwowego Zakladu Higieny</i>, 69`(4).
    """.strip()