"use client";

import { useEffect, useState } from "react";
import { getRepositories } from "@/lib/api";
import type { Repository } from "@/types";
import { ProjectCard } from "./ProjectCard";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { ErrorMessage } from "./ErrorMessage";

export function ProjectsGrid() {
  const [repos, setRepos] = useState<Repository[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRepos = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await getRepositories();
      
      if (response.error) {
        setError(response.error);
        setRepos(null);
      } else if (response.data) {
        // Sort: pinned first, then by updated_at descending
        const sorted = [...response.data.repos].sort((a, b) => {
          if (a.is_pinned && !b.is_pinned) return -1;
          if (!a.is_pinned && b.is_pinned) return 1;
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        });
        setRepos(sorted);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load projects. Please try again.");
      setRepos(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRepos();
  }, []);

  if (isLoading) {
    return (
      <section id="projects" className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-white">Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <LoadingSkeleton key={i} />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="projects" className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-white">Projects</h2>
          <ErrorMessage message="Could not load projects. Please try again." onRetry={fetchRepos} />
        </div>
      </section>
    );
  }

  if (!repos || repos.length === 0) {
    return (
      <section id="projects" className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-white">Projects</h2>
          <p className="text-gray-400">No projects found.</p>
        </div>
      </section>
    );
  }

  return (
    <section id="projects" className="py-20 px-4">
      <div className="container mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-white">Projects</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {repos.map((repo) => (
            <ProjectCard key={repo.id} repo={repo} />
          ))}
        </div>
      </div>
    </section>
  );
}
