import { describe, expect, test } from "vitest";

import {
  getStoryboardChapter,
  getStoryboardDurationSummary,
  walkthroughStoryboard,
} from "./walkthrough_storyboard.mjs";

describe("walkthrough storyboard", () => {
  test("targets tax-domain viewers with a source-led dual-peak narrative", () => {
    expect(walkthroughStoryboard.audience).toBe("tax_domain_expert");
    expect(walkthroughStoryboard.strategy).toBe("source_led_dual_peak");
    expect(walkthroughStoryboard.primaryMemoryPoint).toBe("treaty_branch_and_source_chain");
    expect(walkthroughStoryboard.secondaryMemoryPoint).toBe("workflow_handoff");
    expect(walkthroughStoryboard.finalMemoryPoint).toBe("explicit_pre_review_boundary");
  });

  test("keeps provenance heavier than workflow handoff", () => {
    const treatyBranch = getStoryboardChapter("treaty_branch");
    const provenance = getStoryboardChapter("source_chain");
    const handoff = getStoryboardChapter("workflow_handoff");
    const boundary = getStoryboardChapter("final_boundary");

    expect(provenance.holdMs).toBeGreaterThan(handoff.holdMs);
    expect(treatyBranch.holdMs).toBeGreaterThanOrEqual(handoff.holdMs);
    expect(boundary.holdMs).toBeGreaterThanOrEqual(handoff.holdMs);
  });

  test("keeps setup shorter than the result-side story", () => {
    const summary = getStoryboardDurationSummary();

    expect(summary.setupMs).toBeLessThan(summary.resultStoryMs);
    expect(summary.setupRatio).toBeLessThan(0.35);
    expect(summary.resultStoryRatio).toBeGreaterThan(0.65);
  });
});
