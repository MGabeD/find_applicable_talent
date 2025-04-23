"use client";

import { useRef, useEffect, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { Loader2, RefreshCw } from "lucide-react";
import Link from "next/link";

import { CandidatePanel } from "@/components/candidate-panel";
import { CandidateDialog } from "@/components/candidate-dialog";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/use-toast";
import RoleBuilder from "@/components/role-builder";
import RoleViewer from "@/components/role-viewer";

import type { Candidate, Filter } from "@/lib/types";

interface Role {
  title: string;
  justification: string;
  rubric: string;
}

export default function IntelligentFilteringPage() {
  const [activeFilters, setActiveFilters] = useState<Filter[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [rolesLoading, setRolesLoading] = useState(true);
  const [roundRobinLoading, setRoundRobinLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("candidates");
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(
    null
  );
  const [dialogOpen, setDialogOpen] = useState(false);

  const fetchRoles = async () => {
    setRolesLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/candidates/reasoner/roles"
      );
      if (!response.ok) throw new Error(`Error: ${response.status}`);
      const data = await response.json();
      setRoles(data);
    } catch {
      setRoles([]);
    } finally {
      setRolesLoading(false);
    }
  };

  const fetchCandidates = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        "http://localhost:8000/candidates/reasoner/load",
        {
          method: "POST",
        }
      );
      if (!response.ok) throw new Error(`Error: ${response.status}`);
      const { tagged_candidates } = await response.json();
      setCandidates(tagged_candidates);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch candidates"
      );
      toast({
        title: "Error",
        description: "Failed to load reasoned candidates. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
    fetchRoles();
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/candidates/reasoner/reset",
        {
          method: "POST",
        }
      );

      if (!response.ok) throw new Error(`Reset failed: ${response.status}`);

      toast({
        title: "Reasoner Reset",
        description: "Recruitment Reasoner has been reset.",
      });

      await fetchCandidates();
      await fetchRoles();
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to reset reasoner. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/candidates/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Candidate not found");

      setCandidates(candidates.filter((c) => c.id !== id));
      toast({
        title: "Success",
        description: "Candidate deleted successfully",
      });
    } catch {
      toast({
        title: "Error",
        description: "Failed to delete candidate",
        variant: "destructive",
      });
    }
  };

  const handleSelect = async (id: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/candidates/selected/${id}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) throw new Error("Error selecting candidate");

      const data = await response.json();
      toast({ title: "Success", description: data.detail });
    } catch {
      toast({
        title: "Error",
        description: "Failed to select candidate",
        variant: "destructive",
      });
    }
  };

  const handleShowDetails = (candidate: Candidate) => {
    setSelectedCandidate(candidate);
    setDialogOpen(true);
  };

  const parentRef = useRef<HTMLDivElement>(null);
  const columnCount = 3;

  const rowVirtualizer = useVirtualizer({
    count: Math.ceil(candidates.length / columnCount),
    getScrollElement: () => parentRef.current,
    estimateSize: () => 300,
    overscan: 5,
    enabled: activeTab === "candidates",
  });

  useEffect(() => {
    if (activeTab === "candidates") {
      requestAnimationFrame(() => rowVirtualizer.measure());
    }
  }, [activeTab, rowVirtualizer]);

  return (
    <main className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">AI-Tagged Candidates</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRefresh} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Reset Reasoner
          </Button>
          <Button asChild>
            <Link href="/">View Base Candidates</Link>
          </Button>
        </div>
      </div>

      {roles.length > 0 && (
        <div className="flex justify-end mb-4">
          <Button
            onClick={() => setRoundRobinLoading(true)}
            disabled={roundRobinLoading}
          >
            {roundRobinLoading && (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            )}
            RoundRobin Candidates
          </Button>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="candidates">Candidates</TabsTrigger>
          <TabsTrigger value="set_roles">Set Roles</TabsTrigger>
          {roles.length > 0 && (
            <TabsTrigger value="view_roles">View Roles</TabsTrigger>
          )}
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
              <p className="text-muted-foreground">
                No tagged candidates found
              </p>
            </div>
          ) : (
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
                          onDelete={handleDelete}
                          onSelect={handleSelect}
                          onShowDetails={handleShowDetails}
                        />
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="set_roles">
          <RoleBuilder />
        </TabsContent>

        <TabsContent value="view_roles">
          {roles.length === 0 ? (
            <div className="p-4 text-muted-foreground">
              No roles available yet.
            </div>
          ) : (
            <RoleViewer roles={roles} loading={rolesLoading} />
          )}
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
