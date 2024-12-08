#!/usr/bin/env bash
set -euo pipefail

# Check for required environment variables
: "${TEMPLATE_PATH:?TEMPLATE_PATH not set. Please set it in Taskfile.yml vars.}"
: "${CONFIG_PATH:?CONFIG_PATH not set. Please set it in Taskfile.yml vars.}"

echo "Project Status"
echo "=============="
echo

# Check directories
echo "Directories:"
for dir in content assets/templates config output; do
    if [ -d "$dir" ]; then
        echo "✓ $dir"
    else
        echo "✗ $dir (missing)"
    fi
done

# Check virtual environment
echo -e "\nVirtual Environment:"
if [ -d ".venv" ]; then
    echo "✓ .venv directory present"
    if source .venv/bin/activate; then
        echo -n "Python version: "
        python --version || echo "Unable to determine Python version"
    else
        echo "✗ Failed to activate virtual environment"
    fi
else
    echo "✗ No .venv directory found. Run 'task install' to create it."
fi

# Check template
echo -e "\nTemplate:"
if [ -f "${TEMPLATE_PATH}" ]; then
    echo "✓ Template found at ${TEMPLATE_PATH}"
else
    echo "✗ Missing template (${TEMPLATE_PATH})"
fi

# Check config
echo -e "\nConfiguration:"
if [ -f "${CONFIG_PATH}" ]; then
    echo "✓ Configuration found at ${CONFIG_PATH}"
else
    echo "✗ Missing config file (${CONFIG_PATH})"
fi

# Check content files
echo -e "\nContent Files:"
content_count=$(ls content/*.yml 2>/dev/null | wc -l || true)
if [ "$content_count" -gt 0 ]; then
    echo "✓ Found $content_count content file(s):"
    ls -1 content/*.yml 2>/dev/null | sed 's/^/  /'
else
    echo "✗ No content files found in content/ directory"
fi

# Check output files
echo -e "\nOutput Files:"
pptx_count=$(ls output/*.pptx 2>/dev/null | wc -l || true)
pdf_count=$(ls output/*.pdf 2>/dev/null | wc -l || true)
if [ "$pptx_count" -gt 0 ] || [ "$pdf_count" -gt 0 ]; then
    echo "Presentations (PPTX): $pptx_count"
    echo "PDFs: $pdf_count"
else
    echo "No output files generated yet."
fi
