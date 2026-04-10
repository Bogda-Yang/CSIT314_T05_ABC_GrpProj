# CI/CD Evidence Report

## 1. Project

- **Project Name**: FireflyFund
- **Repository**: `Bogda-Yang/CSIT314_T05_ABC_GrpProj`
- **Application Type**: FastAPI web application

## 2. Objective

This report provides evidence that FireflyFund uses an automated CI/CD workflow.

- **Continuous Integration (CI)** is used to automatically validate the code after each push or pull request.
- **Continuous Deployment (CD)** is used to automatically deploy the latest version of the application after repository updates.

The purpose of this pipeline is to reduce manual work, improve code quality, and ensure that tested code can be delivered more reliably.

## 3. CI Pipeline Design

The project uses **GitHub Actions** for continuous integration.

### CI Workflow File

- Workflow path: [/.github/workflows/ci.yml](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/.github/workflows/ci.yml)

### CI Trigger Conditions

The workflow runs automatically when:

- code is pushed to `main`,
- code is pushed to a `codex/*` branch,
- a pull request is opened against `main`.

### CI Validation Steps

The workflow performs the following automated checks:

1. Checkout repository source code
2. Set up Python 3.11
3. Install project dependencies from `requirements.txt`
4. Compile backend code with `python -m py_compile main.py`
5. Set up Node.js
6. Validate frontend JavaScript syntax with:
   - `node --check static/auth.js`
   - `node --check static/site.js`
7. Build the Docker image using the project `Dockerfile`

### CI Evidence Screenshots To Capture

Please capture the following screenshots after pushing the workflow to GitHub:

1. **Workflow file in repository**
   - Open GitHub and show `.github/workflows/ci.yml`
   - This proves that the CI workflow has been configured

2. **GitHub Actions run list**
   - Open the `Actions` tab in GitHub
   - Show the workflow name `FireflyFund CI`
   - Show that the workflow was triggered automatically after a push

3. **Successful workflow run details**
   - Open one completed run
   - Show all green steps:
     - Checkout repository
     - Set up Python
     - Install dependencies
     - Compile backend
     - Set up Node.js
     - Validate frontend scripts
     - Build Docker image

4. **Commit status evidence**
   - Show a commit or pull request page with a green check mark
   - This proves that CI is linked to repository activity

## 4. CD Pipeline Design

The project is prepared for deployment using **Render** with automatic deployment enabled from GitHub.

### CD Configuration File

- Deployment config path: [/render.yaml](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/render.yaml)
- Docker runtime file: [/Dockerfile](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/Dockerfile)

### CD Deployment Logic

The intended deployment flow is:

1. Push code to GitHub
2. GitHub stores the latest commit
3. Render detects repository changes
4. Render automatically rebuilds and redeploys the application
5. The live website updates to the newest version

### Required Environment Variables for Deployment

The following variables must be configured in Render:

- `DATABASE_URL`
- `SECRET_KEY`
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_HOST`
- `SMTP_PORT`

### CD Evidence Screenshots To Capture

After linking the repository to Render, please capture:

1. **Render service dashboard**
   - Show the service name and repository connection
   - This proves the deployment target is connected to GitHub

2. **Render environment variables page**
   - Show that required environment variables are configured
   - You may blur or hide sensitive values

3. **Deployment log triggered by a new commit**
   - Push a small change to GitHub
   - Open the Render deploy logs
   - Show that a new deployment started automatically

4. **Successful deployment status**
   - Show the Render page with status such as `Live`, `Deploy successful`, or equivalent

5. **Live application page**
   - Open the deployed FireflyFund URL
   - Show that the latest changes are visible online

## 5. Suggested Demonstration Procedure

To create clear evidence for your lecturer, use the following sequence:

1. Push the new `.github/workflows/ci.yml` file to GitHub
2. Open the `Actions` tab and wait for the CI workflow to finish
3. Capture the CI screenshots listed above
4. Create or connect a Render web service to this repository
5. Add the required environment variables in Render
6. Trigger one more GitHub push
7. Capture the Render deployment screenshots listed above
8. Open the live site and capture the final running application screenshot

## 6. Suggested Figure Captions

You may use the following captions in your final report:

- **Figure 1.** GitHub Actions CI workflow file configured for FireflyFund.
- **Figure 2.** CI workflow triggered automatically after code was pushed to GitHub.
- **Figure 3.** Successful CI pipeline run with all validation steps completed.
- **Figure 4.** Render service connected to the FireflyFund GitHub repository.
- **Figure 5.** Automatic deployment triggered after a repository update.
- **Figure 6.** Live FireflyFund application after successful deployment.

## 7. Conclusion

The FireflyFund project is prepared with an automated CI/CD workflow.

- The **CI pipeline** uses GitHub Actions to automatically validate backend code, frontend JavaScript syntax, and Docker build readiness.
- The **CD pipeline** is configured for automatic deployment through Render after repository updates.

This demonstrates that the project follows an automated software delivery workflow rather than a fully manual process.

## 8. Submission Note

Before submission, replace this line with your actual evidence screenshots and fill in:

- screenshot images,
- deployment URL,
- test dates,
- any platform-specific deployment status details.
