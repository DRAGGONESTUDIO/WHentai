# Installation Instructions

## Base Dependencies

Install the base requirements:
```bash
pip install -r requirements.txt
```

## Playwright Support (Optional)

If you want to use Playwright for JavaScript-heavy sites:

1. Install Playwright:
   ```bash
   pip install -r requirements-playwright.txt
   ```

2. Install Playwright browsers:
   ```bash
   python -m playwright install
   ```

## One-liner Installation

To install everything including Playwright support:
```bash
pip install -r requirements.txt && pip install -r requirements-playwright.txt && python -m playwright install
```