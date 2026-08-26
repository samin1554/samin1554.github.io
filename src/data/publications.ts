export interface Publication {
  title: string;
  year: number;
  citations?: number;
}

export const scholarUrl =
  "https://scholar.google.com/citations?hl=en&user=LVeArBgAAAAJ";

export const scholarInterests = [
  "Machine Learning",
  "Artificial Intelligence",
  "Digital Health",
  "Mental Health",
];

// Newest first.
export const publications: Publication[] = [
  {
    title: "Exploring #Zyn-related video content posted by Zynfluencers on TikTok",
    year: 2026,
    citations: 1,
  },
  {
    title:
      "An mHealth-based rural cardiac rehabilitation and smoking cessation system: Proposal for a proof-of-concept study",
    year: 2026,
  },
  {
    title:
      "Exploring the role of virtual reality for childbirth induction to improve pain, anxiety, and maternal experience",
    year: 2026,
  },
  {
    title:
      "Public engagement with lung cancer screening information: Topic modeling of lung cancer-related Reddit posts",
    year: 2025,
    citations: 1,
  },
  {
    title:
      "Exploring intention to use mobile health apps in lung cancer treatment adherence",
    year: 2025,
  },
  {
    title: "Mobile app use for monitoring physical activity in Bangladeshi students",
    year: 2025,
  },
  {
    title:
      "University application distress: An Instagram-based investigation of youth experiences",
    year: 2024,
  },
  {
    title:
      "The impact of COVID-19 on the mental health of adolescents: Global scenario",
    year: 2022,
  },
  {
    title: "Is there an internet addiction escalating in COVID-19?",
    year: 2021,
  },
];
