/**
 * Integration tests for About Section feature.
 * Tests all acceptance criteria from specs/02-features.md Feature 4.
 */
import { render, screen } from "@testing-library/react";
import { AboutSection } from "@/components/AboutSection";

// ---------------------------------------------------------------------------
// FEATURE 4: About Section
// Integration test covering all acceptance criteria
// ---------------------------------------------------------------------------

describe("About Section", () => {
  test("section is visible on the page", () => {
    const { container } = render(<AboutSection />);
    
    const section = container.querySelector("section#about");
    expect(section).toBeInTheDocument();
  });

  test("section contains heading labeled About or About Me", () => {
    render(<AboutSection />);
    
    const heading = screen.getByRole("heading", { name: /about/i });
    expect(heading).toBeInTheDocument();
    expect(heading.textContent).toMatch(/about/i);
  });

  test("paragraph references Gauntlet AI program, full-stack engineering, AI engineering, and Austin TX", () => {
    render(<AboutSection />);
    
    const paragraph = screen.getByText(/Gauntlet AI program/i);
    expect(paragraph).toBeInTheDocument();
    expect(paragraph.textContent).toMatch(/full-stack/i);
    expect(paragraph.textContent).toMatch(/AI engineer/i);
    expect(paragraph.textContent).toMatch(/Austin/i);
  });

  test("Download Resume link is present and functional", () => {
    render(<AboutSection />);
    
    const resumeLink = screen.getByRole("link", { name: /download resume/i });
    expect(resumeLink).toBeInTheDocument();
    expect(resumeLink).toHaveAttribute("href", "/resume.pdf");
    expect(resumeLink).toHaveAttribute("download");
  });

  test("section is responsive with container classes", () => {
    const { container } = render(<AboutSection />);
    
    const section = container.querySelector("section");
    expect(section).toHaveClass("px-4"); // Mobile padding
    expect(section).toHaveClass("py-20"); // Vertical padding
  });

  test("section has dark theme styling", () => {
    const { container } = render(<AboutSection />);
    
    const section = container.querySelector("section");
    expect(section).toHaveClass("bg-gray-950"); // Dark background
    
    const heading = screen.getByRole("heading", { name: /about/i });
    expect(heading).toHaveClass("text-white");
  });
});

// ---------------------------------------------------------------------------
// NOT COVERED IN THIS FILE — intentional v1 exclusions
// ---------------------------------------------------------------------------
// - CMS-editable bio text
// - Skills list or technology icons
// - Work history timeline
// - Profile photo in this section
// - Actual PDF file download testing - would require E2E
// - Actual viewport size testing (375px, 1280px) - would require E2E
// ---------------------------------------------------------------------------
