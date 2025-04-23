import { useRef, useEffect } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { CandidatePanel } from "@/components/candidate-panel";
import type { Candidate } from "@/lib/types";

interface VirtualizedCandidateGridProps {
  candidates: Candidate[];
  loading?: boolean;
  error?: string | null;
  columnCount?: number;
  onDelete?: (id: string) => void;
  onSelect?: (id: string) => void;
  onShowDetails?: (candidate: Candidate) => void;
  heightPx?: number;
}

export function VirtualizedCandidateGrid({
  candidates,
  loading = false,
  error = null,
  columnCount = 3,
  onDelete,
  onSelect,
  onShowDetails,
  heightPx = 70 * 16,
}: VirtualizedCandidateGridProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  const rowVirtualizer = useVirtualizer({
    count: Math.ceil(candidates.length / columnCount),
    getScrollElement: () => parentRef.current,
    estimateSize: () => 300,
    overscan: 5,
  });

  useEffect(() => {
    requestAnimationFrame(() => rowVirtualizer.measure());
  }, [candidates]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin h-8 w-8 border-4 border-gray-300 border-t-primary rounded-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8 border rounded-lg bg-red-50">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (candidates.length === 0) {
    return (
      <div className="text-center p-8 border rounded-lg">
        <p className="text-muted-foreground">No candidates found</p>
      </div>
    );
  }

  return (
    <div ref={parentRef} className="max-h-[70vh] overflow-y-auto p-2">
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          position: "relative",
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const rowIndex = virtualRow.index;
          const itemsInRow = candidates.slice(
            rowIndex * columnCount,
            rowIndex * columnCount + columnCount
          );

          return (
            <div
              key={rowIndex}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                transform: `translateY(${virtualRow.start}px)`,
              }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-4 gap-y-2"
            >
              {itemsInRow.map((candidate) => (
                <CandidatePanel
                  key={candidate.id}
                  candidate={candidate}
                  onDelete={onDelete}
                  onSelect={onSelect}
                  onShowDetails={onShowDetails}
                />
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}
