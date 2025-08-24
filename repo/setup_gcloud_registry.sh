#!/bin/bash
# Setup Google Cloud Artifact Registry for Python packages

PROJECT_ID="segnomms"
LOCATION="us-central1"
REPOSITORY_NAME="prerelease"

echo "Setting up Google Cloud Artifact Registry for project: $PROJECT_ID"
echo "============================================================"

# Set the project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "\nEnabling required APIs..."
gcloud services enable artifactregistry.googleapis.com

# Create the repository
echo -e "\nCreating Python package repository..."
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=python \
    --location=$LOCATION \
    --description="Public Python package repository for segnomms"

# Make the repository public
echo -e "\nMaking repository public..."
gcloud artifacts repositories add-iam-policy-binding $REPOSITORY_NAME \
    --location=$LOCATION \
    --member="allUsers" \
    --role="roles/artifactregistry.reader"

# Configure authentication for uploads
echo -e "\nConfiguring authentication for package uploads..."
gcloud artifacts print-settings python \
    --repository=$REPOSITORY_NAME \
    --location=$LOCATION

# Get the repository URL
REPO_URL="https://${LOCATION}-python.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/"
echo -e "\n✅ Repository created successfully!"
echo "Repository URL: $REPO_URL"
echo ""
echo "To configure pip for installing from this repository:"
echo "pip install --index-url $REPO_URL simple"
echo ""
echo "To configure twine for uploading packages:"
echo "1. Install keyring and keyrings.google-artifactregistry-auth:"
echo "   pip install keyring keyrings.google-artifactregistry-auth"
echo ""
echo "2. Create ~/.pypirc with:"
echo "[distutils]"
echo "index-servers ="
echo "    $REPOSITORY_NAME"
echo ""
echo "[$REPOSITORY_NAME]"
echo "repository = $REPO_URL"
echo ""
echo "3. Upload with:"
echo "   twine upload --repository $REPOSITORY_NAME dist/*"