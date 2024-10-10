import sys
import urllib.request
import json
from datetime import datetime

# Function to fetch GitHub activity
def fetch_github_activity(username):
    url = f"https://api.github.com/users/{username}/events"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode()
            try:
                events = json.loads(data)
                return events
            except json.JSONDecodeError:
                print("Error: Unable to decode the response from GitHub API.")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: User '{username}' not found.")
        else:
            print(f"HTTPError: {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URLError: {e.reason}")
        sys.exit(1)

# Function to display activity in a user-friendly way
def display_activity(events):
    if not events:
        print("No recent activity found.")
        return
    
    print(f"Recent activity for user: {events[0]['actor']['login']}\n")
    seen_events = set()  # To track displayed events
    for event in events:
        repo_name = event['repo']['name']
        event_time = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        formatted_time = event_time.strftime("%Y-%m-%d %H:%M:%S")

        # Create a unique identifier for the event to avoid duplicates
        event_id = f"{repo_name}:{event['type']}:{formatted_time}"

        if event_id in seen_events:
            continue  # Skip already displayed events

        seen_events.add(event_id)  # Mark this event as seen

        if event['type'] == 'PushEvent':
            print(f"[{formatted_time}] Pushed {len(event['payload']['commits'])} commits to {repo_name}")
        elif event['type'] == 'IssuesEvent':
            action = event['payload']['action']
            print(f"[{formatted_time}] {action.capitalize()} a new issue in {repo_name}")
        elif event['type'] == 'WatchEvent':
            print(f"[{formatted_time}] Starred {repo_name}")
        elif event['type'] == 'ForkEvent':
            print(f"[{formatted_time}] Forked {repo_name}")
        elif event['type'] == 'PullRequestEvent':
            action = event['payload']['action']
            print(f"[{formatted_time}] {action.capitalize()} a pull request in {repo_name}")
        else:
            print(f"[{formatted_time}] {event['type']} on {repo_name}")

# Main function
if __name__ == "__main__":
    # Check if a username was provided
    if len(sys.argv) != 2:
        print("Usage: github-activity <username>")
        sys.exit(1)

    username = sys.argv[1].strip()
    
    # Validate that the username is not empty
    if not username:
        print("Error: Username cannot be empty.")
        sys.exit(1)

    print(f"Fetching recent activity for user: {username}")
    events = fetch_github_activity(username)
    
    if events:
        display_activity(events)
    else:
        print(f"No recent activity found for user: {username}")
