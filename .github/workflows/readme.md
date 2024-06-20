# Documentation for GitHub Actions Workflows

## Table of Contents

- [Documentation for GitHub Actions Workflows](#documentation-for-github-actions-workflows)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Setup and Configuration](#setup-and-configuration)
  - [Continuous Integration Workflow](#continuous-integration-workflow)
    - [Triggers](#triggers)
    - [Jobs and Steps](#jobs-and-steps)
  - [Continuous Delivery Workflow](#continuous-delivery-workflow)
    - [Triggers](#triggers-1)
    - [Jobs and Steps](#jobs-and-steps-1)
  - [Continuous Deployment Workflow](#continuous-deployment-workflow)
    - [Triggers](#triggers-2)
    - [Jobs and Steps](#jobs-and-steps-2)

## Introduction

This documentation provides a comprehensive guide to the CI/CD workflows configured for the Django application using GitHub Actions. It covers all steps, tasks, triggers, installation, configuration, and testing procedures.

## Setup and Configuration

Before using the workflows, ensure you have the necessary secrets set up in your GitHub repository. The required secrets are:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_PASSWORD`
- `AZURE_CREDENTIALS`
- `SUBSCRIPTION_ID`
- `RESOURCE_GROUP`
- `RESSOURCE_GROUP`
- `WORKSPACE_NAME`
- `SERVER`
- `DATABASE`
- `POSTGRES_USER`
- `PASSWORD`
- `SECRET_KEY`

To add these secrets:

1. Navigate to your GitHub repository.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Click on **New repository secret**.
4. Add each secret with the appropriate values.

## Continuous Integration Workflow

### Triggers

The CI workflow is triggered on every push to features branch or develop branch


### Jobs and Steps

Job: Health Check
This job ensures the code quality and correctness through unittesting, code formatting checks and code security check

## Continuous Delivery Workflow
### Triggers
The Continuous delivery workflow is triggered on pull requests on develop and main branches and on push on develop branch

paths:
    - 'api/**'
    - '.github/workflows/cd.yaml'

### Jobs and Steps
Job: Build and Deploy
This job builds a Docker image, pushes it to Docker Hub, and deploys it to a test Azure Container Instance.
Then it delete the ACRI

## Continuous Deployment Workflow
### Triggers
The Continuous delivery workflow is triggered on pushes on the main branch.

paths:
    - 'api/**'
    - '.github/workflows/cd.yaml'

### Jobs and Steps
Job: Build and Deploy
This job builds a Docker image, pushes it to Docker Hub, and deploys it to Azure Container Instance.