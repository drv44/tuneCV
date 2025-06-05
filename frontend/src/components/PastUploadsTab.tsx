"use client";

import { useEffect, useState } from "react";
import { fetchResumes, fetchResumeDetails } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ResumeDetailsDisplay } from "./UploadResumeTab";
import { Spinner } from "./ui/Spinner";

export function PastUploadsTab() {
  const [resumes, setResumes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedResume, setSelectedResume] = useState<any | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    fetchResumes()
      .then(setResumes)
      .catch(() => setResumes([]))
      .finally(() => setLoading(false));
  }, []);

  const handleDetails = async (id: number) => {
    setSelectedResume(null);
    setModalOpen(true);
    const data = await fetchResumeDetails(id);
    setSelectedResume(data);
  };

  return (
    <div>
      {loading ? (
        <Spinner />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>File Name</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Phone</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {resumes.map((resume) => (
              <TableRow key={resume.id}>
                <TableCell>{resume.file_name}</TableCell>
                <TableCell>{resume.name}</TableCell>
                <TableCell>{resume.email}</TableCell>
                <TableCell>{resume.phone}</TableCell>
                <TableCell>
                <Dialog open={modalOpen} onOpenChange={setModalOpen}>
                    <DialogTrigger asChild>
                        <Button onClick={() => handleDetails(resume.id)}>Details</Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl w-full">
                        <DialogHeader>
                        <DialogTitle>Resume Details</DialogTitle>
                        </DialogHeader>
                        {selectedResume ? (
                        <ResumeDetailsDisplay data={selectedResume} />
                        ) : (
                        <Spinner />
                        )}
                    </DialogContent>
                </Dialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}