import { useState, useRef, useEffect } from "react";
import api from "../Api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface RepoChatProps {
	repoName: string;
	conversationId: number;
}

interface Message {
	id: string;
	text: string;
	sender: "user" | "assistant";
	timestamp: Date;
}

const getErrorMessage = (error: unknown) => {
	if (typeof error === "object" && error !== null && "response" in error) {
		const response = (error as { response?: { data?: any } }).response;
		const data = response?.data;
		return (
			data?.detail || data?.message || data?.error || "Something went wrong."
		);
	}

	return "Something went wrong.";
};

const RepoChat = ({ repoName, conversationId }: RepoChatProps) => {
	const [messages, setMessages] = useState<Message[]>([]);
	const [inputValue, setInputValue] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	console.log("Conversation ID:", conversationId, repoName); // Debugging log
	// Auto-scroll to bottom when messages change
	// useEffect(() => {
	// 	messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	// }, [messages]);

	useEffect(() => {
		const fetchChatHistory = async () => {
			if (!conversationId) return;
			setError(null);
			try {
				const response = await api.get(`/chat/${conversationId}`);
				const fetchedMessages = response.data.map((msg: any) => ({
					id: `msg-${msg.id}`,
					text: msg.content,
					sender: msg.role,
					timestamp: new Date(msg.created_at),
				}));
				setMessages(fetchedMessages);
			} catch (error) {
				console.error("Error fetching chat history:", error);
				setMessages([]);
				setError(getErrorMessage(error));
				setIsLoading(false);
			}
		};

		fetchChatHistory();
	}, [conversationId]);
	const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();

		if (!inputValue.trim()) return;
		setError(null);

		// Add user message
		const userMessage: Message = {
			id: `msg-${Date.now()}`,
			text: inputValue,
			sender: "user",
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInputValue("");
		setIsLoading(true);

		try {
			const response = await api.post("/chat", {
				conversation_id: conversationId,
				role: "user",
				content: String(inputValue),
			});

			const answer = response.data?.final_ai_answer;
			if (!answer) {
				throw new Error("The server returned an empty response.");
			}

			const botMessage: Message = {
				id: `msg-${Date.now() + 1}`,
				text: String(answer),
				sender: "assistant",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, botMessage]);
		} catch (error) {
			console.error("Error sending chat message:", error);
			setMessages((prev) =>
				prev.filter((message) => message.id !== userMessage.id),
			);
			setError(getErrorMessage(error));
		} finally {
			setIsLoading(false);
		}

		// Simulate API call - replace with actual server call
		// setTimeout(() => {
		// 	const botMessage: Message = {
		// 		id: `msg-${Date.now() + 1}`,
		// 		text: `Response to: "${userMessage.text}"`,
		// 		sender: "assistant",
		// 		timestamp: new Date(),
		// 	};
		// 	setMessages((prev) => [...prev, botMessage]);
		// 	setIsLoading(false);
		// }, 1500);
	};

	return (
		<div className='flex flex-col h-full bg-gray-900 text-gray-100 rounded-lg'>
			{/* Header */}
			<div className='bg-gray-800 border-b border-gray-700 p-4'>
				<h2 className='text-lg font-semibold'>Chat - {repoName}</h2>
			</div>

			{error && (
				<div className='border-b border-red-900 bg-red-950/60 px-4 py-3 text-sm text-red-200'>
					{error}
				</div>
			)}

			{/* Messages Container */}
			<div className='flex-1 overflow-y-auto p-4 space-y-4'>
				{messages.length === 0 && !isLoading && (
					<div className='flex items-center justify-center h-full text-gray-500'>
						<div className='text-center'>
							<p className='text-lg'>Start a conversation about {repoName}</p>
							<p className='text-sm mt-2'>
								Ask questions about the code, get suggestions, and more.
							</p>
						</div>
					</div>
				)}

				{messages.map((message) => (
					<div
						key={message.id}
						className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
					>
						<div
							className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
								message.sender === "user"
									? "bg-blue-600 text-white rounded-br-none"
									: "bg-gray-800 text-gray-100 rounded-bl-none border border-gray-700"
							}`}
						>
							{message.sender === "assistant" ? (
								<ReactMarkdown remarkPlugins={[remarkGfm]}>
									{message.text}
								</ReactMarkdown>
							) : (
								<p className='text-xl'>{message.text}</p>
							)}

							<span className='text-lg mt-1 block opacity-60'>
								{message.timestamp.toLocaleTimeString([], {
									hour: "2-digit",
									minute: "2-digit",
								})}
							</span>
						</div>
					</div>
				))}

				{/* Loading State */}
				{isLoading && (
					<div className='flex justify-start'>
						<div className='bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg rounded-bl-none'>
							<div className='flex space-x-2'>
								<div className='w-2 h-2 bg-gray-500 rounded-full animate-bounce'></div>
								<div
									className='w-2 h-2 bg-gray-500 rounded-full animate-bounce'
									style={{ animationDelay: "0.1s" }}
								></div>
								<div
									className='w-2 h-2 bg-gray-500 rounded-full animate-bounce'
									style={{ animationDelay: "0.2s" }}
								></div>
							</div>
						</div>
					</div>
				)}

				<div ref={messagesEndRef} />
			</div>

			{/* Input Form */}
			<div className='bg-gray-800 border-t border-gray-700 p-4'>
				<form
					onSubmit={handleSendMessage}
					className='flex gap-2'
				>
					<input
						type='text'
						value={inputValue}
						onChange={(e) => setInputValue(e.target.value)}
						placeholder='Ask about the repository...'
						disabled={isLoading}
						className='flex-1 bg-gray-700 text-white placeholder-gray-400 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50'
					/>
					<button
						type='submit'
						disabled={isLoading || !inputValue.trim()}
						className='bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-medium px-4 py-2 rounded-lg transition-colors disabled:cursor-not-allowed'
					>
						{isLoading ? "..." : "Send"}
					</button>
				</form>
			</div>
		</div>
	);
};

export default RepoChat;
