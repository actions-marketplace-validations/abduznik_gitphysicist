# ⚛️ GitPhysicist

**"The Code Reviewer that reads Datasheets."**

GitPhysicist uses Google's **Gemma 3 27B** to analyze your Pull Requests against strict hardware constraints defined in a YAML profile. It catches floating-point math on FPU-less chips, stack overflows on low-RAM micros, and blocking delays in ISRs.

## 🚀 Usage

Add this to your `.github/workflows/hardware-check.yml`:

```yaml
name: Physics Check
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run GitPhysicist
        uses: abduznik/gitphysicist@main
        with:
          google_api_key: ${{ secrets.GOOGLE_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          hardware_profile: 'profiles/stm32_f103.yaml'
```
