export interface SocialLink {
  label: string;
  href: string;
  icon: "github" | "linkedin" | "scholar" | "mail";
}

export interface Profile {
  name: string;
  /** Full legal name, used in the academic Publications list. */
  fullName: string;
  role: string;
  tagline: string;
  location: string;
  bio: string;
  education: {
    school: string;
    degree: string;
    detail: string;
  };
  resumeHref: string;
  socials: SocialLink[];
}

const EMAIL = "Samiul27a@gmail.com";
const LINKEDIN_URL = "https://www.linkedin.com/in/samiul-amin-8b3a7a32b";

export const profile: Profile = {
  name: "Sam Amin",
  fullName: "Sayed Mahmud Samiul Amin",
  role: "Software Engineer",
  tagline:
    "I like building full-stack systems, and learning what holds them together.",
  location: "San Bernardino, CA",
  bio: "I'm an undergraduate software engineer, still early in the journey. I've been fortunate to build on a Fortune 500 team, contribute to a few open-source projects, and help with published research along the way. Mostly I enjoy figuring out how the pieces fit: the services, data flows, and pipelines behind a working product.",
  education: {
    school: "California State University, San Bernardino",
    degree: "B.S. in Computer Science",
    detail: "Expected 2027–2028",
  },
  resumeHref: "/resume.pdf",
  socials: [
    { label: "GitHub", href: "https://github.com/samin1554", icon: "github" },
    { label: "LinkedIn", href: LINKEDIN_URL, icon: "linkedin" },
    {
      label: "Google Scholar",
      href: "https://scholar.google.com/citations?hl=en&user=LVeArBgAAAAJ",
      icon: "scholar",
    },
    { label: "Email", href: `mailto:${EMAIL}`, icon: "mail" },
  ],
};
