# SKILL: Interactive Task Workflow

This workflow serves as a structured blueprint for managing development tasks interactively within a Git environment. It ensures clear goal definition, branch isolation, architectural alignment, and deliberate progress verification through strict check-ins before any final automation or execution takes place.

---

## 📋 The 6-Step Workflow Blueprint

### Step 1: Understand the Requirements*   **Objective:** Capture and isolate the core deliverables for the assigned task.*   **Action:** Document the functional scope, edge cases, and explicit constraints.*   **State Check:** Ensure the scope is fully defined before moving forward.

### Step 2: Create an Instructive Branch*   **Objective:** Establish a clean, isolated workspace with a meaningful context identifier.*   **Action:** Generate a standardized, descriptive slug based on the primary requirement (e.g., `feature/short-requirement-summary`) and switch to it immediately: `git checkout -b feature/your-descriptive-task-name`.*   **State Check:** Verify branch creation and dynamic name relevance before initializing analysis.

### Step 3: Parse and Explain Requirements 🛑 (Checkpoint 1)*   **Objective:** Verify absolute alignment on the task's final goal.*   **Action:** Present the collected requirements clearly back to the user to confirm nothing was missed or misinterpreted.*   **State Check:** **Pause for Approval.** Do not write any code or advance the workflow until you receive explicit User Approval.

### Step 4: Explain the Technical Approach 🛑 (Checkpoint 2)*   **Objective:** Define architectural boundaries and engineering best practices before execution.*   **Action:** Present a high-level strategy detailing target components, modularity guidelines, and local validation plans.*   **State Check:** **Pause for Approval.** Do not advance until you receive explicit User Approval on this specific strategy.

### Step 5: Outline the Concrete Execution Steps 🛑 (Checkpoint 3)*   **Objective:** Define the exact roadmap to reach completion.*   **Action:** Present a sequential implementation plan breaking down base file layout layout (Phase A), integration checks (Phase B), and auto-staging (Phase C).*   **State Check:** **Pause for Approval.** Do not advance until you receive explicit User Approval on the final execution plan.

### Step 6: Run the Steps and Finalize Tracking*   **Objective:** Execute the approved, automated roadmap.*   **Action:** Auto-generate a local requirement-tracking manifest (`TASK_REQUIREMENTS.md`) inside the workspace root and run `git add TASK_REQUIREMENTS.md` to stage it into Git tracking.*   **State Check:** Formally hand over the cleanly prepared, staged, and synchronized workspace branch to the user to begin code development.

### Step 7: Run "git add ." and then "git commit -m "{Outline of the steps you did}"". 

---

> ### 💡 System Prompt Directive
> You must strictly adhere to the pauses indicated at **Step 3, Step 4, and Step 5**. Under no circumstances should you generate code modifications or run setup steps until the user has explicitly typed their approval for that specific checkpoint phase.