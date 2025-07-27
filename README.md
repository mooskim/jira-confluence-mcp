# Jira Confluence MCP Server

jira-confluence-mcp is a Model Context Protocol (MCP) server that provides a standardized way for AI models to access and interact with resources from Jira and Confluence.

## Configuration

```json
{
  "mcpServers": {
    "jira-confluence-mcp": {
      "command": "uvx",
      "args": [
        "jira-confluence-mcp"
      ],
      "env": {
        "AZURE_OPENAI_API_KEY": "",
        "AZURE_OPENAI_API_VERSION": "",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "",
        "AZURE_OPENAI_ENDPOINT": "",
        "CONFLUENCE_BASE_URL": "",
        "CONFLUENCE_PERSONAL_ACCESS_TOKEN": "",
        "JIRA_BASE_URL": "",
        "JIRA_PERSONAL_ACCESS_TOKEN": ""
      }
    }
  }
}
```

## Tools

### create_issue_jira

    Creates a new Jira issue in a specified project.

    When to Use:
        Use this function to programmatically create a new issue in Jira by specifying the project key, issue type, summary, and description.
        This is useful for automated issue reporting, workflows, or integrating services that need to log new tickets in Jira.

    Args:
        project (str): The key for the Jira project where the issue should be created (e.g., "PROJ").
        issuetype (str): The type of issue to create (e.g., "Bug", "Task", "Story").
        summary (str): A brief summary or title for the new issue.
        description (str): A detailed description of the issue to provide context and reproduction steps if applicable.

    Returns:
        dict[str, Any]: A dictionary containing metadata about the newly created Jira issue, which may include:
            - 'id' (str): The unique identifier of the issue.
            - 'key' (str): The key of the new issue (e.g., "PROJ-123").
            - 'self' (str): The REST API URL of the created issue.

        The returned dictionary structure matches what is returned by Jira's REST API, and may include additional fields.

### get_issue_content_jira

    Retrieves detailed information about a specific Jira issue using its issue ID or key.

    When to Use:
        Use this function to obtain comprehensive and structured information about a Jira issue by specifying its issue ID or key
        (e.g., "PROJ-123"). This includes metadata, status, description, attachments, comments, and more.

    Args:
        issue_id_or_key (str): The issue ID or key of the Jira issue to retrieve (e.g., "PROJ-123").

    Returns:
        dict[str, Any]: A dictionary containing extensive information about the Jira issue, including but not limited to:
            - 'expand' (str): Comma-separated fields that can be expanded with further API calls.
            - 'fields' (dict): A dictionary containing major fields:
                - 'assignee' (dict): Details of the issue assignee (if assigned).
                - 'attachment' (list): List of attached files and their metadata.
                - 'comment' (dict): Metadata for comments, with a list of comment details (author, body, created/updated time, etc.).
                - 'components' (list): List of components related to the issue.
                - 'created' (str): The creation datetime (ISO 8601).
                - 'description' (str): A detailed description, may contain wiki markup or HTML.
                - 'issuetype' (dict): Issue type information (name, description, icons, etc.).
                - 'labels' (list): List of any labels on the issue.
                - 'reporter' (dict): Details of the issue reporter.
                - 'status' (dict): Current workflow status (name, description, etc.).
                - 'summary' (str): A short title or summary of the issue.
                - 'updated' (str): Last updated datetime.
            - 'id' (str): The unique identifier of the issue.
            - 'key' (str): The key of the issue (e.g., "PROJ-123").
            - Other top-level metadata, such as 'self' (REST API URL for this issue), may be present.

        The returned dictionary structure matches what is returned by Jira's REST API for the selected fields, and will contain
        any relevant or additional keys if available in the response. Paging and meta fields are included for comment lists.

### describe_image_jira

    Generates a description of an image attachment from a Jira issue using an AI language model.

    When to Use:
        Use this function to obtain an intelligent summary or analysis of a specific image attachment from Jira (such as a screenshot, diagram, or photo)
        by providing the direct download URL of the image and a custom prompt to guide the AI's description or analysis.

    Args:
        url (str): The direct download URL for the image attachment stored in Jira.
        mime_type (str): The MIME type of the image file (e.g., "image/png", "image/jpeg").
        prompt (str): The prompt or question to guide the AI's description or analysis of the image (e.g., "Describe the main features of this diagram.").

    Returns:
        dict[str, Any] | None: A dictionary containing the AI-generated response, which may include:
            - A summary or description of the image's contents
            - Analysis or interpretation based on the provided prompt
            - Any relevant insights or extracted information depending on the image type and user prompt

        The returned dictionary will be the direct output from the AI language model, structured according to the response format
        of the underlying Azure OpenAI API. Returns None if the image content cannot be retrieved.

