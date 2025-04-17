// CandidateDialog.tsx
"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { Candidate, WorkExperience, Degree } from "@/lib/types";

/**
 * CandidateDialog
 * ---------------
 * Displays **all** information we have for a single candidate in a scroll‑able modal.
 *
 * Props
 * -----
 * `candidate` – the `Candidate` object whose details we want to inspect.
 * `open`      – boolean – whether the dialog should be visible.
 * `onOpenChange` – callback to control outside state.
 */
interface CandidateDialogProps {
  candidate: Candidate;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CandidateDialog({
  candidate,
  open,
  onOpenChange,
}: CandidateDialogProps) {
  /* -------------------------------------------------------------------- */
  /* Helpers                                                              */
  /* -------------------------------------------------------------------- */

  const formatDate = (date?: string) => {
    if (!date) return "—";
    const parsed = new Date(date);
    return isNaN(parsed.getTime()) ? date : parsed.toLocaleDateString();
  };

  const formatSalary = (amount?: number, workType?: string) => {
    if (amount === undefined) return "—";
    const formatter = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    });
    return `${formatter.format(amount)} ${workType ?? ""}`.trim();
  };

  const hasExperience = (candidate.work_experiences?.length ?? 0) > 0;
  const hasDegrees = (candidate.education?.degrees?.length ?? 0) > 0;

  /* -------------------------------------------------------------------- */
  /* Render                                                               */
  /* -------------------------------------------------------------------- */

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* Tailwind: responsive width & scrollable body */}
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage
                src="/placeholder.svg"
                alt={candidate?.name || "Candidate"}
              />
              <AvatarFallback>{candidate?.name?.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <DialogTitle className="text-2xl leading-tight">
                {candidate.name ?? "Unnamed Candidate"}
              </DialogTitle>
              <p className="text-muted-foreground text-sm">
                {hasExperience
                  ? candidate.work_experiences!.length > 1
                    ? `${
                        candidate.work_experiences![0].roleName ?? "Unknown"
                      } – ${
                        candidate.work_experiences!.at(-1)?.roleName ??
                        "Unknown"
                      }`
                    : candidate.work_experiences![0].roleName ?? "Unknown"
                  : "No experience recorded"}
              </p>
            </div>
          </div>
        </DialogHeader>

        {/* ---------------------------------------------------------------- */}
        {/* Contact & Meta                                                   */}
        {/* ---------------------------------------------------------------- */}
        <section className="space-y-1 mb-6">
          <h3 className="text-lg font-semibold">Contact & Meta</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
            <div>
              <span className="font-medium">Email:</span>{" "}
              {candidate.email ?? "—"}
            </div>
            <div>
              <span className="font-medium">Phone:</span>{" "}
              {candidate.phone ?? "—"}
            </div>
            <div>
              <span className="font-medium">Location:</span>{" "}
              {candidate.location ?? "—"}
            </div>
            <div>
              <span className="font-medium">Submitted:</span>{" "}
              {formatDate(candidate.submitted_at)}
            </div>
          </div>
        </section>

        <Separator />

        {/* ---------------------------------------------------------------- */}
        {/* Work Preferences                                                 */}
        {/* ---------------------------------------------------------------- */}
        <section className="space-y-2 my-6">
          <h3 className="text-lg font-semibold">Work Preferences</h3>
          {candidate.work_availability &&
            candidate.work_availability.length > 0 && (
              <div>
                <span className="font-medium">Availability:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {candidate.work_availability.map((item) => (
                    <Badge key={item} variant="outline">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          {candidate.annual_salary_expectation && (
            <div>
              <span className="font-medium">Salary Expectation:</span>{" "}
              {formatSalary(
                candidate.annual_salary_expectation.pay,
                candidate.annual_salary_expectation.work_type
              )}
            </div>
          )}
        </section>

        <Separator />

        {/* ---------------------------------------------------------------- */}
        {/* Skills                                                           */}
        {/* ---------------------------------------------------------------- */}
        {candidate.skills && candidate.skills.length > 0 && (
          <section className="space-y-2 my-6">
            <h3 className="text-lg font-semibold">Skills</h3>
            <div className="flex flex-wrap gap-1">
              {candidate.skills.map((skill) => (
                <Badge key={skill} variant="secondary">
                  {skill}
                </Badge>
              ))}
            </div>
          </section>
        )}

        {candidate.skills && candidate.skills.length > 0 && <Separator />}

        {/* ---------------------------------------------------------------- */}
        {/* Work Experience                                                  */}
        {/* ---------------------------------------------------------------- */}
        {hasExperience && (
          <section className="space-y-4 my-6">
            <h3 className="text-lg font-semibold">Work Experience</h3>
            {candidate.work_experiences!.map(
              (exp: WorkExperience, idx: number) => (
                <div
                  key={`${exp.company}-${idx}`}
                  className="border rounded-lg p-4 space-y-1"
                >
                  <div className="font-semibold text-sm">
                    {exp.roleName ?? "Unknown Role"}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {exp.company ?? "Unknown Company"}
                  </div>
                </div>
              )
            )}
          </section>
        )}

        {hasExperience && hasDegrees && <Separator />}

        {/* ---------------------------------------------------------------- */}
        {/* Education                                                        */}
        {/* ---------------------------------------------------------------- */}
        <section className="space-y-4 my-6">
          <h3 className="text-lg font-semibold">Education</h3>
          <div>
            <span className="font-medium">Highest Level:</span>{" "}
            {candidate.education?.highest_level ?? "—"}
          </div>

          {hasDegrees ? (
            candidate.education!.degrees!.map((degree: Degree, idx: number) => (
              <div
                key={`${degree.school}-${degree.degree}-${idx}`}
                className="border rounded-lg p-4 space-y-2"
              >
                <div className="font-semibold">
                  {degree.degree ?? "Unknown Degree"}
                  {degree.subject && ` in ${degree.subject}`}
                </div>
                {degree.school && (
                  <div>
                    <span className="font-medium">School:</span> {degree.school}
                    {(degree.isTop50 || degree.isTop25) && (
                      <>
                        {degree.isTop50 && (
                          <Badge className="ml-2" variant="outline">
                            Top 50
                          </Badge>
                        )}
                        {degree.isTop25 && (
                          <Badge className="ml-1" variant="outline">
                            Top 25
                          </Badge>
                        )}
                      </>
                    )}
                  </div>
                )}
                {degree.gpa !== undefined && (
                  <div>
                    <span className="font-medium">GPA:</span> {degree.gpa}
                  </div>
                )}
                <div>
                  <span className="font-medium">Duration:</span>{" "}
                  {`${formatDate(degree.startDate)} – ${formatDate(
                    degree.endDate
                  )}`}
                </div>
                {degree.originalSchool &&
                  degree.originalSchool !== degree.school && (
                    <div>
                      <span className="font-medium">Original School:</span>{" "}
                      {degree.originalSchool}
                    </div>
                  )}
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">
              No degrees recorded.
            </p>
          )}
        </section>
      </DialogContent>
    </Dialog>
  );
}
