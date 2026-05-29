"use client";

import { useEffect } from "react";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface ChartRendererProps {
  operation?: string;
  result?: Record<string, any>;
}

const plotConfig = {
  responsive: true,
  displayModeBar: false,
};

const baseLayout = {
  autosize: true,
  margin: { l: 48, r: 24, t: 56, b: 48 },
  paper_bgcolor: "rgba(255,255,255,0)",
  plot_bgcolor: "rgba(255,255,255,0)",
  font: {
    family: "Inter, system-ui, sans-serif",
    color: "#111827",
  },
};

const aggregationLabels: Record<string, string> = {
  average: "Average",
  avg: "Average",
  sum: "Sum",
  count: "Count",
  median: "Median",
};

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function chartTitle(operation: string, result: Record<string, any>) {
  switch (operation) {
    case "histogram":
      return `${capitalize(String(result.column || "Value"))} Distribution`;
    case "groupby": {
      const label = aggregationLabels[String(result.aggregation)?.toLowerCase()] || capitalize(String(result.aggregation || "Value"));
      return `${label} by ${String(result.group_column || "Group")}`;
    }
    case "trend":
      return `Trend Analysis${result.y_column ? `: ${result.y_column}` : ""}`;
    case "missing":
      return "Missing Data Analysis";
    case "correlation":
      return "Correlation Analysis";
    default:
      return capitalize(operation);
  }
}

