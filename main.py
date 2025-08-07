import base64
import collections
import mimetypes
import os
import re
from typing import Any

from mcp.server import fastmcp
import requests

mcp = fastmcp.FastMCP("jira-confluence-mcp")


@mcp.tool()
def create_issue_jira(
    project: str, issue_type: str, summary: str, description: str
) -> dict[str, Any]:
    """
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
    """
    base_url = os.environ["JIRA_BASE_URL"]
    url = f"{base_url}/rest/api/2/issue"
    payload = {
        "fields": {
            "description": description,
            "issuetype": {"name": issue_type},
            "project": {"key": project},
            "summary": summary,
        }
    }
    personal_access_token = os.environ["JIRA_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_issue_jira(issue_id_or_key: str) -> dict[str, Any]:
    """
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


def get_attachment_jira(url: str) -> bytes:
    personal_access_token = os.environ["JIRA_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content


@mcp.tool()
def describe_image_jira(url: str, prompt: str) -> str:
    """
    When to use:
        Use this function to ask a prompt about the contents of an image attachment in a Jira issue and retrieve the answer.

    Args:
        url (str): The URL of the attached file.
        prompt (str): The prompt about the image.

    Returns:
        str: The answer returned after processing the prompt about the image.
    """
    openai_url = (
        f"{os.environ["AZURE_OPENAI_ENDPOINT"]}"
        f"/openai/deployments/{os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]}"
        f"/chat/completions?api-version={os.environ["AZURE_OPENAI_API_VERSION"]}"
    )
    media_type, _ = mimetypes.guess_type(url)
    try:
        attachment = get_attachment_jira(url)
    except Exception as e:
        return ""
    attachment_b64 = base64.b64encode(attachment)
    attachment_b64_utf8 = attachment_b64.decode("utf-8")
    payload = {
        "messages": [
            {
                "content": [
                    {
                        "image_url": {
                            "url": f"data:{media_type};base64,{attachment_b64_utf8}"
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
    response = requests.post(openai_url, json=payload, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"]


@mcp.tool()
def get_page_id_confluence(space_key: str, title: str) -> str:
    """
    When to use:
        Use this function to retrieve the page ID in Confluence.

    Args:
        space_key (str): The space key of the page to retrieve.
        title (str): The title of the page to retrieve.

    Returns:
        str: The ID of the retrieved page.
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


def get_space_key_confluence(page_id: str) -> str:
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    url = f"{base_url}/rest/api/content/{page_id}"
    params = {"expand": "space"}
    personal_access_token = os.environ["CONFLUENCE_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, params, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return response_json["space"]["key"]


@mcp.tool()
def create_page_confluence(
    parent_page_id: str, title: str, body: str
) -> dict[str, Any]:
    """
    When to use:
        Use this function to create a Confluence page.

    Args:
        parent_page_id (str): The ID of the parent page under which to create the page.
        title (str): The title of the new page to be created.
        body (str): The body of the page to be created.

    Returns:
        dict[str, Any]: Information about the created Confluence page as a dictionary.
    """
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    url = f"{base_url}/rest/api/content"
    space_key = get_space_key_confluence(parent_page_id)
    payload = {
        "ancestors": [{"id": parent_page_id}],
        "body": {"storage": {"representation": "storage", "value": body}},
        "space": {"key": space_key},
        "title": title,
        "type": "page",
    }
    personal_access_token = os.environ["CONFLUENCE_PERSONAL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def get_attachment_confluence(page_id: str, filename: str) -> bytes:
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


def get_page_confluence(page_id: str) -> dict[str, Any]:
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
def get_page_with_gliffy_confluence(page_id: str) -> dict[str, Any]:
    """
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
    """
    pattern = (
        r'<ac:structured-macro[^>]+ac:name="gliffy"[^>]+>'
        r'.*?<ac:parameter ac:name="name">(.*?)</ac:parameter>.*?'
        r"</ac:structured-macro>"
    )

    def repl(match: re.Match[str]) -> str:
        filename = match.group(1)
        try:
            attachment = get_attachment_confluence(page_id, filename)
        except Exception as e:
            return ""
        attachment_utf8 = attachment.decode("utf-8")
        return (
            '<ac:structured-macro ac:name="code">'
            '<ac:parameter ac:name="language">json</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{attachment_utf8}]]></ac:plain-text-body>"
            "</ac:structured-macro>"
        )

    page = get_page_confluence(page_id)
    page["body"]["storage"]["value"] = re.sub(
        pattern, repl, page["body"]["storage"]["value"], flags=re.DOTALL
    )
    return page


@mcp.tool()
def describe_image_confluence(page_id: str, filename: str, prompt: str) -> str:
    """
    When to use:
        Use this function to ask a prompt about the contents of an image attachment in a Confluence page and retrieve the answer.

    Args:
        page_id (str): The ID of the Confluence page that contains the image attachment.
        filename (str): The filename of the attached image.
        prompt (str): The prompt about the image.

    Returns:
        str: The answer returned after processing the prompt about the image.
    """
    openai_url = (
        f"{os.environ["AZURE_OPENAI_ENDPOINT"]}"
        f"/openai/deployments/{os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]}"
        f"/chat/completions?api-version={os.environ["AZURE_OPENAI_API_VERSION"]}"
    )
    media_type, _ = mimetypes.guess_type(filename)
    try:
        attachment = get_attachment_confluence(page_id, filename)
    except Exception as e:
        return ""
    attachment_b64 = base64.b64encode(attachment)
    attachment_b64_utf8 = attachment_b64.decode("utf-8")
    payload = {
        "messages": [
            {
                "content": [
                    {
                        "image_url": {
                            "url": f"data:{media_type};base64,{attachment_b64_utf8}"
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
    response = requests.post(openai_url, json=payload, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"]


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
        {"id": child_page["id"], "title": child_page["title"], "children": []}
        for child_page in response_json["page"]["results"]
    ]


@mcp.tool()
def get_page_tree_confluence(page_id: str, title: str = "") -> dict[str, Any]:
    """
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
    """
    queue = collections.deque()
    page_tree = {"id": page_id, "title": title, "children": []}
    queue.append(page_tree)
    while queue:
        current_page = queue.popleft()
        child_pages = get_child_pages_confluence(current_page["id"])
        for child_page in child_pages:
            current_page["children"].append(child_page)
            queue.append(child_page)
    return page_tree


def main():
    mcp.run()


if __name__ == "__main__":
    main()
