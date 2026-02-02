import os
import sys
import yaml
from google import genai
from google.genai import types
from github import Github

def load_profile(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"::error::Hardware profile not found at {path}")
        sys.exit(1)

def get_pr_diff(token):
    # In GitHub Actions, GITHUB_EVENT_PATH points to the event JSON
    # Ideally, we use PyGithub to get the PR diff cleanly
    g = Github(token)
    repo_name = os.getenv('GITHUB_REPOSITORY')
    
    # Robustly handle GITHUB_REF for PRs (refs/pull/123/merge)
    ref = os.getenv('GITHUB_REF', '')
    if not ref or 'pull' not in ref:
        # Fallback for local testing or non-PR events if needed, 
        # or just fail gracefully.
        # For now, let's assume standard PR workflow.
        print("::warning::Not a standard PR ref, attempting to parse anyway or failing.")
        
    try:
        pr_number = int(ref.split('/')[-2])
    except (IndexError, ValueError):
        print(f"::error::Could not parse PR number from GITHUB_REF: {ref}")
        sys.exit(1)

    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Get the diff (files changed)
    diffs = ""
    for file in pr.get_files():
        if file.filename.endswith(('.c', '.cpp', '.h', '.py')): # Limit to code
            diffs += f"\n--- File: {file.filename} ---\n{file.patch}\n"
    
    return pr, diffs

def analyze_with_gemma(diff, profile, api_key):
    client = genai.Client(api_key=api_key)
    
    system_prompt = f"""
    You are a Senior Embedded Systems Engineer acting as a code reviewer.
    TARGET HARDWARE: {profile['device']} ({profile['architecture']})
    
    STRICT HARDWARE CONSTRAINTS:
    {yaml.dump(profile['constraints'])}

    TASK:
    Review the code diff below. If (and ONLY if) the code violates a hardware constraint, issue a warning.
    Be brief. Use technical language. If code is safe, say "HARDWARE CHECK PASSED".
    """

    prompt = f"{system_prompt}\n\nCODE DIFF:\n{diff}"

    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
        )
    )
    return response.text

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    profile_path = os.getenv("HARDWARE_PROFILE_PATH")
    gh_token = os.getenv("GITHUB_TOKEN")

    if not api_key:
        print("::error::Missing GOOGLE_API_KEY")
        sys.exit(1)

    print(f"Loading profile from: {profile_path}")
    profile = load_profile(profile_path)
    
    print("Fetching PR Diff...")
    try:
        pr, diff_content = get_pr_diff(gh_token)
    except Exception as e:
        print(f"::warning::Could not fetch PR diff (might be running locally?): {e}")
        sys.exit(0)

    if not diff_content.strip():
        print("No relevant code changes found.")
        sys.exit(0)

    print("Analyzing with Gemma 3...")
    review = analyze_with_gemma(diff_content, profile, api_key)
    
    print("Posting comment to PR...")
    pr.create_issue_comment(f"## gitphysicist Report\n**Target:** {profile['device']}\n\n{review}")

if __name__ == "__main__":
    main()
