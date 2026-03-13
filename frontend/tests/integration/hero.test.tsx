/**
 * Integration tests for Hero Section feature.
 * Tests all acceptance criteria from specs/02-features.md Feature 1.
 */
import { render, screen } from "@testing-library/react";
import { HeroSection } from "@/components/HeroSection";

// ---------------------------------------------------------------------------
// FEATURE 1: Hero Section
// Integration test covering all acceptance criteria
// ---------------------------------------------------------------------------

describe("Hero Section", () => {
  test("displays name Luis Alarcon prominently", () => {
    render(<HeroSection />);
    
    const name = screen.getByText("Luis Alarcon");
    expect(name).toBeInTheDocument();
    expect(name.tagName).toBe("H1");
  });

  test("displays title exactly as Full-Stack & AI Engineer", () => {
    render(<HeroSection />);
    
    const title = screen.getByText("Full-Stack & AI Engineer");
    expect(title).toBeInTheDocument();
    expect(title.tagName).toBe("H2");
  });

  test("displays bio referencing Gauntlet AI program and Austin TX", () => {
    render(<HeroSection />);
    
    const bio = screen.getByText(/Gauntlet AI program/i);
    expect(bio).toBeInTheDocument();
    expect(bio.textContent).toContain("Austin");
  });

  test("GitHub link points to correct URL and opens in new tab", () => {
    render(<HeroSection />);
    
    const githubLink = screen.getByRole("link", { name: /github/i });
    expect(githubLink).toHaveAttribute("href", "https://github.com/luisalarcon-gauntlet");
    expect(githubLink).toHaveAttribute("target", "_blank");
    expect(githubLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("LinkedIn link is present and opens in new tab", () => {
    render(<HeroSection />);
    
    const linkedinLink = screen.getByRole("link", { name: /linkedin/i });
    expect(linkedinLink).toBeInTheDocument();
    expect(linkedinLink).toHaveAttribute("target", "_blank");
    expect(linkedinLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("section has dark theme styling", () => {
    const { container } = render(<HeroSection />);
    
    const section = container.querySelector("section");
    expect(section).toHaveClass("min-h-screen");
    // Check for dark theme classes (text-white, etc.)
    const heading = screen.getByText("Luis Alarcon");
    expect(heading).toHaveClass("text-white");
  });

  test("section is responsive with mobile-first classes", () => {
    const { container } = render(<HeroSection />);
    
    const section = container.querySelector("section");
    expect(section).toHaveClass("px-4"); // Mobile padding
    expect(section).toHaveClass("pt-20"); // Top padding for nav
  });
});

// ---------------------------------------------------------------------------
// NOT COVERED IN THIS FILE — intentional v1 exclusions
// ---------------------------------------------------------------------------
// - Animated entrance effects or typewriter text
// - Profile photo or avatar
// - Resume download link in Hero (covered in About Section)
// - Custom tagline CMS or editable content
// - Viewport size testing (1280px desktop, 375px mobile) - would require E2E
// - JavaScript console error checking - would require E2E
// ---------------------------------------------------------------------------
