import base64
import collections
import os
import re
from typing import Any

from mcp.server import fastmcp
import requests

mcp = fastmcp.FastMCP("jira-confluence-mcp")


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
    base_url = os.environ["JIRA_BASE_URL"]
    url = f"{base_url}/rest/api/2/issue/{issue_id_or_key}"
    fields = [
        "assignee",
        "attachment",
        "comment",
        "components",
        "created",
        "description",
        "issuetype",
        "labels",
        "reporter",
        "status",
        "summary",
        "updated",
    ]
    params = {"fields": ",".join(fields)}
    personal_access_token = os.environ["JIRA_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_attachment_content_jira(url: str) -> bytes | None:
    personal_access_token = os.environ["JIRA_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content


@mcp.tool()
def describe_image_jira(url: str, mime_type: str, prompt: str) -> dict[str, Any] | None:
    """
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
    """
    openai_url = (
        f"{os.environ["AZURE_OPENAI_ENDPOINT"]}"
        f"/openai/deployments/{os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]}"
        f"/chat/completions?api-version={os.environ["AZURE_OPENAI_API_VERSION"]}"
    )
    content = get_attachment_content_jira(url)
    if not content:
        return None
    content_b64 = base64.b64encode(content)
    content_b64_utf8 = content_b64.decode("utf-8")
    data = {
        "messages": [
            {
                "content": [
                    {
                        "image_url": {
                            "url": f"data:{mime_type};base64,{content_b64_utf8}"
                        },
                        "type": "image_url",
                    },
                    {"text": prompt, "type": "text"},
                ],
                "role": "user",
            }
        ]
    }
    headers = {
        "api-key": os.environ["AZURE_OPENAI_API_KEY"],
        "Content-Type": "application/json",
    }
    response = requests.post(openai_url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


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
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    url = f"{base_url}/rest/api/content"
    params = {"spaceKey": space_key, "title": title}
    personal_access_token = os.environ["CONFLUENCE_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return response_json["results"][0]["id"]


def get_attachment_content_confluence(page_id: str, filename: str) -> bytes:
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    url = f"{base_url}/download/attachments/{page_id}/{filename}"
    personal_access_token = os.environ["CONFLUENCE_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content


def get_page_content_confluence(page_id: str) -> dict[str, Any]:
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    url = f"{base_url}/rest/api/content/{page_id}"
    params = {"expand": "body.storage"}
    personal_access_token = os.environ["CONFLUENCE_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_page_content_with_gliffy_confluence(page_id: str) -> dict[str, Any]:
    """
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
    """
    pattern = (
        r'<ac:structured-macro[^>]+ac:name="gliffy"[^>]+>'
        r'.*?<ac:parameter ac:name="name">(.*?)</ac:parameter>.*?'
        r"</ac:structured-macro>"
    )

    def repl(match: re.Match[str]) -> str:
        filename = match.group(1)
        attachment_content = get_attachment_content_confluence(page_id, filename)
        if not attachment_content:
            return ""
        attachment_content_utf8 = attachment_content.decode("utf-8")
        return (
            '<ac:structured-macro ac:name="code">'
            '<ac:parameter ac:name="language">json</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{attachment_content_utf8}]]></ac:plain-text-body>"
            "</ac:structured-macro>"
        )

    content = get_page_content_confluence(page_id)
    content["body"]["storage"]["value"] = re.sub(
        pattern, repl, content["body"]["storage"]["value"], flags=re.DOTALL
    )
    return content


@mcp.tool()
def describe_image_confluence(
    page_id: str, filename: str, mime_type: str, prompt: str
) -> dict[str, Any] | None:
    """
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
    """
    openai_url = (
        f"{os.environ["AZURE_OPENAI_ENDPOINT"]}"
        f"/openai/deployments/{os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]}"
        f"/chat/completions?api-version={os.environ["AZURE_OPENAI_API_VERSION"]}"
    )
    content = get_attachment_content_confluence(page_id, filename)
    if not content:
        return None
    content_b64 = base64.b64encode(content)
    content_b64_utf8 = content_b64.decode("utf-8")
    data = {
        "messages": [
            {
                "content": [
                    {
                        "image_url": {
                            "url": f"data:{mime_type};base64,{content_b64_utf8}"
                        },
                        "type": "image_url",
                    },
                    {"text": prompt, "type": "text"},
                ],
                "role": "user",
            }
        ]
    }
    headers = {
        "api-key": os.environ["AZURE_OPENAI_API_KEY"],
        "Content-Type": "application/json",
    }
    response = requests.post(openai_url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_child_pages_confluence(page_id: str) -> list[dict[str, str]]:
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    url = f"{base_url}/rest/api/content/{page_id}/child"
    params = {"expand": "page.body.VIEW"}
    personal_access_token = os.environ["CONFLUENCE_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return [
        {"id": page["id"], "title": page["title"], "children": []}
        for page in response_json["page"]["results"]
    ]


@mcp.tool()
def get_descendant_pages_confluence(page_id: str, title: str = "") -> dict[str, Any]:
    """
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
    """
    queue = collections.deque()
    root = {"id": page_id, "title": title, "children": []}
    queue.append(root)
    while queue:
        current_node = queue.popleft()
        child_pages = get_child_pages_confluence(current_node["id"])
        for child_page in child_pages:
            current_node["children"].append(child_page)
            queue.append(child_page)
    return root


def main():
    mcp.run()


if __name__ == "__main__":
    main()
