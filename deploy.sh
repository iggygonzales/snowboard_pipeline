#!/bin/bash
echo "Pulling latest changes from GitHub..."
cd /home/ec2-user/snowboard_pipeline
git stash
git pull

echo "Rebuilding Docker image..."
docker build -t snowboard-pipeline .

echo "Restarting container..."
docker stop snowboard
docker rm snowboard
docker run -d -p 8501:8501 \
  -v /home/ec2-user/snowboard_pipeline/data:/app/data \
  --env-file /home/ec2-user/snowboard_pipeline/.env \
  --name snowboard snowboard-pipeline

echo "Done! Dashboard running at http://52.14.162.178:8501"
