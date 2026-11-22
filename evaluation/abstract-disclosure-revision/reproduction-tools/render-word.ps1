param([string]$FileName='evaluation-updated.docx')
$ErrorActionPreference='Stop'
$taskDir='C:\Users\piatkowskigs\Desktop\.submission-abstract-disclosure-review'
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$doc=$null
try {
 $doc=$word.Documents.Open((Join-Path $taskDir $FileName),$false,$true)
 $doc.ExportAsFixedFormat((Join-Path $taskDir 'evaluation-updated.pdf'),17)
 Write-Output ('Word pages: '+$doc.ComputeStatistics(2))
} finally { if($doc){$doc.Close(0)};if($word.Documents.Count -eq 0){$word.Quit()} }
