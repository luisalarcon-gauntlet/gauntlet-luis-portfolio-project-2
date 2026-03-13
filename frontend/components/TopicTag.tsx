export function TopicTag({ topic }: { topic: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700">
      {topic}
    </span>
  );
}
