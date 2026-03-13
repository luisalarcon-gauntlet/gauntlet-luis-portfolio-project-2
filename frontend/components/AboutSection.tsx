"use client";

export function AboutSection() {
  return (
    <section id="about" className="py-20 px-4 bg-gray-950">
      <div className="container mx-auto max-w-3xl">
        <h2 className="text-3xl font-bold mb-6 text-white">About</h2>
        <p className="text-gray-400 text-lg leading-relaxed mb-6">
          I'm a full-stack and AI engineer participating in the Gauntlet AI program, 
          based in Austin, TX. I build modern web applications and AI-powered solutions 
          using cutting-edge technologies. My work focuses on creating efficient, scalable 
          systems that solve real-world problems.
        </p>
        <a
          href="/resume.pdf"
          download
          className="inline-flex items-center px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Download Resume
        </a>
      </div>
    </section>
  );
}
