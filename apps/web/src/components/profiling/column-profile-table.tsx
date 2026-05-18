"use client";

import { Badge } from "@/components/ui/badge";

interface ColumnProfile {
  columnName: string;
  dataType: string;
  nullPercentage: number;
  distinctCount: number;
  minValue: string | null;
  maxValue: string | null;
  sampleValues: string[];
}

interface ColumnProfileTableProps {
  columns: ColumnProfile[];
}

export function ColumnProfileTable({ columns }: ColumnProfileTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="text-left p-3 font-medium">Column</th>
            <th className="text-left p-3 font-medium">Type</th>
            <th className="text-left p-3 font-medium">Null %</th>
            <th className="text-left p-3 font-medium">Distinct</th>
            <th className="text-left p-3 font-medium">Min</th>
            <th className="text-left p-3 font-medium">Max</th>
            <th className="text-left p-3 font-medium">Samples</th>
          </tr>
        </thead>
        <tbody>
          {columns.map((col) => (
            <tr key={col.columnName} className="border-b hover:bg-muted/30 transition">
              <td className="p-3">
                <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">
                  {col.columnName}
                </code>
              </td>
              <td className="p-3">
                <Badge variant="secondary" className="text-xs">
                  {col.dataType}
                </Badge>
              </td>
              <td className="p-3">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        col.nullPercentage > 10
                          ? "bg-red-500"
                          : col.nullPercentage > 2
                          ? "bg-amber-500"
                          : "bg-green-500"
                      }`}
                      style={{ width: `${Math.min(col.nullPercentage, 100)}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {col.nullPercentage.toFixed(1)}%
                  </span>
                </div>
              </td>
              <td className="p-3 text-muted-foreground">
                {col.distinctCount.toLocaleString()}
              </td>
              <td className="p-3 text-muted-foreground font-mono text-xs">
                {col.minValue ?? "-"}
              </td>
              <td className="p-3 text-muted-foreground font-mono text-xs">
                {col.maxValue ?? "-"}
              </td>
              <td className="p-3">
                <div className="flex flex-wrap gap-1">
                  {col.sampleValues.slice(0, 3).map((val, i) => (
                    <span
                      key={i}
                      className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded"
                    >
                      {val}
                    </span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
