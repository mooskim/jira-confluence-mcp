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

    When to use:
        Use this function to create a new Jira issue.

    Args:
        project (str): The key of the project where the issue will be created.
        issue_type (str): The type of issue to create. Available types are Bug, Story, or Task.
            Bug: A problem which impairs or prevents the functions of a product.
            Story: The smallest unit of work that needs to be done.
            Task: Represents work that needs to be done.
        summary (str): A brief summary of the issue to create.
        description (str): A detailed description of the issue to create.

    Returns:
        dict[str, Any]: Information about the created Jira issue as a dictionary, including:
            id: The id of the created issue.
            key: The key of the created issue.
            self: The URL of the created issue.

### get_issue_jira

    When to use:
        Use this function to retrieve the contents of a Jira issue.

    Args:
        issue_id_or_key (str): The id or key of the Jira issue to retrieve.

    Returns:
        dict[str, Any]: Information about the retrieved Jira issue as a dictionary, including:
            expand: Additional fields that can be requested.
            fields: Details of the issue, including:
                assignee: The person to whom the issue is currently assigned.
                attachment: Files attached to the issue.
                comment: Comments on the issue.
                components: Project components to which this issue relates.
                created: The time and date when this issue was created.
                description: A detailed description of the issue.
                issuetype: The type of the issue.
                labels: Labels to which this issue relates.
                reporter: The person who created the issue.
                status: The current status of the issue in its workflow.
                summary: A brief one-line summary of the issue.
                updated: The time and date when this issue was last updated.
            id: The id of the retrieved issue.
            key: The key of the retrieved issue.
            self: The URL of the retrieved issue.

### describe_image_jira

    When to use:
        Use this function to ask a prompt about the contents of an image attachment in a Jira issue and retrieve the answer.

    Args:
        url (str): The URL of the attached file.
        prompt (str): The prompt about the image.

    Returns:
        str: The answer returned after processing the prompt about the image.

### search_jira

    When to use:
        Use this function to search for Jira issues using JQL (Jira Query Language).

    Args:
        jql (str): The JQL query string to use for searching issues.
        start_at (int): The index of the first issue to return.
        max_results (int): The maximum number of issues to return.

    Returns:
        dict[str, Any]: Information about the searched Jira issues as a dictionary, including:
            expand (str): Additional fields that can be requested.
            issues (list): List of matching Jira issues. Each issue includes:
                expand (str): Additional fields that can be requested.
                fields (dict): Details of the issue, including:
                    assignee (dict): The person to whom the issue is currently assigned.
                    attachment (list): Files attached to the issue.
                    comment (dict): Comments on the issue.
                    components (list): Project components to which this issue relates.
                    created (str): The time and date when this issue was created.
                    description (str): A detailed description of the issue.
                    issuetype (dict): The type of the issue.
                    labels (list): Labels to which this issue relates.
                    reporter (dict): The person who created the issue.
                    status (dict): The current status of the issue in its workflow.
                    summary (str): A brief one-line summary of the issue.
                    updated (str): The time and date when this issue was last updated.
                id (str): The id of the issue.
                key (str): The key of the issue.
                self (str): The URL of the issue.
            maxResults (int): The maximum number of issues returned.
            startAt (int): The index of the first returned issue.
            total (int): The total number of results matching the JQL query.

### get_page_id_confluence

    When to use:
        Use this function to retrieve the page ID in Confluence.

    Args:
        space_key (str): The space key of the page to retrieve.
        title (str): The title of the page to retrieve.

    Returns:
        str: The ID of the retrieved page.

### create_page_confluence

    When to use:
        Use this function to create a Confluence page.

    Args:
        parent_page_id (str): The ID of the parent page under which to create the page.
        title (str): The title of the new page to be created.
        body (str): The body of the page to be created.

    Returns:
        dict[str, Any]: Information about the created Confluence page as a dictionary.

### get_page_with_gliffy_confluence

    When to use:
        Use this function to retrieve the contents of a Confluence page. If a Gliffy diagram is included in the page body, the corresponding Gliffy file will be displayed inline within the body as JSON.

    Args:
        page_id (str): The page ID of the page to retrieve.

    Returns:
        dict[str, Any]: Information about the retrieved Confluence page as a dictionary, including:
            _expandable (dict): Related pages of the retrieved page.
            _links (dict): Related links of the retrieved page.
            body (dict): The content of the retrieved page.
                storage (dict): The storage format and structure of the content.
                    value (str): The actual page content as a string.
            extensions (dict): The position of the retrieved page within the space.
            id (str): The ID of the retrieved page.
            status (str): The status of the retrieved page.
            title (str): The title of the retrieved page.
            type (str): The type of the retrieved page.

### describe_image_confluence

    When to use:
        Use this function to ask a prompt about the contents of an image attachment in a Confluence page and retrieve the answer.

    Args:
        page_id (str): The ID of the Confluence page that contains the image attachment.
        filename (str): The filename of the attached image.
        prompt (str): The prompt about the image.

    Returns:
        str: The answer returned after processing the prompt about the image.

### get_page_tree_confluence

    When to use:
        Use this function to retrieve all descendant pages of a Confluence page.

    Args:
        page_id (str): The page ID of the page to retrieve descendants for.
        title (str, optional): The title of the page.

    Returns:
        dict[str, Any]: Information about all descendant pages as a dictionary, including:
            page_id (str): The page ID of the current node.
            title (str): The title of the current node.
            children (list): The child nodes of the current node.

### search_confluence

    When to use:
        Use this function to search for Confluence pages, attachments, or comments using CQL (Confluence Query Language).

    Args:
        cql (str): The CQL query string to use for searching content.
        start (int): The start index of the result set.
        limit (int): The maximum number of results returned.

    Returns:
        dict[str, Any]: Information about the searched Confluence contents as a dictionary, including:
            _links (dict): Links for pagination and API context (e.g., self, next, base, context).
            cqlQuery (str): The CQL query string used for the search.
            limit (int): The maximum number of results returned.
            results (list): List of matching content items, each including:
                _expandable (dict): API paths to fetch more information for the content, such as container, children, body, version, ancestors, space, etc. May vary by type.
                _links (dict): Various endpoint links related to the content, including webui, edit, tinyui, download, thumbnail, and self.
                extensions (dict): Additional metadata about the content, such as position for pages, mediaType for attachments, etc.
                id (str): The ID of the content item.
                metadata (dict, optional): Metadata including mediaType for attachments.
                status (str): The status of the content item.
                title (str): The title of the content (for pages and attachments).
                type (str): The type of the content item (e.g., page, comment, attachment).
            searchDuration (int): The server-side time taken to process the search (in ms).
            size (int): The number of results included in this response.
            start (int): The start index of the result set.
            totalSize (int): Total number of matching contents for the query.
