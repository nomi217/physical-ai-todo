"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { createTask, getTasks, updateTask, deleteTask } from "@/lib/api";
import { Task } from "@/lib/types";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface Message {
  role: "user" | "assistant";
  content: string;
  tool_calls?: any[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [authError, setAuthError] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [taskFormMode, setTaskFormMode] = useState<'add' | 'update' | 'list'>('add');
  const [tasks, setTasks] = useState<Task[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load tasks
  const loadTasks = async () => {
    try {
      const data = await getTasks({});
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  useEffect(() => {
    if (user) {
      loadTasks();
    }
  }, [user]);

  // Handle tool button clicks
  const handleToolClick = async (tool: string) => {
    if (!user) {
      alert('Please sign in to use this feature');
      return;
    }

    switch (tool) {
      case 'add_task':
        router.push('/dashboard');
        break;
      case 'list_tasks':
        await loadTasks();
        setTaskFormMode('list');
        setShowTaskForm(true);
        break;
      case 'complete_task':
      case 'update_task':
      case 'delete_task':
        await loadTasks();
        setTaskFormMode('update');
        setShowTaskForm(true);
        break;
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    if (!user) {
      setAuthError(true);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Please sign in to use the chatbot. I need to know who you are to manage your tasks!",
        },
      ]);
      return;
    }

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);
    setAuthError(false);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          conversation_id: conversationId,
          message: userMessage,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          setAuthError(true);
          throw new Error("Session expired. Please sign in again.");
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.assistant_message,
          tool_calls: data.tool_calls,
        },
      ]);

      // Reload tasks after AI action
      await loadTasks();

      // Trigger notification refresh for instant notification updates
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new Event('refreshNotifications'));
      }
    } catch (error: any) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: error.message || "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTaskAction = async (action: string, taskId?: number) => {
    try {
      if (action === 'complete' && taskId) {
        await updateTask(taskId, { completed: true });
        setMessages((prev) => [...prev, { role: "assistant", content: "✅ Task completed!" }]);
      } else if (action === 'delete' && taskId) {
        await deleteTask(taskId);
        setMessages((prev) => [...prev, { role: "assistant", content: "🗑️ Task deleted!" }]);
      }
      await loadTasks();
      setShowTaskForm(false);
    } catch (error) {
      console.error('Task action error:', error);
    }
  };

  const availableTools = [
    {
      name: "add_task",
      icon: "➕",
      desc: "Create new tasks",
      action: () => handleToolClick('add_task')
    },
    {
      name: "list_tasks",
      icon: "📋",
      desc: "Show all tasks",
      action: () => handleToolClick('list_tasks')
    },
    {
      name: "complete_task",
      icon: "✅",
      desc: "Mark as done",
      action: () => handleToolClick('complete_task')
    },
    {
      name: "update_task",
      icon: "✏️",
      desc: "Edit tasks",
      action: () => handleToolClick('update_task')
    },
    {
      name: "delete_task",
      icon: "🗑️",
      desc: "Remove tasks",
      action: () => handleToolClick('delete_task')
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {!authLoading && !user && (
          <div className="mb-4 bg-yellow-100 dark:bg-yellow-900/30 border-l-4 border-yellow-500 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="font-semibold text-yellow-800 dark:text-yellow-200">Not Signed In</p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">
                    You need to sign in to use the AI Task Assistant
                  </p>
                </div>
              </div>
              <a
                href="/auth/signin"
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-colors"
              >
                Sign In
              </a>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Tools Sidebar - NOW CLICKABLE */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-purple-100 dark:border-purple-900/50 p-4 sticky top-8">
              <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                <span className="text-xl">🔧</span>
                Quick Actions
              </h3>
              <div className="space-y-2">
                {availableTools.map((tool) => (
                  <button
                    key={tool.name}
                    onClick={tool.action}
                    className="w-full flex items-start gap-2 p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800 hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-all cursor-pointer"
                  >
                    <span className="text-lg">{tool.icon}</span>
                    <div className="text-left">
                      <p className="text-xs font-mono text-purple-700 dark:text-purple-300">
                        {tool.name}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {tool.desc}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  Powered by GPT-4 Turbo
                </p>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="mb-6 text-center">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
                AI Task Assistant
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Click tools or chat naturally to manage your tasks
              </p>
              {user && (
                <p className="text-sm text-green-600 dark:text-green-400 mt-2">
                  ✓ Signed in as {user.email}
                </p>
              )}
            </div>

            {/* Task Form Modal */}
            {showTaskForm && (
              <div className="mb-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-purple-100 dark:border-purple-900/50 p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                    {taskFormMode === 'list' ? 'Your Tasks' : 'Manage Tasks'}
                  </h3>
                  <button
                    onClick={() => setShowTaskForm(false)}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <div className="flex-1">
                        <p className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-800 dark:text-gray-200'}`}>
                          {task.title}
                        </p>
                        <p className="text-xs text-gray-500">Priority: {task.priority}</p>
                      </div>
                      <div className="flex gap-2">
                        {!task.completed && (
                          <button
                            onClick={() => handleTaskAction('complete', task.id)}
                            className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
                          >
                            ✓ Complete
                          </button>
                        )}
                        <button
                          onClick={() => handleTaskAction('delete', task.id)}
                          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                  {tasks.length === 0 && (
                    <p className="text-center text-gray-500 py-4">No tasks found</p>
                  )}
                </div>
              </div>
            )}

            {/* Chat Container */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-2xl border border-purple-100 dark:border-purple-900/50 overflow-hidden">
              <div className="h-[60vh] overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 dark:text-gray-400 mt-20">
                    <div className="text-6xl mb-4">💬</div>
                    <p className="text-lg mb-2">Start a conversation!</p>
                    <p className="text-sm">
                      Try: "Add a task to buy groceries" or "Show my tasks"
                    </p>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-6 py-3 ${
                        msg.role === "user"
                          ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white"
                          : "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
                      }`}
                    >
                      <div className="text-sm font-medium mb-1">
                        {msg.role === "user" ? "You" : "AI Assistant"}
                      </div>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      {msg.tool_calls && msg.tool_calls.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600 text-xs opacity-70">
                          🔧 Used: {msg.tool_calls.map((t) => t?.function?.name || t?.name || 'tool').join(", ")}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl px-6 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce delay-100"></div>
                        <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce delay-200"></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50/50 dark:bg-gray-900/50">
                <div className="flex items-end space-x-3">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message... (Press Enter to send)"
                    className="flex-1 resize-none rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-600 placeholder-gray-400 dark:placeholder-gray-500"
                    rows={1}
                    disabled={loading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={loading || !input.trim()}
                    className="rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-3 text-white font-medium hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    {loading ? "..." : "Send"}
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                  Powered by GPT-4 Turbo • {conversationId ? `Conversation #${conversationId}` : "New conversation"}
                </p>
              </div>
            </div>

            <div className="mt-6 text-center">
              <a
                href="/dashboard"
                className="text-purple-600 dark:text-purple-400 hover:underline text-sm"
              >
                ← Back to Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
