/**
 * Language badge component with color mapping
 */

// Language color mapping (from GitHub's language colors)
const LANGUAGE_COLORS: Record<string, string> = {
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Python: "#3572A5",
  Java: "#b07219",
  "C++": "#f34b7d",
  C: "#555555",
  Go: "#00ADD8",
  Rust: "#dea584",
  Ruby: "#701516",
  PHP: "#4F5D95",
  Swift: "#FA7343",
  Kotlin: "#A97BFF",
  Dart: "#00B4AB",
  HTML: "#e34c26",
  CSS: "#563d7c",
  Shell: "#89e051",
  Dockerfile: "#384d54",
  Makefile: "#427819",
  Vue: "#4fc08d",
  React: "#61dafb",
  Angular: "#dd0031",
  Svelte: "#ff3e00",
};

export function LanguageBadge({ language }: { language: string | null }) {
  if (!language) return null;

  const color = LANGUAGE_COLORS[language] || "#6b7280"; // Default gray

  return (
    <span
      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: `${color}20`,
        color: color,
        borderColor: color,
        borderWidth: "1px",
      }}
    >
      {language}
    </span>
  );
}
