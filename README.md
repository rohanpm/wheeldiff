# wheeldiff

Find differences between two Python wheels.

[![PyPI](https://img.shields.io/pypi/v/wheeldiff)](https://pypi.org/project/wheeldiff/)

<!--TOC-->

- [wheeldiff](#wheeldiff)
  - [Overview](#overview)
  - [Examples](#examples)
  - [License](#license)

<!--TOC-->

## Overview

`wheeldiff` is a command-line tool to show differences between two Python wheels.

`wheeldiff` exits with an exit code of 2 if any differences were found, or 0 if no
differences were found.

Some types of difference can be ignored via the following options:

- `--ignore version`: ignore differences in version number
- `--ignore record`: ignore differences in dist-info `RECORD` file (checksums of wheel
  content)

## Examples

Finding various differences:

```
$ wheeldiff rpmdyn-2023.5.7-py3-none-any.whl rpmdyn-2023.5.7.3-py3-none-any.whl; $?
--- rpmdyn-2023.5.7-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn/__init__.py
+++ rpmdyn-2023.5.7.3-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn/__init__.py
@@ -1 +1 @@
-__version__ = '2023.5.7'  # generated by buildsys-dateversion
+__version__ = '2023.5.7.3'  # generated by buildsys-dateversion
--- rpmdyn-2023.5.7-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn-$VERSION.dist-info/METADATA
+++ rpmdyn-2023.5.7.3-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn-$VERSION.dist-info/METADATA
@@ -1,6 +1,6 @@
 Metadata-Version: 2.1
 Name: rpmdyn
-Version: 2023.5.7
+Version: 2023.5.7.3
 Summary: Alternative dynamic RPM bindings for Python
 Author-email: Rohan McGovern <rohan@mcgovern.id.au>
 Maintainer-email: Rohan McGovern <rohan@mcgovern.id.au>
--- rpmdyn-2023.5.7-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn-$VERSION.dist-info/RECORD
+++ rpmdyn-2023.5.7.3-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn-$VERSION.dist-info/RECORD
@@ -1,5 +1,5 @@
 rpmdyn.pth,sha256=wXLoNTnlvRUqLcf1828EUQvWW7oeVpjvk8nnKz50dvk,24
-rpmdyn/__init__.py,sha256=TzLtWAxsW-BR7PfWUHCs7VZDzRZs1LLMqiBp7FoCHdA,62
+rpmdyn/__init__.py,sha256=itJUHIwN99xPHGm8aXUcGwJoiSHkT6ZApzwAxVizlbs,64
 rpmdyn/_const.py,sha256=UIJUExCXjAoT3SpWK3UVIheSRsbjzwv7lCNUXxJVGcw,24226
 rpmdyn/_ffi.py,sha256=-7Y_1R6sI9vhM7wc-t05-ImEsKdo_wXmdb3iDFgF27M,3809
 rpmdyn/_keyring.py,sha256=FmlbH3F9-UPqfpqxSKlg715UB7gleSeVjchkR29wprg,157
@@ -7,8 +7,8 @@
 rpmdyn/_rpm.py,sha256=J__OwBn4FdP-nVqdyPiHIx2BtuBNcFVrXbgu1UrpST8,513
 rpmdyn/_transaction.py,sha256=sq_iWJAhkXb5WJ9ryYqHjvN6B-uIihz8iF6L_OCvu5o,3445
 rpmdyn/rpmdyn.pth,sha256=wXLoNTnlvRUqLcf1828EUQvWW7oeVpjvk8nnKz50dvk,24
-rpmdyn-2023.5.7.dist-info/LICENSE,sha256=OXLcl0T2SZ8Pmy2_dmlvKuetivmyPd5m1q-Gyd-zaYY,35149
-rpmdyn-2023.5.7.dist-info/METADATA,sha256=VMv3OH7xsu_iJc_4aLpS7U8QpuEvMo2z0T860eUBCCM,43843
-rpmdyn-2023.5.7.dist-info/WHEEL,sha256=pkctZYzUS4AYVn6dJ-7367OJZivF2e8RA9b_ZBjif18,92
-rpmdyn-2023.5.7.dist-info/top_level.txt,sha256=juyQtSPbaEJ3AiMzwEI5aX67FyfxqrpJ-mVuZQayvIU,7
-rpmdyn-2023.5.7.dist-info/RECORD,,
+rpmdyn-2023.5.7.3.dist-info/LICENSE,sha256=OXLcl0T2SZ8Pmy2_dmlvKuetivmyPd5m1q-Gyd-zaYY,35149
+rpmdyn-2023.5.7.3.dist-info/METADATA,sha256=PHfp8XarCfrc6-wYaUfF_m5pgZp4CoDKSeFcyEn4Yqs,43845
+rpmdyn-2023.5.7.3.dist-info/WHEEL,sha256=pkctZYzUS4AYVn6dJ-7367OJZivF2e8RA9b_ZBjif18,92
+rpmdyn-2023.5.7.3.dist-info/top_level.txt,sha256=juyQtSPbaEJ3AiMzwEI5aX67FyfxqrpJ-mVuZQayvIU,7
+rpmdyn-2023.5.7.3.dist-info/RECORD,,
2
```

Suppressing version number differences:

```
$ wheeldiff rpmdyn-2023.5.7-py3-none-any.whl rpmdyn-2023.5.7.3-py3-none-any.whl --ignore version; echo $?
--- rpmdyn-2023.5.7-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn-$VERSION.dist-info/RECORD
+++ rpmdyn-2023.5.7.3-py3-none-any.whl/rpmdyn-$VERSION/rpmdyn-$VERSION.dist-info/RECORD
@@ -1,5 +1,5 @@
 rpmdyn.pth,sha256=wXLoNTnlvRUqLcf1828EUQvWW7oeVpjvk8nnKz50dvk,24
-rpmdyn/__init__.py,sha256=TzLtWAxsW-BR7PfWUHCs7VZDzRZs1LLMqiBp7FoCHdA,62
+rpmdyn/__init__.py,sha256=itJUHIwN99xPHGm8aXUcGwJoiSHkT6ZApzwAxVizlbs,64
 rpmdyn/_const.py,sha256=UIJUExCXjAoT3SpWK3UVIheSRsbjzwv7lCNUXxJVGcw,24226
 rpmdyn/_ffi.py,sha256=-7Y_1R6sI9vhM7wc-t05-ImEsKdo_wXmdb3iDFgF27M,3809
 rpmdyn/_keyring.py,sha256=FmlbH3F9-UPqfpqxSKlg715UB7gleSeVjchkR29wprg,157
@@ -8,7 +8,7 @@
 rpmdyn/_transaction.py,sha256=sq_iWJAhkXb5WJ9ryYqHjvN6B-uIihz8iF6L_OCvu5o,3445
 rpmdyn/rpmdyn.pth,sha256=wXLoNTnlvRUqLcf1828EUQvWW7oeVpjvk8nnKz50dvk,24
 rpmdyn-$VERSION.dist-info/LICENSE,sha256=OXLcl0T2SZ8Pmy2_dmlvKuetivmyPd5m1q-Gyd-zaYY,35149
-rpmdyn-$VERSION.dist-info/METADATA,sha256=VMv3OH7xsu_iJc_4aLpS7U8QpuEvMo2z0T860eUBCCM,43843
+rpmdyn-$VERSION.dist-info/METADATA,sha256=PHfp8XarCfrc6-wYaUfF_m5pgZp4CoDKSeFcyEn4Yqs,43845
 rpmdyn-$VERSION.dist-info/WHEEL,sha256=pkctZYzUS4AYVn6dJ-7367OJZivF2e8RA9b_ZBjif18,92
 rpmdyn-$VERSION.dist-info/top_level.txt,sha256=juyQtSPbaEJ3AiMzwEI5aX67FyfxqrpJ-mVuZQayvIU,7
 rpmdyn-$VERSION.dist-info/RECORD,,
2
```

Suppressing version and RECORD differences; in this case, there are no remaining
differences, so no output is generated and the exit code is 0.

```
$ wheeldiff rpmdyn-2023.5.7-py3-none-any.whl rpmdyn-2023.5.7.3-py3-none-any.whl --ignore version,record; echo $?
0
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
