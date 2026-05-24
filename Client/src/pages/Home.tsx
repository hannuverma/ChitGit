import { SignOutButton } from "@clerk/react";
import { PenLine } from "lucide-react";
import { useMemo, useState } from "react";
import NewRepo from "../components/NewRepo";
import RepoChat from "../components/RepoChat";
import api from "../Api";

const Home = () => {
	const [currRepo, setCurrRepo] = useState<string | null>(null);
	const [newRepo, setNewRepo] = useState<boolean | null>(true);
	const [conversation, setConversation] = useState<number | null>(null);
	const [repoError, setRepoError] = useState<string | null>(null);

	interface reposInterface {
		repo_name: string;
		conversation_id: number;
	}
	const [repos, setRepos] = useState<reposInterface[]>([]);

	const fetchRepos = async () => {
		setRepoError(null);

		try {
			const res = await api.get("/all-repos");
			setRepos(Array.isArray(res.data) ? res.data : []);
		} catch (error) {
			console.error("Error fetching repositories:", error);
			setRepos([]);
			setRepoError("Unable to load repositories right now.");
		}
	};

	useMemo(() => {
		fetchRepos();
	}, []);

	const repoClickHandler = (repoName: string, conversationId: number) => {
		setCurrRepo(repoName);
		setNewRepo(false);
		setConversation(conversationId);
	};

	const newRepoClickHandler = () => {
		setCurrRepo(null);
		setNewRepo(true);
	};
	return (
		<div className='h-screen w-full flex justify-around bg-gray-950 text-white p-2'>
			<SignOutButton>
				<button className='bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded absolute top-4 right-4'>
					Sign Out
				</button>
			</SignOutButton>
			<div className='w-[25vw] bg-gray-900 rounded-3xl p-4 text-3xl relative'>
				<h1 className='text-center mb-4 text-7xl'>ChitGit</h1>
				{repoError && (
					<div className='mb-3 rounded-2xl border border-red-900 bg-red-950/60 px-3 py-2 text-sm text-red-200'>
						{repoError}
					</div>
				)}
				<p
					className='text-right text-xl mb-2 bg-gray-800 p-2 rounded-lg capitalize hover:bg-gray-700 cursor-pointer flex gap-3 justify-between'
					onClick={newRepoClickHandler}
				>
					<PenLine /> search for new repo
				</p>
				<div className='flex flex-col py-20 px-4 h-full gap-1'>
					{repos.map((repo, index) => {
						return (
							<h1
								className='hover:bg-gray-700 p-2 rounded-lg transition-all duration-300 cursor-pointer'
								key={index}
								onClick={() =>
									repoClickHandler(repo.repo_name, repo.conversation_id)
								}
							>
								{repo.repo_name}
							</h1>
						);
					})}
				</div>
			</div>
			<div className='w-[70vw] text-lg rounded-3xl overflow-hidden h-full'>
				{newRepo ? (
					<NewRepo
						setNewRepo={setNewRepo}
						onUploadComplete={fetchRepos}
					/>
				) : (
					<RepoChat
						repoName={currRepo!}
						conversationId={conversation!}
					/>
				)}
			</div>
		</div>
	);
};

export default Home;
