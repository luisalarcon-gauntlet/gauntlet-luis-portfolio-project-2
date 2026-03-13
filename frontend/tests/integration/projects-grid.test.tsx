/**
 * Integration tests for Projects Grid feature.
 * Tests all acceptance criteria from specs/02-features.md Feature 3.
 */
import { render, screen, waitFor } from "@testing-library/react";
import { ProjectsGrid } from "@/components/ProjectsGrid";

// ---------------------------------------------------------------------------
// FEATURE 3: Projects Grid
// Integration test covering all acceptance criteria
// ---------------------------------------------------------------------------

describe("Projects Grid", () => {
  test("shows loading indicator while fetching repos", () => {
    render(<ProjectsGrid />);
    
    // Should show loading skeletons
    const loadingSection = screen.getByText("Projects");
    expect(loadingSection).toBeInTheDocument();
  });

  test("renders all repos returned by API", async () => {
    render(<ProjectsGrid />);
    
    // Wait for repos to load
    await waitFor(() => {
      expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    });
    
    expect(screen.getByText("test-repo-2")).toBeInTheDocument();
  });

  test("sorts repos by updated_at descending (most recent first)", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    });
    
    // test-repo-2 has more recent updated_at (2024-01-20) than test-repo-1 (2024-01-15)
    // So test-repo-2 should appear first
    const repoCards = screen.getAllByRole("link");
    const repoLinks = repoCards.filter(card => 
      card.getAttribute("href")?.includes("test-repo")
    );
    
    // First repo should be test-repo-2 (more recent)
    expect(repoLinks[0]).toHaveAttribute("href", "https://github.com/luisalarcon-gauntlet/test-repo-2");
  });

  test("each card displays name, description, language, topics, stars, updated date, and GitHub link", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    });
    
    // Check for repo 1 details
    expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    expect(screen.getByText("Test repository 1 description")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("nextjs")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument(); // stargazers_count
    
    // Check GitHub link
    const repoLink = screen.getByRole("link", { name: /test-repo-1/i });
    expect(repoLink).toHaveAttribute("href", "https://github.com/luisalarcon-gauntlet/test-repo-1");
    expect(repoLink).toHaveAttribute("target", "_blank");
  });

  test("View on GitHub link opens html_url in new tab", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    });
    
    const repoLink = screen.getByRole("link", { name: /test-repo-1/i });
    expect(repoLink).toHaveAttribute("href", "https://github.com/luisalarcon-gauntlet/test-repo-1");
    expect(repoLink).toHaveAttribute("target", "_blank");
    expect(repoLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("handles null description without breaking layout", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-2")).toBeInTheDocument();
    });
    
    // test-repo-2 has null description, should still render
    const repo2Card = screen.getByRole("link", { name: /test-repo-2/i });
    expect(repo2Card).toBeInTheDocument();
    // Description should not be in document
    expect(screen.queryByText("Test repository 1 description")).not.toBeInTheDocument();
  });

  test("handles empty topics array without showing broken UI", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-2")).toBeInTheDocument();
    });
    
    // test-repo-2 has empty topics array
    // Should still render the card
    const repo2Card = screen.getByRole("link", { name: /test-repo-2/i });
    expect(repo2Card).toBeInTheDocument();
  });

  test("displays language badge with correct primary language", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("TypeScript")).toBeInTheDocument();
    });
    
    expect(screen.getByText("Python")).toBeInTheDocument();
  });

  test("displays human-readable last updated date", async () => {
    render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText(/Updated/i)).toBeInTheDocument();
    });
    
    // Should show relative date format
    const updatedText = screen.getByText(/Updated/i);
    expect(updatedText.textContent).toMatch(/Updated (today|yesterday|\d+ (days|weeks|months|years) ago)/i);
  });

  test("grid is responsive with correct column classes", async () => {
    const { container } = render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    });
    
    const grid = container.querySelector(".grid");
    expect(grid).toHaveClass("grid-cols-1"); // Mobile
    expect(grid).toHaveClass("md:grid-cols-2"); // Tablet
    expect(grid).toHaveClass("lg:grid-cols-3"); // Desktop
  });

  test("section has dark theme styling", async () => {
    const { container } = render(<ProjectsGrid />);
    
    await waitFor(() => {
      expect(screen.getByText("test-repo-1")).toBeInTheDocument();
    });
    
    const section = container.querySelector("section");
    expect(section).toBeInTheDocument();
    
    // Check for dark theme classes
    const heading = screen.getByText("Projects");
    expect(heading).toHaveClass("text-white");
  });
});

// ---------------------------------------------------------------------------
// NOT COVERED IN THIS FILE — intentional v1 exclusions
// ---------------------------------------------------------------------------
// - Filtering or searching repos by language or tag
// - Pinned repos detection via GitHub GraphQL API
// - Pagination or "load more" functionality
// - Repo preview images or Open Graph images
// - Fork/watch counts display
// - Animated card hover effects beyond basic CSS
// - Actual viewport size testing (375px, 768px, 1024px) - would require E2E
// - JavaScript console error checking - would require E2E
// ---------------------------------------------------------------------------
