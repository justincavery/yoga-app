export function CardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  );
}

export function GridSkeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

export function PoseCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
      <div className="h-48 bg-gray-200"></div>
      <div className="p-4">
        <div className="h-5 bg-gray-200 rounded w-3/4 mb-3"></div>
        <div className="flex gap-2 mb-3">
          <div className="h-6 bg-gray-200 rounded w-20"></div>
          <div className="h-6 bg-gray-200 rounded w-16"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>
    </div>
  );
}

export function SequenceCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
      <div className="h-48 bg-gray-200"></div>
      <div className="p-6">
        <div className="h-6 bg-gray-200 rounded w-2/3 mb-3"></div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-4/5 mb-4"></div>
        <div className="flex gap-2 mb-4">
          <div className="h-6 bg-gray-200 rounded w-20"></div>
          <div className="h-6 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-10 bg-gray-200 rounded w-full"></div>
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="animate-pulse">
      <div className="h-10 bg-gray-200 rounded mb-4"></div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-16 bg-gray-100 rounded mb-2"></div>
      ))}
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
      <div className="flex items-center justify-between mb-3">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
        <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
      </div>
      <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
      <div className="h-3 bg-gray-200 rounded w-32"></div>
    </div>
  );
}

export default {
  CardSkeleton,
  GridSkeleton,
  PoseCardSkeleton,
  SequenceCardSkeleton,
  TableSkeleton,
  StatCardSkeleton,
};
