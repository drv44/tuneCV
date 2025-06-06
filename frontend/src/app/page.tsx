"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@radix-ui/react-tabs";
import { UploadResumeTab } from "@/components/UploadResumeTab";
import { PastUploadsTab } from "@/components/PastUploadsTab";
import { useState } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("upload");
  return (
    <main className="container mx-auto py-8">
      {/* Hero Section */}
      <section className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-blue-700 mb-2">AI-Powered Resume Analyzer</h1>
        <p className="text-lg text-gray-600 mb-4">
          Upload your resume and get instant, actionable feedback and upskilling suggestions from AI.
        </p>
        <div className="flex justify-center gap-4">
          <button
            type="button"
            className="bg-blue-600 text-white px-6 py-2 rounded shadow hover:bg-blue-700 transition"
            onClick={() => setActiveTab("upload")}
          >
            Get Started
          </button>
          <button
            type="button"
            className="bg-white border border-blue-600 text-blue-600 px-6 py-2 rounded shadow hover:bg-blue-50 transition"
            onClick={() => setActiveTab("history")}
          >
            View Past Uploads
          </button>
        </div>
      </section>

      {/* Tab section */}
      <Card>
        <CardHeader className="flex flex-col items-center justify-center">
          <CardTitle className="text-2xl text-center">TuneCV Resume Analyzer</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <div className="w-1/2 mx-auto">
              <TabsList className="flex justify-center w-full mb-4">
                <TabsTrigger value="upload" className="flex-1">Upload Resume</TabsTrigger>
                <TabsTrigger value="history" className="flex-1">Past Uploads</TabsTrigger>
              </TabsList>
            </div>
            <TabsContent value="upload">
              <UploadResumeTab />
            </TabsContent>
            <TabsContent value="history"> 
              <PastUploadsTab />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </main>
  );
}
