import { HeroSection } from "@/components/ui/hero-section-dark";
import { ResumeAnalyzer } from "@/components/resume-analyzer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <HeroSection
        subtitle={{
          regular: "Match your resume to job descriptions with ",
          gradient: "intelligent AI scoring",
        }}
        description="Upload your resume and job description to get instant compatibility scores, skill matching, and personalized recommendations to land your dream job."
        ctaText="Start Analyzing"
        ctaHref="#analyzer"
        gridOptions={{
          angle: 65,
          opacity: 0.4,
          cellSize: 50,
          lightLineColor: "#4a4a4a",
          darkLineColor: "#2a2a2a",
        }}
      />
      <ResumeAnalyzer />
    </main>
  );
}
