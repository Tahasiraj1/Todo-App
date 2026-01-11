// [Task]: T046, T056, T089 [From]: spec.md §US-002
"use client";

/**
 * Dashboard page with task list and creation form.
 * Main authenticated user interface.
 */

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TaskForm } from "@/components/tasks/task-form";
import { TaskList } from "@/components/tasks/task-list";
import { TaskEditDialog } from "@/components/tasks/task-edit-dialog";
import { DeleteTaskDialog } from "@/components/tasks/delete-task-dialog";
import { SignOutButton } from "@/components/auth/sign-out-button";
import { listTasks, ApiClientError } from "@/lib/api";
import type { Task } from "@/types/task";

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit dialog state
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  // Delete dialog state
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Ref to task form for focus
  const formRef = useRef<HTMLDivElement>(null);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetchedTasks = await listTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(typeof err.detail === "string" ? err.detail : "Failed to load tasks");
      } else {
        setError("Failed to load tasks. Please refresh the page.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle new task created
  const handleTaskCreated = (newTask: Task) => {
    setTasks((prev) => [newTask, ...prev]);
  };

  // Handle task updated (from edit or toggle)
  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  };

  // Handle task deleted
  const handleTaskDeleted = (taskId: number) => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  // Open edit dialog
  const handleEditClick = (task: Task) => {
    setEditingTask(task);
    setIsEditDialogOpen(true);
  };

  // Open delete dialog
  const handleDeleteClick = (task: Task) => {
    setDeletingTask(task);
    setIsDeleteDialogOpen(true);
  };

  // Scroll to and focus on form
  const handleAddFirstTask = () => {
    formRef.current?.scrollIntoView({ behavior: "smooth" });
    const input = formRef.current?.querySelector("input");
    input?.focus();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-xl font-bold text-gray-900 sm:text-2xl">
            Todo App
          </h1>
          <SignOutButton />
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Error banner */}
        {error && (
          <div
            className="mb-6 rounded-md bg-red-50 p-4 text-sm text-red-600"
            role="alert"
          >
            {error}
            <button
              onClick={loadTasks}
              className="ml-2 font-medium underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        )}

        {/* Task creation form */}
        <Card className="mb-6" ref={formRef}>
          <CardHeader>
            <CardTitle>Add New Task</CardTitle>
          </CardHeader>
          <CardContent>
            <TaskForm onTaskCreated={handleTaskCreated} />
          </CardContent>
        </Card>

        {/* Task list */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Your Tasks</span>
              {!isLoading && tasks.length > 0 && (
                <span className="text-sm font-normal text-gray-500">
                  {tasks.filter((t) => !t.completed).length} remaining
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TaskList
              tasks={tasks}
              isLoading={isLoading}
              onTaskUpdated={handleTaskUpdated}
              onEditClick={handleEditClick}
              onDeleteClick={handleDeleteClick}
              onAddFirstTask={handleAddFirstTask}
            />
          </CardContent>
        </Card>

        {/* Edit dialog */}
        <TaskEditDialog
          task={editingTask}
          open={isEditDialogOpen}
          onOpenChange={setIsEditDialogOpen}
          onTaskUpdated={handleTaskUpdated}
        />

        {/* Delete dialog */}
        <DeleteTaskDialog
          task={deletingTask}
          open={isDeleteDialogOpen}
          onOpenChange={setIsDeleteDialogOpen}
          onTaskDeleted={handleTaskDeleted}
        />
      </main>
    </div>
  );
}
