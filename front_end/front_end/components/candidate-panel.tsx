import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import type { Candidate } from "@/lib/types"

interface CandidatePanelProps {
  candidate: Candidate
}

export function CandidatePanel({ candidate }: CandidatePanelProps) {
  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center gap-4 pb-2">
        <Avatar className="h-12 w-12">
          <AvatarImage src={candidate.avatar || "/placeholder.svg"} alt={candidate.name} />
          <AvatarFallback>{candidate.name.charAt(0)}</AvatarFallback>
        </Avatar>
        <div>
          <h3 className="font-semibold">{candidate.name}</h3>
          <p className="text-sm text-muted-foreground">{candidate.title}</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            {candidate.skills.map((skill) => (
              <Badge key={skill} variant="secondary" className="text-xs">
                {skill}
              </Badge>
            ))}
          </div>
          <div className="text-sm">
            <span className="font-medium">Experience:</span> {candidate.experience} years
          </div>
          <div className="text-sm">
            <span className="font-medium">Location:</span> {candidate.location}
          </div>
          <div className="text-sm">
            <span className="font-medium">Email:</span> {candidate.email}
          </div>
          <div className="text-sm">
            <span className="font-medium">Submitted:</span> {formatDate(candidate.submitted_at)}
          </div>
          <div className="text-sm">
            <span className="font-medium">Education:</span> {candidate.education.highest_level} in{" "}
            {candidate.education.degrees[0].subject}
          </div>
          <div className="text-sm">
            <span className="font-medium">Salary Expectation:</span>{" "}
            {candidate.annual_salary_expectation?.amount.toLocaleString()}{" "}
            {candidate.annual_salary_expectation?.currency}
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button size="sm" className="w-1/2">
          Select Candidate
        </Button>
        <Button size="sm" className="w-1/2 ml-2 bg-red-600">
          Delete Candidate
        </Button>
      </CardFooter>
      <CardFooter>
      </CardFooter>
    </Card>
  )
}
