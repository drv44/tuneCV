"use client";

import { uploadResume } from "@/lib/api";
import { useState } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
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
        } catch (err: any) {
            setError(err.message || "Upload Failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 px-4 flex flex-col items-center justify-center bg-white shadow-sm hover:shadow-md transition mb-4">
            <Input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileChange}
                className="w-full"
            />
            {/* {file && (
                <div className="mt-2 text-sm text-gray-700">
                Selected: <span className="font-medium">{file.name}</span>
                </div>
            )} */}
            {result && (
                <div className="w-full mt-6" >
                    <div className="max-h-[500px] overflow-auto rounded-lg shadow bg-white p-6 border border-gray-200">
                        <ResumeDetailsDisplay data={result} />
                    </div>
                </div>
                )}
            <Button
                onClick={handleUpload}
                disabled={!file || loading}
                className="mt-4 w-full"
                size="lg"
            >
                {loading ? <Spinner className="mr-2 h-4 w-4" /> : null}
                Upload & Analyze
            </Button>
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

            {/* <div>
                <strong>Skills:</strong>
                <div className="flex flex-wrap gap-2 mt-1">
                    {data.technical_skills?.map((skill: string, idx: number) => (
                    <span key={idx} className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">{skill}</span>
                    ))}
                </div>
            </div>
            <Accordion type="single" collapsible>
                {data.work_experience?.map((exp: any, idx: number) => (
                    <AccordionItem value={`exp-${idx}`} key={idx}>
                    <AccordionTrigger>
                        {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})
                    </AccordionTrigger>
                    <AccordionContent>
                        <div className="text-sm text-gray-700">
                        <div><strong>Responsibilities:</strong> {exp.responsibilities?.join(", ")}</div>
                        <div><strong>Achievements:</strong> {exp.achievements?.join(", ")}</div>
                        </div>
                    </AccordionContent>
                    </AccordionItem>
                ))}
            </Accordion> */}
            <div>
                <strong>Skills:</strong>
                <div className="flex flex-wrap gap-2 mt-1">
                    {data.technical_skills?.map((skill: string, idx: number) => (
                    <span key={idx} className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">{skill}</span>
                    ))}
                </div>
                </div>
            <Accordion type="single" collapsible>
                {data.work_experience?.map((exp: any, idx: number) => (
                    <AccordionItem value={`exp-${idx}`} key={idx}>
                    <AccordionTrigger>
                        {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})
                    </AccordionTrigger>
                    <AccordionContent>
                        <div className="text-sm text-gray-700">
                        <div><strong>Responsibilities:</strong> {exp.responsibilities?.join(", ")}</div>
                        <div><strong>Achievements:</strong> {exp.achievements?.join(", ")}</div>
                        </div>
                    </AccordionContent>
                    </AccordionItem>
                ))}
            </Accordion>
            <div>
                <strong>LLM Analysis:</strong>
                <div className="bg-gray-50 rounded p-2 max-h-60 overflow-auto text-xs">
                    <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                        {JSON.stringify(data.llm_analysis, null, 2)}
                    </pre>
                </div>
            </div>
        </div>
    )
}