const chapters = [
  {
    id: "input",
    phase: "setup",
    allocatedMs: 9000,
    holdMs: 0,
  },
  {
    id: "guided_facts",
    phase: "setup",
    allocatedMs: 14000,
    holdMs: 0,
  },
  {
    id: "treaty_branch",
    phase: "result_story",
    allocatedMs: 12000,
    holdMs: 1200,
  },
  {
    id: "source_chain",
    phase: "result_story",
    allocatedMs: 15000,
    holdMs: 1550,
  },
  {
    id: "workflow_handoff",
    phase: "result_story",
    allocatedMs: 9000,
    holdMs: 950,
  },
  {
    id: "final_boundary",
    phase: "result_story",
    allocatedMs: 11000,
    holdMs: 1250,
  },
];

export const walkthroughStoryboard = {
  audience: "tax_domain_expert",
  strategy: "source_led_dual_peak",
  primaryMemoryPoint: "treaty_branch_and_source_chain",
  secondaryMemoryPoint: "workflow_handoff",
  finalMemoryPoint: "explicit_pre_review_boundary",
  chapters,
  capturePlan: {
    intro: {
      initialCursor: { x: 220, y: 180, steps: 8 },
      initialHoldMs: 560,
    },
    selection: {
      moveSteps: 20,
      pauseBeforeMs: 90,
      pauseAfterMs: 150,
      postSelectHoldMs: 150,
    },
    typedField: {
      moveSteps: 22,
      pauseBeforeClickMs: 90,
      pauseAfterClickMs: 80,
      keyDelayMs: 58,
      pauseAfterTypeMs: 150,
    },
    supportingSelect: {
      moveSteps: 16,
      pauseBeforeMs: 60,
      pauseAfterMs: 100,
      postSelectHoldMs: 110,
    },
    runAction: {
      moveSteps: 24,
      pauseBeforeMs: 140,
      pauseAfterMs: 720,
    },
    resultBeat: {
      scrollSettleMs: 560,
      focusMoveSteps: 16,
    },
  },
};

export function getStoryboardChapter(id) {
  const chapter = chapters.find((item) => item.id === id);
  if (!chapter) {
    throw new Error(`Unknown walkthrough storyboard chapter: ${id}`);
  }
  return chapter;
}

export function getStoryboardDurationSummary() {
  const totalMs = chapters.reduce((sum, chapter) => sum + chapter.allocatedMs, 0);
  const setupMs = chapters
    .filter((chapter) => chapter.phase === "setup")
    .reduce((sum, chapter) => sum + chapter.allocatedMs, 0);
  const resultStoryMs = totalMs - setupMs;

  return {
    totalMs,
    setupMs,
    resultStoryMs,
    setupRatio: setupMs / totalMs,
    resultStoryRatio: resultStoryMs / totalMs,
  };
}
