  export const pathOptions = [
    // Basic Info
    { value: "name", label: "Name", type: "text" },
    { value: "email", label: "Email", type: "text" },
    { value: "phone", label: "Phone", type: "text" },
    { value: "location", label: "Location", type: "text" },
    { value: "submitted_at", label: "Submitted At", type: "date" },
    { value: "work_availability", label: "Work Availability", type: "text" },
  
    // Salary
    { value: "annual_salary_expectation.pay", label: "Expected Pay", type: "number" },
    { value: "annual_salary_expectation.work_type", label: "Employment Type", type: "text" },
  
    // Skills
    { value: "skills", label: "Skills", type: "text" },
  
    // Work Experience
    { value: "work_experiences.company", label: "Work Experience - Company", type: "text" },
    { value: "work_experiences.roleName", label: "Work Experience - Role", type: "text" },
  
    // Education (root-level)
    { value: "education.highest_level", label: "Highest Education Level", type: "text" },
    { value: "education.most_recent_end_date", label: "Most Recent Graduation Date", type: "date" },
    { value: "education.most_recent_gpa", label: "Most Recent GPA", type: "number" },
  
    // Education Degrees
    { value: "education.degrees.degree", label: "Degree", type: "text" },
    { value: "education.degrees.subject", label: "Subject", type: "text" },
    { value: "education.degrees.school", label: "School", type: "text" },
    { value: "education.degrees.gpa", label: "GPA", type: "number" },
    { value: "education.degrees.startDate", label: "Education Start Date", type: "date" },
    { value: "education.degrees.endDate", label: "Education End Date", type: "date" },
    { value: "education.degrees.originalSchool", label: "Original School", type: "text" },
    { value: "education.degrees.isTop50", label: "Is Top 50 School", type: "boolean" },
    { value: "education.degrees.isTop25", label: "Is Top 25 School", type: "boolean" },
  ];
  
  export const operatorOptions = [
    { value: "==", label: "==" },
    { value: "!=", label: "!=" },
    { value: ">", label: ">" },
    { value: ">=", label: ">=" },
    { value: "<", label: "<" },
    { value: "<=", label: "<=" },
    { value: "in", label: "in" },
    { value: "contains", label: "contains" },
  ];