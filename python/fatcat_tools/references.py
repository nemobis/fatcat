"""
Helper routines for working with the fatcat citation graph, which is a separate
index of reference links between works in the main catalog.

See bulk citation and citation API proposals for design documentation.
"""

import sys
import datetime
import argparse
from typing import Optional, List, Any, Dict, Union

from pydantic import BaseModel
import elasticsearch
from elasticsearch_dsl import Search
from fatcat_openapi_client import ReleaseEntity

from fatcat_tools import public_api
from fatcat_tools.transforms.access import release_access_options, AccessOption


class BiblioRef(BaseModel):
    """bibliographic reference"""
    # ("release", source_release_ident, ref_index)
    # ("wikipedia", source_wikipedia_article, ref_index)
    _key: Optional[str]
    update_ts: Optional[datetime.datetime]

    # metadata about source of reference
    source_release_ident: Optional[str]
    source_work_ident: Optional[str]
    # with lang prefix like "en:Superglue"
    source_wikipedia_article: Optional[str]
    source_release_stage: Optional[str]
    source_year: Optional[int]

    # context of the reference itself
    # 1-indexed, not 0-indexed
    ref_index: Optional[int] # TODO: actually optional?
    # eg, "Lee86", "BIB23"
    ref_key: Optional[str]
    # eg, page number
    ref_locator: Optional[str]

    # target of reference (identifiers)
    target_release_ident: Optional[str]
    target_work_ident: Optional[str]
    target_openlibrary_work: Optional[str]
    # TODO: target_url_surt: Optional[str]
    # would not be stored in elasticsearch, but would be auto-generated by all "get" methods from the SURT, so calling code does not need to do SURT transform
    target_url: Optional[str]

    # crossref, pubmed, grobid, etc
    match_provenance: Optional[str]
    # strong, weak, etc
    match_status: Optional[str]
    # TODO: "match_strength"?
    # "doi", "isbn", "fuzzy title, author", etc
    # maybe "fuzzy-title-author"?
    match_reason: Optional[str]

    # only if no release_ident link/match
    target_unstructured: Optional[str]
    target_csl: Optional[Dict[str, Any]]

    def hacks(self):
        """
        Temporary (?) hacks to work around schema/data issues
        """
        if self.target_openlibrary_work and self.target_openlibrary_work.startswith("/works/"):
            self.target_openlibrary_work = self.target_openlibrary_work[7:]

        # work-arounds for bad/weird ref_key
        if self.ref_key:
            self.ref_key = self.ref_key.strip()
            if self.ref_key[0] in ['/', '_']:
                self.ref_key = self.ref_key[1:]
            if self.ref_key.startswith("10.") and 'SICI' in self.ref_key and '-' in self.ref_key:
                self.ref_key = self.ref_key.split('-')[-1]
            if self.ref_key.startswith("10.") and '_' in self.ref_key:
                self.ref_key = self.ref_key.split('_')[-1]
            if len(self.ref_key) > 10 and "#" in self.ref_key:
                self.ref_key = self.ref_key.split('#')[-1]
            if len(self.ref_key) > 10 and "_" in self.ref_key:
                self.ref_key = self.ref_key.split('_')[-1]
        if not self.ref_key and self.ref_index is not None:
            self.ref_key = str(self.ref_index)
        return self


class EnrichedBiblioRef(BaseModel):
    # enriched version of BiblioRef with complete ReleaseEntity object as
    # fetched from the fatcat API. CSL-JSON metadata would be derived from
    # the full release entity.
    ref: BiblioRef
    release: Optional[ReleaseEntity]
    # TODO: openlibrary work?
    access: List[AccessOption]

    class Config:
        arbitrary_types_allowed = True


class RefHits(BaseModel):
    count_returned: int
    count_total: int
    offset: int
    limit: int
    query_time_ms: int
    query_wall_time_ms: int
    result_refs: List[Union[BiblioRef,EnrichedBiblioRef]]


