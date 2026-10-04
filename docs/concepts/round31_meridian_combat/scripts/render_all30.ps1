# Round 30: Meridian close (day + night), 16-frame animation, and every HQ map sprite for the v5 city map.
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$jobs = @(@("meridian_hq","close"), @("meridian_hq","anim"), @("meridian_hq","map"), @("solace_hq","map"), @("halcyon_hq","map"), @("orbital_hq","map"), @("rebel_cell_hq","map"))
foreach ($j in $jobs) {
  $dst = if ($j[1] -eq "map") { "$o\scratch\map" } else { "$o\scratch\bl" }
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- $j[0] $dst $j[1] > "$o\scratch\log_$($j[0])_$($j[1]).log" 2>&1
  Write-Output "$($j[0]) $($j[1]) ok=$(Select-String -Path "$o\scratch\log_$($j[0])_$($j[1]).log" -Pattern DONE -Quiet)"
}
