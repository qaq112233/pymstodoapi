#!/usr/bin/env python3
"""
Demo script to show HTML rendering output
This creates a mock HTML output to demonstrate the styling for e-ink displays
"""
from datetime import datetime
import pytz

# Mock task data
mock_tasks = [
    {'title': 'Regular task 1', 'is_starred': False, 'is_due_today': False},
    {'title': 'Important task (starred)', 'is_starred': True, 'is_due_today': False},
    {'title': 'Due today task', 'is_starred': False, 'is_due_today': True},
    {'title': 'Important AND due today', 'is_starred': True, 'is_due_today': True},
    {'title': 'Regular task 2', 'is_starred': False, 'is_due_today': False},
    {'title': 'Another due today task', 'is_starred': False, 'is_due_today': True},
]

# Generate timestamp
shanghai_tz = pytz.timezone('Asia/Shanghai')
generated_at = datetime.now(shanghai_tz).strftime('%Y-%m-%d %H:%M:%S')

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tasks</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1600px;
            height: 960px;
            background-color: #FFFFFF;
            font-family: Arial, Helvetica, sans-serif;
            overflow: hidden;
            padding: 20px;
        }}
        
        .timestamp {{
            font-size: 12px;
            color: #666666;
            margin-bottom: 15px;
        }}
        
        .task-list {{
            width: 100%;
        }}
        
        .task-item {{
            width: 100%;
            padding: 15px 10px;
            border-bottom: 2px solid #000000;
            line-height: 1.6;
            font-size: 18px;
        }}
        
        .task-item.starred {{
            color: #FF0000;
            font-weight: bold;
        }}
        
        .task-item.due-today {{
            background-color: #FFE599;
            font-weight: bold;
        }}
        
        .task-item.starred.due-today {{
            background-color: #FFE599;
            color: #FF0000;
            font-weight: bold;
        }}
        
        .task-title {{
            font-size: 20px;
        }}
    </style>
</head>
<body>
    <div class="timestamp">Generated at: {generated_at} (UTC+8)</div>
    <div class="task-list">
"""

for task in mock_tasks:
    classes = []
    if task['is_starred']:
        classes.append('starred')
    if task['is_due_today']:
        classes.append('due-today')
    
    class_str = ' '.join(classes)
    html += f"""        <div class="task-item {class_str}">
            <div class="task-title">{task['title']}</div>
        </div>
"""

html += """    </div>
</body>
</html>"""

# Save to file
output_file = '/tmp/tasks_demo.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Demo HTML generated at: {output_file}")
print(f"\nYou can open this file in a browser to see the e-ink display layout")
print(f"\nLayout specifications:")
print(f"  - Resolution: 1600x960 (2x for 800x480 e-ink displays)")
print(f"  - Background: White (#FFFFFF)")
print(f"  - Starred tasks: Red (#FF0000), bold")
print(f"  - Due today tasks: Yellow background (#FFE599), bold")
print(f"  - Combined: Yellow background + red text + bold")
print(f"\nGenerated at: {generated_at} (UTC+8)")
