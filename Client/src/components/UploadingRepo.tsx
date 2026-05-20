import { useEffect, useState } from "react";
import api from "../Api.tsx";
type ChildProps = {
	setUploading: React.Dispatch<React.SetStateAction<boolean>>;
	setNewRepo: React.Dispatch<React.SetStateAction<boolean | null>>;
	jobId: string | null;
	onUploadComplete: () => void;
};

const UploadingRepo = ({
	setUploading,
	setNewRepo,
	jobId,
	onUploadComplete,
}: ChildProps) => {
	const [status, setStatus] = useState<string>("");
	useEffect(() => {
		if (!jobId) return;

		const interval = setInterval(async () => {
			try {
				const res = await api.get(`/job/${jobId}`);
				const currentStatus = res.data?.status?.status;

				if (currentStatus) {
					setStatus(currentStatus);
				}

				if (currentStatus === "finished" || currentStatus === "failed") {
					clearInterval(interval);
					setUploading(false);
					setNewRepo(true);
					onUploadComplete();
				}
			} catch (error) {
				console.error("Error checking upload status:", error);
				clearInterval(interval);
				setStatus("failed");
				setUploading(false);
				setNewRepo(true);
			}
		}, 6000);

		return () => clearInterval(interval);
	}, [jobId, onUploadComplete, setNewRepo, setUploading]);
	return (
		<div className='w-full h-full flex flex-col gap-9 items-center justify-center'>
			<div className='text-4xl font-bold'>Uploading Repository...</div>
			<div className='w-1/2 h-3 bg-gray-300 rounded-full'>
				<div className='w-[50%] h-full bg-blue-500 rounded-full'></div>
			</div>
			<div className='text-2xl font-semibold'>Current Status: {status}</div>
		</div>
	);
};

export default UploadingRepo;