### get_page_id_confluence

    Retrieves the unique Confluence page ID based on the space key and page title.

    When to Use:
        Use this function to obtain the internal unique identifier (page ID) of a specific Confluence page,
        by specifying its space key and page title. This ID can be used for subsequent operations such as
        listing attachments, retrieving page content, or updating the page.

    Args:
        space_key (str): The key of the Confluence space where the page is located (e.g., "ENG").
        title (str): The title of the Confluence page as shown in the UI (e.g., "Design Overview").

    Returns:
        str: The unique identifier (page ID) assigned to the specified Confluence page. For example, "123456".

        The returned string represents the page's internal ID in the Confluence instance and can be used
        as input to other functions that require a page identifier.

### create_page_confluence

    Creates a new Confluence page under a specified parent.

    When to Use:
        Use this function to programmatically create a new page in a Confluence space under a given parent page
        by specifying the ancestor (parent page) ID, title, and content body.
        This is useful for automation, documentation workflows, or integrating services that need to add new pages to Confluence.

    Args:
        ancestor_id (str): The page ID of the ancestor (parent page) under which the new page will be added.
        title (str): The title of the new Confluence page.
        body (str): The content of the new page, in Confluence storage format (HTML-based).

    Returns:
        dict[str, Any]: A dictionary containing metadata about the created Confluence page, which may include:
            - 'id' (str): The unique identifier of the new page.
            - 'title' (str): The title of the page.
            - 'space' (dict): Information about the Confluence space.
            - 'body' (dict): Content details, depending on the API's response structure.

        The returned dictionary structure matches what is returned by Confluence's REST API and may contain additional fields.

### get_page_content_with_gliffy_confluence

    Retrieves and processes rich content from a specific Confluence page with embedded Gliffy diagram data.

    When to Use:
        Use this function to obtain detailed HTML content of a Confluence page by specifying its page ID.
        Especially useful when you need to extract or replace embedded Gliffy diagrams as JSON data blocks.

    Args:
        page_id (str): The unique identifier of the Confluence page (e.g., "123456").

    Returns:
        dict[str, Any]: A dictionary containing the page's processed HTML content with the following characteristics:
            - If the page contains Gliffy diagrams (embedded as structured macros), each will be detected via regex,
              and the diagram file's content will be extracted from the Confluence attachment.
            - Gliffy diagram macros are replaced inline with <ac:structured-macro ac:name="code"> blocks,
              presenting the attachment content as CDATA.
            - The rest of the page's HTML markup, including headings, text, expand blocks, lists, links, and Confluence macros
              (such as tables of contents, page links, images, etc.), is preserved.
            - Non-Gliffy attachments, images, and meta structures remain unaffected, except as present in the original page content.

        The returned dictionary structure contains all page content and data in the same format as the original Confluence page,
        except for the processing of Gliffy diagram macros.

### describe_image_confluence

    Generates a description of an image attachment from a specific Confluence page using an AI language model.

    When to Use:
        Use this function to obtain an intelligent summary or analysis of a particular image (such as a screenshot, diagram, or photo)
        stored as an attachment on a Confluence page. The AI's response can be tailored by providing a custom prompt.

    Args:
        page_id (str): The unique identifier of the Confluence page that contains the image attachment.
        filename (str): The filename of the attached image to be described (e.g., "diagram.png").
        mime_type (str): The MIME type of the image file (e.g., "image/png", "image/jpeg").
        prompt (str): The prompt or question to guide the AI's description or analysis of the image (e.g., "Describe the main features of this diagram.").

    Returns:
        dict[str, Any] | None: A dictionary containing the AI-generated response, which may include:
            - A summary or description of the image's contents
            - Analysis or interpretation based on the provided prompt
            - Any relevant insights or extracted information depending on the image type and user prompt

        The returned dictionary will be the direct output from the AI language model, structured according to the response format
        of the underlying Azure OpenAI API. Returns None if the image content cannot be retrieved.

### get_descendant_pages_confluence

    Retrieves the hierarchical tree of all descendant pages for a specific Confluence page.

    When to Use:
        Use this function to obtain the entire descendant page structure (including children, grandchildren, etc.)
        of a given Confluence page by specifying its page ID. This is useful when you need the full nested tree of subpages
        for navigation, visualization, or content aggregation purposes.

    Args:
        page_id (str): The unique identifier of the root Confluence page (e.g., "123456").
        title (str, optional): The title of the root Confluence page. If not provided, an empty string is used.

    Returns:
        dict[str, Any]: A dictionary containing the hierarchical structure of descendant pages in the format:
            - 'id' (str): The ID of the current (root) page.
            - 'title' (str): The title of the current (root) page.
            - 'children' (list): A list of child pages, where each child is itself a dictionary
              with the same structure ('id', 'title', 'children'), forming a recursive tree.

        The returned structure represents the complete page tree rooted at the specified page, allowing you to traverse all levels of descendants.
