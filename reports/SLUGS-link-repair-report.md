# SLUGS /new link repairs — 14 November 2026

Only `/volume1/web/slugs/new` was edited. All 10,268 original files outside `/new` were verified unchanged using SHA-256 checksums.

- Scanned all 2,138 existing HTML pages and their 53,598 HTML references, plus CSS image references.
- Published and checksum-verified 164 repaired or added files.
- Repaired archive paths, malformed links, email links and missing section references. Recovered 116 references to existing archive files.
- Rebuilt the missing 1975 Yorkshire Dales slide 021 page around its existing photograph.
- Removed obsolete missing editor metadata and one missing decorative CSS image reference.
- Missing original files/images are labelled unavailable. No replacement historical content was invented.
- Tested 606 distinct external HTTP(S) addresses. Dead destinations are labelled unavailable, keeping their original address in the page markup. Verified HTTPS equivalents were adopted. Five inconclusive results were restored as links.
- Final HTTP checks passed for all 7,891 tested local destinations, including every changed file. Initial timeouts passed on retry.

External timeouts, certificate problems and access-blocked destinations remain unverified. FTP/Gopher links, arbitrary JavaScript-generated URLs and form submissions were not comprehensively tested.

The repairs are live at [the new website](https://slugs.granvillehouse.synology.me/new/). Detailed checks and changes are in `SLUGS-link-repair-details.json`. The pre-repair snapshot is retained locally under `work/link-audit/`; no backup was exposed on the public website.

These are repairs to the current `/new` copy. Rebuilding it from the untouched originals will require reapplying the repairs.
