"use client";

import { useState } from "react";
import { Loader2, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/components/ui/use-toast";

interface RoleBuilderProps {
  onRolesUpdated?: () => void;
}

interface Role {
  title: string;
  justification: string;
  rubric: string;
}

export default function RoleBuilder({ onRolesUpdated }: RoleBuilderProps) {
  const [userContext, setUserContext] = useState("");
  const [userFeedback, setUserFeedback] = useState("");
  const [roles, setRoles] = useState<Role[]>([]);
  const [roleLoading, setRoleLoading] = useState(false);
  const [hasSubmittedContext, setHasSubmittedContext] = useState(false);

  const handleDefineRoles = async () => {
    setRoleLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/candidates/reasoner/define_roles",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_context: userContext }),
        }
      );

      if (!response.ok) throw new Error(`Error: ${response.status}`);

      const data = await response.json();
      setRoles(data.roles);
      setHasSubmittedContext(true);
      toast({ title: "Roles Defined" });
    } catch {
      toast({
        title: "Error",
        description: "Failed to define roles",
        variant: "destructive",
      });
    } finally {
      setRoleLoading(false);
    }
  };

  const handleRefineRoles = async () => {
    setRoleLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/candidates/reasoner/refine_roles",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_roles: roles,
            user_feedback: userFeedback,
          }),
        }
      );

      if (!response.ok) throw new Error(`Error: ${response.status}`);

      const data = await response.json();
      setRoles(data.roles);
      setUserFeedback("");
      toast({ title: "Roles Refined" });
    } catch {
      toast({
        title: "Error",
        description: "Failed to refine roles",
        variant: "destructive",
      });
    } finally {
      setRoleLoading(false);
    }
  };

  const handleUpdateRoleCriteria = async () => {
    setRoleLoading(true);
    try {
      const payload = {
        roles: roles.map(({ title, justification }) => ({
          title,
          justification,
        })),
      };

      const response = await fetch(
        "http://localhost:8000/candidates/reasoner/update_roles_with_criteria",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) throw new Error(`Error: ${response.status}`);

      toast({
        title: "Criteria Updated",
        description: "Rubrics have been generated for all roles.",
      });

      if (onRolesUpdated) onRolesUpdated();
    } catch {
      toast({
        title: "Error",
        description: "Failed to update role criteria.",
        variant: "destructive",
      });
    } finally {
      setRoleLoading(false);
    }
  };

  const handleRestart = () => {
    setUserContext("");
    setUserFeedback("");
    setRoles([]);
    setHasSubmittedContext(false);
  };

  return (
    <div className="space-y-6 p-4">
      {!hasSubmittedContext ? (
        <div>
          <h2 className="text-xl font-semibold">What does your company do?</h2>
          <Textarea
            value={userContext}
            onChange={(e) => setUserContext(e.target.value)}
            placeholder="e.g. We build AI tools for small businesses to automate operations."
            className="mt-2"
          />
          <Button
            onClick={handleDefineRoles}
            disabled={!userContext || roleLoading}
            className="mt-4"
          >
            {roleLoading ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : null}
            Generate Roles
          </Button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Proposed Roles</h2>
            <Button variant="outline" onClick={handleRestart}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Restart
            </Button>
          </div>
          {roleLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <ul className="space-y-3 mt-2">
              {roles.map((role, idx) => (
                <li key={idx} className="border p-3 rounded bg-muted/50">
                  <p className="font-bold">{role.title}</p>
                  <p className="text-sm">{role.justification}</p>
                </li>
              ))}
            </ul>
          )}

          <div>
            <h3 className="text-md font-medium">
              Give feedback to refine these roles:
            </h3>
            <Textarea
              value={userFeedback}
              onChange={(e) => setUserFeedback(e.target.value)}
              placeholder="e.g. I want more emphasis on backend systems or remove sales roles."
            />
            <div className="flex gap-3 mt-2 flex-wrap">
              <Button
                onClick={handleRefineRoles}
                disabled={!userFeedback || roleLoading}
              >
                {roleLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                Refine Roles
              </Button>
              <Button
                variant="secondary"
                onClick={handleUpdateRoleCriteria}
                disabled={roles.length === 0 || roleLoading}
              >
                {roleLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                Update Criteria for All Roles
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
