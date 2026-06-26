# Monocle Man live proof network classification

The GitHub Pages live proof remains fail-closed for network failures.

## Blocking failures

The proof must fail when any first-party request from the deployed page origin fails. It must also fail on unexpected non-allowlisted network failures.

## Expected non-blocking third-party warnings

The proof may classify aborted YouTube privacy-enhanced embed requests as expected non-blocking warnings only when all of the following are true:

- failure text is `net::ERR_ABORTED`;
- host is `www.youtube-nocookie.com` and the request is YouTube embed lifecycle traffic at `/api/stats/qoe`, `/youtubei/v1/log_event`, or `/youtubei/v1/next`, the iframe document under `/embed/NBxByrz5BRE`, or a no-cookie embed script under `/s/_/ytembeds/_/js/`; or
- host is `www.google.com`, resource type is `script`, and the path is an embed helper script under `/js/th/`.

These requests are recorded in `expected_third_party_network_warnings` and do not block deployment proof.

## Required proof fields

The generated `delivery-proof/monocle-man/latest/deployment-proof.json` should distinguish:

- `blocking_network_errors`;
- `expected_third_party_network_warnings`;
- raw observed `network_errors`.

A live proof may report `status: PASS` only when `blocking_network_errors` is empty, `hero_heading_contains_monocle_man` is true, `normal_motion_animation_name` is `spin`, and `blocking_network_errors_count` is 0.
