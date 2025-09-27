import base64
import mimetypes
import os
from typing import Any

import requests


def add_tools(mcp):
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
                id (str): The id of the created issue.
                key (str): The key of the created issue.
                self (str): The URL of the created issue.
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
    def get_issue_jira(issue_id_or_key: str) -> dict[str, Any]:
        """
        When to use:
            Use this function to retrieve the contents of a Jira issue.

        Args:
            issue_id_or_key (str): The id or key of the Jira issue to retrieve.

        Returns:
            dict[str, Any]: Information about the retrieved Jira issue as a dictionary, including:
                assignee (dict): The person to whom the issue is currently assigned.
                attachment (list): Files attached to the issue.
                comment (dict): Comments on the issue. Includes individual comments, authors, timestamps, and content.
                components (list): Project components to which this issue relates.
                created (str): The time and date when this issue was created.
                description (str): A detailed description of the issue.
                expand (str): Additional fields that can be requested.
                fields (dict): Details of the issue, including all other keys in this section.
                id (str): The id of the retrieved issue.
                issuetype (dict): The type of the issue (e.g. Bug, Story, Task).
                key (str): The key of the retrieved issue.
                labels (list): Labels to which this issue relates.
                reporter (dict): The person who created the issue.
                self (str): The URL of the retrieved issue.
                status (dict): The current status of the issue in its workflow.
                summary (str): A brief one-line summary of the issue.
                updated (str): The time and date when this issue was last updated.
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

    @mcp.tool()
    def search_jira(jql: str, start_at: int, max_results: int) -> dict[str, Any]:
        """
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
        """
        base_url = os.environ["JIRA_BASE_URL"]
        url = f"{base_url}/rest/api/2/search"
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
        params = {
            "fields": ",".join(fields),
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
        }
        personal_access_token = os.environ["JIRA_PERSONAL_ACCESS_TOKEN"]
        headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, params, headers=headers)
        response.raise_for_status()
        return response.json()

    @mcp.tool()
    def update_issue_jira(issue_id_or_key: str, fields: dict[str, Any]) -> int:
        """
        When to use:
            Use this function to update the fields of a Jira issue.

        Args:
            issue_id_or_key (str): The id or key of the Jira issue to update.
            fields (dict[str, Any]): A dictionary containing the fields to update in the issue.

        Returns:
            int: The HTTP status code of the update operation.
        """
        base_url = os.environ["JIRA_BASE_URL"]
        url = f"{base_url}/rest/api/2/issue/{issue_id_or_key}"
        personal_access_token = os.environ["JIRA_PERSONAL_ACCESS_TOKEN"]
        headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Content-Type": "application/json",
        }
        payload = {"fields": fields}
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.status_code
