
import subprocess
import sys
import tempfile
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    PageBreak,
    Image 
)
from xml.sax.saxutils import escape

# ==================================================
# CONFIGURATION
# ==================================================

PLATFORMS = ["8051", "STM32"]

REPORT_FILE = Path("evaluation_report.md")


# ==================================================
# REPOSITORY DOWNLOAD
# ==================================================

def clone_repository(repo_url, destination):
    print("\nDownloading student repository...")

    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(destination)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("[FAIL] Could not download repository.")
        print(result.stderr)
        return False

    print("[PASS] Repository downloaded.")
    return True


# ==================================================
# PROJECT IDENTIFICATION
# ==================================================

def has_project_files(folder, platform):

    if platform == "8051":
        return (
            any(folder.glob("*.uvproj")) or
            any(folder.glob("*.uvprojx"))
        )

    elif platform == "STM32":
        return any(folder.glob("*.ioc"))

    return False


# ==================================================
# TASK DISCOVERY
# ==================================================


def discover_tasks(platform_path, platform):

    tasks = []

    cat_folders = [
        folder for folder in platform_path.iterdir()
        if folder.is_dir() and not folder.name.startswith(".")
    ]

    for cat_folder in sorted(cat_folders):

        # If the CAT folder itself is a project, use it.
        if has_project_files(cat_folder, platform):
            tasks.append(cat_folder)
            continue

        # Otherwise, search recursively for actual project files.
        if platform == "8051":
            patterns = ["*.uvproj", "*.uvprojx"]
        else:
            patterns = ["*.ioc"]

        discovered_projects = set()

        for pattern in patterns:
            for project_file in cat_folder.rglob(pattern):

                # Ignore hidden directories and Git metadata.
                if any(
                    part.startswith(".")
                    for part in project_file.relative_to(
                        cat_folder
                    ).parts
                ):
                    continue

                discovered_projects.add(project_file.parent)

        tasks.extend(sorted(discovered_projects))

    return sorted(tasks)



# ==================================================
# CHECK HELPERS
# ==================================================

def check_pattern(folder, pattern):

    if not folder.is_dir():
        return False

    return any(folder.glob(pattern))


def check_item(folder, item):

    return (folder / item).exists()


def check_case_insensitive_file(folder, filename):

    if not folder.is_dir():
        return False

    return any(
        file.name.lower() == filename.lower()
        for file in folder.iterdir()
        if file.is_file()
    )


# ==================================================
# 8051 EVALUATION
# ==================================================

def evaluate_8051(task_path):

    results = []

    results.append((
        "Keil project (*.uvproj or *.uvprojx)",
        check_pattern(task_path, "*.uvproj") or
        check_pattern(task_path, "*.uvprojx")
    ))

    results.append((
        "C source file (*.c)",
        check_pattern(task_path, "*.c")
    ))

    results.append((
        "STARTUP.A51",
        check_case_insensitive_file(task_path, "STARTUP.A51")
    ))

    objects_folder = task_path / "Objects"

    results.append((
        "Objects/ folder",
        objects_folder.is_dir()
    ))

    results.append((
        "Objects/*.hex",
        check_pattern(objects_folder, "*.hex")
    ))

    return results


# ==================================================
# STM32 EVALUATION
# ==================================================

def evaluate_stm32(task_path):

    results = []

    results.append((
        ".ioc file",
        check_pattern(task_path, "*.ioc")
    ))

    results.append((
        ".mxproject",
        check_item(task_path, ".mxproject")
    ))

    results.append((
        "Core/ folder",
        (task_path / "Core").is_dir()
    ))

    results.append((
        "Drivers/ folder",
        (task_path / "Drivers").is_dir()
    ))

    md_folder = task_path / "MDK-ARM"

    results.append((
        "MDK-ARM/ folder",
        md_folder.is_dir()
    ))

    results.append((
        "MDK-ARM/*.uvprojx",
        check_pattern(md_folder, "*.uvprojx")
    ))

    results.append((
    "MDK-ARM/startup_*.s",
    check_pattern(md_folder, "startup_*.s")
    ))

    return results


# ==================================================
# README COLLECTION
# ==================================================

def read_readme(task_path):

    readme_path = task_path / "README.md"

    if not readme_path.is_file():
        return None

    try:
        return readme_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

    except OSError:
        return None


# ==================================================
# REPORT GENERATION
# ==================================================

