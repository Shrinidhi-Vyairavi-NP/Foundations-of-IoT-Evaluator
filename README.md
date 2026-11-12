# Foundations of IoT – Automated Repository Evaluation

This guide explains how to use the Foundations of IoT Evaluator to evaluate your GitHub repository and download your evaluation report.

## 1. Before You Begin

Make sure that:

- You have uploaded your Foundations of IoT experiments to GitHub.
- Your repository follows the prescribed folder structure.
- Your repository is set to **Public**.
- You have copied your GitHub repository URL.

Example repository URL:

`https://github.com/your-username/25011102059_FIoT_Lab`

**Important:** Private repositories cannot currently be evaluated because the evaluator does not use GitHub authentication.

## 2. Open the Evaluator Repository

1. Open the GitHub repository containing the Foundations of IoT Evaluator.
2. Make sure you are logged into your GitHub account.
3. Navigate to the **Actions** tab at the top of the repository.

![GitHub Actions workflow input](steps/actions.jpeg)

## 3. Select the Evaluation Workflow

1. On the left-hand sidebar, find the workflow named:

   **Foundations of IoT Evaluator**

![GitHub Actions workflow input](steps/evaluator_workflow.jpeg)

2. Click the workflow name.
3. You should see a **Run workflow** button on the right-hand side.

![GitHub Actions workflow input](steps/run_workflow.jpeg)

## 4. Run the Evaluation

1. Click **Run workflow**.
2. A dropdown will appear containing an input field named:

   `Public GitHub URL of the student repository`

3. Paste your GitHub repository URL into this field.

   Example:

   `https://github.com/your-username/25011102059_FIoT_Lab`

4. Make sure the URL is correct.
5. Click the green **Run workflow** button.

Your evaluation will now begin.

![GitHub Actions workflow input](steps/upload_gitlink.jpeg)

## 5. Wait for the Evaluation to Complete

1. GitHub will create a new workflow run.
2. Click the running workflow to view its progress.
3. Wait until the workflow finishes.

The status indicators mean:

- **Yellow:** Evaluation is in progress.
- **Green:** Workflow completed successfully.
- **Red:** Workflow encountered an error.

![GitHub Actions workflow input](steps/evaluation_process.jpeg)

**Note:** A green workflow status means the evaluation process completed successfully. It does not necessarily mean that your repository passed all evaluation checks.

## 6. Download Your Evaluation Report

After the workflow finishes:

1. Open the completed workflow run.
2. Go inside Summary
3. Scroll down to the **Artifacts** section.

![GitHub Actions workflow input](steps/download_zip.jpeg)

4. Find the artifact named:

   `Foundations-of-IoT-Evaluation-Report`

5. Click the artifact name to download it.
6. GitHub will download a ZIP file.
7. Extract the ZIP file on your computer.

You will find the evaluation report inside.

## 7. Understand Your Evaluation Report

The report contains:

- Number of experiments discovered.
- Number of experiments passed and failed.
- File and folder checks.
- Missing or incorrect files.
- README availability and contents.
- Overall evaluation status.

Check the failed items carefully and correct any issues in your repository if permitted by your course instructions.

## 8. Troubleshooting

| Problem | What to check |
|---|---|
| Workflow does not start | Make sure you clicked Run workflow. |
| Invalid repository URL | Check that you pasted the complete GitHub HTTPS URL. |
| Repository download fails | Make sure the repository is Public. |
| No experiments discovered | Check your 8051 and STM32 folder structure. |
| Missing file errors | Verify that all required files have been uploaded. |
| Artifact not available | Check whether the workflow generated an evaluation report. |

If the workflow fails, open the workflow run and inspect the failed step to identify the error.

## 9. Important Instructions

- Use your own GitHub repository URL.
- Make sure your repository is Public.
- Do not modify the evaluator repository.
- Do not submit someone else's repository URL.
- Download and inspect your evaluation report after every evaluation.
- A successful workflow execution does not guarantee that all evaluation requirements have passed.

**Ensure that your repository is complete and accessible before submitting its GitHub URL through the designated submission channel.**