def _execute_ref_query(search: Any, limit: int, offset: Optional[int] = None) -> RefHits:
    """
    Internal helper for querying elasticsearch refs index and transforming hits
    """

    limit = min((int(limit or 15), 200))
    if not offset or offset < 0:
        offset = 0

    search = search.params(track_total_hits=True)
    search = search[offset : (offset + limit)]

    query_start = datetime.datetime.now()
    try:
        resp = search.execute()
    except elasticsearch.exceptions.RequestError as e_raw:
        # this is a "user" error
        e: Any = e_raw
        #logging.warn("elasticsearch 400: " + str(e.info))
        if e.info.get("error", {}).get("root_cause", {}):
            raise ValueError(str(e.info["error"]["root_cause"][0].get("reason"))) from e
        else:
            raise ValueError(str(e.info)) from e
    except elasticsearch.exceptions.TransportError as e:
        # all other errors
        #logging.warn(f"elasticsearch non-200 status code: {e.info}")
        raise IOError(str(e.info)) from e
    query_delta = datetime.datetime.now() - query_start

    result_refs = []
    for h in resp.hits:
        # might be a list because of consolidation
        if isinstance(h._d_.get('source_work_ident'), list):
            h._d_['source_work_ident'] = h._d_['source_work_ident'][0]
        result_refs.append(BiblioRef.parse_obj(h._d_).hacks())

    return RefHits(
        count_returned=len(result_refs),
        # ES 7.x style "total"
        count_total=resp.hits.total.value,
        offset=offset,
        limit=limit,
        query_time_ms=int(resp.took),
        query_wall_time_ms=int(query_delta.total_seconds() * 1000),
        result_refs=result_refs,
    )


def get_outbound_refs(
    es_client: Any,
    release_ident: Optional[str] = None,
    work_ident: Optional[str] = None,
    wikipedia_article: Optional[str] = None,
    limit: int = 100,
    offset: Optional[int] = None,
    es_index: str = "fatcat_ref",
) -> RefHits:

    search = Search(using=es_client, index=es_index)

    if release_ident:
        search = search.filter("term", source_release_ident=release_ident)
    elif work_ident:
        search = search.filter("term", source_work_ident=work_ident)
    elif wikipedia_article:
        search = search.filter("term", source_wikipedia_article=wikipedia_article)
    else:
        raise ValueError("require a lookup key")

    search = search.sort("ref_index")

    # re-sort by index
    hits = _execute_ref_query(search, limit=limit, offset=offset)
    hits.result_refs = sorted(hits.result_refs, key=lambda r: r.ref_index or 0)
    return hits


def get_inbound_refs(
    es_client: Any,
    release_ident: Optional[str] = None,
    work_ident: Optional[str] = None,
    openlibrary_work: Optional[str] = None,
    url: Optional[str] = None,
    consolidate_works: bool = True,
    filter_stage: List[str] = [],
    sort: Optional[str] = None,
    limit: int = 25,
    offset: Optional[int] = None,
    es_index: str = "fatcat_ref",
) -> List[BiblioRef]:

    search = Search(using=es_client, index=es_index)

    if consolidate_works:
        search = search.extra(
            collapse={
                "field": "source_work_ident",
                "inner_hits": {"name": "source_more", "size": 0,},
            }
        )

    if release_ident:
        search = search.filter("term", target_release_ident=release_ident)
    elif work_ident:
        search = search.filter("term", target_work_ident=work_ident)
    elif openlibrary_work:
        search = search.filter("term", target_openlibrary_work=openlibrary_work)
    else:
        raise ValueError("require a lookup key")

    if filter_stage:
        search = search.filter("term", source_stage=filter_stage)

    if sort == "newest":
        search = search.sort("-source_year")
    elif sort == "oldest":
        search = search.sort("source_year")
    else:
        search = search.sort("-source_year")

    return _execute_ref_query(search, limit=limit, offset=offset)


def count_inbound_refs(
    es_client: Any,
    release_ident: Optional[str] = None,
    work_ident: Optional[str] = None,
    openlibrary_work: Optional[str] = None,
    url: Optional[str] = None,
    filter_stage: List[str] = [],
    es_index: str = "fatcat_ref",
) -> int:
    """
    Same parameters as get_inbound_refs(), but returns just a count
    """

    search = Search(using=es_client, index=es_index)

    if release_ident:
        search = search.filter("term", target_release_ident=release_ident)
    elif work_ident:
        search = search.filter("term", target_work_ident=work_ident)
    elif openlibrary_work:
        search = search.filter("term", target_openlibrary_work=openlibrary_work)
    else:
        raise ValueError("require a lookup key")

    if filter_stage:
        search = search.filter("term", source_stage=filter_stage)

    return search.count()


# run fatcat API fetches for each ref and return "enriched" refs
def enrich_inbound_refs(refs: List[BiblioRef], fatcat_api_client: Any, hide: Optional[str] = "refs", expand: Optional[str] = "container,files,webcaptures,filesets") -> List[EnrichedBiblioRef]:
    enriched = []
    for ref in refs:
        if ref.source_release_ident:
            release = fatcat_api_client.get_release(ref.source_release_ident, hide=hide, expand=expand)
            enriched.append(EnrichedBiblioRef(
                ref=ref,
                #csl=None,
                access=release_access_options(release),
                release=release,
            ))
        else:
            enriched.append(EnrichedBiblioRef(
                ref=ref,
                #csl=None,
                access=[],
                release=None,
            ))
    return enriched