def generate_report(repository):

    report = []

    total_tasks = 0
    passed_tasks = 0
    failed_tasks = 0

    total_checks = 0
    passed_checks = 0

    platform_failures = []

    report.append("# Foundations of IoT - Evaluation Report")
    report.append("")
    report.append(f"Repository: `{repository.name}`")
    report.append("")

    # Evaluate both platforms.
    for platform in PLATFORMS:

        report.append(f"# Platform: {platform}")
        report.append("")

        platform_path = repository / platform

        if not platform_path.is_dir():

            report.append("**FAIL: Platform folder is missing.**")
            report.append("")

            platform_failures.append(platform)
            continue

        tasks = discover_tasks(platform_path, platform)

        if not tasks:

            report.append("**FAIL: No project folders found.**")
            report.append("")

            platform_failures.append(platform)
            continue

        # Evaluate every discovered project.
        for task_path in tasks:

            total_tasks += 1

            task_name = task_path.relative_to(
                repository
            ).as_posix()

            print("TASK PATH:", task_path.resolve())
            print("TASK NAME:", task_name)

            report.append(f"## {task_name}")
            report.append(f"<!-- TASK_PATH: {task_path.resolve()} -->")
            report.append("")
            report.append("### File checks")
            report.append("")

            if platform == "8051":
                results = evaluate_8051(task_path)

            else:
                results = evaluate_stm32(task_path)

            task_passed = True

            # Record file check results.
            for item, exists in results:

                total_checks += 1

                if exists:

                    passed_checks += 1
                    report.append(f"- [PASS] {item}")

                else:

                    task_passed = False
                    report.append(f"- [FAIL] {item}")

            # Check README.
            readme_content = read_readme(task_path)

            total_checks += 1

            if readme_content is None:

                task_passed = False

                report.append(
                    "- [FAIL] README.md is missing or unreadable."
                )

            else:

                passed_checks += 1
                report.append("- [PASS] README.md exists.")

            report.append("")

            status = "PASSED" if task_passed else "FAILED"

            report.append(f"**Task result: {status}**")
            report.append("")

            # Include README contents.
            report.append("### README content")
            report.append("")

            if readme_content is None:

                report.append("*No README content available.*")

            else:

                report.append(readme_content)

            report.append("")
            report.append("---")
            report.append("")

            if task_passed:
                passed_tasks += 1

            else:
                failed_tasks += 1

    # ==================================================
    # OVERALL SUMMARY
    # ==================================================

    overall_passed = (
        total_tasks > 0
        and failed_tasks == 0
        and len(platform_failures) == 0
    )

    report.append("# Overall Summary")
    report.append("")

    report.append(f"- Tasks discovered: {total_tasks}")
    report.append(f"- Tasks passed: {passed_tasks}")
    report.append(f"- Tasks failed: {failed_tasks}")
    report.append(
        f"- File checks passed: {passed_checks}/{total_checks}"
    )

    if platform_failures:

        report.append("")
        report.append("### Platform errors")

        for platform in platform_failures:
            report.append(f"- Missing or empty platform: {platform}")

    report.append("")

    status = "PASSED" if overall_passed else "FAILED"

    report.append(f"## Overall Status: {status}")

    # Save report.
    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    generate_pdf(repository)

    # Display summary.
    print("\n========== EVALUATION SUMMARY ==========")

    print(f"Tasks discovered: {total_tasks}")
    print(f"Tasks passed: {passed_tasks}")
    print(f"Tasks failed: {failed_tasks}")

    print(
        f"File checks passed: {passed_checks}/{total_checks}"
    )

    print(f"Overall status: {status}")

    print("\nReport saved to:")
    print(REPORT_FILE.resolve())

    return overall_passed

# ==================================================
# PDF GENERATION 
# ==================================================

