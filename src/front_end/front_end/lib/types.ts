export type Operator = "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "contains"

export interface Filter {
  path: string
  operator: Operator
  value: string
}

export interface WorkExperience {
  company?: string
  roleName?: string
}

export interface Degree {
  degree?: string
  subject?: string
  school?: string
  gpa?: number
  startDate?: string // use ISO string format like "2020-01-01"
  endDate?: string   // same here
  originalSchool?: string
  isTop50: boolean
}

export interface Education {
  highest_level?: string
  degrees?: Degree[]
}

export interface Candidate {
  name?: string
  email?: string
  phone?: string
  location?: string
  submitted_at?: string // ISO string e.g. "2025-01-28T05:15:13.000Z"
  work_availability?: string[]
  annual_salary_expectation?: {
    [key: string]: number | string // e.g., { full-time: "$100000" } or currency info
  }
  work_experiences?: WorkExperience[]
  education?: Education
  skills?: string[]
}
