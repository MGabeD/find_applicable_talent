"use client";

import { useEffect, useState } from "react";
import { Loader2, RefreshCw, ArrowLeft } from "lucide-react";
import Link from "next/link";

import { CandidatePanel } from "@/components/candidate-panel";
import { Button } from "@/components/ui/button";
import { CandidateDialog } from "@/components/candidate-dialog";
import { toast } from "@/components/ui/use-toast";
import type { Candidate } from "@/lib/types";

export default function SelectedCandidates() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(
    null
  );
  const [dialogOpen, setDialogOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fetch selected candidates from API
  useEffect(() => {
    const fetchSelectedCandidates = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(
          "http://localhost:8000/candidates/selected/"
        );
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        const data = await response.json();
        setCandidates(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to fetch selected candidates"
        );
        toast({
          title: "Error",
          description: "Failed to fetch selected candidates. Please try again.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSelectedCandidates();
  }, [refreshTrigger]);

  // Handle delete candidate
  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/candidates/selected/${id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Candidate not in selected list");
        }
        throw new Error(`Error: ${response.status}`);
      }

      // Remove from local state
      setCandidates(candidates.filter((candidate) => candidate.id !== id));
      toast({
        title: "Success",
        description: "Candidate removed from selection",
      });
    } catch (err) {
      toast({
        title: "Error",
        description:
          err instanceof Error ? err.message : "Failed to remove candidate",
        variant: "destructive",
      });
    }
  };

  // Handle show candidate details
  const handleShowDetails = (candidate: Candidate) => {
    setSelectedCandidate(candidate);
    setDialogOpen(true);
  };

  // Handle refresh
  const handleRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <main className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" asChild>
            <Link href="/">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <h1 className="text-3xl font-bold">Selected Candidates</h1>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : error ? (
        <div className="text-center p-8 border rounded-lg bg-red-50">
          <p className="text-red-500">{error}</p>
          <Button variant="outline" onClick={handleRefresh} className="mt-4">
            Try Again
          </Button>
        </div>
      ) : candidates.length === 0 ? (
        <div className="text-center p-8 border rounded-lg">
          <p className="text-muted-foreground">No selected candidates found</p>
          <Button asChild className="mt-4">
            <Link href="/">Go back to all candidates</Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[70vh] overflow-y-auto p-2">
          {candidates.map((candidate) => (
            <CandidatePanel
              key={candidate.id}
              candidate={candidate}
              onDelete={handleDelete}
              onShowDetails={handleShowDetails}
              isSelected={true}
            />
          ))}
        </div>
      )}

      {selectedCandidate && (
        <CandidateDialog
          candidate={selectedCandidate}
          open={dialogOpen}
          onOpenChange={setDialogOpen}
        />
      )}
    </main>
  );
}
