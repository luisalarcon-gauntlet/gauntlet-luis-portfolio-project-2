import { HeroSection } from "@/components/HeroSection";
import { ProjectsGrid } from "@/components/ProjectsGrid";
import { AboutSection } from "@/components/AboutSection";
import { ContactSection } from "@/components/ContactSection";

export default function Home() {
  return (
    <main className="min-h-screen">
      <HeroSection />
      <ProjectsGrid />
      <AboutSection />
      <ContactSection />
    </main>
  );
}
