import base64
from dotenv import load_dotenv
#from mcp.server.fastmcp import FastMCP # type: ignore
from fastmcp import FastMCP # type: ignore
import os
import requests
load_dotenv()

mcp = FastMCP("GitHub MCP")

@mcp.prompt()
def summarize_pull_request(main, branch) -> str:
    """
    Returns the text of a pull request, summarizing changes to
    the code 
    """
    return f"""
    Write a GitHub pull request. Consider the changes seen in the
    new code vs. the old code and draw attention to relevant bug fixes,
    feature updates, and comments.

    Master: 
    {main}

    Local: 
    {branch}
    """
@mcp.prompt()
def title_pull_request(summary) -> str:
    """
    Returns the title of a pull request given its summary text 
    """
    return f"""
    Provide a short, informative title for a pull request with the given summary: 

    {summary}
    """

@mcp.tool()
def create_pull_request(owner, repo_name, branch_name, title, body=""):
    """Open a pull request via GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {
        "Authorization": f"Bearer {os.getenv("GITHUB_TOKEN_FINEGRAINED")}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "title": title,
        "head": branch_name,
        "base": "main",
        "body": body
    }
    response = requests.post(url, json=data, headers=headers).json()
    return response

@mcp.tool()
def get_list_of_files_in_repo_branch(owner, repo_name, branch_name="main"): 
    """
    Fetch a list of all the files in a given repo and branch. Can
    be used in tandem with `get_remote_code_from_single_file` to
    produce a summary for a pull request.
    """
    url=f"https://api.github.com/repos/{owner}/{repo_name}/contents/?ref={branch_name}"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN_FINEGRAINED')}",
        "Accept": "application/vnd.github.object",
        'X-GitHub-Api-Version': '2022-11-28'
    }
    response = requests.get(url, headers=headers).json()
    if "message" in response: 
        if response["message"] == "Bad credentials": 
            return """
            Check that GitHub finegrained access token is set as environmental variable `GITHUB_TOKEN_FINEGRAINED`.
            For security reasons, the user must do this manually.
            """
    list_of_files = []
    for file in response["entries"]: 
        list_of_files.append(file["path"])
    return list_of_files

@mcp.tool()
def get_remote_code_from_single_file(repo_owner, repo_name, path, branch_name="main"): 
    """
    Fetch the remote code from a specified file in a
    GitHub repository branch as a string.
    """
    url=f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch_name}"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN_FINEGRAINED')}",
        "Accept": "application/vnd.github.object",
        'X-GitHub-Api-Version': '2022-11-28'
    }
    response = requests.get(url, headers=headers).json()
    if "message" in response: 
        if response["message"] == "Bad credentials": 
            return """
            Check that GitHub finegrained access token is set as environmental variable `GITHUB_TOKEN_FINEGRAINED`.
            For security reasons, the user must do this manually.
            """
    content = base64.b64decode((response["content"]).encode("ascii")).decode("ascii")

    return content

if __name__ == "__main__":
    print("Starting GitHub MCP")
    #mcp.run(transport="stdio")
    # Create config for streamable-http
    #mcp.run(transport="streamable-http")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
    print("Finished GitHub MCP")
