# CI/CD Evidence Report for FireflyFund

## 1. Project Overview

- **Project Name**: FireflyFund
- **Repository**: `Bogda-Yang/CSIT314_T05_ABC_GrpProj`
- **Technology Stack**: FastAPI, SQLAlchemy, Supabase PostgreSQL, JavaScript, Docker
- **Live Deployment URL**: [https://fireflyfund.onrender.com](https://fireflyfund.onrender.com)

This report presents the final evidence that the FireflyFund project uses an automated **Continuous Integration (CI)** and **Continuous Deployment (CD)** workflow.

## 2. Objective

The objective of this report is to demonstrate that:

- code validation is automated through GitHub Actions,
- deployment is automated through Render,
- repository updates can trigger deployment updates without manual reconfiguration,
- the deployed system becomes accessible online after successful pipeline execution.

## 3. CI Implementation

The project uses **GitHub Actions** as its CI platform.  
The workflow is defined in the repository under:

- [/.github/workflows/ci.yml](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/.github/workflows/ci.yml)

The workflow runs automatically on push events to `main` and validates the project by:

1. checking out the repository,
2. setting up Python 3.11,
3. installing project dependencies,
4. compiling backend code with `python -m py_compile main.py`,
5. setting up Node.js,
6. checking frontend JavaScript syntax,
7. building the Docker image.

## 4. CD Implementation

The project uses **Render** as its deployment platform.  
Deployment is configured with:

- [/render.yaml](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/render.yaml)
- [/Dockerfile](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/Dockerfile)

Render is connected to the GitHub repository and automatically redeploys the application after new commits are pushed to `main`.

## 5. Evidence

### Figure 1. GitHub Actions workflow file configured in the repository

![Figure 1](/Users/apple/Desktop/1.png)

**Explanation:**  
This figure shows that the CI workflow file `ci.yml` exists inside `.github/workflows/`. This is the configuration that enables automated CI execution in GitHub Actions.

### Figure 2. GitHub Actions workflow executed successfully

![Figure 2](/Users/apple/Desktop/2.png)

**Explanation:**  
This figure shows a successful run of the `FireflyFund CI` workflow after a push to the `main` branch. It proves that CI was triggered automatically and completed successfully.

### Figure 3. Render deployment history showing failure, auto-redeployment, and successful live deployment

![Figure 3](/Users/apple/Desktop/3.png)

**Explanation:**  
This figure shows the Render deployment history. It demonstrates that:

- an initial deployment failed,
- a later commit triggered a new deployment automatically,
- the latest deployment became `live`.

This is strong evidence of continuous deployment automation and iterative troubleshooting.

### Figure 4. Render service logs confirming successful startup and live service status

![Figure 4](/Users/apple/Desktop/4.png)

**Explanation:**  
This figure shows the Render service logs. The log confirms that the application started successfully and that the service became live at the provided Render URL.

### Figure 5. Render environment variables configured for deployment

![Figure 5](/Users/apple/Desktop/5.png)

**Explanation:**  
This figure shows that the deployment environment variables were configured in Render, including database connection, secret key, and SMTP settings. Sensitive values were appropriately hidden.

### Figure 6. Live FireflyFund application running online after deployment

![Figure 6](/Users/apple/Desktop/6.png)

**Explanation:**  
This figure shows the FireflyFund website running through the Render deployment URL, demonstrating that the CD pipeline produced a live and accessible web application.

## 6. Deployment Troubleshooting Note

During the deployment process, two issues were encountered and resolved:

1. **Missing dependency issue**
   - Render initially failed because the package `itsdangerous` was not listed in `requirements.txt`.
   - After adding the missing dependency and pushing a new commit, Render automatically triggered another deployment.

2. **Template rendering compatibility issue**
   - The deployed environment exposed a template rendering issue related to deployment compatibility.
   - After adjusting the template response implementation and pushing the fix, GitHub Actions re-ran automatically and Render redeployed the project successfully.

This troubleshooting process further demonstrates the value of CI/CD automation, since each correction was revalidated and redeployed through the pipeline.

## 7. Conclusion

The FireflyFund project successfully demonstrates an automated CI/CD workflow.

- **CI** was implemented using GitHub Actions to automatically validate backend compilation, frontend JavaScript syntax, and Docker build readiness.
- **CD** was implemented using Render to automatically deploy repository updates to a live public URL.
- The evidence shows that pushes to GitHub triggered both automated CI checks and automated redeployment.

Therefore, the project satisfies the requirement of demonstrating a working CI/CD process with practical deployment evidence.

## 8. Deployment Limitation Note

The deployed application currently uses a **Render free instance**.

This means:

- the service may spin down after inactivity,
- the first request after inactivity may be slower,
- temporary gateway errors such as `502 Bad Gateway` may occasionally appear during cold start or recovery.

This behaviour is related to the hosting plan rather than the CI/CD design itself. The automated pipeline remains valid because repository updates still trigger automatic validation and redeployment successfully.

## 9. Final Evidence Summary

The final evidence set includes:

1. GitHub workflow configuration screenshot
2. GitHub Actions successful run screenshot
3. Render deployment history screenshot
4. Render successful log screenshot
5. Render environment variable screenshot
6. Live deployed website screenshot

These figures together provide sufficient evidence for both CI and CD in the FireflyFund project.
