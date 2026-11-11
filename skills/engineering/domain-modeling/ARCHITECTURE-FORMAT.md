# Architecture Doc Format

`ARCHITECTURE.md` sits beside `GLOSSARY.md` (repo root, or one per context). It describes the system as it exists now. Writers: `bootstrap-context` and `ship`. Both shape the file by this reference.

## Fixed core

In this order:

1. **Header**:
   - one sentence on the system
   - kind of repo (single app, monorepo, library)
   - pointers to `docs/adr/`, `docs/specs/README.md` and `GLOSSARY.md`
   - `Last updated: <spec number and title>`, the spec that caused the last change (`Brownfield bootstrap (no spec)` until the first `ship`)
2. `## Shape`: one ASCII-arrow diagram. Not Mermaid.
3. `## Modules`: one `###` section per Module.
4. `## Flows`: two to five paths, each a numbered list of steps.
5. `## Rules across modules`: rules that hold across Modules, each backed by a confirmed ADR or stated by the user. `none yet` when there are none.

## Module

A Module is one top-level source folder with its own interface. Each Module section has exactly six one-line fields, in this order:

```markdown
### billing

- Does: creates, numbers, sends and voids **Invoices**.
- Lives in: `src/billing/`
- Interface: `src/billing/index.ts` (`createInvoice`, `sendInvoice`)
- Uses: ledger, mailer
- ADRs: [0004 Invoice numbers never reused](docs/adr/0004-invoice-numbers.md)
- Specs: [0001 First release](docs/specs/0001-first-release.md), [0007 Recurring invoices](docs/specs/0007-recurring-invoices.md)
```

- Write `none` when a field has nothing. Never omit a field.
- Links use number and title. A spec that amends another says what it amends.
- Glossary terms in bold, spelled as in the glossary.

## Optional sections by kind of repo

- Single app and monorepo apps: `## External services` after Flows.
- Library: `## Public API` after Shape. It replaces Flows when there is no runtime flow.
- Monorepo: `## Packages` before Modules. Group Modules by package.
- Multi-context repo: each context has a full doc. The root file is a short map with `## How contexts talk`.

## Limit

200 lines for the whole file. Past that, group small Modules into one section or split by context.

## Stays out

- Why a choice was made: ADR.
- What a feature must do: spec.
- What a term means: glossary.
- Anything one `ls` or one file read shows.
- Install and deploy steps.
- Test setup: how tests run, test commands.
- Plans and history.
