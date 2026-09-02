function Bar({ className }: { className: string }) {
  return <div className={`animate-pulse rounded-md bg-surface-raised ${className}`} />;
}

export function RepoDashboardSkeleton() {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-3">
        <Bar className="h-7 w-48" />
        <Bar className="h-4 w-64" />
        <Bar className="h-4 w-96" />
      </div>
      <div className="grid grid-cols-2 gap-px overflow-hidden rounded-md border border-border sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex flex-col gap-2 px-4 py-3">
            <Bar className="h-3 w-16" />
            <Bar className="h-5 w-10" />
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-3">
        <Bar className="h-2 w-full" />
        <Bar className="h-4 w-56" />
      </div>
    </div>
  );
}
