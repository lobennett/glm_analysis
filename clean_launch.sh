for batch_file in ./task_*_fixed-effects.batch; do
    echo "Processing batch file: $batch_file"
    
    # Find the line number of "echo "Running analysis..."" in the batch file
    line_number=$(grep -n 'echo "Running analysis..."' "$batch_file" | cut -d: -f1)
    
    if [ -n "$line_number" ]; then
        # Remove everything under the line "echo "Running analysis..."" in the batch file
        sed -i "$((line_number + 1)),\$d" "$batch_file"
        echo "Removed lines under 'echo \"Running analysis...\"' in $batch_file"
    else
        echo "'echo \"Running analysis...\"' not found in $batch_file"
    fi
done
