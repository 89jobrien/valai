from valai.tools import (
    calendar_tools,
    code_tools,
    email_tools,
    file_tools,
    knowledge_tools,
    note_tools,
    search_tools,
    system_tools,
    todo_tools,
    webscraping_tools,
    writing_tools,
)

TOOL_REGISTRY = {
    # Search
    "web_search": search_tools.web_search,
    # Note Taking
    "save_note": note_tools.save_note,
    "retrieve_notes": note_tools.retrieve_notes,
    "search_notes": note_tools.search_notes,
    "delete_note": note_tools.delete_note,
    # Knowledge Base
    "add_document_to_knowledge_base": knowledge_tools.add_document_to_knowledge_base,
    "search_knowledge_base": knowledge_tools.search_knowledge_base,
    "get_knowledge_base_stats": knowledge_tools.get_knowledge_base_stats,
    # Code Execution
    "run_python_code": code_tools.run_python_code,
    # File Management
    "write_file": file_tools.write_file,
    "read_file": file_tools.read_file,
    "list_directory": file_tools.list_directory,
    "create_directory": file_tools.create_directory,
    "delete_file_or_directory": file_tools.delete_file_or_directory,
    # Calendar
    "list_upcoming_events": calendar_tools.list_upcoming_events,
    "create_calendar_event": calendar_tools.create_calendar_event,
    # Web Scraping
    "scrape_url": webscraping_tools.scrape_url,
    # Email
    "send_email": email_tools.send_email,
    # System
    "get_system_metrics": system_tools.get_system_metrics,
    "get_current_time": system_tools.get_current_time,
    # To-Do
    "add_todo": todo_tools.add_todo,
    "view_todos": todo_tools.view_todos,
    "complete_todo": todo_tools.complete_todo,
    # Writing
    "improve_writing": writing_tools.improve_writing,
    "fix_spelling_grammar": writing_tools.fix_spelling_grammar,
    "make_shorter": writing_tools.make_shorter,
    "make_longer": writing_tools.make_longer,
    "change_tone": writing_tools.change_tone,
}
