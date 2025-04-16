import { CandidatePanel } from "@/components/candidate-panel"
import { FilterBuilder } from "@/components/filter-builder"
import { candidates } from "@/lib/data"

export default function Home() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Candidate Filtering System</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Candidates</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {candidates.map((candidate) => (
              <CandidatePanel key={candidate.id} candidate={candidate} />
            ))}
          </div>
        </div>

        <div className="lg:col-span-1">
          <FilterBuilder />
        </div>
      </div>
    </main>
  )
}
