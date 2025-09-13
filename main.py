from mcp.server import fastmcp

import confluence
import jira

mcp = fastmcp.FastMCP("jira-confluence-mcp")
confluence.add_tools(mcp)
jira.add_tools(mcp)

if __name__ == "__main__":
    mcp.run()
