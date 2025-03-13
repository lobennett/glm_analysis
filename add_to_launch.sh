for batch_file in ./task_*_fixed-effects.batch; do
    task_name=$(echo "$batch_file" | awk -F'_' '{print $2}')
    echo "Processing batch file: $batch_file with task name: $task_name"
    
    # Prompt for line numbers
    echo "Enter the line numbers you want to process (e.g., 1-20 or a single line like 5):"
    read line_range
    
    # Validate and process the line range or single line
    if [[ $line_range =~ ^[0-9]+-[0-9]+$ ]]; then
        start_line=$(echo $line_range | cut -d'-' -f1)
        end_line=$(echo $line_range | cut -d'-' -f2)
        sed -n "${start_line},${end_line}p" subs.txt | while IFS= read -r id || [ -n "$id" ]; do
            echo "Processing ID: $id"
            echo "" >> "$batch_file"
            # echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events" >> "$batch_file"
            # echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events" >> "$batch_file"
            # echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break" >> "$batch_file"
            # echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break" >> "$batch_file"
            # echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --omit_deriv" >> "$batch_file"
            # echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --omit_deriv" >> "$batch_file"
            echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break --only_breaks_with_performance_feedback --omit_deriv" >> "$batch_file"
            echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break --only_breaks_with_performance_feedback --omit_deriv" >> "$batch_file"
            echo "" >> "$batch_file"
        done
    elif [[ $line_range =~ ^[0-9]+$ ]]; then
        sed -n "${line_range}p" subs.txt | while IFS= read -r id || [ -n "$id" ]; do
            echo "Processing ID: $id"
            echo "" >> "$batch_file"
            echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events" >> "$batch_file"
            echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events" >> "$batch_file"
            echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break" >> "$batch_file"
            echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break" >> "$batch_file"
            echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --omit_deriv" >> "$batch_file"
            echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --omit_deriv" >> "$batch_file"
            echo "echo ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break --omit_deriv" >> "$batch_file"
            echo "python3 ./analyze_lev1_v4.py ${task_name} ${id} rt_centered --fixed_effects --simplified_events --model_break --omit_deriv" >> "$batch_file"
            echo "" >> "$batch_file"
        done
    else
        echo "Invalid input. Please enter a valid range like 1-20 or a single line number."
    fi
done