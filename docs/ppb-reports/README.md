# PPB quarterly pharmacovigilance reports (OCR text)

This folder holds the text of two quarterly pharmacovigilance summary reports of the Pharmacy and Poisons Board (PPB). The reports are public.

| File | Report | Source |
|---|---|---|
| `2025-q2-oct-dec.txt` | Q2 FY2025/26, 1 October to 31 December 2025 | https://web.pharmacyboardkenya.org/wp-content/uploads/2026/03/PV_-Report_1st-October_-31st-December-2025.pdf |
| `2026-q3-jan-mar.txt` | Q3 FY2025/26, 1 January to 31 March 2026 | https://web.pharmacyboardkenya.org/wp-content/uploads/2026/04/Quarter-3-Pharmacovigilance-Summary-Jan-Mar-2026.pdf |

The list of all reports is at https://web.pharmacyboardkenya.org/pharmacovigilance/.

## Method

1. The PDF files are scans. They hold no text.
2. `pdftoppm -r 200 -gray -png` made one image for each page.
3. `tesseract <image> <output> --psm 6 -l eng` read each image.
4. The text of the pages was joined in page order.

## Limits

- The text is not checked against the PDF. A number can be wrong. Check a number in the PDF before you use it.
- Tables and charts read badly. Columns can mix, and some cells are noise.
- The text has not been edited.
- The reports hold totals for each field. They do not hold single cases.
- The reports have no table of causality assessment levels.
