export interface Project {
  name: string;
  tagline: string;
  description: string;
  stack: string[];
  repo?: string;
  live?: { label: string; href: string };
  featured?: boolean;
  /**
   * Optional cover image, e.g. "/projects/openbook.png".
   * Drop the file in public/projects/ and set this path. Falls back to a
   * painterly gradient banner when omitted.
   */
  image?: string;
}

export const projects: Project[] = [
  {
    name: "OpenBook",
    tagline: "NotebookLM clone · RAG document Q&A platform",
    description:
      "A 6-service Java / Spring Boot microservices platform for retrieval-augmented document Q&A. pgvector semantic search with LLaMA 3.3 70B, event-driven RabbitMQ messaging, async podcast generation, and Stripe subscription billing.",
    stack: [
      "Java",
      "Spring Boot",
      "FastAPI",
      "React",
      "pgvector",
      "RabbitMQ",
      "Docker",
      "Stripe",
    ],
    repo: "https://github.com/samin1554/OpenBook",
    featured: true,
    image: "/projects/openbook.jpg",
  },
  {
    name: "TechGenie",
    tagline: "AI career toolkit · full-stack SaaS",
    description:
      "A deployed SaaS for GitHub profile analysis, ATS-optimized resume generation, and job matching. RESTful backend with JWT auth, GitHub / Google OAuth2, Stripe billing, and PostgreSQL JSONB caching; integrates the JSearch API for real-time listings from LinkedIn, Indeed, and Glassdoor.",
    stack: [
      "Next.js",
      "TypeScript",
      "FastAPI",
      "PostgreSQL",
      "OAuth2",
      "Stripe",
      "Vercel",
      "Railway",
    ],
    repo: "https://github.com/samin1554/TechGenie",
    live: { label: "techgenie.cc", href: "https://techgenie.cc" },
    featured: true,
    image: "/projects/techgenie.jpg",
  },
  {
    name: "Life OS",
    tagline: "Multi-agent AI system",
    description:
      "A 12-agent LangGraph orchestration system with ChromaDB semantic memory, Gmail OAuth integration, and bring-your-own-key support across 9 LLM providers. Generates DOCX / XLSX / PDF files; full stack deployed on Railway + Vercel.",
    stack: [
      "Next.js",
      "FastAPI",
      "LangGraph",
      "PostgreSQL",
      "ChromaDB",
      "Redis",
      "Clerk",
    ],
    repo: "https://github.com/samin1554/Life-os",
    featured: true,
    image: "/projects/lifeos.jpg",
  },
  {
    name: "European Soccer Web App",
    tagline: "League data, standings, and match browsing",
    description:
      "A full-stack app for exploring European league data: standings, fixtures, and match browsing, on a Spring Boot backend with a TypeScript front end.",
    stack: ["TypeScript", "Java", "Spring Boot"],
    repo: "https://github.com/samin1554/European-Soccer-Web-App",
    image: "/projects/soccer.jpg",
  },
  {
    name: "Fitness App",
    tagline: "Workout logging and progress tracking",
    description:
      "A full-stack fitness tracker with workout logging and progress tracking over a Spring Boot API and a React front end.",
    stack: ["Java", "Spring Boot", "React"],
    repo: "https://github.com/samin1554/Fitness-App",
    image: "/projects/fitness.jpg",
  },
];
