# Open Collective setup guide

**Not urgent** — set this up after you have at least one foundation conversation. GitHub Sponsors is sufficient for individual and lab-tier supporters.

---

## Why Open Collective

Foundations and institutional funders often prefer Open Collective over GitHub Sponsors for grant-friendly invoicing. Open Collective provides:

- Public, transparent expense tracking (funders can see exactly where money goes)
- Invoicing for institutional payments (purchase orders, grant disbursements)
- A separate legal entity for the funds (the fiscal host handles accounting)

This matters because many conservation program budgets require formal invoices that GitHub Sponsors cannot produce.

---

## Steps

1. **Create an Open Collective account** at opencollective.com using your GitHub login.

2. **Apply to a fiscal host** — Open Source Collective (opencollective.com/opensource) is the default for Apache-licensed projects. It charges 10% of funds raised. The application asks for:
   - A link to the GitHub repo
   - A brief description of the project
   - Confirmation of the open-source license

3. **Create a SpeciesNet Studio collective** — set the name, description ("Self-hosted review UI for SpeciesNet wildlife classifier predictions"), and logo.

4. **Set up transparent expense categories:**
   - Maintenance hours
   - Feature development (model adapters)
   - Feature development (export formats)
   - Community / documentation work

5. **Add a "Sponsor on Open Collective" badge to README** — once the collective exists, Open Collective generates a badge URL. Add it to the badge row in README.md.

6. **Cross-link** — add the Open Collective URL to `.github/FUNDING.yml`:
   ```yaml
   github: arunrajiah
   open_collective: speciesnet-studio
   ```

---

## Notes

- Open Collective funds and GitHub Sponsors funds are separate. Sponsors on one platform don't automatically appear on the other.
- For the first year, GitHub Sponsors is simpler. Only add Open Collective when a funder specifically asks for it.
- The 10% Open Collective fee is standard and acceptable to most grant-making foundations.
