# jinja templates

REPORT_TEMPLATE = """
<head>
<!-- Defie font size, family, and page margins left, right, top, bottom-->
<style>
body {
    font-size: 12pt;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    margin: 25mm 25mm 25mm 25mm;
}
</style>
</head>
<br/>
<h1>Report</h1>

<h3>Reason hierarchy</h3>

<p>{{ reason_hierarchy }}</p>

<div style="width: 100%; overflow: auto;">
{{ argmap_svg }}
</div>

<h3>Essay annotation</h3>
<div style="width: 100%; overflow: auto;">
{{ annotation_svg }}
</div>

<h3>Evaluation</h3>


<h3>Tests</h3>
<p>
<details open><summary>Test 1</summary>more content</details>
</p>
"""

