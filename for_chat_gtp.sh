#!/bin/dash
# Print all Python, Markdown, and Shell script files and relevant configuration files to a single file project_files.txt

find /home/sami/sorsat/GPTonRoids -type d \( -name "__pycache__" -o -name "venv" -o -name ".pytest_cache" \) -prune -o \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) -print > /tmp/project_files.txt
echo '/home/sami/sorsat/GPTonRoids/requirements.txt' >> /tmp/project_files.txt
echo '/home/sami/sorsat/GPTonRoids/openapi/openapi.yaml' >> /tmp/project_files.txt
echo '/home/sami/sorsat/GPTonRoids/task_plan.txt' >> /tmp/project_files.txt
echo '/home/sami/sorsat/GPTonRoids/instructions_for_gtp.txt' >> /tmp/project_files.txt

# Append the content of each file to project_files.txt
echo > /tmp/project_files_content.txt
for file in $(cat /tmp/project_files.txt); do
  echo "$file:" >> /tmp/project_files_content.txt
  cat "$file" >> /tmp/project_files_content.txt
  echo "\n" >> /tmp/project_files_content.txt
done

# Copy the content of project_files_content.txt to the clipboard
xclip -selection clipboard < /tmp/project_files_content.txt