# HappyGene Standards Implementation Runbook

**Purpose:** Execute Phase 0 (Infrastructure) before writing any code
**Duration:** 4 hours
**Effort:** Boilerplate only (no complexity)

---

## Pre-Flight Check

Verify prerequisites:

```bash
# Check git initialized
cd /Users/vorthruna/ProjectsWATTS/HappyGene
git status  # Should show "On branch main, no commits yet"

# Check directory empty (except docs)
ls -la | grep -v "^d" | grep -v ".md$"  # Should be minimal
```

---

## Hour 1: Directory Structure & Templates

### Step 1.1: Create Core Directories

```bash
cd /Users/vorthruna/ProjectsWATTS/HappyGene

mkdir -p happygene
mkdir -p tests
mkdir -p docs
mkdir -p examples
mkdir -p .github/workflows

echo "✓ Directories created"
```

### Step 1.2: Create Python Package Markers

```bash
touch happygene/__init__.py
touch tests/__init__.py
touch tests/conftest.py

echo "✓ Python package markers created"
```

### Step 1.3: Verify Templates Exist

```bash
ls -la TEMPLATES/
# Should show:
#   .gitignore
#   pyproject.toml
#   README.md
#   CONTRIBUTING.md
#   .github_workflows_tests.yml
#   PRE_COMMIT_CHECKLIST.txt
```

### Status After Hour 1:

```
✓ Core directories created
✓ Python package initialized
✓ Templates ready for deployment
```

---

## Hour 2: Deploy Critical Files

### Step 2.1: Copy .gitignore

```bash
cp TEMPLATES/.gitignore /Users/vorthruna/ProjectsWATTS/HappyGene/.gitignore

# Verify
cat .gitignore | head -5
echo "✓ .gitignore deployed"
```

### Step 2.2: Deploy pyproject.toml

```bash
cp TEMPLATES/pyproject.toml /Users/vorthruna/ProjectsWATTS/HappyGene/pyproject.toml

# Verify by attempting to install
pip install -e . 2>&1 | grep -q "Editable" && echo "✓ pyproject.toml valid"
```

### Step 2.3: Deploy README.md

```bash
# Backup existing if present
[ -f README.md ] && mv README.md README_OLD.md

cp TEMPLATES/README.md /Users/vorthruna/ProjectsWATTS/HappyGene/README.md

# Verify
head -10 README.md | grep -q "HappyGene" && echo "✓ README.md deployed"
```

### Step 2.4: Create MIT LICENSE

```bash
# Create license with author
cat > /Users/vorthruna/ProjectsWATTS/HappyGene/LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Eric Mumford

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Verify
grep -q "MIT License" LICENSE && echo "✓ LICENSE created"
```

### Step 2.5: Deploy CONTRIBUTING.md

```bash
cp TEMPLATES/CONTRIBUTING.md /Users/vorthruna/ProjectsWATTS/HappyGene/CONTRIBUTING.md

# Verify
head -5 CONTRIBUTING.md | grep -q "Contributing" && echo "✓ CONTRIBUTING.md deployed"
```

### Status After Hour 2:

```
✓ .gitignore deployed
✓ pyproject.toml deployed
✓ README.md deployed
✓ LICENSE created
✓ CONTRIBUTING.md deployed
✓ Installation verified (pip install -e . works)
```

---

## Hour 3: CI/CD & Testing Infrastructure

### Step 3.1: Deploy GitHub Actions Workflow

```bash
cp TEMPLATES/.github_workflows_tests.yml .github/workflows/tests.yml

# Verify
[ -f .github/workflows/tests.yml ] && echo "✓ GitHub Actions workflow deployed"
```

### Step 3.2: Add pytest Configuration to pyproject.toml

Already included in template, verify:

```bash
grep -A 5 "\[tool.pytest" pyproject.toml | head -10
echo "✓ pytest configuration verified"
```

