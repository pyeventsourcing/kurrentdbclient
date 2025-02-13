# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import ssl
from pathlib import Path

# from tempfile import NamedTemporaryFile
from unittest import TestCase

BASE_DIR = Path(__file__).parents[1]


class TestDocs(TestCase):
    def setUp(self) -> None:
        self.setup_environ()
        # try:
        #     loop = asyncio.get_event_loop()
        # except RuntimeError as e:
        #     if str(e).startswith("There is no current event loop in thread"):
        #         loop = asyncio.new_event_loop()
        #         asyncio.set_event_loop(loop)
        #     else:
        #         raise

    def setup_environ(self) -> None:
        os.environ["ESDB_ROOT_CERTIFICATES"] = ssl.get_server_certificate(
            addr=("localhost", 2114)
        )
        os.environ["ESDB_URI"] = "kdb://admin:changeit@localhost:2114"

    def tearDown(self) -> None:
        del os.environ["ESDB_URI"]
        try:
            del os.environ["ESDB_ROOT_CERTIFICATES"]
        except KeyError:
            pass

    def test_readme(self) -> None:
        self._out = ""

        path = BASE_DIR / "README.md"
        if not path.exists():
            self.fail(f"README file not found: {path}")
        self.check_code_snippets_in_file(path)

    def check_code_snippets_in_file(self, doc_path: Path) -> None:  # noqa: C901
        # Extract lines of Python code from the README.md file.

        PRINT_BLOCK_LINE_NUMBERS = True
        if PRINT_BLOCK_LINE_NUMBERS:
            lines = ["import sys"]
        else:
            lines = []
        num_code_lines = 0
        num_code_lines_in_block = 0
        is_code = False
        is_md = False
        is_rst = False
        last_line = ""
        is_literalinclude = False
        with doc_path.open() as doc_file:
            for line_index, orig_line in enumerate(doc_file, start=-len(lines)):
                line = orig_line.strip("\n")
                if line.startswith("```python"):
                    # Start markdown code block.
                    if is_rst:
                        self.fail(
                            "Markdown code block found after restructured text block "
                            "in same file."
                        )
                    is_code = True
                    is_md = True
                    if PRINT_BLOCK_LINE_NUMBERS:
                        line = (
                            f"sys.stderr.write('Block on line: {line_index}\\n') and"
                            " sys.stderr.flush()"
                        )
                    else:
                        line = ""
                    num_code_lines_in_block = 0
                elif is_code and is_md and line.startswith("```"):
                    # Finish markdown code block.
                    if not num_code_lines_in_block:
                        self.fail(f"No lines of code in block: {line_index + 1}")
                    is_code = False
                    line = ""
                elif is_code and is_rst and line.startswith("```"):
                    # Can't finish restructured text block with markdown.
                    self.fail(
                        "Restructured text block terminated with markdown format '```'"
                    )
                elif (
                    line.startswith(".. code:: python")
                    or line.strip() == ".."
                    # and "exclude-when-testing" not in last_line
                ):
                    # Start restructured text code block.
                    if is_md:
                        self.fail(
                            "Restructured text code block found after markdown block "
                            "in same file."
                        )
                    is_code = True
                    is_rst = True
                    line = ""
                    num_code_lines_in_block = 0
                elif line.startswith(".. literalinclude::"):
                    is_literalinclude = True
                    line = ""

                elif is_literalinclude:
                    if "pyobject" in line:
                        # Assume ".. literalinclude:: ../../xxx/xx.py"
                        # Or ".. literalinclude:: ../xxx/xx.py"
                        module = last_line.strip().split(" ")[-1][:-3]
                        module = module.lstrip("./")
                        module = module.replace("/", ".")
                        # Assume "    :pyobject: xxxxxx"
                        pyobject = line.strip().split(" ")[-1]
                        statement = f"from {module} import {pyobject}"
                        line = statement
                        is_literalinclude = False

                elif is_code and is_rst and line and not line.startswith(" "):
                    # Finish restructured text code block.
                    if not num_code_lines_in_block:
                        self.fail(f"No lines of code in block: {line_index + 1}")
                    is_code = False
                    line = ""
                elif is_code:
                    # Process line in code block.
                    if is_rst:
                        # Restructured code block normally indented with four spaces.
                        if len(line.strip()):
                            if not line.startswith("    "):
                                self.fail(
                                    f"Code line needs 4-char indent: {repr(line)}: "
                                    f"{doc_path}"
                                )
                            # Strip four chars of indentation.
                            line = line[4:]

                    if len(line.strip()):
                        num_code_lines_in_block += 1
                        num_code_lines += 1
                else:
                    line = ""

                if "get_server_certificate" in line:
                    line = line.replace("2113", "2114")

                lines.append(line)
                last_line = orig_line

        print(f"{num_code_lines} lines of code in {doc_path}")

        for i, line in enumerate(lines):
            if "set_tracer_provider(" in line:
                lines[i] = ""
            if "instrument()" in line:
                lines[i] = ""
            if "uninstrument()" in line:
                lines[i] = ""

        source = "\n".join(lines) + "\n"

        # # Write the code into a temp file.
        # tempfile = NamedTemporaryFile("w+")
        # tempfile.writelines(source)
        # tempfile.flush()

        exec(
            compile(source=source, filename=doc_path, mode="exec"), globals(), globals()
        )
        return

        # print(Path.cwd())
        # print("\n".join(lines) + "\n")
        #
        # # Run the code and catch errors.
        # p = Popen(
        #     [sys.executable, temp_path],
        #     stdout=PIPE,
        #     stderr=PIPE,
        #     env={"PYTHONPATH": BASE_DIR},
        # )
        # print(sys.executable, temp_path, PIPE)
        # out, err = p.communicate()
        # decoded_out = out.decode("utf8").replace(temp_path, str(doc_path))
        # decoded_err = err.decode("utf8").replace(temp_path, str(doc_path))
        # exit_status = p.wait()
        #
        # print(decoded_out)
        # print(decoded_err)
        #
        # # Check for errors running the code.
        # if exit_status:
        #     self.fail(decoded_out + decoded_err)
        #
        # # Close (deletes) the tempfile.
        # tempfile.close()


class TestDocsInsecure(TestDocs):
    def setup_environ(self) -> None:
        os.environ["ESDB_URI"] = "kdb://localhost:2113?Tls=false"
