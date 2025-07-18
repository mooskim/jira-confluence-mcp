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

```
@mcp.tool()
def get_issue_content_jira(issue_id_or_key: str) -> dict[str, Any]:
    """
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
    """
```

```
@mcp.tool()
def get_page_id_confluence(space_key: str, title: str) -> str:
    """
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
    """
```

```
@mcp.tool()
def list_attachments_confluence(page_id: str) -> list[dict[str, Any]]:
    """
    Lists all attachments from a specified Confluence page.

    When to Use:
        Use this function to obtain metadata for all attachments associated with a particular Confluence page,
        identified by its page ID.

    Args:
        page_id (str): The unique identifier of the Confluence page whose attachments you want to list.

    Returns:
        list[dict[str, Any]]: A list of attachment objects for the given page. Each object contains detailed metadata, including (but not limited to):
            - '_expandable' (dict): More expandable Confluence fields (for advanced use).
            - '_links' (dict): Various URLs, including:
                - 'download' (str): Direct download URL for the file.
                - 'self' (str): API detail URL for the attachment.
                - 'thumbnail' (str, optional): Thumbnail preview URL (for images).
                - 'webui' (str): Web UI preview URL.
            - 'extensions' (dict): Additional metadata:
                - 'comment' (str): Same as above.
                - 'fileSize' (int): File size in bytes.
                - 'mediaType' (str): MIME type.
            - 'id' (str): The unique identifier for the attachment.
            - 'metadata' (dict): Metadata about the attachment, which contains:
                - '_expandable' (dict): Expandable fields (for internal Confluence use).
                - 'comment' (str): Attachment description (e.g., 'GLIFFY DIAGRAM', 'GLIFFY IMAGE').
                - 'labels' (dict): Label metadata (may include 'results', 'start', 'limit', 'size', and '_links').
                - 'mediaType' (str): MIME type, such as 'application/gliffy+json' or 'image/png'.
            - 'status' (str): The attachment's status (e.g., 'current').
            - 'title' (str): The filename or title of the attachment.
            - 'type' (str): The content type (typically 'attachment').

        The returned objects may include additional keys depending on the Confluence API.
    """
```

```
@mcp.tool()
def get_page_content_with_gliffy_confluence(page_id: str) -> str:
    """
    Retrieves and processes rich content from a specific Confluence page with embedded Gliffy diagram data.

    When to Use:
        Use this function to obtain detailed HTML content of a Confluence page by specifying its page ID.
        Especially useful when you need to extract or replace embedded Gliffy diagrams as JSON data blocks.

    Args:
        page_id (str): The unique identifier of the Confluence page (e.g., "123456").

    Returns:
        str: A string containing the page's processed HTML content with the following characteristics:
            - If the page contains Gliffy diagrams (embedded as structured macros), each will be detected via regex,
              and the diagram file's content will be extracted from the Confluence attachment.
            - Gliffy diagram macros are replaced inline with <ac:structured-macro ac:name="code"> blocks,
              presenting the attachment content as CDATA.
            - The rest of the page's HTML markup, including headings, text, expand blocks, lists, links, and Confluence macros
              (such as tables of contents, page links, images, etc.), is preserved.
            - Non-Gliffy attachments, images, and meta structures remain unaffected, except as present in the original page content.

        The returned HTML content may contain, but is not limited to, the following structures:
            - Headings (e.g., <h1>, <h2>)
            - Lists and nested lists (<ul>, <li>)
            - Tables (class="relative-table wrapped")
            - Confluence macros (expand, toc, jira-link, image, etc.)
            - Custom macros that reference Confluence/Jira/attachments
            - Embedded diagrams or code blocks
    """
```

```
@mcp.tool()
def describe_image_confluence(
    page_id: str, filename: str, prompt: str
) -> dict[str, Any] | None:
    """
    Generates a description of an image attachment from a specific Confluence page using an AI language model.

    When to Use:
        Use this function to obtain an intelligent summary or analysis of a particular image (such as a screenshot, diagram, or photo)
        stored as an attachment on a Confluence page. The AI's response can be tailored by providing a custom prompt.

    Args:
        page_id (str): The unique identifier of the Confluence page that contains the image attachment.
        filename (str): The filename of the attached image to be described (e.g., "diagram.png").
        prompt (str): The prompt or question to guide the AI's description or analysis of the image (e.g., "Describe the main features of this diagram.").

    Returns:
        dict[str, Any]: A dictionary containing the AI-generated response, which may include:
            - A summary or description of the image's contents
            - Analysis or interpretation based on the provided prompt
            - Any relevant insights or extracted information depending on the image type and user prompt

        The returned dictionary will be the direct output from the AI language model, structured according to the response format
        of the underlying Azure OpenAI API.
    """
```
