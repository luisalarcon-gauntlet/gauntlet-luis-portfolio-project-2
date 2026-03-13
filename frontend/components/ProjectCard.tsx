"use client";

import type { Repository } from "@/types";
import { LanguageBadge } from "./LanguageBadge";
import { TopicTag } from "./TopicTag";

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) return "Updated today";
  if (diffInDays === 1) return "Updated yesterday";
  if (diffInDays < 7) return `Updated ${diffInDays} days ago`;
  if (diffInDays < 30) return `Updated ${Math.floor(diffInDays / 7)} weeks ago`;
  if (diffInDays < 365) return `Updated ${Math.floor(diffInDays / 30)} months ago`;
  return `Updated ${Math.floor(diffInDays / 365)} years ago`;
}

export function ProjectCard({ repo }: { repo: Repository }) {
  const displayTopics = repo.topics.slice(0, 4); // Show up to 4 tags

  return (
    <a
      href={repo.html_url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-gray-900 border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-xl font-bold text-white hover:text-gray-300 transition-colors">
          {repo.name}
        </h3>
        {repo.is_pinned && (
          <span className="text-xs text-gray-500">📌</span>
        )}
      </div>
      
      {repo.description && (
        <p className="text-gray-400 mb-4 line-clamp-2">{repo.description}</p>
      )}

      <div className="flex flex-wrap gap-2 mb-4">
        {repo.primary_language && (
          <LanguageBadge language={repo.primary_language} />
        )}
        {displayTopics.map((topic) => (
          <TopicTag key={topic} topic={topic} />
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            {repo.stargazers_count}
          </span>
          <span>{formatDate(repo.updated_at)}</span>
        </div>
        <span className="text-gray-600 hover:text-gray-400 transition-colors">
          View on GitHub →
        </span>
      </div>
    </a>
  );
}
