# Round 29: crane-keep variants. "" = lowered (recommended; day + night), "raised" = night; map sprites for both.
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$jobs = @(@("close",""), @("close","raised"), @("mapprev","lowered"), @("mapprev","raised"))
foreach ($j in $jobs) {
  $dst = if ($j[0] -eq "mapprev") { "$o\scratch\opt" } else { "$o\scratch\bl" }
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- meridian_hq $dst $j[0] $j[1] > "$o\scratch\log_$($j[0])_$($j[1]).log" 2>&1
  Write-Output "$($j[0]) $($j[1]) ok=$(Select-String -Path "$o\scratch\log_$($j[0])_$($j[1]).log" -Pattern DONE -Quiet)"
}
