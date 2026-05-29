"use client";

import { useEffect, useState } from "react";
import ChartRenderer from "../components/ChartRenderer";

interface SampleValues extends Array<any> {}

interface ColumnStats {
  min: number;
  max: number;
  mean: number;
}

interface SchemaColumn {
  name: string;
  type: string;
  missing_count: number;
  unique_count: number;
  sample_values: SampleValues;
  stats?: ColumnStats;
}

interface PreviewData {
  filename: string;
  rows: number;
  columns: number;
  schema: SchemaColumn[];
  preview: Record<string, any>[];
}

interface QueryResult {
  intent?: ParsedIntent;
  result?: Record<string, any>;
  explanation?: string;
  error?: boolean;
  message?: string;
  suggestions?: string[];
}

interface ParsedIntent {
  operation?: string;
  column?: string;
  target_column?: string;
  group_column?: string;
  aggregation?: string;
  x_column?: string;
  y_column?: string;
}

interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  text?: string;
  response?: QueryResult;
}

const suggestedQueries = [
  "Summarize this dataset",
  "Show histogram of marks",
  "Show missing values",
  "Average marks by class",
];

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const BACKEND_UNAVAILABLE_MESSAGE = "DataChat backend is currently unavailable.";

export default function Home() {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [query, setQuery] = useState("");
  const [queryLoading, setQueryLoading] = useState(false);
  const [conversation, setConversation] = useState<ChatMessage[]>([]);

  const getFriendlyError = (message: string) => {
    if (message.includes("Groq API error")) {
      return "The AI service is currently unavailable. Please try again in a minute.";
    }

    if (message.includes("Groq API key not configured")) {
      return "Groq API key is not configured on the backend.";
    }

    return message;
  };

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
          setStatus(BACKEND_UNAVAILABLE_MESSAGE);
          return;
        }
        const data = await response.json();
        setStatus(data.status);
      } catch (error) {
        setStatus(BACKEND_UNAVAILABLE_MESSAGE);
      } finally {
        setLoading(false);
      }
    };

    checkBackend();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setPreviewData(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || "Upload failed");
        return;
      }

      const data = await response.json();
      setPreviewData(data);
      setQuery("");
      setConversation([]);
    } catch (error) {
      setError(BACKEND_UNAVAILABLE_MESSAGE);
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const submitQuestion = async (questionText: string) => {
    const trimmedQuestion = questionText.trim();
    if (!trimmedQuestion || queryLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      text: trimmedQuestion,
    };

    setConversation((messages) => [...messages, userMessage]);
    setQuery("");
    setQueryLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmedQuestion }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const message = getFriendlyError(errorData.detail || "Query failed");
        setConversation((messages) => [
          ...messages,
          {
            id: Date.now() + 1,
            role: "assistant",
            response: { error: true, message: message },
          },
        ]);
        return;
      }

      const result = await response.json();
      
      // Handle both old and new error formats
      let responsePayload: QueryResult;
      if (result.error === true || (typeof result.error === 'string' && result.error)) {
        // New format or old string format
        responsePayload = {
          error: true,
          message: result.message || result.error || "An error occurred",
          suggestions: result.suggestions,
        };
      } else if (result.error) {
        // Old error format - string in error field
        responsePayload = {
          error: true,
          message: getFriendlyError(result.error)
        };
      } else {
        // Success case
        responsePayload = result;
      }

      setConversation((messages) => [
        ...messages,
        {
          id: Date.now() + 1,
          role: "assistant",
          response: responsePayload,
        },
      ]);
    } catch (error) {
      setConversation((messages) => [
        ...messages,
        {
          id: Date.now() + 1,
          role: "assistant",
          response: { error: true, message: BACKEND_UNAVAILABLE_MESSAGE },
        },
      ]);
      console.error(error);
    } finally {
      setQueryLoading(false);
    }
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitQuestion(query);
  };

  const formatSampleValues = (values: any[]) => {
    return values
      .map((v) => {
        if (typeof v === "number") {
          return v.toFixed(2);
        }
        return String(v).substring(0, 20);
      })
      .join(", ");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <header className="text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-blue-600 font-semibold mb-3">
            Conversational AI for Data Analysis
          </p>
          <h1 className="text-4xl md:text-5xl font-semibold text-slate-900">DataChat</h1>
          <p className="mt-3 text-base text-slate-600 max-w-2xl mx-auto">
            Ask questions, explore charts, and understand your dataset with a polished analytics assistant.
          </p>
        </header>

        <div className="mt-8 flex justify-center">
          <div className="inline-flex items-center rounded-full border border-slate-200 bg-white/90 px-5 py-2 text-sm text-slate-700 shadow-sm">
            {loading ? (
              <span>Checking backend...</span>
            ) : (
              <span className={status === "Backend running" ? "text-slate-900" : "text-amber-700"}>
                {status}
              </span>
            )}
          </div>
        </div>

        <div className="mt-10 space-y-8">
        {/* CSV Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Upload CSV</h2>
          <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 bg-blue-50 text-center cursor-pointer hover:bg-blue-100 transition">
            <label htmlFor="csv-upload" className="cursor-pointer">
              <div className="text-gray-600 mb-4">
                <svg
                  className="w-16 h-16 mx-auto text-blue-400 mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <p className="text-lg font-medium text-gray-700">
                {uploading ? "Uploading..." : "Click to upload CSV"}
              </p>
              <p className="text-sm text-gray-500 mt-2">or drag and drop</p>
              <input
                id="csv-upload"
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {previewData && (
          <div className="grid gap-4 sm:grid-cols-3 mb-8">
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500 font-semibold">Filename</p>
              <p className="mt-3 text-lg font-semibold text-slate-900 truncate">{previewData.filename}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500 font-semibold">Rows</p>
              <p className="mt-3 text-lg font-semibold text-blue-600">{previewData.rows.toLocaleString()}</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500 font-semibold">Columns</p>
              <p className="mt-3 text-lg font-semibold text-emerald-600">{previewData.columns}</p>
            </div>
          </div>
        )}

        {!previewData && !uploading && (
          <div className="rounded-3xl border border-dashed border-slate-300 bg-white/90 p-10 text-center shadow-sm mb-8">
            <p className="text-xl font-semibold text-slate-900">Upload a CSV dataset to start analyzing with DataChat</p>
            <p className="mt-3 text-sm text-slate-600 max-w-xl mx-auto">
              Bring your data to life with conversational analytics, chart insights, and fast dataset summaries.
            </p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-700 font-medium">Error: {error}</p>
          </div>
        )}

        {/* Dataset Analysis */}
        {previewData && (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <p className="text-gray-600 text-sm font-medium">Filename</p>
                <p className="text-2xl font-bold text-gray-900 mt-2 truncate">
                  {previewData.filename}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <p className="text-gray-600 text-sm font-medium">Rows</p>
                <p className="text-2xl font-bold text-blue-600 mt-2">
                  {previewData.rows.toLocaleString()}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <p className="text-gray-600 text-sm font-medium">Columns</p>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  {previewData.columns}
                </p>
              </div>
            </div>

            {/* Schema Analysis Table */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Dataset Schema Analysis</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left font-semibold text-gray-900">Column</th>
                      <th className="px-6 py-3 text-left font-semibold text-gray-900">Type</th>
                      <th className="px-6 py-3 text-center font-semibold text-gray-900">Missing</th>
                      <th className="px-6 py-3 text-center font-semibold text-gray-900">Unique</th>
                      <th className="px-6 py-3 text-left font-semibold text-gray-900">Sample Values</th>
                      <th className="px-6 py-3 text-left font-semibold text-gray-900">Statistics</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {previewData.schema.map((col, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{col.name}</td>
                        <td className="px-6 py-4">
                          <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {col.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center text-gray-700">
                          {col.missing_count}
                        </td>
                        <td className="px-6 py-4 text-center text-gray-700">
                          {col.unique_count}
                        </td>
                        <td className="px-6 py-4 text-gray-700 text-xs">
                          {formatSampleValues(col.sample_values)}
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-700">
                          {col.stats ? (
                            <div className="space-y-1">
                              <div>
                                <span className="font-medium">Min:</span> {col.stats.min.toFixed(2)}
                              </div>
                              <div>
                                <span className="font-medium">Max:</span> {col.stats.max.toFixed(2)}
                              </div>
                              <div>
                                <span className="font-medium">Mean:</span> {col.stats.mean.toFixed(2)}
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Conversation Section */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Ask DataChat</h3>

              <div className="mb-6 max-h-[760px] space-y-5 overflow-y-auto rounded-lg border border-gray-200 bg-gray-50 p-5">
                {conversation.length === 0 && !queryLoading && (
                  <div className="rounded-lg border border-dashed border-gray-300 bg-white p-5 text-sm text-gray-600">
                    Ask a question about the uploaded dataset to start the analysis conversation.
                  </div>
                )}

                {conversation.map((message) => {
                  if (message.role === "user") {
                    return (
                      <div key={message.id} className="flex justify-end">
                        <div className="max-w-[78%] rounded-3xl rounded-br-none bg-slate-900 px-5 py-4 text-sm text-white shadow-lg shadow-slate-200/50">
                          {message.text}
                        </div>
                      </div>
                    );
                  }

                  const response = message.response;

                  return (
                    <div key={message.id} className="flex justify-start">
                      <div className="max-w-[92%] rounded-3xl rounded-bl-none border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/50">
                        {response?.error ? (
                          <div className="space-y-4">
                            <div className="rounded-2xl bg-red-50 border border-red-200 p-4">
                              <p className="text-sm font-semibold text-red-900">Error</p>
                              <p className="mt-2 text-sm text-red-800">
                                {response.message}
                              </p>
                            </div>

                            {response.suggestions && response.suggestions.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-slate-700 mb-2">
                                  Try one of these:
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {response.suggestions.map((suggestion, idx) => (
                                    <button
                                      key={idx}
                                      type="button"
                                      onClick={() => setQuery(suggestion)}
                                      disabled={queryLoading}
                                      className="rounded-full border border-amber-300 bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-50 transition"
                                    >
                                      {suggestion}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="space-y-5">
                            <p className="text-sm leading-6 text-slate-800">
                              {response?.explanation}
                            </p>

                            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                              <ChartRenderer
                                key={`${message.id}-${response?.result?.operation ?? "unknown"}`}
                                operation={response?.result?.operation}
                                result={response?.result}
                              />
                            </div>

                            <details className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                              <summary className="cursor-pointer text-sm font-semibold text-slate-800">
                                Parsed intent
                              </summary>
                              <pre className="mt-3 overflow-x-auto rounded border border-slate-200 bg-white p-3 text-xs text-slate-800">
                                {JSON.stringify(response?.intent, null, 2)}
                              </pre>
                            </details>

                            <details className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                              <summary className="cursor-pointer text-sm font-semibold text-slate-800">
                                Raw result JSON
                              </summary>
                              <pre className="mt-3 overflow-x-auto rounded border border-slate-200 bg-white p-3 text-xs text-slate-800">
                                {JSON.stringify(response?.result, null, 2)}
                              </pre>
                            </details>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {queryLoading && (
                  <div className="flex justify-start">
                    <div className="rounded-3xl border border-slate-200 bg-white px-5 py-4 text-sm text-slate-900 shadow-sm shadow-slate-200/50 flex items-center gap-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-blue-600 animate-pulse" />
                      <div>
                        <p className="font-medium">DataChat is analyzing...</p>
                        <p className="text-xs text-slate-500">Hang tight while we process your request.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={handleQuerySubmit} className="space-y-4">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder='Ask a question like "Show histogram of marks"'
                  disabled={queryLoading}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />

                <div className="flex flex-wrap gap-2">
                  {suggestedQueries.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => setQuery(suggestion)}
                      disabled={queryLoading}
                      className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={queryLoading || !query.trim()}
                  className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {queryLoading ? "Analyzing..." : "Send"}
                </button>
              </form>
            </div>

            {/* Preview Table */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Preview (First 5 Rows)</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      {previewData.preview.length > 0 &&
                        Object.keys(previewData.preview[0]).map((col) => (
                          <th
                            key={col}
                            className="px-6 py-3 text-left font-semibold text-gray-900"
                          >
                            {col}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {previewData.preview.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.values(row).map((val, colIdx) => (
                          <td key={colIdx} className="px-6 py-4 text-gray-700">
                            {String(val).substring(0, 50)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  </div>
  );
}
