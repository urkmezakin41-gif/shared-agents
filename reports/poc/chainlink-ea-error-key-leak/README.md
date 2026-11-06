# PoC: API key in EA HTTP error response (smartcontractkit/external-adapters-js)

Local, no real provider traffic, dummy key only.

1. Clone external-adapters-js and copy `packages/core/bootstrap/src/lib/modules/requester.ts` and `error.ts` unchanged into `src/lib/modules/` of a scratch project.
2. Copy `stubs/` to `src/` (stubs replace util/logger/config/metrics/types only).
3. `npm i axios@0.27.2 object-path typescript tsx @types/node` then `npx tsx repro.ts`.

Expected: the printed JSON error body contains `"apikey":"TD_LIVE_KEY_abc123SECRET"` and the script prints `API KEY IN HTTP RESPONSE BODY: true`.
