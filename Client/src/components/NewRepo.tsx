import { useState } from "react";
import UploadingRepo from "./UploadingRepo";
import api from "../Api.tsx";

type ChildProps = {
	// setCurrRepo: React.Dispatch<React.SetStateAction<string | null>>;
	setNewRepo: React.Dispatch<React.SetStateAction<boolean | null>>;
	onUploadComplete: () => void;
};
const NewRepo = ({ setNewRepo, onUploadComplete }: ChildProps) => {
	const [repoUrl, setRepoUrl] = useState<string>("");
	const [uploading, setUploading] = useState<boolean>(false);
	const [jobId, setJobId] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const handleSubmit = async () => {
		if (!repoUrl.trim()) return;

		setError(null);
		setUploading(true);

		try {
			const res = await api.post("/repo", { url: repoUrl });
			setJobId(res.data?.job_id ?? null);
			setRepoUrl("");
		} catch (err) {
			console.error("Error uploading repository:", err);
			setUploading(false);
			setJobId(null);
			setError(
				typeof err === "object" && err !== null && "response" in err
					? (err as { response?: { data?: any } }).response?.data?.detail ||
							(err as { response?: { data?: any } }).response?.data?.message ||
							"Failed to upload repository."
					: "Failed to upload repository.",
			);
		}
	};
	return uploading ? (
		<UploadingRepo
			setNewRepo={setNewRepo}
			setUploading={setUploading}
			jobId={jobId}
			onUploadComplete={onUploadComplete}
			repoUrl={repoUrl}
		/>
	) : (
		<div className='w-full h-full flex flex-col gap-9 items-center justify-center'>
			{error && (
				<div className='w-[50%] rounded-2xl border border-red-900 bg-red-950/60 px-4 py-3 text-sm text-red-200'>
					{error}
				</div>
			)}
			<input
				type='text'
				placeholder='paste here your git repository URL'
				className='px-10 py-4 rounded-full text-4xl w-[50%] border-2 border-zinc-400 '
				value={repoUrl}
				onChange={(e) => setRepoUrl(e.target.value)}
			/>
			<input
				type='submit'
				value='Create Repository'
				className='ml-4 bg-blue-800 hover:bg-blue-950 transition-all duration-200 cursor-pointer text-white font-bold py-2 px-4 rounded-full'
				onClick={handleSubmit}
			/>
		</div>
	);
};

export default NewRepo;
