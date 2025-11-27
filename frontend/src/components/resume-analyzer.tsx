"use client";

import React, { useState, useCallback } from "react";
import { Upload, FileText, Briefcase, Loader2, X, CheckCircle2, AlertCircle } from "lucide-react";
import { SkillsRadarChart } from "./radar-chart";

interface AnalysisResult {
  overall_score: number;
  breakdown: {
    [key: string]: number;
  };
  weights: {
    [key: string]: number;
  };
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
  recommendations: string;
  resume_insights: {
    content_depth: number;
    word_count: number;
    estimated_completeness: number;
  };
}

export function ResumeAnalyzer() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<"text" | "file">("text");

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
      if (!validTypes.includes(file.type)) {
        setError("Please upload a PDF, DOCX, or TXT file");
        return;
      }
      setUploadedFile(file);
      setError("");
    }
  }, []);

  const removeFile = useCallback(() => {
    setUploadedFile(null);
  }, []);

  const handleAnalyze = async () => {
    if (uploadMode === "text" && (!resumeText.trim() || !jobDescription.trim())) {
      setError("Please provide both resume and job description");
      return;
    }

    if (uploadMode === "file" && (!uploadedFile || !jobDescription.trim())) {
      setError("Please upload a resume file and provide a job description");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      let response;
      
      if (uploadMode === "file" && uploadedFile) {
        const formData = new FormData();
        formData.append("resume_file", uploadedFile);
        formData.append("job_description", jobDescription);

        response = await fetch("http://localhost:8000/analyze-file", {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch("http://localhost:8000/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            resume_text: resumeText,
            job_description: jobDescription,
          }),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to analyze resume"
      );
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-green-600 dark:text-green-400";
    if (score >= 50) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 70) return "bg-green-100 dark:bg-green-900/20";
    if (score >= 50) return "bg-yellow-100 dark:bg-yellow-900/20";
    return "bg-red-100 dark:bg-red-900/20";
  };

  const getRadarData = () => {
    if (!result) return [];
    return [
      { category: "Semantic Match", score: result.breakdown.semantic || 0, fullMark: 100 },
      { category: "Skills", score: result.breakdown.skills || 0, fullMark: 100 },
      { category: "Experience", score: result.breakdown.experience || 0, fullMark: 100 },
      { category: "Education", score: result.breakdown.education || 0, fullMark: 100 },
      { category: "Content Quality", score: result.breakdown.content_quality || 0, fullMark: 100 },
    ];
  };

  return (
    <section id="analyzer" className="relative z-30 py-20 px-4 md:px-8 max-w-7xl mx-auto bg-white dark:bg-gray-950">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-500 dark:from-purple-300 dark:to-orange-200">
          Resume Analysis Tool
        </h2>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Get instant feedback on how well your resume matches a job description
        </p>
      </div>

      {/* Upload Mode Toggle */}
      <div className="flex justify-center gap-4 mb-8">
        <button
          onClick={() => setUploadMode("text")}
          className={`px-6 py-2 rounded-lg font-semibold transition-all ${
            uploadMode === "text"
              ? "bg-purple-600 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
          }`}
        >
          <FileText className="w-4 h-4 inline mr-2" />
          Paste Text
        </button>
        <button
          onClick={() => setUploadMode("file")}
          className={`px-6 py-2 rounded-lg font-semibold transition-all ${
            uploadMode === "file"
              ? "bg-purple-600 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
          }`}
        >
          <Upload className="w-4 h-4 inline mr-2" />
          Upload File
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Resume Input */}
        <div className="space-y-4">
          <label className="flex items-center gap-2 text-lg font-semibold text-gray-800 dark:text-gray-200">
            <FileText className="w-5 h-5" />
            Your Resume
          </label>
          
          {uploadMode === "text" ? (
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume text here..."
              className="w-full h-80 p-4 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            />
          ) : (
            <div className="w-full h-80 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 flex flex-col items-center justify-center p-6">
              {uploadedFile ? (
                <div className="text-center w-full">
                  <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <p className="text-gray-800 dark:text-gray-200 font-semibold mb-2">
                    {uploadedFile.name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {(uploadedFile.size / 1024).toFixed(2)} KB
                  </p>
                  <button
                    onClick={removeFile}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                    Remove File
                  </button>
                </div>
              ) : (
                <>
                  <Upload className="w-16 h-16 text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-300 mb-2 font-semibold">
                    Upload your resume
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    PDF, DOCX, or TXT (Max 10MB)
                  </p>
                  <label className="cursor-pointer inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
                    <Upload className="w-4 h-4" />
                    Choose File
                    <input
                      type="file"
                      accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                </>
              )}
            </div>
          )}
        </div>

        {/* Job Description Input */}
        <div className="space-y-4">
          <label className="flex items-center gap-2 text-lg font-semibold text-gray-800 dark:text-gray-200">
            <Briefcase className="w-5 h-5" />
            Job Description
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full h-80 p-4 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          />
        </div>
      </div>

      {/* Analyze Button */}
      <div className="text-center mb-12">
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600 text-white font-semibold rounded-full shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              Analyze Match
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-8 p-4 bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-600 rounded-lg text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Overall Score */}
          <div
            className={`p-8 rounded-2xl ${getScoreBgColor(
              result.overall_score
            )} text-center`}
          >
            <h3 className="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200">
              Overall Match Score
            </h3>
            <div
              className={`text-7xl font-bold ${getScoreColor(
                result.overall_score
              )}`}
            >
              {result.overall_score.toFixed(1)}%
            </div>
            <p className="text-gray-600 dark:text-gray-300 mt-2">
              {result.overall_score >= 70 ? "Excellent Match! 🎯" : 
               result.overall_score >= 50 ? "Good Match 👍" : 
               "Needs Improvement 📈"}
            </p>
          </div>

          {/* Detailed Analysis with Percentages */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-8">
            <h3 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200 flex items-center gap-2">
              <AlertCircle className="w-6 h-6 text-purple-600" />
              Detailed Match Analysis
            </h3>
            
            <div className="space-y-6">
              {Object.entries(result.breakdown).map(([key, value]) => {
                const weight = result.weights[key] || 0;
                const displayName = key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                
                return (
                  <div key={key} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                        {displayName}
                      </h4>
                      <div className="text-right">
                        <span className={`text-2xl font-bold ${getScoreColor(value)}`}>
                          {value.toFixed(1)}%
                        </span>
                        {weight > 0 && weight < 1 && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Weight: {(weight * 100).toFixed(0)}%
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-3 rounded-full transition-all duration-500 ${
                          value >= 70
                            ? "bg-gradient-to-r from-green-500 to-green-600"
                            : value >= 50
                            ? "bg-gradient-to-r from-yellow-500 to-yellow-600"
                            : "bg-gradient-to-r from-red-500 to-red-600"
                        }`}
                        style={{ width: `${Math.min(value, 100)}%` }}
                      ></div>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {value >= 70 ? "✅ Strong match" : 
                       value >= 50 ? "⚠️ Moderate match" : 
                       "❌ Needs improvement"}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Radar Chart */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-8">
            <h3 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200 text-center">
              Visual Match Overview
            </h3>
            <SkillsRadarChart data={getRadarData()} />
            <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-4">
              The radar chart visualizes your match across different categories. A larger area indicates better alignment.
            </p>
          </div>

          {/* Skills Analysis */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-8">
            <h3 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">
              Skills Breakdown
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="p-6 bg-green-50 dark:bg-green-900/10 rounded-xl border-2 border-green-300 dark:border-green-800">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-bold text-green-800 dark:text-green-400 flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5" />
                    Matched Skills
                  </h4>
                  <span className="text-2xl font-bold text-green-700 dark:text-green-300">
                    {result.matched_skills.length}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.matched_skills.length > 0 ? (
                    result.matched_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm font-medium shadow-sm"
                      >
                        ✓ {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-600 dark:text-gray-400 italic">
                      No matched skills found
                    </p>
                  )}
                </div>
              </div>

              <div className="p-6 bg-red-50 dark:bg-red-900/10 rounded-xl border-2 border-red-300 dark:border-red-800">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-bold text-red-800 dark:text-red-400 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Missing Skills
                  </h4>
                  <span className="text-2xl font-bold text-red-700 dark:text-red-300">
                    {result.missing_skills.length}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.missing_skills.length > 0 ? (
                    result.missing_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-full text-sm font-medium shadow-sm"
                      >
                        ✗ {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-600 dark:text-gray-400 italic">
                      All required skills present! 🎉
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Skills Match Percentage */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                  Skills Coverage
                </h4>
                <span className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {result.matched_skills.length > 0 || result.missing_skills.length > 0
                    ? ((result.matched_skills.length / (result.matched_skills.length + result.missing_skills.length)) * 100).toFixed(1)
                    : 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                <div
                  className="h-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                  style={{
                    width: `${
                      result.matched_skills.length > 0 || result.missing_skills.length > 0
                        ? (result.matched_skills.length / (result.matched_skills.length + result.missing_skills.length)) * 100
                        : 0
                    }%`,
                  }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                You have {result.matched_skills.length} out of {result.matched_skills.length + result.missing_skills.length} required skills
              </p>
            </div>
          </div>

          {/* Explanation */}
          <div className="bg-blue-50 dark:bg-blue-900/10 rounded-2xl border-2 border-blue-300 dark:border-blue-800 p-8">
            <h3 className="text-2xl font-bold text-blue-800 dark:text-blue-400 mb-6 flex items-center gap-2">
              📊 Analysis Explanation
            </h3>
            <div className="prose dark:prose-invert max-w-none">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line text-base">
                {result.explanation}
              </p>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 dark:from-purple-900/10 dark:via-pink-900/10 dark:to-orange-900/10 rounded-2xl border-2 border-purple-300 dark:border-purple-800 p-8">
            <h3 className="text-2xl font-bold text-purple-800 dark:text-purple-400 mb-6 flex items-center gap-2">
              💡 Personalized Recommendations
            </h3>
            <div className="bg-white/50 dark:bg-gray-900/50 rounded-xl p-6">
              <ul className="space-y-3">
                {result.recommendations.split('\n').filter(r => r.trim()).map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                    <span className="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="text-base leading-relaxed">{rec.replace(/^[🚨📝🛠️🎓📈✨🎯📋📊]+\s*/, '')}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Resume Insights */}
            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="bg-white/70 dark:bg-gray-800/70 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Word Count</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {result.resume_insights.word_count}
                </p>
              </div>
              <div className="bg-white/70 dark:bg-gray-800/70 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Completeness</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {result.resume_insights.estimated_completeness.toFixed(0)}%
                </p>
              </div>
              <div className="bg-white/70 dark:bg-gray-800/70 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Content Depth</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {(result.resume_insights.content_depth * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
