# Round 28: Meridian texture variants (close night + map sprite each); t3 (recommended) close day + night.
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$jobs = @(@("close","t1"), @("close","t2"), @("close",""), @("close","t4"), @("mapprev","t1"), @("mapprev","t2"), @("mapprev","t3"), @("mapprev","t4"))
foreach ($j in $jobs) {
  $dst = if ($j[0] -eq "mapprev") { "$o\scratch\opt" } else { "$o\scratch\bl" }
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- meridian_hq $dst $j[0] $j[1] > "$o\scratch\log_$($j[0])_$($j[1]).log" 2>&1
  Write-Output "$($j[0]) $($j[1]) ok=$(Select-String -Path "$o\scratch\log_$($j[0])_$($j[1]).log" -Pattern DONE -Quiet)"
}
