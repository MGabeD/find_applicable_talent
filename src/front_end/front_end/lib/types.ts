export type Operator = "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "contains";

export interface Filter {
  path: string;
  operator: Operator;
  value: string;
  invert?: boolean;
}

export interface WorkExperience {
  company?: string;
  roleName?: string;
}

export interface Degree {
  degree?: string;
  subject?: string;
  school?: string;
  gpa?: number;
  startDate?: string;
  endDate?: string;
  originalSchool?: string;
  isTop50: boolean;
  isTop25: boolean;
}

export interface Education {
  highest_level?: string;
  degrees?: Degree[];
  most_recent_end_date?: string;
  most_recent_gpa?: number;
}

export interface AnnualSalaryExpectation {
  work_type: string; // "full-time" or "part-time"
  pay: number;
}

export interface Candidate {
  id: string;
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  submitted_at?: string;
  work_availability?: string[];
  annual_salary_expectation?: AnnualSalaryExpectation;
  work_experiences?: WorkExperience[];
  education?: Education;
  skills?: string[];
}
