import { NextResponse } from "next/server"
import { candidates } from "@/lib/data"

export async function GET() {
  // In a real app, this would fetch from your actual API
  return NextResponse.json(candidates)
}
