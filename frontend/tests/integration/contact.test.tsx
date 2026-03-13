/**
 * Integration tests for Contact Section feature.
 * Tests all acceptance criteria from specs/02-features.md Feature 5.
 */
import { render, screen } from "@testing-library/react";
import { ContactSection } from "@/components/ContactSection";

// ---------------------------------------------------------------------------
// FEATURE 5: Contact Section
// Integration test covering all acceptance criteria
// ---------------------------------------------------------------------------

describe("Contact Section", () => {
  test("section is visible at or near the bottom of the page", () => {
    const { container } = render(<ContactSection />);
    
    const section = container.querySelector("section#contact");
    expect(section).toBeInTheDocument();
  });

  test("section contains heading labeled Contact or Get in Touch", () => {
    render(<ContactSection />);
    
    const heading = screen.getByRole("heading", { name: /contact/i });
    expect(heading).toBeInTheDocument();
    expect(heading.textContent).toMatch(/contact/i);
  });

  test("email is rendered as mailto anchor tag", () => {
    render(<ContactSection />);
    
    const emailLink = screen.getByRole("link", { name: /luis@example.com/i });
    expect(emailLink).toBeInTheDocument();
    expect(emailLink).toHaveAttribute("href", "mailto:luis@example.com");
  });

  test("GitHub link href is correct and opens in new tab", () => {
    render(<ContactSection />);
    
    const githubLink = screen.getByRole("link", { name: /github/i });
    expect(githubLink).toHaveAttribute("href", "https://github.com/luisalarcon-gauntlet");
    expect(githubLink).toHaveAttribute("target", "_blank");
    expect(githubLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("LinkedIn link is present and opens in new tab", () => {
    render(<ContactSection />);
    
    const linkedinLink = screen.getByRole("link", { name: /linkedin/i });
    expect(linkedinLink).toBeInTheDocument();
    expect(linkedinLink).toHaveAttribute("target", "_blank");
    expect(linkedinLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("no contact form exists in v1", () => {
    render(<ContactSection />);
    
    // Should not have a form element
    const form = document.querySelector("form");
    expect(form).not.toBeInTheDocument();
  });

  test("section is responsive with container classes", () => {
    const { container } = render(<ContactSection />);
    
    const section = container.querySelector("section");
    expect(section).toHaveClass("px-4"); // Mobile padding
    expect(section).toHaveClass("py-20"); // Vertical padding
  });

  test("section has dark theme styling", () => {
    const { container } = render(<ContactSection />);
    
    const heading = screen.getByRole("heading", { name: /contact/i });
    expect(heading).toHaveClass("text-white");
  });
});

// ---------------------------------------------------------------------------
// NOT COVERED IN THIS FILE — intentional v1 exclusions
// ---------------------------------------------------------------------------
// - Contact form with backend email sending
// - Copy-to-clipboard for email address
// - Twitter/X or other social links
// - reCAPTCHA or spam protection
// - Actual mailto: link opening system mail client - would require E2E
// - Actual viewport size testing (mobile and desktop) - would require E2E
// ---------------------------------------------------------------------------
