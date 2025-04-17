"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import type { Filter, Operator } from "@/lib/types";

interface FilterBuilderProps {
  onApplyFilters: (filters: Filter[]) => void;
}

export function FilterBuilder({ onApplyFilters }: FilterBuilderProps) {
  const [buttonClicked, setButtonClicked] = useState(false);
  const [filters, setFilters] = useState<Filter[]>([]);
  const [currentFilter, setCurrentFilter] = useState<Filter>({
    path: "",
    operator: "==",
    value: "",
  });
  const [currentValueType, setCurrentValueType] = useState<
    "text" | "number" | "boolean" | "date"
  >("text");

  const addFilter = () => {
    if (
      currentFilter.path &&
      (currentFilter.value || currentValueType === "boolean")
    ) {
      // For boolean values, use "true" or "false" as the value
      const value =
        currentValueType === "boolean"
          ? currentFilter.value || "false"
          : currentFilter.value;

      setFilters([...filters, { ...currentFilter, value }]);
      setCurrentFilter({ path: "", operator: "==", value: "" });
    }
    setButtonClicked(true);
    setTimeout(() => setButtonClicked(false), 300);
  };

  const removeFilter = (index: number) => {
    const newFilters = [...filters];
    newFilters.splice(index, 1);
    setFilters(newFilters);
  };

  const clearFilters = () => {
    setFilters([]);
  };

  const applyFilters = () => {
    onApplyFilters(filters);
  };

  // Organize paths by category for better UX
  const pathOptions = [
    // Basic info
    { value: "name", label: "Name", type: "text" },
    { value: "email", label: "Email", type: "text" },
    { value: "phone", label: "Phone", type: "text" },
    { value: "location", label: "Location", type: "text" },
    { value: "submitted_at", label: "Submitted At", type: "date" },
    { value: "work_availability", label: "Work Availability", type: "text" },

    // Salary
    {
      value: "annual_salary_expectation.amount",
      label: "Salary Amount",
      type: "number",
    },
    {
      value: "annual_salary_expectation.currency",
      label: "Salary Currency",
      type: "text",
    },

    // Skills
    { value: "skills", label: "Skills", type: "text" },

    // Education
    {
      value: "education.highest_level",
      label: "Highest Education Level",
      type: "text",
    },
    { value: "education.degrees.degree", label: "Degree", type: "text" },
    { value: "education.degrees.subject", label: "Subject", type: "text" },
    { value: "education.degrees.school", label: "School", type: "text" },
    { value: "education.degrees.gpa", label: "GPA", type: "number" },
    {
      value: "education.degrees.startDate",
      label: "Education Start Date",
      type: "date",
    },
    {
      value: "education.degrees.endDate",
      label: "Education End Date",
      type: "date",
    },
    {
      value: "education.degrees.originalSchool",
      label: "Original School",
      type: "text",
    },
    {
      value: "education.degrees.isTop50",
      label: "Is Top 50 School",
      type: "boolean",
    },
  ];

  const operatorOptions = [
    { value: "==", label: "==" },
    { value: "!=", label: "!=" },
    { value: ">", label: ">" },
    { value: ">=", label: ">=" },
    { value: "<", label: "<" },
    { value: "<=", label: "<=" },
    { value: "in", label: "in" },
    { value: "contains", label: "contains" },
  ];

  // Filter operators based on the current value type
  const filteredOperators = operatorOptions.filter((op) => {
    if (currentValueType === "boolean") {
      return ["==", "!="].includes(op.value);
    }
    if (currentValueType === "text") {
      return true; // All operators can work with text
    }
    if (currentValueType === "number" || currentValueType === "date") {
      return op.value !== "contains"; // "contains" doesn't make sense for numbers/dates
    }
    return true;
  });

  // Update value type when path changes
  const handlePathChange = (path: string) => {
    if (path === "placeholder") return;

    const selectedPath = pathOptions.find((p) => p.value === path);
    if (selectedPath) {
      setCurrentValueType(selectedPath.type as any);
      setCurrentFilter({
        ...currentFilter,
        path,
        // Reset value when changing types
        value: "",
      });
    }
  };
  const isReadyToAdd =
    currentFilter.path !== "" &&
    (currentFilter.value !== "" || currentValueType === "boolean");
  return (
    <Card>
      <CardHeader>
        <CardTitle>Custom Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="grid grid-cols-3 gap-2">
            <div>
              <Select
                value={currentFilter.path}
                onValueChange={handlePathChange}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Path" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="placeholder" disabled>
                    Select a field
                  </SelectItem>
                  {pathOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select
                value={currentFilter.operator}
                onValueChange={(value) =>
                  setCurrentFilter({
                    ...currentFilter,
                    operator: value as Operator,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Operator" />
                </SelectTrigger>
                <SelectContent>
                  {filteredOperators.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              {currentValueType === "boolean" ? (
                <div className="flex items-center space-x-2 w-full">
                  <Checkbox
                    id="isTrue"
                    checked={currentFilter.value === "true"}
                    onCheckedChange={(checked) =>
                      setCurrentFilter({
                        ...currentFilter,
                        value: checked ? "true" : "false",
                      })
                    }
                  />
                  <Label htmlFor="isTrue">True</Label>
                </div>
              ) : currentValueType === "date" ? (
                <Input
                  type="date"
                  value={currentFilter.value}
                  onChange={(e) =>
                    setCurrentFilter({
                      ...currentFilter,
                      value: e.target.value,
                    })
                  }
                />
              ) : currentValueType === "number" ? (
                <Input
                  type="number"
                  placeholder="Value"
                  value={currentFilter.value}
                  onChange={(e) =>
                    setCurrentFilter({
                      ...currentFilter,
                      value: e.target.value,
                    })
                  }
                />
              ) : (
                <Input
                  placeholder="Value"
                  value={currentFilter.value}
                  onChange={(e) =>
                    setCurrentFilter({
                      ...currentFilter,
                      value: e.target.value,
                    })
                  }
                />
              )}
              <Button
                size="icon"
                variant="outline"
                onClick={addFilter}
                className={buttonClicked ? "animate-ping-once" : ""}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {filters.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium">Active Filters:</div>
            <div className="flex flex-wrap gap-2">
              {filters.map((filter, index) => {
                const pathLabel =
                  pathOptions.find((p) => p.value === filter.path)?.label ||
                  filter.path;
                const operatorLabel =
                  operatorOptions.find((o) => o.value === filter.operator)
                    ?.label || filter.operator;

                return (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    <span>
                      {pathLabel} {operatorLabel} "{filter.value}"
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-4 w-4 p-0 ml-1"
                      onClick={() => removeFilter(index)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </Badge>
                );
              })}
              {filters.length > 1 && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs"
                  onClick={clearFilters}
                >
                  Clear All
                </Button>
              )}
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button
          variant={isReadyToAdd ? "default" : "outline"}
          className={
            isReadyToAdd
              ? "flex-1 bg-primary text-white"
              : "flex-1 bg-muted text-muted-foreground"
          }
          onClick={applyFilters}
          disabled={!isReadyToAdd}
        >
          Apply Filters
        </Button>
        <Button
          className="flex-1"
          variant="destructive"
          onClick={clearFilters}
          disabled={filters.length === 0}
        >
          Reset Filters
        </Button>
      </CardFooter>
    </Card>
  );
}
