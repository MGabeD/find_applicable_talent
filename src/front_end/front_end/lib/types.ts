export type Operator = "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "contains"

export interface Filter {
  path: string
  operator: Operator
  value: string
}

export interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  location: string
  submitted_at: string
  work_availability: string[]
  annual_salary_expectation?: { amount: number; currency: string }
  skills: string[]
  title: string
  experience: number
  education: {
    highest_level: string
    degrees: Array<{
      degree: string
      subject: string
      school: string
      gpa: number
      startDate: string
      endDate: string
      originalSchool: string
      isTop50: boolean
    }>
  }
  avatar: string
}
