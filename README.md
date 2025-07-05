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
      ]
    }
  }
}
```

## Tools

```
@mcp.tool()
def get_issue_jira(issue_id_or_key: str) -> dict[str, Any]:
    """
    Retrieves detailed information about a specific Jira issue using its ID or key.

    When to Use:
        Use this function to obtain information about a Jira issue by specifying its issue ID or key (e.g., "PROJ-123").

    Args:
        issue_id_or_key (str): The issue ID or key of the Jira issue (e.g., "PROJ-123").

    Returns:
        dict[str, Any]: A dictionary containing comprehensive information about the Jira issue.

        The returned dictionary includes (but is not limited to) the following keys:

        - 'expand' (str): Comma-separated list of fields that can be expanded for more details.
        - 'fields' (dict[str, Any]): A dictionary of issue fields and their values. Important fields include:
            - 'assignee' (dict or None): The user assigned to the issue.
            - 'attachment' (list[dict]): List of attachments, each containing:
                - 'author' (dict): Info about the user who added the attachment.
                - 'content' (str): Direct download URL.
                - 'created' (str): Date/time the attachment was added.
                - 'filename' (str): Name of the file.
                - 'id' (str): The attachment ID.
                - 'mimeType' (str): MIME type.
                - 'size' (int): Attachment size in bytes.
            - 'comment' (dict): Comments meta and a list of comment objects. Each comment provides:
                - 'author' (dict): Author info.
                - 'body' (str): Comment text.
                - 'created' (str): Creation datetime.
                - 'id' (str): Comment ID.
                - 'updated' (str): Last update datetime.
            - 'components' (list[dict]): List of components assigned to this issue.
            - 'created' (str): Creation date/time (ISO 8601).
            - 'description' (str): The detailed description of the issue (may contain Jira wiki markup or HTML).
            - 'issuetype' (dict): Information about the issue type (e.g., name, iconUrl, etc).
            - 'labels' (list[str]): List of labels on this issue.
            - 'reporter' (dict): The user who reported the issue.
            - 'status' (dict): The current status of the issue (e.g., name, id, category).
            - 'summary' (str): The summary or title of the issue.
            - 'updated' (str): Last update date/time (ISO 8601).
        - 'id' (str): The unique identifier of the issue.
        - 'key' (str): The issue key (e.g., "PROJ-123").
        - 'self' (str): The REST API URL for this issue resource.
        - Additional metadata keys (e.g., 'maxResults', 'total', 'startAt') may be present for paged fields like comments.
    """
```

```
@mcp.tool()
def get_content_confluence(page_id: str) -> str:
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
              presenting the binary or JSON content (as CDATA).
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
