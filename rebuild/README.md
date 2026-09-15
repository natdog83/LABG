# LABG website recovery and WordPress development starter

This is a public-content recovery, not a WordPress database backup or a recovered Enfold PHP codebase. The original portal goal remains in `../dist/index.html` and its README. No live site, DNS, GitHub Pages deployment, member data, or payments have been modified.

## What is included

- `archive/public/`: unchanged successful public responses: HTML, REST JSON, CSS, JavaScript, media and fonts. Treat HTML here as archival evidence, not the safe preview.
- `archive/manifest.json`: URL, response type, byte count, SHA-256 and errors. `pending.json` lists any unfinished capture targets.
- `generated/preview/`: local, inert visual recovery. Live scripts and forms are disabled. Images and captured styles are served locally.
- `generated/pages.json`: rendered page bodies and styling for the WordPress importer.
- `wordpress/theme/`: newly written recovery theme, **not Enfold or its child-theme PHP**.
- `wordpress/import.php`: repeatable WP-CLI importer matching pages by source URL, preserving captured URLs through source-URL routing and retaining parent relationships where parents were captured.
- `compose.yaml`: local WordPress/database starter; requires Docker. Bind address is localhost only.
- `tools/capture.py`, `tools/build.py`: reproducible recovery/build scripts.

## Restore the captured files

Download `LABG-public-capture-2026-09-15.tar.gz` supplied with this branch and extract it at the repository root. It contains `rebuild/archive/` and `rebuild/generated/`; code stays in this Git branch. The archive uses standard tar hard links to avoid storing duplicate image bytes. macOS Archive Utility or `tar -xzf` can extract it.

## Preview without WordPress

From `rebuild`:

```sh
python3 tools/build.py
python3 -m http.server 8090 --directory generated/preview
```

Open http://localhost:8090/. Use HTTP; opening the HTML directly will not resolve root-relative resources. Preview links to pages not captured will return 404. Slideshows, dropdown menus, directory filters, maps, calendar navigation, sign-in, subscription and submission forms require rebuilding. Some animated content is forced visible to make it inspectable.

## Start WordPress locally

This environment did not include Docker or PHP, so the Docker startup, PHP execution and import have **not** been run here. The scripts are a development starting point pending those checks on your machine. The starter uses the official `wordpress:php8.3-apache` tag; record the resolved WordPress version and pin image digests after validating the stack.

1. Copy `.env.example` to `.env` and replace both passwords with random local values.
2. Run `docker compose up -d --build wordpress` and wait for WordPress to finish initializing.
3. Visit http://localhost:8080/ and complete the fresh WordPress setup using test admin details.
4. Run:

```sh
docker compose run --rm cli theme activate labg-recovery
docker compose run --rm cli eval-file /rebuild/wordpress/import.php
```

5. Visit the homepage, About, Breweries, Events, news articles and nested pages. The WordPress editor contains the captured HTML body, including the public header/footer; use the code editor for initial edits. This is not a recovered Avia builder layout. The REST originals retain published rendered page/post content and public metadata for a later proper content-model import.

The importer uses pages for visual recovery, including articles and listings. Before production, migrate posts, events and brewery listings into their correct native post types and replace repeated header/footer markup with maintained templates. Archived original IDs remain in JSON; they are not recreated as WordPress IDs.

## CiviCRM next setup

CiviCRM is **not installed or configured by this recovery**. Use its official WordPress distribution and installer after the recovered site starts:

https://docs.civicrm.org/installation/en/latest/wordpress/
https://docs.civicrm.org/installation/en/latest/requirements/

The container uses PHP 8.3 with additional BCMath, Intl and PDO MySQL extensions and increased PHP limits. Run CiviCRM's requirements checker; extension and image compatibility must still be verified. Download the selected supported WordPress ZIP from https://civicrm.org/download, install it under WordPress Plugins, activate it, then run Settings → CiviCRM Installer. For this disposable development instance the existing WordPress database is an option; design the final database/backup arrangement before production. Use test-only records and no payment processors. The staging mu-plugin blocks WordPress email; separately disable CiviCRM outbound mail and scheduled jobs, because CiviCRM does not necessarily use `wp_mail`.

## Preserve the original template when access becomes available

The public home identifies Enfold 7.1, Enfold Child 1.0, WordPress 7.0.4, Avia Builder 6.0 and Avia Framework 5.6. These are self-reported page comments, not authenticated server inventory. Public files also reference Directorist, The Events Calendar/Pro and Instagram Feed. This package does not recover installable copies of those plugins.

Ask the outgoing host for a full SQL export, all `wp-content` files, original Enfold download/license, child theme, uploads, Avia settings, directory/event exports, redirects and plugin/license inventory. Reuse or obtain the required theme/font/plugin licenses. Public CSS/JS assets do not contain server-side templates, builder metadata, credentials or plugin settings.

## Acceptance before moving production

- Compare recovered page text, logos, fonts, images and URL inventory against the live site.
- Confirm missing assets and failed URLs in the recovery report; do not infer completeness from an HTTP 200 alone.
- Import structured content into maintained WordPress post types and native templates.
- Implement organization/representative access in CiviCRM using server-side authorization; demo UI roles are not security.
- Test membership renewals, representative invitations, private content, submissions, mail and payments in test mode.
- Preserve redirects, metadata and analytics configuration; replace archive-specific noindex only at intentional launch.
- Back up, test restore, compare counts and only then plan the DNS cutover.

## Optional structured import

`python3 tools/export_wxr.py` produces `generated/public-content-reconstructed.xml`, a WXR assembled from public REST fields. It retains original post types/IDs, dates, published rendered content and attachment source URLs. It is **not** the original WordPress export: Avia layouts, protected metadata, taxonomies and plugin-specific records/settings are incomplete. Use it in a separate fresh test database from the visual importer. Register/install matching custom post types before importing brewery/events/venues. WordPress's importer may fetch attachments from the live site; those are source URLs, not automatically mapped to the local asset archive. Do not run both imports together without planning deduplication.

## Verification

Run `python3 tools/verify.py` after generation. The output `generated/verification.json` separates archive-integrity errors, unresolved local image/style references, external references and source failures. Source 404s and protected REST endpoints remain documented; they are not treated as recovered data. The cloud browser inspected the live homepage but could not open the local server, so visual equivalence has not been certified.

## Capture result — September 15, 2026

The live server returned HTTP 429 responses, so capture stopped. This is a **partial recovery** with 1,471 successful responses, 110 failed requests and 1,541 queued/retry URLs. The successful set includes 60 Google-hosted font files. These are response counts, not unique original media counts.

There are 52 preview pages: 40 captured HTML documents and 12 missing pages reconstructed from public REST content inside the recovered site shell. See each page's `recovery_method` in `generated/pages.json`. The structured export contains 17 pages, 8 posts, 74 brewery listings, 717 event records, 95 venues, 28 organizers and 561 attachments. The media API advertised 575 records, so 14 are not present in the recovered public responses. The full media page 4 returned a server error; a reduced-field public response recovered 99 records from that page.

Some page backgrounds, image variants and plugin icons remain missing. Available sizes of the same image are substituted where possible and logged in `generated/image-variant-substitutions.json`; original bytes remain unchanged. The preview is a useful reference, not a claim of pixel-perfect or functional duplication. `generated/verification.json` has the exact unresolved references and runtime limitations.

`tools/capture.py` retains already captured responses, schedules remaining URLs, starts new transfers at no more than six per minute, and stops a batch when the host returns 429. Run it only after the live host permits further requests. An outgoing-host backup remains the best route to original theme code, builder layouts, private data and complete plugin configuration.
