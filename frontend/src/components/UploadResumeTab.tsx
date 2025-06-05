"use client";

import { uploadResume } from "@/lib/api";
import { useState } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Spinner } from "./ui/Spinner";

export function UploadResumeTab() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const data = await uploadResume(file);
            setResult(data.data);
        } catch (err:any) {
            setError(err.message || "Upload Failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space y-6">
            <div className="flex items-center gap-4">
                <Input type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleFileChange}/>
                <Button onClick={handleUpload} disabled={!file || loading}>
                    {loading ? <Spinner className="mr-2 h-4 w-4"/> : null}
                    Upload
                </Button>
            </div>
            {error && <div className="test-red-500">{error}</div>}
            {result && (
                <Card>
                    <CardHeader>
                        <CardTitle>Extracted Resume Information</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResumeDetailsDisplay data={result} />
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

//Hrlper function for displaying resume details
export function ResumeDetailsDisplay({ data }: { data: any}) {
    return (
        <div className="sapce-y-2">
            <div>
                <strong>Name:</strong> {data.name}
            </div>
            <div>
                <strong>Email:</strong> {data.email}
            </div>
            <div>
                <strong>Phone:</strong> {data.phone}
            </div>
            <div>
                <strong>LinkedIn:</strong> {data.linkedin_url}
            </div>
            <div>
                <strong>GitHub:</strong> {data.github_url}
            </div>
            <div>
                <strong>Summary:</strong> {data.summary}
            </div>

            <div>
                <strong>Skills:</strong> {data.technical_skills?.join(",")}
            </div>
            <div>
                <strong>Work Experience:</strong> {data.email}
                <ul className="list-disc ml-6">
                    {data.work_experience?.map((exp: any, idx: number) => (
                        <li key={idx}>
                            {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})
                        </li>
                    ))}
                </ul>
            </div>
            <div>
                <strong>LLM Analysis:</strong>
                <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                    {JSON.stringify(data.llm_analysis, null, 2)}
                </pre>
            </div>
        </div>
    )
}