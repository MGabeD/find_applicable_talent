import { NextResponse } from "next/server"

export async function POST(request: Request, { params }: { params: { id: string } }) {
  const id = params.id

  // In a real app, this would call your actual API
  // For now, we'll just simulate a successful response
  return new NextResponse(null, { status: 200 })
}