### Step 3.3: Deploy Checklist

```bash
cp TEMPLATES/PRE_COMMIT_CHECKLIST.txt /Users/vorthruna/ProjectsWATTS/HappyGene/PRE_COMMIT_CHECKLIST.txt

# Verify
[ -f PRE_COMMIT_CHECKLIST.txt ] && echo "✓ Pre-commit checklist deployed"
```

### Step 3.4: Create Minimal Test File

This allows CI to pass immediately (empty repo, no tests = success):

```bash
cat > tests/test_placeholder.py << 'EOF'
"""Placeholder test to verify pytest infrastructure."""


def test_import():
    """Verify happygene package imports."""
    import happygene  # noqa: F401
    assert True
EOF

echo "✓ Placeholder test created"
```

### Step 3.5: Verify pytest Works

```bash
pip install -e ".[dev]"  # Install dev dependencies
pytest tests/ -v

# Should output:
# tests/test_placeholder.py::test_import PASSED
echo "✓ pytest validated"
```

### Status After Hour 3:

```
✓ GitHub Actions workflow deployed
✓ pytest configuration verified
✓ Placeholder test created
✓ pytest execution verified
```

---

## Hour 4: Git Initialization & Final Verification

### Step 4.1: Verify .gitignore Works

```bash
# Create test artifacts
mkdir __pycache__
touch __pycache__/test.pyc
touch .coverage

# Check git ignores them
git status | grep -q "__pycache__" && echo "❌ .gitignore not working" || echo "✓ .gitignore verified"

# Clean up
rm -rf __pycache__ .coverage
```

### Step 4.2: Stage Critical Files

```bash
git add .gitignore
git add pyproject.toml
git add README.md
git add LICENSE
git add CONTRIBUTING.md
git add .github/workflows/tests.yml
git add happygene/__init__.py
git add tests/__init__.py
git add tests/test_placeholder.py
git add tests/conftest.py
git add PRE_COMMIT_CHECKLIST.txt
git add STANDARDS_GAP_ANALYSIS.md
git add ARCHITECTURE_ANALYSIS.md
git add RESEARCH_SUMMARY.md
git add QUICKSTART.md
git add README_RESEARCH.md

echo "✓ Critical files staged"
```

### Step 4.3: Verify No Artifacts Staged

```bash
# Check for common artifacts
git status --cached | grep -E "__pycache__|\.pyc|\.coverage" && {
  echo "❌ ERROR: Artifacts staged. Run: git reset"
  exit 1
}

echo "✓ No artifacts staged"
```

### Step 4.4: Create Initial Commit

```bash
git commit -m "chore: initialize project infrastructure

- Add Python package structure (happygene/)
- Add pytest configuration and placeholder test
- Add GitHub Actions CI/CD workflow
- Add .gitignore, LICENSE, README, CONTRIBUTING
- Add project standards documentation
- Add pre-commit checklist for quality gates

This commit establishes production-ready infrastructure
before Phase 1 (core model implementation).

Closes: #0"

echo "✓ Initial commit created"
```

### Step 4.5: Final Verification

```bash
# Verify no uncommitted changes
git status | grep -q "nothing to commit" || {
  echo "⚠️ Uncommitted changes exist:"
  git status
}

# Show commit log
echo "Recent commits:"
git log --oneline -3

# Show file structure
echo "✓ Final structure:"
find . -type f -name "*.md" -o -name "*.toml" -o -name "*.txt" -o -name ".gitignore" | \
  grep -v ".git" | \
  sort
```

### Status After Hour 4:

```
✓ .gitignore verified working
✓ Critical files staged
✓ No artifacts accidentally staged
✓ Initial commit created
✓ Project ready for Phase 1
```

---

## Validation Checklist

After all 4 hours, verify everything:

