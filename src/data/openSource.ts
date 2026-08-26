export interface OpenSourceContribution {
  project: string;
  org?: string;
  link?: { label: string; href: string };
  summary: string;
}

export const openSource: OpenSourceContribution[] = [
  {
    project: "Notte",
    org: "nottelabs",
    link: {
      label: "PR #855",
      href: "https://github.com/nottelabs/notte/pull/855",
    },
    summary:
      "Designed and implemented prefix-based model validation for a new LLM provider integration, with tests, addressing a maintainer-identified architecture gap.",
  },
  {
    project: "Hermes Agent",
    org: "Nous Research",
    summary:
      "Added a Semantic Scholar research skill covering 9 API endpoint types, closing a documented gap in the existing arXiv skill.",
  },
  {
    project: "JavaScript Mastery Pro",
    summary:
      "Fixed a missing await on a Mongoose findOneAndUpdate call that left a Promise unresolved in a POST handler (merged).",
  },
];
