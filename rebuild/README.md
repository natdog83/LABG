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

## Start WordPress locally on your Mac

Install and open [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) using the installer for your Mac's processor. The Compose file does not force Intel emulation. Python 3 is also required for the helper and recovery tools.

From the repository root, after extracting the capture archive:

```sh
bash rebuild/tools/mac-start.sh
```

The helper checks Docker, Compose and the extracted files, creates random database passwords in an ignored `.env` file if one does not already exist, and starts WordPress at http://localhost:8080/. Complete the WordPress setup in your browser, then run:

```sh
bash rebuild/tools/mac-import.sh
```

The importer now preserves existing recovered pages by default. You can edit them without losing your work on the next normal import. Only use the following command if you deliberately want to replace those edits with the captured versions:

```sh
bash rebuild/tools/mac-import.sh --refresh
```

Stop the containers without deleting data:

```sh
cd rebuild
docker compose stop
```

Run the start helper again to resume. Keep `.env` together with your local setup; changing its database passwords after the database volume is initialized does not change the database's stored passwords. The named project `labg-local` keeps these volumes separate from unrelated projects named `rebuild`.

This environment has no Docker or PHP, so startup, PHP execution and import still require runtime checks on your Mac. The starter uses the official `wordpress:php8.3-apache` tag; record the resolved WordPress version and pin image digests after validating the stack.

## Template files you can work on now

- `wordpress/theme/header.php`: WordPress document head and header for new pages.
- `wordpress/theme/footer.php`: shared document footer and footer for new pages.
- `wordpress/theme/index.php`: recovered-page rendering and normal editable pages.
- `wordpress/theme/style.css`: versioned styling for new native pages.
- `wordpress/theme/functions.php`: theme support, captured styling classes and original URL routing.

Captured pages still include their original visible header/footer inside their imported content to preserve the source layout. Moving those elements into a single editable navigation/header is a later template migration, not something the public capture has already recovered. New WordPress pages use the shared native header/footer and the Primary navigation menu set in WordPress. Create future CiviCRM pages as new native pages; archived forms remain disabled.

The importer uses pages for visual recovery, including captured articles and listings. Before production, migrate posts, events and brewery listings into their correct native post types. Original IDs remain in REST JSON and the reconstructed WXR; the visual import creates fresh IDs.

Local Compose sets WordPress's [environment type](https://developer.wordpress.org/reference/functions/wp_get_environment_type/) to `local`. WordPress email and indexing protections apply only to local/development/staging environments. Archived form blocking applies only to recovered pages, allowing future native CiviCRM pages to submit. CiviCRM outgoing mail still needs its own configuration.

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