function ChartCard({ children, isChart = false }: { children: React.ReactNode; isChart?: boolean }) {
  return (
    <div className={`rounded-2xl border border-slate-200 bg-white p-6 shadow-sm ${isChart ? "min-h-[540px] overflow-hidden" : ""}`}>
      {children}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
      <p className="text-sm font-medium text-slate-600">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function PlotFrame({
  plotKey,
  data,
  layout,
}: {
  plotKey: string;
  data: any[];
  layout: Record<string, any>;
}) {
  return (
    <Plot
      key={plotKey}
      data={data}
      layout={layout}
      config={plotConfig}
      style={{ width: "100%", height: "500px" }}
      useResizeHandler={true}
    />
  );
}

export default function ChartRenderer({ operation, result }: ChartRendererProps) {
  const operationType = String(result?.operation ?? operation ?? "").toLowerCase();

  console.log("ChartRenderer operation:", operationType);
  console.log("ChartRenderer result:", result);

  useEffect(() => {
    if (!result) return;
    window.dispatchEvent(new Event("resize"));
  }, [result]);

  if (!operationType || !result) {
    return null;
  }

  const banner = (
    <div className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-800">
      Current visualization: {operationType}
    </div>
  );

  switch (operationType) {
    case "summary": {
      const numericColumns = Array.isArray(result.numeric_columns)
        ? result.numeric_columns.length
        : result.numeric_columns ?? result.numeric_column_count ?? 0;
      const categoricalColumns = Array.isArray(result.categorical_columns)
        ? result.categorical_columns.length
        : result.categorical_columns ?? result.categorical_column_count ?? 0;

      return (
        <div className="space-y-4">
          {banner}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Rows" value={result.rows ?? 0} />
            <MetricCard label="Columns" value={result.columns ?? 0} />
            <MetricCard label="Numeric Columns" value={numericColumns} />
            <MetricCard label="Categorical Columns" value={categoricalColumns} />
          </div>
        </div>
      );
    }

    case "correlation": {
      const correlation = result.value ?? result.correlation;
      const value = typeof correlation === "number" ? correlation.toFixed(2) : "N/A";

      return (
        <div className="space-y-4">
          {banner}
          <ChartCard>
            <p className="text-sm font-medium uppercase tracking-[0.3em] text-slate-500">Correlation</p>
            <p className="mt-4 text-5xl font-semibold text-slate-900">{value}</p>
            {result.x_column && result.y_column && (
              <p className="mt-3 text-sm text-slate-600">
                {result.x_column} vs {result.y_column}
              </p>
            )}
          </ChartCard>
        </div>
      );
    }

    case "histogram":
      return (
        <div className="space-y-5">
          {banner}
          <div className="grid gap-4 sm:grid-cols-2">
            <MetricCard
              label="Mean"
              value={typeof result.mean === "number" ? result.mean.toFixed(2) : "N/A"}
            />
            <MetricCard
              label="Median"
              value={typeof result.median === "number" ? result.median.toFixed(2) : "N/A"}
            />
          </div>
          <ChartCard isChart>
            <PlotFrame
              plotKey={`histogram-${JSON.stringify(result.bins)}-${JSON.stringify(result.counts)}`}
              data={[
                {
                  type: "bar",
                  x: result.bins ?? [],
                  y: result.counts ?? [],
                  marker: { color: "#2563eb" },
                },
              ]}
              layout={{
                ...baseLayout,
                bargap: 0,
                title: { text: chartTitle(operationType, result), x: 0.02 },
                xaxis: { title: { text: "Bins" } },
                yaxis: { title: { text: "Counts" } },
              }}
            />
          </ChartCard>
        </div>
      );

    case "groupby": {
      const groupedResults = result.results ?? result.grouped_results ?? result.groups ?? [];
      const groups = groupedResults.map((item: Record<string, any>) => String(item.group ?? item[result.group_column] ?? "Missing"));
      const values = groupedResults.map((item: Record<string, any>) => item.value ?? item[result.target_column] ?? 0);

      return (
        <div className="space-y-4">
          {banner}
          <ChartCard isChart>
            <PlotFrame
              plotKey={`groupby-${JSON.stringify(groups)}-${JSON.stringify(values)}`}
              data={[
                {
                  type: "bar",
                  x: groups,
                  y: values,
                  marker: { color: "#059669" },
                },
              ]}
              layout={{
                ...baseLayout,
                title: { text: chartTitle(operationType, result), x: 0.02 },
                xaxis: { title: { text: result.group_column || "Group" } },
                yaxis: { title: { text: result.target_column || "Value" } },
              }}
            />
          </ChartCard>
        </div>
      );
    }

    case "trend":
      return (
        <div className="space-y-4">
          {banner}
          <ChartCard isChart>
            <PlotFrame
              plotKey={`trend-${JSON.stringify(result.x_values)}-${JSON.stringify(result.y_values)}`}
              data={[
                {
                  type: "scatter",
                  mode: "lines+markers",
                  x: result.x_values ?? [],
                  y: result.y_values ?? [],
                  line: { color: "#7c3aed", width: 3 },
                  marker: { color: "#7c3aed" },
                },
              ]}
              layout={{
                ...baseLayout,
                title: { text: chartTitle(operationType, result), x: 0.02 },
                xaxis: { title: { text: result.x_column || "X" } },
                yaxis: { title: { text: result.y_column || "Y" } },
              }}
            />
          </ChartCard>
        </div>
      );

    case "missing": {
      const missing = (result.missing ?? result.missing_counts ?? {}) as Record<string, number>;

      return (
        <div className="space-y-4">
          {banner}
          <ChartCard isChart>
            <PlotFrame
              plotKey={`missing-${JSON.stringify(missing)}`}
              data={[
                {
                  type: "bar",
                  x: Object.keys(missing),
                  y: Object.values(missing),
                  marker: { color: "#dc2626" },
                },
              ]}
              layout={{
                ...baseLayout,
                title: { text: chartTitle(operationType, result), x: 0.02 },
                xaxis: { title: { text: "Columns" } },
                yaxis: { title: { text: "Missing Count" } },
              }}
            />
          </ChartCard>
        </div>
      );
    }

    default:
      return (
        <div className="space-y-4">
          {banner}
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-700">
            No visualization available for this analysis.
          </div>
        </div>
      );
  }
}
