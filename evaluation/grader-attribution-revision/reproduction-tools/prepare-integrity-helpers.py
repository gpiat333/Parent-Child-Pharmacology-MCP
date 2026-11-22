from pathlib import Path
W=Path(__file__).parent;OLD=W.parent/'.submission-report-context-review'
for name in ['check-artifact-metrics.py','refresh-final-manifests.py','verify-final-integrity.py']:
 text=(OLD/name).read_text(encoding='utf-8').replace('evaluation/report-context-revision','evaluation/grader-attribution-revision').replace('report-context-revision/REPORT.md','grader-attribution-revision/REPORT.md')
 if name=='check-artifact-metrics.py':
  text=text.replace("f'Slide 44 {arm} time', cell(44, 4, col), str(B[arm]['median_seconds'])","f'Slide 44 {arm} new answers', cell(44, 4, col), '0'")
  text=text.replace("expected = ['562 passed',", "expected = ['562 passed', '30 passed',")
 if name=='verify-final-integrity.py':
  start=text.index("assert summary['chat']['diagnostic_grading']['task_fulfilled'] == 20")
  end=text.index("assert not summary['github_push']",start)
  text=text[:start]+"assert summary['grader_tests']['tests'] == 30\nassert summary['calibration']['controls'] == 10\nassert not summary['answer_generation_repeated'] and not summary['runtime_source_changed']\nassert not summary['deployment_performed_this_revision']\n"+text[end:]
 text=text.replace('.read_text()',".read_text(encoding='utf-8-sig')")
 (W/name).write_text(text,encoding='utf-8')
print('Prepared current-revision metric and integrity checks.')
