param([string]$FileName='preview.pptx',[string]$Target='native-slides')
$ErrorActionPreference='Stop'
$taskDir='C:\Users\piatkowskigs\Desktop\.submission-abstract-disclosure-review'
$nativeDir=Join-Path $taskDir $Target
New-Item -ItemType Directory -Path $nativeDir -Force | Out-Null
$powerpoint=New-Object -ComObject PowerPoint.Application
$deck=$null
try {
 $deck=$powerpoint.Presentations.Open((Join-Path $taskDir $FileName),$true,$false,$false)
 $deck.Export($nativeDir,'PNG',1280,720)
 Write-Output ('PowerPoint slides: '+$deck.Slides.Count)
} finally {if($deck){$deck.Close()};if($powerpoint.Presentations.Count -eq 0){$powerpoint.Quit()}}
