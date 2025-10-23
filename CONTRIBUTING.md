# Contributing to Cheeky

Thanks for your interest in contributing! 🍑

This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and kind to all community members. No harassment, discrimination, or unwelcome behavior.

## Ways to Contribute

### 🐛 Report Bugs

Found a bug? [Open an issue](https://github.com/cheeky-radio/cheeky/issues/new) with:
- Clear description of the problem
- Steps to reproduce
- Expected behavior vs actual behavior
- Your Pi model and OS version
- Relevant error messages or logs

### 💡 Suggest Features

Have an idea? [Start a discussion](https://github.com/cheeky-radio/cheeky/discussions) or [open an issue](https://github.com/cheeky-radio/cheeky/issues/new) with:
- Clear description of the feature
- Why it would be useful
- Any alternative approaches you've considered

### 📖 Improve Documentation

Documentation improvements are always welcome:
- Fix typos or clarify explanations
- Add examples or tutorials
- Update API documentation
- Translate to other languages

### 💻 Submit Code

Want to submit code? Follow these steps:

#### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/cheeky.git
cd cheeky
git remote add upstream https://github.com/cheeky-radio/cheeky.git
```

#### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

#### 3. Make Your Changes

- Follow existing code style
- Keep changes focused and minimal
- Write clear commit messages
- Test thoroughly (in QEMU if possible)

#### 4. Test Your Changes

**For configuration changes**:
```bash
# Build a test image
cd scripts
chmod +x build.sh
sudo ./build.sh --arch armv8 --base-image ../base.img --output test.img --version dev
```

**For web UI changes**:
```bash
# Test in QEMU
cd qemu/linux
./start-qemu.sh
# Visit http://localhost:6680 and http://localhost:8080
```

**For Python code**:
```bash
# Run tests (when available)
python -m pytest tests/

# Check code style
flake8 config/bluetooth-web-manager/
black --check config/bluetooth-web-manager/
```

#### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then [create a pull request](https://github.com/cheeky-radio/cheeky/pulls) with:
- Clear title describing the change
- Description of what changed and why
- Reference to any related issues
- Checklist of testing done

#### 6. Code Review

- Be patient - maintainers will review when available
- Be open to feedback
- Ask questions if something is unclear
- Make requested changes in new commits

## Development Setup

### Local Development Environment

```bash
# Clone the repository
git clone https://github.com/cheeky-radio/cheeky.git
cd cheeky

# Install dependencies
pip install -r config/bluetooth-web-manager/requirements.txt

# Run tests
pytest tests/  # When tests are added

# Test in QEMU
cd qemu/linux
./start-qemu.sh
```

### Project Structure

See [CLAUDE.md](CLAUDE.md) for detailed architecture and file organization.

## Coding Standards

### Python

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Format with [Black](https://black.readthedocs.io/)
- Check style with [Flake8](https://flake8.pycqa.org/)

```python
# Example
async def get_devices() -> List[Dict[str, Any]]:
    """Get all paired Bluetooth devices."""
    devices = []
    # Implementation
    return devices
```

### JavaScript/HTML/CSS

- Use Tailwind CSS for styling (no custom CSS unless necessary)
- Alpine.js for interactivity (lightweight, no build step)
- Semantic HTML5
- Mobile-first responsive design

```html
<!-- Example -->
<div x-data="{ open: false }">
  <button @click="open = !open" class="px-4 py-2 bg-pink-500 rounded">
    Toggle
  </button>
</div>
```

### Bash

- Use `set -e` to exit on error
- Quote variables: `"$var"` not `$var`
- Use descriptive variable names
- Add comments for complex logic

```bash
#!/bin/bash
set -e

DEVICE_MAC="$1"
if [ -z "$DEVICE_MAC" ]; then
    echo "Error: MAC address required"
    exit 1
fi
```

## Commit Messages

Write clear commit messages following this format:

```
Short description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain WHAT changed and WHY, not HOW.

Fixes #123
Relates to #456
```

Examples:
- ✓ `Add WiFi configuration guide`
- ✓ `Fix Bluetooth reconnect timeout issue`
- ✓ `Update Mopidy version to v3.4.0`
- ✗ `fixed stuff` (too vague)
- ✗ `Changed mopidy.conf line 45` (too specific)

## Labels & Issues

### Issue Labels

- **bug**: Something isn't working
- **enhancement**: New feature or improvement
- **documentation**: Docs/README improvements
- **good-first-issue**: Good for new contributors
- **help-wanted**: Need assistance
- **question**: Questions from users

### Claim an Issue

Comment on an issue saying "I'd like to work on this" and it's yours!

## Release Process

Releases are tagged and built automatically via GitHub Actions:

```bash
# Create a release tag (maintainers only)
git tag -a v1.1.0 -m "Release v1.1.0: Add new features"
git push origin v1.1.0

# GitHub Actions will:
# 1. Build all Pi images
# 2. Build QEMU bundles
# 3. Create release with assets
# 4. Generate release notes
```

## Community

- 💬 [GitHub Discussions](https://github.com/cheeky-radio/cheeky/discussions) - Questions & ideas
- 🐛 [GitHub Issues](https://github.com/cheeky-radio/cheeky/issues) - Bug reports
- 📖 [Documentation](docs/) - User guides
- 🍑 Be cheeky, be kind!

## Recognition

Contributors will be:
- Added to the CONTRIBUTORS.md file
- Mentioned in release notes
- Thanked in the community!

## Questions?

- Check [CLAUDE.md](CLAUDE.md) for architecture and development info
- See [docs/](docs/) for user guides
- Ask in [GitHub Discussions](https://github.com/cheeky-radio/cheeky/discussions)
- Email: hello@cheeky-radio.io (when set up)

---

Thank you for contributing to Cheeky! 🍑

Together we make radio fun again!
