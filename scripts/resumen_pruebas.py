"""Escribe un resumen de los resultados de pytest en la página del workflow de GitHub Actions."""
import os
import xml.etree.ElementTree as ET

RUTA = "reports/junit.xml"

if os.path.exists(RUTA) and os.environ.get("GITHUB_STEP_SUMMARY"):
    raiz = ET.parse(RUTA).getroot()
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz)
    total = sum(int(s.get("tests", 0)) for s in suites)
    fallidas = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)
    omitidas = sum(int(s.get("skipped", 0)) for s in suites)
    lineas = ["## Resultados de las pruebas", "",
              f"**{total - fallidas - omitidas} aprobadas · {fallidas} fallidas · {omitidas} omitidas** (de {total})", "",
              "| Resultado | Archivo | Prueba |", "|---|---|---|"]
    for suite in suites:
        for caso in suite.iter("testcase"):
            if caso.find("failure") is not None or caso.find("error") is not None:
                marca = "❌"
            elif caso.find("skipped") is not None:
                marca = "⏭️"
            else:
                marca = "✅"
            archivo = caso.get("classname", "").split(".")[-1]
            lineas.append(f"| {marca} | `{archivo}` | `{caso.get('name')}` |")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as salida:
        salida.write("\n".join(lineas) + "\n")
