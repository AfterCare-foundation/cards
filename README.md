# AfterCare cards

Generates printable sheets of AfterCare paper cards. Each card carries a random
token in a QR code (`https://<domain>/connect#et=<token>`). The token is never
stored or printed anywhere else, so generated sheets must **not** be committed.

## Usage

    python generate_cards.py --count 200 --domain after-care.eu --output aftercare-cards

Output: `sheet-001.html`, `sheet-002.html`, ... (8 cards per sheet, front plus
mirrored back for double-sided printing, with crop marks). Open in a browser and print at 100% scale.

## Notes

- Tokens: `secrets.token_urlsafe(16)` (128 bits).
- The app must hash the raw 16 decoded bytes of the token. See the backend `docs/CRYPTO.md`.
- Output folder and `sheet-*.html` are git-ignored.

## License

AGPL-3.0. See `LICENSE`.
