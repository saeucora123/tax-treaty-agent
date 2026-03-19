# Walkthrough Main Video Refinement Design

Date: 2026-03-19
Status: Approved for implementation
Scope: Public GitHub Pages walkthrough refinement only

## Summary

Refine the existing single walkthrough video so it feels closer to a product-launch page and less like a stitched demo artifact.

This slice does not change runtime product behavior. It only improves the public walkthrough layer on the GitHub Pages site.

The approved storytelling direction is now `source-led dual peak` for a tax-domain-first audience:

- first memory point: the system can point to the treaty branch and visible source chain
- second memory point: the system returns a workflow-ready handoff package
- final memory point: the product stops at an explicit pre-review boundary rather than pretending to issue a final tax conclusion

## Goals

- Replace the current synthetic-feeling walkthrough motion with a real browser interaction capture.
- Raise the walkthrough export quality from low-frame-rate demo motion to a launch-page-style high-frame-rate product video.
- Reframe the walkthrough away from equal-weight demo beats and toward a provenance-first story for tax-domain viewers.
- Make cursor behavior feel human and intentional:
  - clicks land on the center of real fields and buttons
  - cursor movement is shorter, more purposeful, and less floaty
- Give the main walkthrough video a more polished presentation:
  - stronger device shell
  - cleaner screen framing
  - deliberate pauses after key actions
- Keep the single-video structure already approved by the user.

## Non-Goals

- No change to the public product flow itself
- No new treaty logic or frontend business behavior
- No return to multiple walkthrough videos
- No audio track or complex video player

## Recommended Approach

Use one browser-native recorded interaction as the source of truth, then apply light post-processing and a product-style device frame on the public site.

This approach is preferred over synthetic state interpolation because:

- it produces more natural cursor motion
- it is easier to trust visually
- it better matches the product-launch reference the user cited

## Video Content

The walkthrough remains one `CN -> NL dividends` case and follows this fixed sequence:

1. Input
2. Guided facts
3. Treaty branch
4. Provenance
5. Handoff artifact
6. Final boundary

Approved narrative priority inside that sequence:

- `Input` and `Guided facts` establish the case quickly and should not dominate the runtime
- `Treaty branch` is the first major pause
- `Provenance` / `Source Chain` is the primary peak and should receive the longest result-side hold
- `Handoff artifact` is still shown clearly, but it is secondary to provenance
- `Final boundary` is the closing beat and must land as a deliberate ending rather than a footnote

Target pacing guidance:

- front-of-flow setup should take roughly the first quarter of the video
- the result-side story should take the remaining three quarters
- the combined `Treaty branch + Provenance` section should outweigh `Handoff artifact`
- `Provenance` should hold longer than `Handoff artifact`
- `Final boundary` should receive a distinct closing hold instead of being rushed after handoff

Required on-screen interactions:

- choose treaty pair
- choose income type
- click `direct_holding_percentage`
- click `payment_date`
- click `holding_period_months`
- click the run/review action
- pause on the treaty branch/result area
- pause on provenance
- pause on handoff and final boundary

Fields that matter most on screen:

- treaty pair
- income type
- `direct_holding_percentage`
- `payment_date`
- `holding_period_months`

Other guided facts may still appear, but they should not each receive tutorial-like dwell time.

## Capture Strategy

### Source of truth

Capture a real browser session against the actual product UI rather than simulating motion entirely from still screenshots.

### Pipeline

1. Start the local app stack required for the walkthrough path.
2. Drive the browser through the approved `CN-NL dividends` path.
3. Capture a real interaction sequence at a denser motion cadence than the current stitched demo flow using a browser-native recording path rather than stitched screenshots.
4. Export one high-frame-rate MP4 intended to feel closer to a polished product-release video than a GIF-like walkthrough.
5. Use a later stable frame as the poster so the walkthrough preview reads as a live product moment rather than an empty start state.

Current implementation note:

- prefer Playwright-based viewport video capture first
- keep screenshot-based assembly only as a final fallback path

### Motion rules

- Cursor moves should be short and direct.
- Every click target should land near the visual center of the intended field or button.
- Input-side motion should feel brisk and purposeful rather than evenly paced across every field.
- Each important transition should include a hold:
  - short hold after selection actions
  - medium hold on the first treaty-branch reveal
  - longest hold on provenance / source chain
  - shorter but still legible hold on workflow handoff
  - distinct closing hold on the final boundary
- Export target should be at least `24fps`, with a preference for `30fps`, so the public walkthrough no longer reads as visibly under-sampled.

Storyboard rule:

- timing and pause priorities should live in a small reusable storyboard/config layer rather than being scattered as unexplained magic numbers inside the recorder
- the recorder should consume that storyboard so future narrative tuning can be tested and adjusted without re-reading the entire capture script

## Public Page Presentation

The walkthrough section keeps one main video and the existing six chapter labels.

Additional presentation refinements:

- stronger device shell around the video
- subtle inner bezel and top chrome
- softer glass/highlight treatment
- more launch-page-like spacing around the main asset
- chapter copy should reinforce provenance-first ordering instead of making provenance and handoff sound equally primary

The surrounding copy and bilingual switch behavior remain intact.

## Files Expected To Change

- `scripts/build_demo_assets.py`
- `docs/index.html`
- `docs/site.css`
- `backend/tests/test_public_site_artifacts.py`

Possible supporting additions:

- a helper capture script under `scripts/`
- a small walkthrough storyboard/config file under `frontend/scripts/`
- regenerated assets under `docs/site-assets/`

## Verification

- The site still references exactly one walkthrough main video.
- The new main video asset exists and is non-empty.
- The walkthrough section still renders correctly in both Chinese and English.
- Public site artifact tests pass.
- Frontend tests and build remain green.

## Acceptance Criteria

- The cursor clearly clicks real fields and buttons rather than drifting near them.
- The walkthrough reads as one coherent product story instead of a stitched slideshow.
- A tax-domain viewer should leave the clip remembering the treaty branch and source chain before the workflow handoff.
- The device shell and pacing feel materially closer to a polished launch page.
- No runtime product behavior changes are introduced.
