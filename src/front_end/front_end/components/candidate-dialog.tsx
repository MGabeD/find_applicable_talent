import { DialogContent, DialogHeader, DialogTitle, Dialog } from "@/components/ui/dialog"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import type { Candidate } from "@/lib/types"

interface CandidateDialogProps {
  candidate: Candidate
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CandidateDialog({ candidate, open, onOpenChange }: CandidateDialogProps) {
  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={candidate.avatar || "/placeholder.svg"} alt={candidate.name} />
              <AvatarFallback>{candidate.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <DialogTitle className="text-2xl">{candidate.name}</DialogTitle>
              <p className="text-muted-foreground">{candidate.title}</p>
            </div>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Contact Information</h3>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Email:</span> {candidate.email}
              </div>
              <div>
                <span className="font-medium">Phone:</span> {candidate.phone}
              </div>
              <div>
                <span className="font-medium">Location:</span> {candidate.location}
              </div>
              <div>
                <span className="font-medium">Submitted:</span> {formatDate(candidate.submitted_at)}
              </div>
            </div>

            <Separator />

            <h3 className="text-lg font-semibold">Work Preferences</h3>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Work Availability:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {candidate.work_availability.map((item) => (
                    <Badge key={item} variant="outline">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
              {candidate.annual_salary_expectation && (
                <div>
                  <span className="font-medium">Salary Expectation:</span>{" "}
                  {candidate.annual_salary_expectation.amount.toLocaleString()}{" "}
                  {candidate.annual_salary_expectation.currency}
                </div>
              )}
            </div>

            <Separator />

            <h3 className="text-lg font-semibold">Skills</h3>
            <div className="flex flex-wrap gap-1">
              {candidate.skills.map((skill) => (
                <Badge key={skill} variant="secondary">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>

          {/* Education */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Education</h3>
            <div>
              <span className="font-medium">Highest Level:</span> {candidate.education.highest_level}
            </div>

            {candidate.education.degrees.map((degree, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-2">
                <div className="font-semibold">
                  {degree.degree} in {degree.subject}
                </div>
                <div>
                  <span className="font-medium">School:</span> {degree.school}
                  {degree.isTop50 && (
                    <Badge className="ml-2" variant="outline">
                      Top 50
                    </Badge>
                  )}
                </div>
                <div>
                  <span className="font-medium">GPA:</span> {degree.gpa}
                </div>
                <div>
                  <span className="font-medium">Duration:</span> {formatDate(degree.startDate)} -{" "}
                  {formatDate(degree.endDate)}
                </div>
                {degree.originalSchool !== degree.school && (
                  <div>
                    <span className="font-medium">Original School:</span> {degree.originalSchool}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
