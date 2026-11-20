# Complete Blogger report import

Source: https://slugsreports.blogspot.com/. The 20 November 2026 import followed every link in **Blog Archive**, checked monthly post counts against the full Blogger feed, fetched each permalink, and copied all 28 post bodies plus 508 image resources. The result includes 19 monthly index pages and an all-reports index under `new/blog-reports`. Existing Events titles/dates/order and non-blog entries are preserved; blog destinations now point locally. Source links and attribution remain on each report. Scripts/iframes/forms and inline event handlers from the source are excluded.

The JSON report in `reports/blog-import-2026-11-20.json` records archive coverage, report URLs, content hashes, media origins/hashes and publication checks. Photographs stay on the NAS; Git contains HTML, tools and manifests. Media restoration/rebuild uses the existing repository scripts.

## Rebuild or audit this import

Use a separate work directory outside the repository. Install `requirements.txt` into a virtual environment. Supply these inputs there:

- `blog.html`: source blog homepage HTML (contains Blog Archive).
- `feed.json`: full JSON feed from `https://slugsreports.blogspot.com/feeds/posts/default?alt=json&max-results=500`.
- `events-before.html`: the exact live `/new/events.html` page before the import, backed up privately.
- `event-metadata.json`: copy the supplied event dates/titles. Event dates take precedence over publication dates in Events; month indexes reflect actual publication dates.

Then run:

```sh
python3 tools/blog-import/prepare.py --work-dir /path/to/work-directory
python3 tools/blog-import/validate.py --work-dir /path/to/work-directory
```

Preparation fetches every archive month and post, compares coverage with the feed, downloads images, and creates `staged/` plus `import-report.json`. Validation checks archive completeness, exact report text, unchanged Events entries and local references against staged output/the repository snapshot. No NAS files change in these two steps. The dates/titles catalog deliberately covers the known 28 posts: update and review it for future posts rather than silently guessing dates.

## Publication safeguards

`publish.py --work-dir /path/to/work-directory` uses the authorised `slugs-nas` SSH alias and rsync. It refuses if the live Events file differs from the supplied backup or `new/blog-reports` already exists. It uploads only the new report directory, checks all uploaded hashes, rechecks Events, and atomically replaces Events. It then requests every imported page/image over public HTTPS and records results. It does not write outside `/volume1/web/slugs/new`. Retain the Events backup for recovery.

This is the initial-import publisher, not an overwrite/synchronisation command. For later refreshes, review live editor changes and adapt the destination/update plan explicitly; do not delete the existing report directory or bypass its safety checks. Network failures stop publication/verification and are reported. A failed public check does not automatically roll back an already successful publication; inspect the live result before retrying.

Archive HTML and media paths are recorded in the repository manifests. Do not regenerate a manifest from a partial checkout in a way that discards NAS-only images.
