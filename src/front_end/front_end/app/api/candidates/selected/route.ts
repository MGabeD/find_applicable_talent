import { NextResponse } from "next/server"
import { candidates } from "@/lib/data"

export async function GET() {
  // In a real app, this would fetch from your actual API
  // For now, we'll return a subset of candidates as "selected"
  const selectedCandidates = candidates.slice(0, 2)
  return NextResponse.json(selectedCandidates)
}
