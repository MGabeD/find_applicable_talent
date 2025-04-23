"use client";

import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface Role {
  title: string;
  justification: string;
  rubric: string;
}

interface RoleViewerProps {
  roles: Role[];
  loading?: boolean;
  onRefresh?: () => void;
}

export default function RoleViewer({ roles, loading = false, onRefresh }: RoleViewerProps) {
  return (
    <div className="space-y-6 p-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Current Roles</h2>
        {onRefresh && (
          <Button onClick={onRefresh} variant="outline" disabled={loading}>
            <Loader2 className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        )}
      </div>

      {loading ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : roles.length === 0 ? (
        <div className="space-y-3 mt-4">
          <p className="text-muted-foreground text-sm">
            No roles found. Use the <span className="font-semibold">Set Roles</span> tab to define roles for your organization.
          </p>
          <Textarea
            readOnly
            value="Go to the Set Roles tab to generate or define initial roles before viewing them here."
            className="bg-muted/50"
          />
        </div>
      ) : (
        <ul className="space-y-4">
          {roles.map((role, idx) => (
            <li key={idx} className="border p-4 rounded bg-muted/50">
              <h3 className="font-bold">{role.title}</h3>
              <p className="text-sm mt-1">{role.justification}</p>
              <div className="mt-3">
                <label className="block text-sm font-medium mb-1">Rubric</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="View rubric" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rubric">{role.rubric}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
