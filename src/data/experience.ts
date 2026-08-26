export interface Experience {
  role: string;
  org: string;
  orgNote?: string;
  location: string;
  period: string;
  bullets: string[];
}

export const experience: Experience[] = [
  {
    role: "Software Engineering Intern",
    org: "Murphy USA",
    orgNote: "Fortune 500",
    location: "El Dorado, AR",
    period: "Jun 2026 – Jul 2026",
    bullets: [
      "Built a C# / .NET integration solution from scratch to replace legacy SnapLogic pipelines: internal financial tooling used by the Financial Systems team to process invoices, purchase orders, and transactions.",
      "Engineered validation queries against IBM i (AS400) DB2 tables across multiple databases to identify incorrect POs, enabling the business to proactively resolve inaccurate customer records.",
      "Redesigned an automated JD Edwards Orchestrator workflow with custom and sub-orchestrations, writing validation logic in JRuby / Ruby on Rails to handle corrupted and blank data and surface clearer logs.",
      "Built an Azure DevOps CI/CD pipeline in YAML that auto-generates user-story tickets for bugs and triggers automated test runs on new code pushed to the C# codebase.",
    ],
  },
  {
    role: "Undergraduate Research Assistant",
    org: "Southern Arkansas University",
    location: "Magnolia, AR",
    period: "2025 – Spring 2026",
    bullets: [
      "Conducted comparative computer-vision research benchmarking VGG16, ViT, ChatGPT, and Claude on a 4-class image-classification dataset, evaluating models with IoU and accuracy metrics.",
    ],
  },
  {
    role: "Research Assistant",
    org: "University of Hawai‘i Cancer Center",
    location: "Honolulu, HI",
    period: "May 2024 – Jul 2024",
    bullets: [
      "Built Python pipelines to scrape and process 5,000+ TikTok posts on oral nicotine products, engineering validation logic that ensured 99% data consistency across heterogeneous sources.",
    ],
  },
];
