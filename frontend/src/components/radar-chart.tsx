"use client";

import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";

interface RadarChartProps {
  data: Array<{
    category: string;
    score: number;
    fullMark: number;
  }>;
}

export function SkillsRadarChart({ data }: RadarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
        <PolarGrid stroke="#e5e7eb" strokeDasharray="3 3" />
        <PolarAngleAxis
          dataKey="category"
          tick={{ fill: "#6b7280", fontSize: 12 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={{ fill: "#6b7280" }}
        />
        <Radar
          name="Match Score"
          dataKey="score"
          stroke="#8b5cf6"
          fill="#8b5cf6"
          fillOpacity={0.6}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            borderRadius: "8px",
            border: "1px solid #e5e7eb",
          }}
        />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
}
