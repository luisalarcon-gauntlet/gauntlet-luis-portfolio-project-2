export function LoadingSkeleton() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-800 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-800 rounded w-full mb-2"></div>
      <div className="h-4 bg-gray-800 rounded w-5/6 mb-4"></div>
      <div className="flex gap-2 mb-4">
        <div className="h-6 bg-gray-800 rounded w-16"></div>
        <div className="h-6 bg-gray-800 rounded w-20"></div>
      </div>
      <div className="flex items-center justify-between">
        <div className="h-4 bg-gray-800 rounded w-24"></div>
        <div className="h-4 bg-gray-800 rounded w-20"></div>
      </div>
    </div>
  );
}
