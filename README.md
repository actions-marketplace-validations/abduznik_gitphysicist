# gitphysicist

**"The Code Reviewer that reads Datasheets."**

gitphysicist uses Google's **Gemma 3 27B** to analyze your Pull Requests against strict hardware constraints defined in a YAML profile. It catches floating-point math on FPU-less chips, stack overflows on low-RAM micros, and blocking delays in ISRs.

## Usage

### 1. Setup Secrets
In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:
- `GOOGLE_API_KEY`: Your Google GenAI API key.

### 2. Create Workflow
Add this to `.github/workflows/gitphysicist.yml`. This configuration allows the check to run automatically on Pull Requests and manually via the "Actions" tab.

```yaml
name: Hardware Constraint Check
on:
  pull_request:
  workflow_dispatch: # Allows manual trigger

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run gitphysicist
        uses: abduznik/gitphysicist@main
        with:
          google_api_key: ${{ secrets.GOOGLE_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          hardware_profile: 'profiles/esp32.yaml' # Point to your profile
```

## Local Development

You can also run the check locally without pushing to GitHub:

```bash
export GOOGLE_API_KEY="your_api_key"
python check_local.py path/to/your_code.c --profile profiles/stm32_f103.yaml
```

## Hardware Profiles

Profiles are stored in the `profiles/` directory as YAML files. You can create your own to match your specific hardware constraints. See `profiles/stm32_f103.yaml` for an example.