def generate_pdf(repository):

    pdf_file = Path("evaluation_report.pdf")

    styles = getSampleStyleSheet()

    # Main title
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        leading=26,
        textColor=colors.HexColor("#17365D"),
        alignment=TA_CENTER,
        spaceAfter=20
    ))

    # Platform headings
    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=16,
        spaceAfter=10
    ))

    # Task headings
    styles.add(ParagraphStyle(
        name="SubHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#2874A6"),
        spaceBefore=12,
        spaceAfter=7
    ))

    styles.add(ParagraphStyle(
        name="SmallHeading",
        parent=styles["Heading3"],
        fontSize=10,
        textColor=colors.HexColor("#34495E"),
        spaceBefore=8,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="PassStyle",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#16803C"),
        fontSize=9,
        leading=13
    ))

    styles.add(ParagraphStyle(
        name="FailStyle",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#C0392B"),
        fontSize=9,
        leading=13
    ))

    document = SimpleDocTemplate(
        str(pdf_file),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=23 * mm,
        bottomMargin=20 * mm
    )

    content = []

    markdown = REPORT_FILE.read_text(encoding="utf-8")

    current_task = None

    for line in markdown.splitlines():

        line = line.strip()

        # Read the exact task directory recorded in the report.
        task_match = re.match(
            r"<!-- TASK_PATH: (.*?) -->",
            line
        )

        if task_match:
            current_task = Path(task_match.group(1))
            continue

        if not line:
            content.append(Spacer(1, 5))
            continue

        # Separators
        if line == "---":
            content.append(HRFlowable(
                width="100%",
                color=colors.HexColor("#D5DDE5"),
                thickness=0.8
            ))
            content.append(Spacer(1, 8))
            continue

        # Main title
        if line.startswith("# "):

            text = escape(line[2:])

            content.append(
                Paragraph(text, styles["ReportTitle"])
            )

            continue

        # Task heading
        if line.startswith("## "):

            heading = line[3:]
            
            content.append(
                Paragraph(
                    escape(heading),
                    styles["SectionHeading"]
                )
            )

            continue

        # Subheading
        if line.startswith("### "):

            content.append(
                Paragraph(
                    escape(line[4:]),
                    styles["SmallHeading"]
                )
            )

            continue

        # Markdown image
        image_match = re.match(
            r"!\[(.*?)\]\((.*?)\)",
            line
        )

        if image_match:

            image_path = image_match.group(2).strip()

            if current_task is not None:

                full_image_path = (
                    current_task / image_path
                ).resolve()


                print("\n--- IMAGE DEBUG ---")
                print("Repository:", repository.resolve())
                print("Current task:", current_task.resolve())
                print("Image path from README:", image_path)
                print("Full image path:", full_image_path)
                print("File exists:", full_image_path.is_file())
                print("-------------------\n")

                if full_image_path.is_file():

                    img = Image(str(full_image_path))

                    max_width = 160 * mm
                    max_height = 110 * mm

                    scale = min(
                        max_width / img.imageWidth,
                        max_height / img.imageHeight,
                        1
                    )

                    img.drawWidth = img.imageWidth * scale
                    img.drawHeight = img.imageHeight * scale

                    content.append(Spacer(1, 8))
                    content.append(img)
                    content.append(Spacer(1, 10))

                else:

                    content.append(
                        Paragraph(
                            "[Diagram not found: "
                            + escape(image_path) + "]",
                            styles["FailStyle"]
                        )
                    )

            continue

        # PASS / FAIL formatting
        if line.startswith("- [PASS]"):

            content.append(
                Paragraph(
                    escape(line),
                    styles["PassStyle"]
                )
            )

            continue

        if line.startswith("- [FAIL]"):

            content.append(
                Paragraph(
                    escape(line),
                    styles["FailStyle"]
                )
            )

            continue

        # Normal text
        text = escape(line)

        text = text.replace("**", "")
        text = text.replace("`", "")

        content.append(
            Paragraph(text, styles["ReportBody"])
        )

    # Header and footer
    def add_page_details(canvas, doc):

        canvas.saveState()

        page_width, page_height = A4

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(
            colors.HexColor("#64748B")
        )

        canvas.drawString(
            20 * mm,
            page_height - 13 * mm,
            "FOUNDATIONS OF IoT | EVALUATION REPORT"
        )

        canvas.drawRightString(
            page_width - 20 * mm,
            12 * mm,
            f"Page {doc.page}"
        )

        canvas.setStrokeColor(
            colors.HexColor("#D5DDE5")
        )

        canvas.line(
            20 * mm,
            page_height - 16 * mm,
            page_width - 20 * mm,
            page_height - 16 * mm
        )

        canvas.restoreState()

    document.build(
        content,
        onFirstPage=add_page_details,
        onLaterPages=add_page_details
    )

    print("\nPDF report saved to:")
    print(pdf_file.resolve())


# ==================================================
# MAIN
# ==================================================

def main():

    if len(sys.argv) >= 2:

        repo_url = sys.argv[1].strip()

    else:

        repo_url = input(
            "Enter the public GitHub repository URL: "
        ).strip()

    if not repo_url.startswith("https://github.com/"):

        print("ERROR: Please enter a valid GitHub HTTPS URL.")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:

        repository = Path(temp_dir) / "student_repo"

        if not clone_repository(repo_url, repository):
            return False

        return generate_report(repository)


# ==================================================
# PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":

    if not main():
        sys.exit(1)
