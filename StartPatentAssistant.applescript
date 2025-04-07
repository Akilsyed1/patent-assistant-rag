-- AppleScript to start Patent Assistant RAG application
tell application "Terminal"
    -- Open a new terminal window
    do script ""
    -- Change to the application directory
    do script "cd /Users/syedhazeena/Desktop/rag/enterprise-rag-ui/frontend" in front window
    -- Run the Flask application
    do script "python app.py" in front window
    -- Open the web browser to the application
    do script "open http://127.0.0.1:5002" in front window
end tell

-- Display notification
display notification "Patent Assistant RAG is starting..." with title "Patent Assistant"
