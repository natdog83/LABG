# LABG Member Portal Concept

Interactive concept for a future Los Angeles County Brewers Guild membership portal built around WordPress and CiviCRM.

## Live demo

[Open the GitHub Pages demo](https://natdog83.github.io/LABG/)

## Concept areas

- Member dashboard and brewery profile
- Brewery representatives and role-based access
- Member and allied-partner directory
- Private Guild forums
- Member event submission and approval
- Resources and committees
- Member Advantage offers and group purchasing
- Advocacy Help Desk
- Compliance Center
- Anonymous brewery benchmarking
- Jobs and Industry Exchange
- Membership-value tracking
- Communication preferences
- Membership, billing, invoices, and receipts

All businesses, dates, prices, savings figures, regulatory items, and benefit terms shown in the demo are illustrative unless independently confirmed by the Guild.

## Structure

The demonstration is a static prototype in `dist/index.html`. GitHub Actions publishes the contents of `dist/` to GitHub Pages whenever the `main` branch changes.

## Intended production architecture

WordPress would provide the member-facing interface. CiviCRM would remain the source of truth for brewery organizations, individual representatives, relationships and roles, membership status, payments, events, communications, activities, and case workflows.