def enrich_outbound_refs(refs: List[BiblioRef], fatcat_api_client: Any, hide: Optional[str] = "refs", expand: Optional[str] = "container,files,webcaptures,filesets") -> List[EnrichedBiblioRef]:
    enriched = []
    for ref in refs:
        if ref.target_release_ident:
            release = fatcat_api_client.get_release(ref.target_release_ident, hide=hide, expand=expand)
            enriched.append(EnrichedBiblioRef(
                ref=ref,
                access=release_access_options(release),
                release=release,
            ))
        else:
            enriched.append(EnrichedBiblioRef(
                ref=ref,
                access=[],
                release=None,
            ))
    return enriched


def run_ref_query(args) -> None:
    """
    CLI helper/debug tool (prints to stdout)
    """
    release_ident = None
    work_ident = None
    if args.ident.startswith("release_"):
        release_ident = args.ident.split('_')[1]
    elif args.ident.startswith("work_"):
        work_ident = args.ident.split('_')[1]
    else:
        release_ident = args.ident

    print("## Outbound References")
    hits = get_outbound_refs(release_ident=release_ident, work_ident=work_ident, es_client=args.es_client)
    print(f"Total: {hits.count_total}  Time: {hits.query_wall_time_ms}ms; {hits.query_time_ms}ms")

    if args.enrich == "fatcat":
        enriched = enrich_outbound_refs(hits.result_refs, hide='refs,abstracts', fatcat_api_client=args.fatcat_api_client)
        for ref in enriched:
            if ref.release:
                print(f"{ref.ref.ref_index or '-'}\trelease_{ref.release.ident}\t{ref.ref.match_provenance}/{ref.ref.match_status}\t{ref.release.release_year or '-'}\t{ref.release.title}\t{ref.release.ext_ids.pmid or ref.release.ext_ids.doi or '-'}")
            else:
                print(f"{ref.ref.ref_index or '-'}\trelease_{ref.target_release_ident}")
    else:
        for ref in hits.result_refs:
            print(f"{ref.ref.ref_index or '-'}\trelease_{ref.target_release_ident}")

    print()
    print("## Inbound References")
    hits = get_inbound_refs(release_ident=release_ident, work_ident=work_ident, es_client=args.es_client)

    print(f"Total: {hits.count_total}  Time: {hits.query_wall_time_ms}ms; {hits.query_time_ms}ms")

    if args.enrich == "fatcat":
        enriched = enrich_inbound_refs(hits.result_refs, hide='refs,abstracts', fatcat_api_client=args.fatcat_api_client)
        for ref in enriched:
            if ref.release:
                print(f"release_{ref.release.ident}\t{ref.ref.match_provenance}/{ref.ref.match_status}\t{ref.release.release_year or '-'}\t{ref.release.title}\t{ref.release.ext_ids.pmid or ref.release.ext_ids.doi or '-'}")
            else:
                print(f"release_{ref.target_release_ident}")
    else:
        for ref in hits.result_refs:
            print(f"work_{ref.source_work_ident}\trelease_{ref.source_release_ident}")

def main() -> None:
    """
    Run this utility like:

        python -m fatcat_tools.references

    Examples:

        python -m fatcat_tools.references query release_pfrind3kh5hqhgqkueulk2tply
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers()

    parser.add_argument("--fatcat-api-base", default="https://api.fatcat.wiki/v0")
    parser.add_argument("--elasticsearch-base", default="https://search.fatcat.wiki")
    parser.add_argument("--elasticsearch-ref-index", default="fatcat_ref")

    sub = subparsers.add_parser(
        "query",
        help="takes a fatcat ident argument, prints both inbound and outbound references",
    )
    sub.set_defaults(func="run_ref_query")
    sub.add_argument("ident", type=str)
    sub.add_argument("--enrich", type=str)

    args = parser.parse_args()
    if not args.__dict__.get("func"):
        parser.print_help(file=sys.stderr)
        sys.exit(-1)

    args.es_client = elasticsearch.Elasticsearch(args.elasticsearch_base)
    args.fatcat_api_client = public_api(args.fatcat_api_base)

    if args.func == "run_ref_query":
        run_ref_query(args)
    else:
        raise NotImplementedError(args.func)

if __name__ == "__main__":
    main()