```bash
cd /Users/vorthruna/ProjectsWATTS/HappyGene

# Git setup
echo "Git Status:"
git log --oneline -1
git branch

# Installation
echo ""
echo "Installation Check:"
pip install -e . 2>&1 | grep -q "Successfully installed" && echo "✓ pip install works"

# Imports
echo ""
echo "Import Check:"
python -c "import happygene; print('✓ happygene imports')"

# Tests
echo ""
echo "Test Check:"
pytest tests/ -q
[ $? -eq 0 ] && echo "✓ All tests pass"

# File Structure
echo ""
echo "File Structure:"
for file in .gitignore pyproject.toml README.md LICENSE CONTRIBUTING.md .github/workflows/tests.yml
do
  [ -f "$file" ] && echo "✓ $file present" || echo "❌ $file missing"
done
```

---

## Rollback (If Something Goes Wrong)

If you need to start over:

```bash
# Preserve work directories
mkdir -p /tmp/happygene_backup

# Remove git history
rm -rf .git

# Remove staged files
rm -f .gitignore pyproject.toml README.md LICENSE CONTRIBUTING.md PRE_COMMIT_CHECKLIST.txt
rm -rf .github

# Re-initialize
git init
git branch -M main

# Start over from Hour 1
```

---

## What's Next (Phase 1)

After this infrastructure is complete:

1. **Create base classes** (2 weeks)
   - `GeneNetwork` (inherits from nothing, but designed for Mesa compatibility)
   - `Gene` entity
   - `Individual` agent

2. **Create first expression model** (1 week)
   - `SimpleLinearExpression`
   - Test with theory validation

3. **Create first selection model** (1 week)
   - `ProportionalFitness`
   - Test with Wright-Fisher theory

4. **Documentation & examples** (2 weeks)
   - Getting Started guide
   - First complete example

---

## Troubleshooting

### Issue: `pip install -e .` fails

**Cause:** pyproject.toml syntax error

**Fix:**
```bash
# Check syntax
python -m tomllib pyproject.toml  # Python 3.11+
# or
python -c "import toml; toml.load('pyproject.toml')"
```

### Issue: GitHub Actions shows in web, but not `/.github/workflows/tests.yml`

**Cause:** File path issue

**Fix:**
```bash
# Verify exact path
ls -la .github/workflows/
# Should show: tests.yml

# Git issue (file not added)
git add .github/
git commit -m "ci: add GitHub Actions workflow"
```

### Issue: pytest can't find tests

**Cause:** conftest.py missing or import issues

**Fix:**
```bash
# Verify structure
tree tests/
# Should show:
#   tests/
#   ├── __init__.py
#   ├── conftest.py
#   └── test_*.py

# Try explicit path
pytest tests/test_placeholder.py -v
```

---

## Success Criteria

Phase 0 complete when:

- [ ] `git log` shows initial commit with infrastructure files
- [ ] `pip install -e .` works without errors
- [ ] `pytest tests/` shows all tests passing
- [ ] No `__pycache__`, `.coverage`, or `.pyc` files in repository
- [ ] `.github/workflows/tests.yml` is tracked by git
- [ ] `README.md`, `CONTRIBUTING.md`, `LICENSE` are visible on GitHub
- [ ] All templates deployed to their final locations
- [ ] Pre-commit checklist printed and posted near monitor

---

## Estimated Timeline

| Hour | Activity | Duration | Status |
|------|----------|----------|--------|
| 1 | Directories + templates | 60 min | Quick |
| 2 | Deploy critical files | 60 min | Copy/Paste |
| 3 | CI/CD + Testing | 45 min | Mostly templates |
| 4 | Git + Verification | 45 min | Standard git ops |

**Total: 4 hours**

**Most time is reading/verification. Actual file operations: 15 minutes.**

---

**Status:** READY FOR EXECUTION

**Next Step:** Print this runbook, execute Hour 1, then continue

**Questions?** Reference `STANDARDS_GAP_ANALYSIS.md` for detailed rationale
