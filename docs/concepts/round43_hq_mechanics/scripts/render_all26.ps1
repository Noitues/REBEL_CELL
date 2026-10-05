# Round 26: every Blender job (close-ups, variants, animation frames, Sites, map sprites).
$o = Split-Path -Parent $PSScriptRoot
$bl = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$jobs = @(
  @("meridian_hq","close",""), @("solace_hq","close",""), @("halcyon_hq","close",""), @("orbital_hq","close",""), @("orbital_hq","close","open"),
  @("solace_hq","anim",""), @("halcyon_hq","anim",""),
  @("solace_site","close",""), @("orbital_site","close",""), @("halcyon_site","close","sphinx"), @("halcyon_site","close","police"), @("meridian_site","close",""),
  @("meridian_hq","map",""), @("solace_hq","map",""), @("halcyon_hq","map",""), @("orbital_hq","map",""), @("rebel_cell_hq","map","")
)
foreach ($j in $jobs) {
  $dst = if ($j[1] -eq "map") { "$o\scratch\map" } else { "$o\scratch\bl" }
  & $bl -b --factory-startup --python "$o\scripts\hq_scene.py" -- $j[0] $dst $j[1] $j[2] > "$o\scratch\log_$($j[0])_$($j[1])_$($j[2]).log" 2>&1
  $ok = Select-String -Path "$o\scratch\log_$($j[0])_$($j[1])_$($j[2]).log" -Pattern "DONE" -Quiet
  Write-Output "$($j[0]) $($j[1]) $($j[2]) ok=$ok"
}
