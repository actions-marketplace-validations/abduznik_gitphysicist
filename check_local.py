import argparse
import os
import sys

# Add src to path so we can import the analyzer
sys.path.append(os.path.abspath('src'))

from main import analyze_with_gemma, load_profile

def main():
    parser = argparse.ArgumentParser(description="Run GitPhysicist on a local file.")
    parser.add_argument("file", help="Path to the source code file to check")
    parser.add_argument("--profile", default="profiles/stm32_f103.yaml", help="Path to hardware profile YAML")
    
    args = parser.parse_args()

    # 1. Check API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("::error::GOOGLE_API_KEY not found in environment variables.")
        print("Run: export GOOGLE_API_KEY='your_key'")
        sys.exit(1)

    # 2. Load Profile
    if not os.path.exists(args.profile):
        print(f"Error: Profile not found at {args.profile}")
        sys.exit(1)
        
    profile = load_profile(args.profile)

    # 3. Read Code
    if not os.path.exists(args.file):
        print(f"Error: File not found at {args.file}")
        sys.exit(1)
        
    with open(args.file, 'r') as f:
        code_content = f.read()
    
    # Wrap it to look like a diff
    diff_context = f"\n--- File: {args.file} (Local Check) ---\n{code_content}\n"

    # 4. Analyze
    print(f"⚛️  Checking {args.file} against {profile.get('device', 'Unknown Device')}...")
    try:
        report = analyze_with_gemma(diff_context, profile, api_key)
        print("\n" + "="*40)
        print("REPORT")
        print("="*40)
        print(report)
        print("="*40 + "\n")
    except Exception as e:
        print(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()
