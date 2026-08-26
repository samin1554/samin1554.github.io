export interface SkillGroup {
  label: string;
  items: string[];
}

export const skills: SkillGroup[] = [
  {
    label: "Languages",
    items: ["Java", "Python", "TypeScript", "JavaScript", "C#", "Go"],
  },
  {
    label: "Frameworks",
    items: ["Spring Boot", "React", "Next.js", "FastAPI"],
  },
  {
    label: "Backend & Systems",
    items: [
      "REST APIs",
      "Microservices",
      "Distributed Systems",
      "OAuth2 / JWT",
      "Event-Driven Architecture",
      "CI/CD",
    ],
  },
  {
    label: "Data & Infrastructure",
    items: [
      "PostgreSQL",
      "MongoDB",
      "Redis",
      "Docker",
      "RabbitMQ",
      "Azure DevOps",
      "GitHub Actions",
    ],
  },
  {
    label: "AI / ML",
    items: ["PyTorch", "TensorFlow", "LangGraph", "Transformers"],
  },
];

export const certifications: string[] = [
  "AI Fluency for Builders · Anthropic",
  "Claude Code in Action · Anthropic",
  "Fundamentals of Agents · Hugging Face",
  "SWE Intern Certification · HackerRank",
];
