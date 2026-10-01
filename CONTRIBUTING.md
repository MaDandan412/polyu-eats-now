# Contributing

Issues and pull requests are welcome. Start with a small, reproducible improvement.

## Report a problem

Include the outlet, approximate Hong Kong time, selected language, device/browser and expected versus actual behavior. Screenshots may help, but remove personal details, order identifiers, session tokens and payment information first. Merchant blocking and unknown evidence are useful reports; they are not proof that a restaurant is closed.

## Change the code

1. Fork the repository and create a branch for one change.
2. Set up the frontend and backend using the README.
3. Keep translations in `frontend/src/locales`; regenerate simplified Chinese with the normal frontend build.
4. For status detection, add a test demonstrating the real behavior being fixed. Prefer public, sanitized evidence and read-only verification.
5. Run `python -m pytest backend/tests tools/tests -q` with the project environment, and `npm run build` in `frontend`.
6. Open a pull request explaining the trigger, changed behavior, validation and any unverified platform limitations.

## Evidence rules

- A visible menu alone is insufficient to mark an outlet OPEN.
- Prefer explicit closed/unavailable evidence over a purchasable-looking menu.
- Do not use opening hours to fill missing statuses or extend expired evidence.
- Check breakfast/lunch/tea categories when needed; an empty first category need not mean the entire outlet is closed.
- Do not add items to carts, place orders, process payments, reuse another user's session or bypass CAPTCHA/login barriers.
- Keep outlet identity, online service support and current orderability separate.
- Reduce concurrency for small hosts rather than multiplying checks for every visitor.

Good contribution areas: H Café/W Kiosk evidence gaps, source-backed bilingual names, clear failure explanations, accessibility and cloud resource measurements. App-only outlets need a reliable permitted source before adding detection.

Contributions to code and original documentation use the repository's MIT license. Do not contribute material you are not entitled to share; school identity and third-party assets retain their own rights.
