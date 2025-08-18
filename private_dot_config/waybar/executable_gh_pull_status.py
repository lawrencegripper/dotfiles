#!/usr/bin/env -S uv run --with PyQt5 --script

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "PyGithub",
# ]
# ///

import base64
import json
import subprocess
from github import Github
from github import Auth
import os

CACHE_DIR = "/tmp/gh_pull_status"
os.makedirs(CACHE_DIR, exist_ok=True)
os.chmod(CACHE_DIR, 0o700)

def get_op_value(path):
    cache_file = os.path.join(CACHE_DIR, base64.urlsafe_b64encode(path.encode()).decode())
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return file.read().strip()
    value = subprocess.check_output(["/bin/bash", "-c", f"op read '{path}'"]).decode().strip()
    
    if value.strip():  # Only write if the value is not empty
        with open(cache_file, 'w') as file:
            file.write(value)
        os.chmod(cache_file, 0o600)
    else:
        raise ValueError(f"Value for {path} is empty or not found in 1Password")
    return value

def send_notification(title: str, body: str):
    """Send a desktop notification via notify-send"""
    try:
        subprocess.run([
            "notify-send",
            "--urgency=normal",
            "--app-name=GitHub Status",
            title,
            body
        ], check=True)
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available

def main():
    # Get GitHub token from environment
    gh_token = get_op_value("op://Private/GitHub/PATs/gh-waybar-integration")

    auth = Auth.Token(gh_token)
    g = Github(auth=auth)
    user = g.get_user()

    # You can also add more specific filters
    pull_requests = g.search_issues(
        "",
        type="pr",
        author=user.login,
        state="open",
        sort="updated",
        order="desc"
    )

    most_recent_prs = []
    for pr in pull_requests[:5]:
        pr_obj = g.get_repo(pr.repository.full_name).get_pull(pr.number)
        mergeable_state = pr_obj.mergeable_state if pr_obj.mergeable_state else "unknown"
        
        # Get review status
        reviews = pr_obj.get_reviews()
        review_status = "pending"
        for review in reviews:
            if review.state == "APPROVED":
                review_status = "approved"
                break
            elif review.state == "CHANGES_REQUESTED":
                review_status = "changes_requested"
            break
        
        # Get check status
        commits = pr_obj.get_commits()
        last_commit = list(commits)[-1]
        check_status = "unknown"
        check_status = last_commit.get_combined_status().state
        
        most_recent_prs.append({
            "title": pr.title,
            "number": pr.number,
            "repo": pr.repository.name,
            "mergeable_state": mergeable_state,
            "state": pr.state,
            "review_status": review_status,
            "check_status": check_status
        })

    output = f"""<span font_weight="bold"> <span color="#0080ff"> </span>  </span>"""

    tooltip = "<b>GitHub Pull Requests</b>\n\n"
    if not most_recent_prs:
        output += " No recent PRs"
    else:
        output += " Recent PRs: "
        for pr in most_recent_prs:
            state_emoji = "?"
            if pr["review_status"] == "approved" and pr["check_status"] == "success":
                state_emoji = "✅🛳" 
            else:
                match pr["check_status"]:
                    case "failure":
                        state_emoji = "🏗🔴 "
                    case "pending":
                        state_emoji = "🏗⏳ "
                    case "success":
                        match pr["review_status"]:
                            case "changes_requested":
                                state_emoji += "👀🔴"
                            case "pending":
                                state_emoji += "👀⏳"
                            case "approved":
                                state_emoji += ""
                            case _:
                                state_emoji += "👀❓"
                    case _:
                        state_emoji = "🏗❓ "

            # main_color = "#8b7dd8"
            truncated_title = pr["title"][:20] + "..." if len(pr["title"]) > 20 else pr["title"]
            output += f'<span>{pr["repo"]}>"{truncated_title}" {state_emoji}</span> '
            # output += f'<span background="{main_color}">{state_emoji} {pr["repo"]} {truncated_title}</span> '

            tooltip += f"<b>{pr['repo']} #{pr['number']}</b>: {pr['title']}\n"
            tooltip += f"  • Review: {pr['review_status'].replace('_', ' ').title()}\n"
            tooltip += f"  • Checks: {pr['check_status'].title()}\n"
            tooltip += f"  • Mergeable: {pr['mergeable_state'].replace('_', ' ').title()}\n\n"

    waybar_data = {
        "text": output,
        "tooltip": tooltip,
    }
    # Print the JSON object
    return json.dumps(waybar_data)


if __name__ == "__main__":
    try:
        print(main())
    except Exception as e:
        print(json.dumps({ "text": f"Error: {str(e)}", "tooltip": "Failed to retrieve GitHub pull request status." }))
        

