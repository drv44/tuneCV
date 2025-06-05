"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@radix-ui/react-tabs";
import { UploadResumeTab } from "@/components/UploadResumeTab";
import { PastUploadsTab } from "@/components/PastUploadsTab";

export default function Home() {
  return (
    <main className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle className="test-2xl">TuneCV Resume Analyzer</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs>
            <TabsList>
              <TabsTrigger value="upload">Upload Resume</TabsTrigger>
              <TabsTrigger value="history">Past Uploads</TabsTrigger>
            </TabsList>
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
