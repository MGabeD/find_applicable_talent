"use client";

import { useEffect, useState } from "react";
import { Loader2, RefreshCw } from "lucide-react";
import Link from "next/link";

import { CandidatePanel } from "@/components/candidate-panel";
import { FilterBuilder } from "@/components/filter-builder";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CandidateDialog } from "@/components/candidate-dialog";
import { toast } from "@/components/ui/use-toast";
import type { Candidate } from "@/lib/types";

export default function Home() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(
    null
  );
  const [dialogOpen, setDialogOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fetch candidates from API
  useEffect(() => {
    const fetchCandidates = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch("http://localhost:8000/candidates");
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        const data = await response.json();
        setCandidates(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch candidates"
        );
        toast({
          title: "Error",
          description: "Failed to fetch candidates. Please try again.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCandidates();
  }, [refreshTrigger]);

  // Handle delete candidate
  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`/api/candidates/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      // Remove from local state
      setCandidates(candidates.filter((candidate) => candidate.id !== id));
      toast({
        title: "Success",
        description: "Candidate deleted successfully",
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to delete candidate. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle select candidate
  const handleSelect = async (id: string) => {
    try {
      const response = await fetch(`/api/candidates/selected/${id}`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      toast({
        title: "Success",
        description: "Candidate selected successfully",
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to select candidate. Please try again.",
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

  // Handle filter application
  const handleApplyFilters = (filters: any[]) => {
    // In a real implementation, you would send these filters to the backend
    // For now, we'll just log them
    console.log("Filters to send to backend:", filters);
    toast({
      title: "Filters Applied",
      description: `${filters.length} filters applied. This would be sent to the backend.`,
    });
  };

  return (
    <main className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Candidate Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRefresh} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
          <Button asChild>
            <Link href="/selected">View Selected Candidates</Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="candidates">
        <TabsList className="mb-4">
          <TabsTrigger value="candidates">Candidates</TabsTrigger>
          <TabsTrigger value="filters">Filters</TabsTrigger>
        </TabsList>

        <TabsContent value="candidates">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : error ? (
            <div className="text-center p-8 border rounded-lg bg-red-50">
              <p className="text-red-500">{error}</p>
              <Button
                variant="outline"
                onClick={handleRefresh}
                className="mt-4"
              >
                Try Again
              </Button>
            </div>
          ) : candidates.length === 0 ? (
            <div className="text-center p-8 border rounded-lg">
              <p className="text-muted-foreground">No candidates found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[70vh] overflow-y-auto p-2">
              {candidates.map((candidate) => (
                <CandidatePanel
                  key={candidate.id}
                  candidate={candidate}
                  onDelete={handleDelete}
                  onSelect={handleSelect}
                  onShowDetails={handleShowDetails}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="filters">
          <FilterBuilder onApplyFilters={handleApplyFilters} />
        </TabsContent>
      </Tabs>

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
