# Week 7 — Mobile and Accessibility Fix Log

## Test environment

- Device: Real Android phone
- Browser: Google Chrome
- Live site: https://sp2023labv2.netlify.app
- Navigation result: All navigation buttons worked smoothly before the changes.

## Before review

The portfolio was already functional on mobile. No horizontal overflow, broken cards, unusable navigation or clipped project tags were found.

### Genuine issues identified

1. Homepage and case-study H1 headings occupied too much of the first mobile viewport.
2. Large section and case-study spacing made long pages slower to scan.
3. Architecture diagrams fitted the screen but their labels were too small to inspect comfortably.
4. Dates, project numbers, breadcrumbs and footer text used a borderline-low secondary colour.
5. Homepage LinkedIn, GitHub and booking links had smaller touch areas than the primary buttons.
6. The longest breadcrumb could become crowded on narrower phones.

## Changes made

1. Reduced phone H1 sizing while retaining the visual hierarchy.
2. Reduced mobile section spacing and case-study section spacing.
3. Added keyboard- and touch-accessible full-size diagram opening.
4. Added a visible “Tap the diagram to view it at full size” hint.
5. Lightened the secondary text colour from `#748198` to `#8592a8`.
6. Increased the homepage social-link touch areas to at least 44px high.
7. Simplified the breadcrumb below 400px by hiding the repeated current-page label.

## Files changed

- `mobile-polish.css` — new responsive and contrast overrides.
- `script.js` — loads the override stylesheet and adds accessible diagram expansion.

## After-test results

- [x] Homepage hero is more compact on the real phone.
- [x] Mobile menu opens, closes and scrolls smoothly.
- [x] LinkedIn, GitHub, booking and CV links work.
- [x] All four case-study links work.
- [x] Diagrams open full-size when tapped.
- [x] No horizontal overflow appears.
- [x] Portrait and landscape orientations checked.
- [x] Tablet width checked.
- [x] Desktop width checked.
- [x] After screenshots captured.

## Final result

The updated portfolio works correctly on a real Android phone using Google Chrome. The mobile layout remains responsive, all navigation and external links work, diagrams can be inspected at full size, secondary text is clearer, and the revised spacing makes long pages easier to scan.